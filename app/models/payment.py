"""Payment model for tracking student payments."""
import uuid
from datetime import date, datetime
from sqlalchemy import Date, DateTime, Enum as SQLEnum, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from enum import Enum
from decimal import Decimal
from app.database import Base


class PaymentType(str, Enum):
    """Payment type enumeration."""
    FULL = "full"
    PARTIAL = "partial"
    DISCOUNT = "discount"


class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    PAID = "paid"
    PENDING = "pending"
    OVERDUE = "overdue"


class Payment(Base):
    """Payment model for tracking student payments."""
    
    __tablename__ = "payments"
    
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
    subscription_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="SET NULL"),
        nullable=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    payment_month: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    payment_type: Mapped[PaymentType] = mapped_column(
        SQLEnum(PaymentType, name="payment_type"),
        nullable=False
    )
    status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus, name="payment_status"),
        nullable=False,
        default=PaymentStatus.PENDING
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="payments")
    subscription: Mapped[Optional["Subscription"]] = relationship("Subscription", back_populates="payments")
    
    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, amount={self.amount}, status={self.status})>"
