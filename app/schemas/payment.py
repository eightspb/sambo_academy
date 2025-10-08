"""Payment schemas for API validation."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
import uuid
from app.models.payment import PaymentType, PaymentStatus


class PaymentBase(BaseModel):
    """Base payment schema."""
    amount: Decimal = Field(..., ge=0)
    payment_date: date
    payment_type: PaymentType
    notes: Optional[str] = None


class PaymentCreate(PaymentBase):
    """Schema for payment creation."""
    student_id: uuid.UUID
    payment_month: date
    subscription_id: Optional[uuid.UUID] = None
    status: PaymentStatus = PaymentStatus.PAID


class PaymentUpdate(BaseModel):
    """Schema for payment update."""
    amount: Optional[Decimal] = Field(None, ge=0)
    payment_date: Optional[date] = None
    payment_month: Optional[date] = None
    payment_type: Optional[PaymentType] = None
    status: Optional[PaymentStatus] = None
    notes: Optional[str] = None


class PaymentResponse(PaymentBase):
    """Schema for payment response."""
    id: uuid.UUID
    student_id: uuid.UUID
    payment_month: date
    subscription_id: Optional[uuid.UUID]
    status: PaymentStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PaymentWithDetails(PaymentResponse):
    """Schema for payment with student details."""
    student_name: str
    subscription_type: Optional[str] = None  # "8_sessions" or "12_sessions"


class MonthlyPaymentSummary(BaseModel):
    """Schema for monthly payment summary."""
    year: int
    month: int
    total_amount: Decimal
    payment_count: int
    paid_count: int
    pending_count: int
    overdue_count: int
