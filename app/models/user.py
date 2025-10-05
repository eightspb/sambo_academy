"""User model for trainers and admins."""
import uuid
from datetime import datetime
from sqlalchemy import Boolean, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    """User model representing trainers and admins."""
    
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    
    # Relationships
    groups: Mapped[list["Group"]] = relationship(
        "Group", 
        back_populates="trainer", 
        cascade="all, delete-orphan"
    )
    students: Mapped[list["Student"]] = relationship(
        "Student", 
        back_populates="trainer", 
        cascade="all, delete-orphan"
    )
    attendances: Mapped[list["Attendance"]] = relationship(
        "Attendance", 
        back_populates="marked_by_user",
        foreign_keys="Attendance.marked_by"
    )
    tournaments: Mapped[list["Tournament"]] = relationship(
        "Tournament", 
        back_populates="creator",
        foreign_keys="Tournament.created_by"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
