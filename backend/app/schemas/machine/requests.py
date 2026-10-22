from pydantic import BaseModel, Field, field_validator

SpecificationValue = str | int | float | bool


def _validate_specs_dict(
    v: dict[str, SpecificationValue],
) -> dict[str, SpecificationValue]:
    if len(v) > 50:
        raise ValueError("Слишком много характеристик (максимум 50)")
    for key, value in v.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Ключ характеристики должен быть непустой строкой")
        if len(key) > 100:
            raise ValueError(
                f"Название характеристики '{key}' слишком длинное (максимум 100 символов)"
            )
        if isinstance(value, str) and len(value) > 255:
            raise ValueError(
                f"Значение характеристики '{key}' слишком длинное (максимум 255 символов)"
            )
    return v


class MachineCreateRequest(BaseModel):
    title: str = Field(..., max_length=255, description="Название техники")
    description: str | None = Field(None, description="Описание техники")
    specifications: dict[str, SpecificationValue] = Field(
        default_factory=dict, description="Характеристики техники в формате JSON"
    )
    price: float | None = Field(None, ge=0, description="Цена техники")
    is_available: bool = True

    @field_validator("specifications")
    @classmethod
    def validate_specifications(
        cls, v: dict[str, SpecificationValue]
    ) -> dict[str, SpecificationValue]:
        return _validate_specs_dict(v)


class MachineUpdateRequest(BaseModel):
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    specifications: dict[str, SpecificationValue] | None = None
    price: float | None = Field(None, ge=0)
    is_available: bool | None = None
    existing_image_urls: list[str] | None = None

    @field_validator("specifications")
    @classmethod
    def validate_specifications(
        cls, v: dict[str, SpecificationValue] | None
    ) -> dict[str, SpecificationValue] | None:
        if v is None:
            return v
        return _validate_specs_dict(v)
