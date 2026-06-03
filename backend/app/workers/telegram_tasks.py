from app.integrations.telegram.client import send_telegram_message
from app.integrations.telegram.keyboards import build_lead_inline_keyboard
from app.integrations.telegram.formatters import escape_markdown_v2
from app.db.database import AsyncSessionLocal     
from app.models.lead import Lead                 

async def task_notify_new_lead(lead_id: int, name: str, phone: str):
    safe_name = escape_markdown_v2(name)
    safe_phone = escape_markdown_v2(phone)

    text = (
        f"🔥 *НОВАЯ ЗАЯВКА НА ЗВОНОК\\!*\n\n"
        f"👤 *Имя:* {safe_name}\n"
        f"📞 *Телефон:* `{safe_phone}`\n\n"
        f"⚡ _Лид зафиксирован в системе\\. Ожидает обработки\\._"
    )

    keyboard = build_lead_inline_keyboard(lead_id)

    tg_message_id = await send_telegram_message(text=text, reply_markup=keyboard)
    
    if tg_message_id:
        async with AsyncSessionLocal() as session:
            lead = await session.get(Lead, lead_id)
            if lead:
                lead.tg_message_id = tg_message_id
                await session.commit()