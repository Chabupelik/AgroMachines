import logging

from app.db.database import AsyncSessionLocal
from app.integrations.telegram.client import (
    edit_telegram_message,
    send_telegram_message,
)
from app.integrations.telegram.formatters import escape_markdown_v2
from app.integrations.telegram.keyboards import build_lead_inline_keyboard
from app.models.lead import Lead, LeadStatus

logger = logging.getLogger(__name__)


async def task_notify_new_lead(lead_id: int, name: str, phone: str) -> None:
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


async def task_update_lead_status_message(
    tg_message_id: int,
    client_name: str,
    client_phone: str,
    admin_username: str,
    new_status: str,
    lead_id: int,
) -> None:
    safe_name = escape_markdown_v2(client_name)
    safe_phone = escape_markdown_v2(client_phone)
    safe_username = escape_markdown_v2(admin_username)

    new_text = ""
    if new_status == LeadStatus.IN_PROGRESS:
        new_text = (
            f"⚡ *Заявка взята в работу\\!*\n\n"
            f"👤 *Имя:* {safe_name}\n"
            f"📞 *Телефон:* `{safe_phone}`\n\n"
            f"👨‍💼 *Заявка взята в работу через сайт менеджером @{safe_username}*"
        )
    elif new_status == LeadStatus.DONE:
        new_text = (
            f"✅ *Заявка закрыта\\!*\n\n"
            f"👤 *Имя:* {safe_name}\n"
            f"📞 *Телефон:* `{safe_phone}`\n\n"
            f"🏁 _Обработка успешно завершена менеджером @{safe_username}_"
        )

    if new_text:
        try:
            await edit_telegram_message(
                message_id=tg_message_id, text=new_text, reply_markup=None
            )
        except Exception as e:
            logger.warning(
                "Не удалось обновить статус заявки %s в Telegram: %s",
                lead_id,
                e,
            )


async def task_update_lead_taken_message(
    message_id: int,
    old_text: str,
    username: str,
    result: str,
    lead_id: int,
) -> None:
    safe_username = escape_markdown_v2(username)

    base_text = old_text
    for separator in ["\n\n👨‍💼", "\n\n⚠️", "\n\n❌", "\n\n??", "\n\n?"]:
        if separator in base_text:
            base_text = base_text.split(separator)[0]

    escaped_base = escape_markdown_v2(base_text)

    if result == "SUCCESS":
        new_text = (
            f"{escaped_base}\n\n"
            f"👨‍💼 *Заявка взята в работу менеджером @{safe_username}*"
        )
        reply_markup = None
    elif result == "ALREADY_TAKEN":
        new_text = (
            f"{escaped_base}\n\n"
            f"⚠️ *Ошибка: заявка уже обрабатывается другим менеджером\\.*"
        )
        reply_markup = None
    elif result == "TG_NOT_LINKED":
        reply_markup = build_lead_inline_keyboard(lead_id)
        new_text = (
            f"{escaped_base}\n\n"
            f"❌ *Ошибка: @{safe_username} не привязан к системе\\. "
            f"Суперадмин должен добавить Telegram username в профиль\\.*"
        )
    else:
        new_text = f"{escaped_base}\n\n❌ *Заявка не найдена или уже удалена\\.*"
        reply_markup = None

    try:
        await edit_telegram_message(
            message_id=message_id, text=new_text, reply_markup=reply_markup
        )
    except Exception as e:
        logger.warning(
            "Не удалось обновить сообщение заявки %s в Telegram: %s",
            lead_id,
            e,
        )
