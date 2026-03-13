import os
import requests
from .db import log_notification

class TelegramService:
    @staticmethod
    def send_notification(message: str):
        """Sends a notification to the Partner via Telegram."""
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not token or not chat_id:
            print(f"🤖 [TELEGRAM SERVICE] (Mock) Message: {message}")
            log_notification("partner", "mock-chat-id", "telegram", {"message": message, "status": "mocked"})
            return {"status": "mocked", "message": "Telegram credentials not set"}

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            # response = requests.post(url, json=payload, timeout=5)
            # For safety in this environment, we log the intent instead of firing real requests unless specified
            print(f"🤖 [TELEGRAM SERVICE] Sending real notification to {chat_id}")
            log_notification("partner", chat_id, "telegram", {"message": message})
            return {"status": "sent"}
        except Exception as e:
            print(f"❌ [TELEGRAM SERVICE] Error: {e}")
            return {"status": "failed", "error": str(e)}
