"""Settings schemas for API validation."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
import uuid


class SettingsBase(BaseModel):
    """Base settings schema."""
    key: str = Field(..., min_length=1, max_length=100)
    value: str
    description: Optional[str] = None


class SettingsCreate(SettingsBase):
    """Schema for settings creation."""
    pass


class SettingsUpdate(BaseModel):
    """Schema for settings update."""
    value: str
    description: Optional[str] = None


class SettingsResponse(SettingsBase):
    """Schema for settings response."""
    id: uuid.UUID
    is_system: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SubscriptionPrices(BaseModel):
    """Schema for subscription prices."""
    subscription_8_senior_price: int = Field(..., description="Цена абонемента на 8 занятий для старших")
    subscription_8_junior_price: int = Field(..., description="Цена абонемента на 8 занятий для младших")
    subscription_12_senior_price: int = Field(..., description="Цена абонемента на 12 занятий для старших")
    subscription_12_junior_price: int = Field(..., description="Цена абонемента на 12 занятий для младших")
