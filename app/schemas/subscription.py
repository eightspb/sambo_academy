"""Subscription schemas for API validation."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
import uuid
from app.models.subscription import SubscriptionType


class SubscriptionBase(BaseModel):
    """Base subscription schema."""
    subscription_type: SubscriptionType
    price: Decimal = Field(..., ge=0)
    start_date: date


class SubscriptionCreate(SubscriptionBase):
    """Schema for subscription creation."""
    student_id: uuid.UUID
    expiry_date: Optional[date] = None


class SubscriptionUpdate(BaseModel):
    """Schema for subscription update."""
    price: Optional[Decimal] = Field(None, ge=0)
    remaining_sessions: Optional[int] = Field(None, ge=0)
    expiry_date: Optional[date] = None
    is_active: Optional[bool] = None


class SubscriptionResponse(SubscriptionBase):
    """Schema for subscription response."""
    id: uuid.UUID
    student_id: uuid.UUID
    total_sessions: int
    remaining_sessions: int
    expiry_date: date
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SubscriptionUsage(BaseModel):
    """Schema for subscription usage statistics."""
    subscription_id: uuid.UUID
    total_sessions: int
    remaining_sessions: int
    used_sessions: int
    usage_percentage: float
