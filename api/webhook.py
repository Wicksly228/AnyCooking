import hmac
import json
import os
from http.server import BaseHTTPRequestHandler

from bot import handle


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        secret = os.environ.get("WEBHOOK_SECRET", "")
        received = self.headers.get(
            "X-Telegram-Bot-Api-Secret-Token", ""
        )

        if not secret or not hmac.compare_digest(secret, received):
            self.send_response(403)
            self.end_headers()
            return

        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 100000:
                raise ValueError()

            update = json.loads(self.rfile.read(size))
            message = update.get("message")

            if message:
                allowed = {
                    int(value.strip())
                    for value in os.getenv("ALLOWED_USER_IDS", "").split(",")
                    if value.strip()
                }

                handle(
                    message,
                    os.environ["TELEGRAM_BOT_TOKEN"],
                    os.environ["OPENAI_API_KEY"],
                    os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
                    allowed,
                )

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
        except Exception:
            print("Webhook processing failed", flush=True)
            self.send_response(500)
            self.end_headers()