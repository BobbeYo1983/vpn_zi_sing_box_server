from dataclasses import dataclass
from typing import Any, Optional, Dict, AnyStr
from django.http import JsonResponse

@dataclass(frozen=True)  # frozen=True делает объект неизменяемым (immutable)
class Result:
    """
    Стандартный результат любой операции.
    
    Гарантированные поля:
    - ok: bool — True при успехе, False при любой ошибке
    - data: Any|None — полезные данные только при ok=True
    - _error: str|None — человекочитаемое описание ошибки при ok=False  
    - status_code: int|None — HTTP-код (опционально, для HTTP-запросов)
    
    Использование:
        result = create_singbox_user(tg_id, tg_username)
        if not result.ok:
            logger.error(f"Ошибка: {result.error}", extra={"result": result})
    """
    
    ok: bool
    data: Optional[Any] = None
    _error: Optional[AnyStr] = None
    status_code: Optional[int] = None

    # getter, чтобы не перекрывал метод error ниже
    @property #добавь getter
    def error(self) -> Optional[str]:
        return self._error
    
    # region Фабричные методы (classmethods) — удобные конструкторы ###########################
    
    @classmethod
    def success(
        cls, 
        data: Optional[Any] = None, 
        status_code: Optional[int] = 200
    ) -> 'Result':
        """
        ✅ Быстрое создание успешного результата.
        
        Args:
            data: Полезные данные (dict с vless_uri, user_id и т.д.)
            status_code: HTTP 200/201/204 для логирования
            
        Returns:
            Result с ok=True
            
        Примеры:
            Result.success({"id": 123, "vless_uri": "vless://..."})
            Result.success()  # пустой успех
        """
        return cls(
            ok=True, 
            data=data, 
            status_code=status_code
        )
    
    @classmethod
    def error(
        cls, 
        error: AnyStr, 
        data: Optional[Any] = None,
        status_code: Optional[int] = 0
    ) -> 'Result':
        """
        ❌ Быстрое создание результата с ошибкой.
        
        Args:
            error: str — "timeout", "user_not_found", "httpx.ConnectError"
            data: редко используется, но можно передать partial response
            status_code: HTTP 400/500 или 0 для non-HTTP операций
            
        Примеры:
            Result.error("User already exists")
            Result.error(str(e), status_code=response.status_code)
        """
        return cls(
            ok=False,
            data=data,
            _error=str(error),  # всегда str для logger.error
            status_code=status_code
        )
    
    # endregion ########################################################################
    
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Сериализация в dict для JsonResponse/DRF Response или логирования.
        
        Используется в:
        - Django ViewSet: return Response(result.to_dict())
        - logger.extra={"result": result.to_dict()}
        - Telegram bot: bot.send_message(json.dumps(result.to_dict()))
        
        Returns:
            {"ok": bool, "data": Any, "error": str|None, "status_code": int|None}
        """
        return {
            "ok": self.ok,
            "data": self.data,
            "error": self._error,
            "status_code": self.status_code,
        }
    
    def is_success(self) -> bool:
        """Короткая проверка успеха (alias для result.ok)."""
        return self.ok
    
    def is_error(self) -> bool:
        """Короткая проверка ошибки."""
        return not self.ok
    
    def to_json_response(
        self, 
        status: Optional[int] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> JsonResponse:
        """Преобразовывает в JSON"""
        from django.http import JsonResponse
        
        response_data = {"status": "ok" if self.ok else "error"}
        if self.ok:
            response_data["data"] = self.data or {}
        else:
            response_data["error"] = self._error
        
        if extra_data:
            response_data.update(extra_data)
        
        return JsonResponse(
            response_data, 
            status=status or 200
        )