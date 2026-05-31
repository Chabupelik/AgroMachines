import uuid
import enum
from sqlalchemy import String, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class RoleEnum(str, enum.Enum):
    SUPERADMIN = "SUPERADMIN"
    EDITOR = "EDITOR"
    MANAGER = "MANAGER"

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum, name="role_enum"), default=RoleEnum.MANAGER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)