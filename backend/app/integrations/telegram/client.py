import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_telegram_message(
    text: str, reply_markup: dict | None = None
) -> int | None:
    url = f"https://api.telegram.org/bot{settings.TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TG_CHAT_ID,
        "text": text,
        "parse_mode": "MarkdownV2",
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=10.0)
            if response.status_code == 200:
                res_data = response.json()
                return res_data["result"]["message_id"]

            logger.error("Telegram API Error: %s", response.text)
        except Exception as e:
            logger.error("Connection to Telegram failed: %s", e)
    return None


async def edit_telegram_message(
    message_id: int, text: str, reply_markup: dict | None = None
) -> bool:
    url = f"https://api.telegram.org/bot{settings.TG_BOT_TOKEN}/editMessageText"
    payload = {
        "chat_id": settings.TG_CHAT_ID,
        "message_id": message_id,
        "text": text,
        "parse_mode": "MarkdownV2",
    }
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=10.0)

            if response.status_code == 400:
                res_data = response.json()
                if "message is not modified" in res_data.get("description", ""):
                    return True

            return response.status_code == 200
        except Exception as e:
            logger.error("Connection to Telegram failed: %s", e)
    return False
