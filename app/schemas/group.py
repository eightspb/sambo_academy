"""Group schemas for API validation."""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, Union
from datetime import datetime
import uuid
from app.models.group import AgeGroup, ScheduleType, SkillLevel


class GroupBase(BaseModel):
    """Base group schema."""
    name: str = Field(..., min_length=1, max_length=100)
    age_group: AgeGroup
    schedule_type: ScheduleType
    skill_level: SkillLevel
    schedule: Optional[Dict[str, Any]] = None
    default_subscription_type: Optional[str] = None
    
    @field_validator('default_subscription_type')
    @classmethod
    def validate_subscription_type(cls, v):
        if v is not None and v not in ['8_sessions', '12_sessions']:
            raise ValueError('default_subscription_type must be either "8_sessions" or "12_sessions"')
        return v


class GroupCreate(GroupBase):
    """Schema for group creation."""
    pass


class GroupUpdate(BaseModel):
    """Schema for group update."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age_group: Optional[AgeGroup] = None
    schedule_type: Optional[ScheduleType] = None
    skill_level: Optional[SkillLevel] = None
    schedule: Optional[Dict[str, Any]] = None
    default_subscription_type: Optional[str] = None
    is_active: Optional[bool] = None
    
    @field_validator('default_subscription_type')
    @classmethod
    def validate_subscription_type(cls, v):
        if v is not None and v not in ['8_sessions', '12_sessions']:
            raise ValueError('default_subscription_type must be either "8_sessions" or "12_sessions"')
        return v


class GroupResponse(GroupBase):
    """Schema for group response."""
    id: uuid.UUID
    trainer_id: uuid.UUID
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class GroupWithStudentCount(GroupResponse):
    """Schema for group with student count."""
    student_count: int = 0
