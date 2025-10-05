"""Tournament models for tracking competitions."""
import uuid
from datetime import date, datetime
from sqlalchemy import Date, DateTime, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.database import Base


class Tournament(Base):
    """Tournament model for competitions."""
    
    __tablename__ = "tournaments"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    tournament_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    creator: Mapped["User"] = relationship(
        "User", 
        back_populates="tournaments",
        foreign_keys=[created_by]
    )
    participations: Mapped[list["TournamentParticipation"]] = relationship(
        "TournamentParticipation", 
        back_populates="tournament",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Tournament(id={self.id}, name={self.name}, date={self.tournament_date})>"


class TournamentParticipation(Base):
    """Tournament participation model for student results."""
    
    __tablename__ = "tournament_participations"
    __table_args__ = (
        UniqueConstraint('tournament_id', 'student_id', name='uq_tournament_student'),
    )
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    tournament_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tournaments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    place: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_fights: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    wins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    losses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    weight_category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    tournament: Mapped["Tournament"] = relationship("Tournament", back_populates="participations")
    student: Mapped["Student"] = relationship("Student", back_populates="tournament_participations")
    
    def __repr__(self) -> str:
        return f"<TournamentParticipation(id={self.id}, student_id={self.student_id}, place={self.place})>"
