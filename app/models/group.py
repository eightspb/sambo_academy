"""Group model for training groups."""
import uuid
from datetime import datetime
from sqlalchemy import Boolean, String, DateTime, Enum as SQLEnum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from enum import Enum
from app.database import Base


class AgeGroup(str, Enum):
    """Age group enumeration."""
    SENIOR = "senior"  # Старшие
    JUNIOR = "junior"  # Младшие


class ScheduleType(str, Enum):
    """Schedule type enumeration."""
    MON_WED_FRI = "mon_wed_fri"  # Понедельник, Среда, Пятница
    TUE_THU = "tue_thu"           # Вторник, Четверг


class SkillLevel(str, Enum):
    """Skill level enumeration."""
    BEGINNER = "beginner"      # Новички
    EXPERIENCED = "experienced"  # Опытные


class Group(Base):
    """Group model representing training groups."""
    
    __tablename__ = "groups"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age_group: Mapped[AgeGroup] = mapped_column(
        SQLEnum(AgeGroup, name="age_group"),
        nullable=False
    )
    schedule_type: Mapped[ScheduleType] = mapped_column(
        SQLEnum(ScheduleType, name="schedule_type"),
        nullable=False
    )
    skill_level: Mapped[SkillLevel] = mapped_column(
        SQLEnum(SkillLevel, name="skill_level"),
        nullable=False
    )
    trainer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    schedule: Mapped[dict] = mapped_column(JSON, nullable=True)  # Дополнительная информация о расписании
    default_subscription_type: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Тип абонемента по умолчанию для группы (8_sessions или 12_sessions)"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    trainer: Mapped["User"] = relationship("User", back_populates="groups")
    students: Mapped[list["Student"]] = relationship(
        "Student", 
        back_populates="group",
        cascade="all, delete-orphan"
    )
    attendances: Mapped[list["Attendance"]] = relationship(
        "Attendance", 
        back_populates="group",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Group(id={self.id}, name={self.name}, type={self.group_type})>"
