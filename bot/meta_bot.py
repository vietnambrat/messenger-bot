"""Webhook для Facebook Messenger и Instagram (общий Graph API)."""

import os
import hmac
import hashlib
import requests
from flask import Blueprint, request, abort

from config.replies import get_reply

meta_bp = Blueprint("meta", __name__)

VERIFY_TOKEN = os.environ.get("META_VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.environ.get("META_PAGE_ACCESS_TOKEN")
APP_SECRET = os.environ.get("META_APP_SECRET")

GRAPH_URL = "https://graph.facebook.com/v19.0/me/messages"


def verify_signature(payload: bytes, signature_header: str) -> bool:
    if not APP_SECRET or not signature_header:
        return False
    expected = "sha256=" + hmac.new(APP_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)


def send_message(recipient_id: str, text: str):
    requests.post(
        GRAPH_URL,
        params={"access_token": PAGE_ACCESS_TOKEN},
        json={"recipient": {"id": recipient_id}, "message": {"text": text}},
        timeout=10,
    )


@meta_bp.route("/webhook/meta", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token and VERIFY_TOKEN and token == VERIFY_TOKEN:
        return challenge or "", 200
    return "Verification failed", 403


@meta_bp.route("/webhook/meta", methods=["POST"])
def receive():
    signature = request.headers.get("X-Hub-Signature-256", "")
    if APP_SECRET and not verify_signature(request.get_data(), signature):
        abort(403)

    data = request.get_json(force=True, silent=True) or {}

    for entry in data.get("entry", []):
        # И Messenger (Facebook Page), и Instagram присылают события в поле "messaging"
        for event in entry.get("messaging", []):
            sender_id = event.get("sender", {}).get("id")
            message = event.get("message", {})
            text = message.get("text")
            if sender_id and text and not message.get("is_echo"):
                reply = get_reply(text)
                send_message(sender_id, reply)

    return "EVENT_RECEIVED", 200
