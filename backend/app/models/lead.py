import enum
from datetime import UTC, datetime

from sqlalchemy import BigInteger, DateTime, Enum, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LeadStatus(str, enum.Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_name: Mapped[str] = mapped_column(String(100))
    client_phone: Mapped[str] = mapped_column(String(20), index=True)
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus, name="lead_status_enum"), default=LeadStatus.NEW
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    processed_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tg_message_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    __table_args__ = (
        Index(
            "uniq_active_phone",
            "client_phone",
            unique=True,
            postgresql_where=(status.in_([LeadStatus.NEW, LeadStatus.IN_PROGRESS])),
        ),
    )
