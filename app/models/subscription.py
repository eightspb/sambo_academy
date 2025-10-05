"""Subscription model for student memberships."""
import uuid
from datetime import date, datetime
from sqlalchemy import Boolean, Integer, Date, DateTime, Enum as SQLEnum, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum
from decimal import Decimal
from app.database import Base


class SubscriptionType(str, Enum):
    """Subscription type enumeration."""
    EIGHT_SESSIONS = "8_sessions"
    TWELVE_SESSIONS = "12_sessions"


class Subscription(Base):
    """Subscription model for student memberships."""
    
    __tablename__ = "subscriptions"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    subscription_type: Mapped[SubscriptionType] = mapped_column(
        SQLEnum(SubscriptionType, name="subscription_type"),
        nullable=False
    )
    total_sessions: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining_sessions: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="subscriptions")
    attendances: Mapped[list["Attendance"]] = relationship(
        "Attendance", 
        back_populates="subscription"
    )
    payments: Mapped[list["Payment"]] = relationship(
        "Payment", 
        back_populates="subscription"
    )
    
    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, type={self.subscription_type}, remaining={self.remaining_sessions})>"
