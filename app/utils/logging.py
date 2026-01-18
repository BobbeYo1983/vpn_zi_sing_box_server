"""
Единая конфигурация логирования проекта.

Особенности:
- Цветной вывод в stdout (colorlog)
- Поддержка structured logging через extra
- Подавление шума от шумных библиотек (httpx / httpcore и тд.)
- Готово для Docker / systemd
"""

import os
import logging
import colorlog
from django.conf import settings


# ==========================
# Formatter с поддержкой extra
# ==========================
class ExtraColoredFormatter(colorlog.ColoredFormatter):
    """
    ColoredFormatter, который красиво выводит extra-поля:

    logger.info(
        "User created",
        extra={"tg_id": 123, "username": "denis"}
    )

    → User created tg_id=123 username=denis
    """

    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)

        reserved = {
            "name", "msg", "args", "levelname", "levelno",
            "pathname", "filename", "module",
            "exc_info", "exc_text", "stack_info",
            "lineno", "funcName",
            "created", "msecs", "relativeCreated",
            "thread", "threadName",
            "processName", "process",
            "message", "asctime",
        }

        extras = {
            k: v for k, v in record.__dict__.items()
            if k not in reserved
        }

        if extras:
            extra_str = " ".join(f"{k}={v}" for k, v in extras.items())
            return f"{base} {extra_str}"

        return base


# ==========================
# Django LOGGING config
# ==========================
LOGGING = {
    'version': 1,

    # Не отключаем логгеры Django и сторонних библиотек
    'disable_existing_loggers': False,

    # --------------------------
    # FORMATTERS
    # --------------------------
    'formatters': {
        'colored_extra': {
            '()': ExtraColoredFormatter,
            'format': (
                '%(log_color)s%(asctime)s '
                '[%(levelname)s] '
                '%(name)s: %(message)s'
            ),
            'log_colors': {
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'bold_red',
            },
        },
    },

    # --------------------------
    # HANDLERS
    # --------------------------
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'colored_extra',
            'level': settings.LOG_LEVEL,
        },
    },

    # --------------------------
    # ROOT LOGGER
    # --------------------------
    'root': {
        'handlers': ['console'],
        'level': settings.LOG_LEVEL,
    },

    # --------------------------
    # Подавление шума
    # --------------------------
    'loggers': {
        'httpx': {
            'level': 'WARNING',
            'propagate': False,
        },
        'httpcore': {
            'level': 'WARNING',
            'propagate': False,
        },
    },
}