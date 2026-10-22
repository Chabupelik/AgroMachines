import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def verify_turnstile_token(token: str, ip: str | None = None) -> bool:
    if not token:
        return False

    url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    payload = {
        "secret": settings.TURNSTILE_SECRET_KEY,
        "response": token,
    }
    if ip:
        payload["remoteip"] = ip

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, data=payload, timeout=5.0)
            if response.status_code == 200:
                result = response.json()
                return result.get("success", False)
            return False
        except Exception as e:
            logger.error("Cloudflare Turnstile Verification Failed: %s", e)
            return False
