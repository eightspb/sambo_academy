"""Attendance model for tracking student attendance."""
import uuid
from datetime import datetime, date
from sqlalchemy import DateTime, Date, Enum as SQLEnum, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from enum import Enum
from app.database import Base


class AttendanceStatus(str, Enum):
    """Attendance status enumeration."""
    PRESENT = "present"
    ABSENT = "absent"
    TRANSFERRED = "transferred"


class Attendance(Base):
    """Attendance model for tracking student presence."""
    
    __tablename__ = "attendances"
    __table_args__ = (
        UniqueConstraint('student_id', 'group_id', 'session_date', name='uq_attendance_student_group_date'),
    )
    
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
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    session_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[AttendanceStatus] = mapped_column(
        SQLEnum(AttendanceStatus, name="attendance_status"),
        nullable=False
    )
    subscription_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subscriptions.id", ondelete="SET NULL"),
        nullable=True
    )
    marked_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="attendances")
    group: Mapped["Group"] = relationship("Group", back_populates="attendances")
    subscription: Mapped[Optional["Subscription"]] = relationship("Subscription", back_populates="attendances")
    marked_by_user: Mapped["User"] = relationship(
        "User", 
        back_populates="attendances",
        foreign_keys=[marked_by]
    )
    
    def __repr__(self) -> str:
        return f"<Attendance(id={self.id}, student_id={self.student_id}, status={self.status})>"
