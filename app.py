import os
import threading

from flask import Flask
from dotenv import load_dotenv

load_dotenv()

from bot.meta_bot import meta_bp
from bot.telegram_webhook import telegram_bp
from bot import telegram_bot

app = Flask(__name__)
app.register_blueprint(meta_bp)
app.register_blueprint(telegram_bp)


@app.route("/")
def health():
    return "Bot is running", 200


if __name__ == "__main__":
    # Long polling — только для локальной разработки без публичного HTTPS.
    # В продакшене (Render и т.п.) Telegram шлёт апдейты на /webhook/telegram.
    if os.environ.get("TELEGRAM_USE_POLLING") == "1":
        threading.Thread(target=telegram_bot.run, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
