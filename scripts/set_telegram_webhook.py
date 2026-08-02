"""Регистрирует webhook Telegram после деплоя на Render.

Использование:
    TELEGRAM_BOT_TOKEN=xxx python3 scripts/set_telegram_webhook.py https://ваш-сервис.onrender.com
"""

import os
import sys

import requests

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python3 scripts/set_telegram_webhook.py <базовый URL сервиса>")
        sys.exit(1)

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Задайте TELEGRAM_BOT_TOKEN в окружении")
        sys.exit(1)

    base_url = sys.argv[1].rstrip("/")
    webhook_url = f"{base_url}/webhook/telegram"
    secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET")

    payload = {"url": webhook_url}
    if secret:
        payload["secret_token"] = secret

    resp = requests.post(
        f"https://api.telegram.org/bot{token}/setWebhook",
        json=payload,
        timeout=10,
    )
    print(resp.status_code, resp.json())
