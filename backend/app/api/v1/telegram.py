from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.config import settings
from app.services.lead_service import LeadService
from app.repositories.lead_repo import LeadRepository
from app.repositories.audit_repo import AuditRepository
from app.integrations.telegram.client import edit_telegram_message
from app.integrations.telegram.formatters import escape_markdown_v2

router = APIRouter()

def get_lead_service(db: AsyncSession = Depends(get_db)) -> LeadService:
    return LeadService(LeadRepository(db), AuditRepository(db))

@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(None),
    db: AsyncSession = Depends(get_db),
    lead_srv: LeadService = Depends(get_lead_service)
):
    if x_telegram_bot_api_secret_token != settings.TG_WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Fake Telegram request")

    data = await request.json()

    if "callback_query" in data:
        callback = data["callback_query"]
        callback_data = callback["data"]
        
        tg_user = callback["from"]
        username = tg_user.get("username") or tg_user.get("first_name") or "Manager"
        
        message = callback["message"]
        message_id = message["message_id"]
        old_text = message["text"]

        if callback_data.startswith("take_lead_"):
            lead_id = int(callback_data.split("_")[2])

            try:
                result = await lead_srv.take_lead_from_tg(lead_id, username)
            except Exception as e:
                result = "NOT_FOUND"

            safe_username = escape_markdown_v2(username)

            base_text = old_text
            for separator in ["\n\n🤝", "\n\n⚠️", "\n\n❌", "\n\n✅"]:
                if separator in base_text:
                    base_text = base_text.split(separator)[0]

            if result == "SUCCESS":
                new_text = (
                    f"{escape_markdown_v2(base_text)}\n\n"
                    f"🤝 *Заявка взята в работу менеджером @{safe_username}*"
                )
                await edit_telegram_message(message_id=message_id, text=new_text, reply_markup=None)

            elif result == "ALREADY_TAKEN":
                new_text = (
                    f"{escape_markdown_v2(base_text)}\n\n"
                    f"⚠️ *Ошибка: Эта заявка уже обрабатывается другим менеджером\\.*"
                )
                await edit_telegram_message(message_id=message_id, text=new_text, reply_markup=None)

            elif result == "TG_NOT_LINKED":
                from app.integrations.telegram.keyboards import build_lead_inline_keyboard
                keyboard = build_lead_inline_keyboard(lead_id)
                
                new_text = (
                    f"{escape_markdown_v2(base_text)}\n\n"
                    f"⚠️ *Ошибка: Менеджер @{safe_username} не привязан к системе\\. Попросите суперадмина добавить ваш Telegram в панель управления\\.*"
                )
                await edit_telegram_message(message_id=message_id, text=new_text, reply_markup=keyboard)

            else:  
                new_text = (
                    f"{escape_markdown_v2(base_text)}\n\n"
                    f"❌ *Такой заявки больше нет в базе данных\\.*"
                )
                await edit_telegram_message(message_id=message_id, text=new_text, reply_markup=None)
    return {"ok": True}