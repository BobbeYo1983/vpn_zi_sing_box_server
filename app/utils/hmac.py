import hmac
import logging
import hashlib
import json
import time
from typing import Optional, Dict, Any
from django.conf import settings
from utils.result import Result
from urllib.parse import urlparse


logger = logging.getLogger(__name__)


def build_hmac_message(
    *,
    timestamp: int,
    method: str,
    path: str,
    payload: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Формирует каноническую строку для HMAC.

    ⚠️ ЭТА ФУНКЦИЯ ДОЛЖНА ИСПОЛЬЗОВАТЬСЯ
    И КЛИЕНТОМ, И СЕРВЕРОМ БЕЗ ИЗМЕНЕНИЙ
    """

    method = method.upper()

    # GET — всегда пустое тело
    if method == "GET" or payload is None:
        body = ""
    else:
        body = json.dumps(
            payload,
            separators=(",", ":"),
            sort_keys=True,
            ensure_ascii=False,
        )

    return "\n".join([
        str(timestamp),
        method,
        path,
        body,
    ])


def build_hmac_headers(
    *,
    secret: str,
    service: str,
    method: str,
    url: str,
    payload: Optional[Dict[str, Any]],
) -> Dict[str, str]:
    """
    Формирует HMAC-заголовки для подписи HTML-запросов на клиенте
    
    :param secret: Секрет
    :type secret: str
    :param service: Наименование сервиса отправителя
    :type service: str
    :param method: Тип метода эндпоинта
    :type method: str
    :param url: Путь к эндпоинту
    :type url: str
    :param payload: Тело запроса
    :type payload: Optional[Dict[str, Any]]
    :return: Заголовки
    :rtype: Dict[str, str]
    """

    timestamp = int(time.time())

    parsed = urlparse(url)
    path = parsed.path  # ❗ БЕЗ query string

    message = build_hmac_message(
        timestamp=timestamp,
        method=method,
        path=path,
        payload=payload,
    )

    signature = hmac.new(
        key=secret.encode(),
        msg=message.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return {
        "X-Service": service,
        "X-Timestamp": str(timestamp),
        "X-Signature": signature,
    }


def verify_hmac_request(request) -> Result:
    """
    Проверяет HMAC подпись входящего запроса
    """

    service = request.headers.get("X-Service")
    timestamp = request.headers.get("X-Timestamp")
    signature = request.headers.get("X-Signature")

    if not service or not timestamp or not signature:
        return Result.failure(
            error="Отсутствуют HMAC-заголовки",
            status_code=401,
        )

    secret = settings.HMAC_SERVICES.get(service)
    if not secret:
        return Result.failure(
            error="Запрос от неизвестного сервиса",
            status_code=401,
        )

    try:
        timestamp = int(timestamp)
    except ValueError:
        return Result.failure(
            error="Некорректная временная метка",
            status_code=401,
        )

    now = int(time.time())
    if abs(now - timestamp) > settings.HMAC_MAX_SKEW:
        return Result.failure(
            error="Временная метка запроса истекла",
            status_code=401,
        )

    payload = None
    if request.body:
        try:
            payload = json.loads(request.body.decode())
        except json.JSONDecodeError:
            payload = None

    message = build_hmac_message(
        timestamp=timestamp,
        method=request.method,
        path=request.path,  # ❗ Django path БЕЗ query
        payload=payload,
    )

    expected_signature = hmac.new(
        key=secret.encode(),
        msg=message.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        logger.warning(
            "Некорректная подпись запроса",
            extra={
                "service": service,
                "ip": request.META.get("REMOTE_ADDR"),
                "ua": request.META.get("HTTP_USER_AGENT"),
                "path": request.path,
            },
        )
        return Result.failure(
            error="Некорректная подпись запроса",
            status_code=401,
        )

    return Result.success()


class HMACAuthMiddleware:
    """
    Проверяет HMAC подпись входящих запросов
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # 🔓 Пропускаем публичные пути
        if request.path.startswith((
            "/admin/",
            "/static/",
            "/health/",
            
            "/api/yookassa/webhook/",
            "/payment/success/",
        )):
            return self.get_response(request)

        result = verify_hmac_request(request)

        if not result.ok:
            return result.to_json_response()

        return self.get_response(request)