from datetime import datetime, timezone
from sqlalchemy import String, Text, Numeric, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class Machine(Base):
    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    specifications: Mapped[dict] = mapped_column(JSONB, default=dict)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    image_urls: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))