def build_lead_inline_keyboard(lead_id: int) -> dict:
    return {
        "inline_keyboard": [
            [{"text": "✅ Взять в работу", "callback_data": f"take_lead_{lead_id}"}]
        ]
    }
