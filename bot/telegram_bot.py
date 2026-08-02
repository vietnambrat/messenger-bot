"""Общие функции Telegram-бота + long polling для локальной разработки.

В продакшене (Render и т.п.) используется webhook — см. telegram_webhook.py.
Long polling здесь удобен только для локального теста без публичного HTTPS.
"""

import os
import time
import requests

from config.replies import get_reply

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def send_message(chat_id, text):
    requests.post(
        f"{API_URL}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=10,
    )


def handle_update(update: dict):
    message = update.get("message")
    if not message or "text" not in message:
        return
    chat_id = message["chat"]["id"]
    reply = get_reply(message["text"])
    send_message(chat_id, reply)


def run():
    """Long polling — только для локальной разработки (python3 -m bot.telegram_bot)."""
    if not TELEGRAM_TOKEN:
        print("[telegram] TELEGRAM_BOT_TOKEN не задан — бот Telegram не запущен")
        return

    print("[telegram] бот запущен (long polling, режим для разработки)")
    offset = 0
    while True:
        try:
            resp = requests.get(
                f"{API_URL}/getUpdates",
                params={"offset": offset, "timeout": 30},
                timeout=35,
            )
            resp.raise_for_status()
            data = resp.json()

            if not data.get("ok"):
                print(f"[telegram] Telegram API вернул ошибку: {data}")
                time.sleep(5)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                handle_update(update)

        except requests.RequestException as e:
            print(f"[telegram] ошибка запроса: {e}")
            time.sleep(5)


if __name__ == "__main__":
    run()
