"""Student schemas for API validation."""
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional, Union, List
from datetime import date
import uuid


class StudentBase(BaseModel):
    """Base student schema."""
    full_name: str = Field(..., min_length=1, max_length=100)
    birth_date: date
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[Union[EmailStr, str]] = None
    notes: Optional[str] = None
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Allow empty string or None for phone."""
        if v == "":
            return None
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Allow empty string or None for email."""
        if v == "":
            return None
        return v


class StudentCreate(StudentBase):
    """Schema for student creation."""
    group_id: uuid.UUID
    additional_group_ids: Optional[List[uuid.UUID]] = Field(default_factory=list)
    subscription_type: Optional[str] = Field(None, pattern="^(8_sessions|12_sessions)$")


class StudentUpdate(BaseModel):
    """Schema for student update."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    birth_date: Optional[date] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[Union[EmailStr, str]] = None
    group_id: Optional[uuid.UUID] = None
    additional_group_ids: Optional[List[uuid.UUID]] = None
    subscription_type: Optional[str] = Field(None, pattern="^(8_sessions|12_sessions)$")
    is_active: Optional[bool] = None
    notes: Optional[str] = None
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Allow empty string or None for phone."""
        if v == "":
            return None
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Allow empty string or None for email."""
        if v == "":
            return None
        return v


class StudentResponse(StudentBase):
    """Schema for student response."""
    id: uuid.UUID
    group_id: uuid.UUID
    additional_group_ids: Optional[List[uuid.UUID]] = Field(default_factory=list)
    trainer_id: uuid.UUID
    registration_date: date
    is_active: bool
    subscription_type: Optional[str] = None
    
    @field_validator('additional_group_ids', mode='before')
    @classmethod
    def validate_additional_groups(cls, v):
        """Ensure additional_group_ids is always a list, never None."""
        if v is None:
            return []
        return v
    
    model_config = ConfigDict(from_attributes=True)


class StudentWithStats(StudentResponse):
    """Schema for student with statistics."""
    active_subscription: Optional[dict] = None
    total_attendances: int = 0
    total_tournaments: int = 0
    total_wins: int = 0
