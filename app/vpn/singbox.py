import json
import os
import logging
from .models import SingBoxUser
from urllib.parse import quote
from django.conf import settings
from pathlib import Path


logger = logging.getLogger(__name__)

FLOW = "xtls-rprx-vision"

def build_users():
    return [
        {
            "name": f"{u.tg_username}({u.tg_id})",
            "uuid": str(u.uuid),
            "flow": FLOW,
        }
        for u in SingBoxUser.objects.filter(active=True) # только активные пользователи
    ]

def write_config():
    # 1️⃣ Формируем конфигурацию полностью,
    #    независимо от того, есть пользователи или нет
    config = {
        "log": {
            "level": "info"
        },
        "inbounds": [
            {
                "type": "vless",
                "tag": "vless-in",
                "listen": "0.0.0.0",
                "listen_port": settings.SINGBOX_SERVER_PORT,  # ОБЯЗАТЕЛЬНО int, не строка
                "users": build_users(),      # фильтр по active=True внутри
                "tls": {
                    "enabled": True,
                    "server_name": settings.SINGBOX_SERVER_NAME,
                    "reality": {
                        "enabled": True,
                        "handshake": {
                            "server": settings.SINGBOX_SERVER_NAME,
                            "server_port": 443
                        },
                        "private_key": settings.SINGBOX_REALITY_PRIVATE_KEY,
                        "short_id": [settings.SINGBOX_SHORT_ID]
                    }
                }
            }
        ],
        "outbounds": [
            {
                "type": "direct",
                "tag": "direct"
            }
        ]
    }

    # 2️⃣ ВАЖНО: атомарная запись
    #    Пишем сначала во временный файл рядом с основным
    tmp_path: Path = settings.SINGBOX_CONFIG_PATH.with_suffix(".tmp")

    tmp_path.write_text(
        json.dumps(
            config,
            indent=2,
            ensure_ascii=False  # чтобы имена пользователей могли быть на русском
        ),
        encoding="utf-8"
    )

    # 3️⃣ АТОМАРНАЯ замена файла
    #    - гарантированно меняет inode
    #    - systemd path unit это УВИДИТ
    #    - файл никогда не бывает "наполовину записан"
    os.replace(tmp_path, settings.SINGBOX_CONFIG_PATH)

    logger.info("Создана конфигурация для sing-box")


def build_vless_uri(user):
    return (
        f"vless://{user.uuid}@{settings.HOST_IP}:{settings.SINGBOX_SERVER_PORT}"
        f"?encryption=none" 
        f"&security=reality"
        f"&fp=firefox"  
        f"&sni={settings.SINGBOX_SERVER_NAME}"
        f"&pbk={settings.SINGBOX_REALITY_PUBLIC_KEY}"
        f"&sid={settings.SINGBOX_SHORT_ID}"
        f"&flow={FLOW}"
        f"&type=tcp"                
        f"# VPNzi ({quote(user.tg_username)})"
    )