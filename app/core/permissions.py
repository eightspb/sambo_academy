"""Permission checking utilities."""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.models.user import User
from app.models.group import Group
from app.models.student import Student


async def check_group_access(
    group_id: uuid.UUID,
    user: User,
    db: AsyncSession
) -> Group:
    """Check if user has access to a group."""
    result = await db.execute(select(Group).where(Group.id == group_id))
    group = result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    if not user.is_admin and group.trainer_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this group"
        )
    
    return group


async def check_student_access(
    student_id: uuid.UUID,
    user: User,
    db: AsyncSession
) -> Student:
    """Check if user has access to a student."""
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    if not user.is_admin and student.trainer_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this student"
        )
    
    return student


def verify_resource_ownership(resource_trainer_id: uuid.UUID, user: User) -> None:
    """Verify that user owns a resource or is admin."""
    if not user.is_admin and resource_trainer_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )
