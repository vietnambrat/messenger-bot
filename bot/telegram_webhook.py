"""Webhook-эндпоинт для Telegram — используется в продакшене (Render)."""

import os
from flask import Blueprint, request

from bot.telegram_bot import handle_update

telegram_bp = Blueprint("telegram", __name__)

WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET")


@telegram_bp.route("/webhook/telegram", methods=["POST"])
def receive():
    if WEBHOOK_SECRET:
        header = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if header != WEBHOOK_SECRET:
            return "Forbidden", 403

    update = request.get_json(force=True, silent=True) or {}
    handle_update(update)
    return "OK", 200
