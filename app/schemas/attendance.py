"""Attendance schemas for API validation."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date
import uuid
from app.models.attendance import AttendanceStatus


class AttendanceBase(BaseModel):
    """Base attendance schema."""
    session_date: date
    status: AttendanceStatus
    notes: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    """Schema for single attendance creation."""
    student_id: uuid.UUID
    group_id: uuid.UUID
    subscription_id: Optional[uuid.UUID] = None


class AttendanceMarkRequest(BaseModel):
    """Schema for marking multiple students' attendance."""
    group_id: uuid.UUID
    session_date: date
    attendances: List[dict] = Field(
        ..., 
        description="List of {'student_id': UUID, 'status': AttendanceStatus, 'notes': Optional[str]}"
    )
    
    class Config:
        # Allow string dates to be parsed
        json_encoders = {
            date: lambda v: v.isoformat() if v else None
        }


class AttendanceUpdate(BaseModel):
    """Schema for attendance update."""
    status: Optional[AttendanceStatus] = None
    notes: Optional[str] = None


class AttendanceResponse(AttendanceBase):
    """Schema for attendance response."""
    id: uuid.UUID
    student_id: uuid.UUID
    group_id: uuid.UUID
    subscription_id: Optional[uuid.UUID]
    marked_by: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AttendanceWithDetails(AttendanceResponse):
    """Schema for attendance with student details."""
    student_name: str
    group_name: str
