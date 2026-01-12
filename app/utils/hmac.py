import hmac
import logging
import hashlib
import json
import time
from typing import Optional, Dict, Any
from django.conf import settings
from utils.result import Result


logger = logging.getLogger(__name__)


def build_hmac_headers(
    *,
    secret: str,
    service: str,
    method: str,
    url: str,
    payload: Optional[Dict[str, Any]],
) -> Dict[str, str]:
    """
    Формирует HMAC-заголовки для подписи HTML-запросов
    
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

    body_str = (
        json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        if payload and method.upper() != "GET"
        else ""
    )

    path = "/" + url.split("/", 3)[-1].split("?", 1)[0]

    message = "\n".join([
        str(timestamp),
        method.upper(),
        path,
        body_str,
    ])

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
        msg = "Отсутствуют HMAC-заголовки"
        logger.warning(
            msg,
            extra={
                "service": service,
                "timestamp": timestamp,
                "path": request.path,
            },
        )
        return Result.error(
            error=msg,
            status_code=401,
        )

    secret = settings.HMAC_SERVICES.get(service)
    if not secret:
        msg = "Запрос от неизвестного сервиса"
        logger.warning(
            msg,
            extra={
                "service": service,
                "path": request.path,
            },
        )
        return Result.error(
            error=msg,
            status_code=401,
        )

    try:
        timestamp = int(timestamp)
    except ValueError:
        msg = "Некорректная временная метка"
        logger.warning(
            msg,
            extra={"service": service},
        )
        return Result.error(
            error=msg,
            status_code=401,
        )

    now = int(time.time())
    if abs(now - timestamp) > settings.HMAC_MAX_SKEW:
        msg = "Временная метка запроса истекла"
        logger.warning(
            msg,
            extra={
                "service": service,
                "timestamp": timestamp,
                "now": now,
            },
        )
        return Result.error(
            error=msg,
            status_code=401,
        )

    body = request.body.decode() if request.body else ""

    message = "\n".join([
        str(timestamp),
        request.method.upper(),
        request.path,
        body,
    ])

    expected_signature = hmac.new(
        key=secret.encode(),
        msg=message.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        msg = "Некорректная подпись запроса"
        logger.warning(
            msg,
            extra={
                "service": service,
                "path": request.path,
            },
        )
        return Result.error(
            error=msg,
            status_code=401,
        )

    # ✅ Всё хорошо
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