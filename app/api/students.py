"""Students API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, any_
from typing import List, Optional
import uuid
from datetime import date, timedelta
from decimal import Decimal

from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.group import Group, AgeGroup
from app.models.subscription import Subscription, SubscriptionType
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse, StudentWithStats
from app.core.security import get_current_user
from app.core.permissions import check_student_access, check_group_access
from app.constants import (
    DEFAULT_SUBSCRIPTION_8_SENIOR_PRICE,
    DEFAULT_SUBSCRIPTION_12_SENIOR_PRICE,
    DEFAULT_SUBSCRIPTION_8_JUNIOR_PRICE,
    DEFAULT_SUBSCRIPTION_12_JUNIOR_PRICE
)

router = APIRouter(prefix="/api/students", tags=["students"])


def get_subscription_params(subscription_type: SubscriptionType, age_group: AgeGroup):
    """Get subscription parameters based on type and age group."""
    if subscription_type == SubscriptionType.EIGHT_SESSIONS:
        total_sessions = 8
        if age_group == AgeGroup.SENIOR:
            price = Decimal(str(DEFAULT_SUBSCRIPTION_8_SENIOR_PRICE))
        else:
            price = Decimal(str(DEFAULT_SUBSCRIPTION_8_JUNIOR_PRICE))
    else:  # TWELVE_SESSIONS
        total_sessions = 12
        if age_group == AgeGroup.SENIOR:
            price = Decimal(str(DEFAULT_SUBSCRIPTION_12_SENIOR_PRICE))
        else:
            price = Decimal(str(DEFAULT_SUBSCRIPTION_12_JUNIOR_PRICE))
    
    # Expiry date: 2 months from start date
    expiry_date = date.today() + timedelta(days=60)
    
    return {
        'total_sessions': total_sessions,
        'remaining_sessions': total_sessions,
        'price': price,
        'expiry_date': expiry_date
    }


@router.get("", response_model=List[StudentResponse])
async def get_students(
    group_id: Optional[uuid.UUID] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all students for the current trainer with optional filters."""
    query = select(Student)
    
    # Filter by trainer (unless admin)
    if not current_user.is_admin:
        query = query.where(Student.trainer_id == current_user.id)
    
    # Apply filters
    if group_id is not None:
        # Include students where group_id matches OR group is in additional_group_ids
        query = query.where(
            or_(
                Student.group_id == group_id,
                group_id == any_(Student.additional_group_ids)
            )
        )
    
    if is_active is not None:
        query = query.where(Student.is_active == is_active)
    
    query = query.order_by(Student.full_name)
    
    result = await db.execute(query)
    students = result.scalars().all()
    
    # Добавляем subscription_type и group_name для каждого студента
    students_list = []
    for student in students:
        # Получаем активный абонемент (самый свежий)
        sub_query = select(Subscription).where(
            Subscription.student_id == student.id,
            Subscription.is_active == True
        ).order_by(Subscription.start_date.desc())
        sub_result = await db.execute(sub_query)
        active_sub = sub_result.scalars().first()
        
        # Получаем название группы
        group_query = select(Group).where(Group.id == student.group_id)
        group_result = await db.execute(group_query)
        group = group_result.scalar_one_or_none()
        
        # Создаем response объект
        student_response = StudentResponse.model_validate(student)
        if active_sub:
            student_response.subscription_type = active_sub.subscription_type.value
        if group:
            student_response.group_name = group.name
        
        students_list.append(student_response)
    
    return students_list


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    student_data: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new student."""
    # Verify group access
    await check_group_access(student_data.group_id, current_user, db)
    
    # Извлекаем subscription_type перед созданием студента
    subscription_type = student_data.subscription_type
    student_dict = student_data.model_dump(exclude={'subscription_type'})
    
    new_student = Student(
        **student_dict,
        trainer_id=current_user.id
    )
    
    db.add(new_student)
    await db.commit()
    await db.refresh(new_student)
    
    # Создаем абонемент если указан тип
    if subscription_type:
        # Получаем группу для определения возрастной категории
        group_result = await db.execute(
            select(Group).where(Group.id == new_student.group_id)
        )
        group = group_result.scalar_one()
        
        # Получаем параметры абонемента
        subscription_params = get_subscription_params(
            SubscriptionType(subscription_type),
            group.age_group
        )
        
        new_subscription = Subscription(
            student_id=new_student.id,
            subscription_type=SubscriptionType(subscription_type),
            start_date=date.today(),
            is_active=True,
            **subscription_params  # total_sessions, remaining_sessions, price, expiry_date
        )
        db.add(new_subscription)
        await db.commit()
    
    # Возвращаем студента с subscription_type
    student_response = StudentResponse.model_validate(new_student)
    
    # Получаем активный абонемент для ответа (самый свежий)
    if subscription_type:
        sub_query = select(Subscription).where(
            Subscription.student_id == new_student.id,
            Subscription.is_active == True
        ).order_by(Subscription.start_date.desc())
        sub_result = await db.execute(sub_query)
        active_sub = sub_result.scalars().first()
        if active_sub:
            student_response.subscription_type = active_sub.subscription_type.value
    
    return student_response


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific student."""
    student = await check_student_access(student_id, current_user, db)
    return student


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: uuid.UUID,
    student_data: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a student."""
    student = await check_student_access(student_id, current_user, db)
    
    # If changing group, verify access to new group
    if student_data.group_id is not None:
        await check_group_access(student_data.group_id, current_user, db)
    
    # Извлекаем subscription_type
    update_data = student_data.model_dump(exclude_unset=True)
    subscription_type = update_data.pop('subscription_type', None)
    
    # Update fields
    for field, value in update_data.items():
        setattr(student, field, value)
    
    await db.commit()
    await db.refresh(student)
    
    # Обновляем абонемент если указан тип
    if subscription_type is not None:
        from datetime import date
        
        # Деактивируем старые абонементы
        old_subs_query = select(Subscription).where(
            Subscription.student_id == student_id,
            Subscription.is_active == True
        )
        old_subs_result = await db.execute(old_subs_query)
        for old_sub in old_subs_result.scalars():
            old_sub.is_active = False
        
        # Получаем группу студента для определения возрастной категории
        group_result = await db.execute(select(Group).where(Group.id == student.group_id))
        group = group_result.scalar_one_or_none()
        
        # Получаем параметры абонемента
        sub_params = get_subscription_params(
            SubscriptionType(subscription_type),
            group.age_group if group else AgeGroup.SENIOR
        )
        
        # Создаем новый абонемент
        new_subscription = Subscription(
            student_id=student_id,
            subscription_type=SubscriptionType(subscription_type),
            total_sessions=sub_params['total_sessions'],
            remaining_sessions=sub_params['remaining_sessions'],
            price=sub_params['price'],
            start_date=date.today(),
            expiry_date=sub_params['expiry_date'],
            is_active=True
        )
        db.add(new_subscription)
        await db.commit()
    
    # Возвращаем студента с subscription_type
    student_response = StudentResponse.model_validate(student)
    
    # Получаем активный абонемент для ответа (самый свежий)
    sub_query = select(Subscription).where(
        Subscription.student_id == student_id,
        Subscription.is_active == True
    ).order_by(Subscription.start_date.desc())
    sub_result = await db.execute(sub_query)
    active_sub = sub_result.scalars().first()
    if active_sub:
        student_response.subscription_type = active_sub.subscription_type.value
    
    return student_response


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a student."""
    student = await check_student_access(student_id, current_user, db)
    
    await db.delete(student)
    await db.commit()
    
    return None


@router.get("/{student_id}/statistics", response_model=StudentWithStats)
async def get_student_statistics(
    student_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get student with statistics."""
    student = await check_student_access(student_id, current_user, db)
    
    # Get attendance count
    attendance_result = await db.execute(
        select(func.count(Attendance.id))
        .where(Attendance.student_id == student_id)
    )
    total_attendances = attendance_result.scalar() or 0
    
    # Get tournament statistics
    tournament_result = await db.execute(
        select(
            func.count(TournamentParticipation.id),
            func.sum(TournamentParticipation.wins)
        )
        .where(TournamentParticipation.student_id == student_id)
    )
    tournament_stats = tournament_result.first()
    total_tournaments = tournament_stats[0] or 0
    total_wins = tournament_stats[1] or 0
    
    return StudentWithStats(
        **student.__dict__,
        total_attendances=total_attendances,
        total_tournaments=total_tournaments,
        total_wins=total_wins
    )
