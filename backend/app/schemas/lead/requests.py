import phonenumbers
from pydantic import BaseModel, field_validator
import html

class LeadCreateRequest(BaseModel):
    client_name: str
    client_phone: str

    @field_validator("client_name")
    def sanitize_name(cls, value: str) -> str:
        clean_name = value.strip()
        if not clean_name:
            raise ValueError("Имя не может быть пустым")
        return html.escape(clean_name)

    @field_validator("client_phone")
    def validate_phone(cls, value: str) -> str:
        try:
            parsed_number = phonenumbers.parse(value, "RU")
            
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError("Введен некорректный или несуществующий номер телефона")
            
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        
        except phonenumbers.NumberParseException:
            raise ValueError("Неверный формат номера. Используйте формат +7XXXXXXXXXX")