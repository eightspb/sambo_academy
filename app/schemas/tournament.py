"""Tournament schemas for API validation."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import date, datetime
import uuid


class TournamentBase(BaseModel):
    """Base tournament schema."""
    name: str = Field(..., min_length=1, max_length=200)
    tournament_date: date
    location: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class TournamentCreate(TournamentBase):
    """Schema for tournament creation."""
    pass


class TournamentUpdate(BaseModel):
    """Schema for tournament update."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    tournament_date: Optional[date] = None
    location: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None


class TournamentResponse(TournamentBase):
    """Schema for tournament response."""
    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ParticipationBase(BaseModel):
    """Base participation schema."""
    place: Optional[int] = Field(None, ge=1)
    total_fights: int = Field(default=0, ge=0)
    wins: int = Field(default=0, ge=0)
    losses: int = Field(default=0, ge=0)
    weight_category: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class ParticipationCreate(ParticipationBase):
    """Schema for participation creation."""
    student_id: uuid.UUID


class ParticipationUpdate(ParticipationBase):
    """Schema for participation update."""
    pass


class ParticipationResponse(ParticipationBase):
    """Schema for participation response."""
    id: uuid.UUID
    tournament_id: uuid.UUID
    student_id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)


class ParticipationWithDetails(ParticipationResponse):
    """Schema for participation with student details."""
    student_name: str
    tournament_name: str
    tournament_date: date


class StudentTournamentStats(BaseModel):
    """Schema for student tournament statistics."""
    student_id: uuid.UUID
    student_name: str
    total_tournaments: int = 0
    total_fights: int = 0
    total_wins: int = 0
    total_losses: int = 0
    win_rate: float = 0.0
    best_place: Optional[int] = None
    participations: List[ParticipationWithDetails] = []
