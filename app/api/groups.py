"""Groups API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import uuid
from datetime import date, timedelta
from decimal import Decimal

from app.database import get_db
from app.models.user import User
from app.models.group import Group, AgeGroup
from app.models.student import Student
from app.models.subscription import Subscription, SubscriptionType
from app.schemas.group import GroupCreate, GroupUpdate, GroupResponse, GroupWithStudentCount
from app.core.security import get_current_user
from app.core.permissions import check_group_access
from app.constants import (
    DEFAULT_SUBSCRIPTION_8_SENIOR_PRICE,
    DEFAULT_SUBSCRIPTION_12_SENIOR_PRICE,
    DEFAULT_SUBSCRIPTION_8_JUNIOR_PRICE,
    DEFAULT_SUBSCRIPTION_12_JUNIOR_PRICE
)

router = APIRouter(prefix="/api/groups", tags=["groups"])


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


@router.get("", response_model=List[GroupWithStudentCount])
async def get_groups(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all groups for the current trainer."""
    # Admins see all groups, trainers see only their own
    if current_user.is_admin:
        result = await db.execute(
            select(Group, func.count(Student.id).label("student_count"))
            .outerjoin(Student, Group.id == Student.group_id)
            .group_by(Group.id)
            .order_by(Group.created_at.desc())
        )
    else:
        result = await db.execute(
            select(Group, func.count(Student.id).label("student_count"))
            .outerjoin(Student, Group.id == Student.group_id)
            .where(Group.trainer_id == current_user.id)
            .group_by(Group.id)
            .order_by(Group.created_at.desc())
        )
    
    groups_with_counts = result.all()
    
    return [
        GroupWithStudentCount(
            **{**group.__dict__, "student_count": count}
        )
        for group, count in groups_with_counts
    ]


@router.post("", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new group."""
    new_group = Group(
        **group_data.model_dump(),
        trainer_id=current_user.id
    )
    
    db.add(new_group)
    await db.commit()
    await db.refresh(new_group)
    
    return new_group


@router.get("/{group_id}", response_model=GroupResponse)
async def get_group(
    group_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific group."""
    group = await check_group_access(group_id, current_user, db)
    return group


@router.put("/{group_id}", response_model=GroupResponse)
async def update_group(
    group_id: uuid.UUID,
    group_data: GroupUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a group."""
    try:
        group = await check_group_access(group_id, current_user, db)
        
        # Get only fields that were actually set in the request
        update_data = group_data.model_dump(exclude_unset=True)
        print(f"DEBUG: Update data received: {update_data}")
        
        # Check if subscription type is being changed
        subscription_type_changed = False
        new_subscription_type = None
        
        if 'default_subscription_type' in update_data:
            new_value = update_data['default_subscription_type']
            old_value = group.default_subscription_type
            print(f"DEBUG: Subscription type check - Old: {old_value}, New: {new_value}")
            if new_value != old_value and new_value is not None:
                subscription_type_changed = True
                new_subscription_type = new_value
                print(f"DEBUG: Subscription type CHANGED! Will update students.")
        
        # Update fields
        for field, value in update_data.items():
            setattr(group, field, value)
        
        await db.commit()
        print(f"DEBUG: Group updated successfully")
    except Exception as e:
        print(f"ERROR in update_group (before subscription update): {type(e).__name__}: {str(e)}")
        await db.rollback()
        raise
    
    # If subscription type changed, update all students' subscriptions
    if subscription_type_changed and new_subscription_type:
        try:
            print(f"DEBUG: Starting subscription update for group {group_id}")
            
            # Get all students in this group
            students_result = await db.execute(
                select(Student).where(
                    Student.group_id == group_id,
                    Student.is_active == True
                )
            )
            students = students_result.scalars().all()
            print(f"DEBUG: Found {len(students)} active students in group")
            
            # Step 1: Deactivate all old subscriptions first
            deactivated_count = 0
            for student in students:
                old_subs_result = await db.execute(
                    select(Subscription).where(
                        Subscription.student_id == student.id,
                        Subscription.is_active == True
                    )
                )
                for old_sub in old_subs_result.scalars():
                    old_sub.is_active = False
                    deactivated_count += 1
            
            print(f"DEBUG: Deactivated {deactivated_count} old subscriptions")
            
            # Commit deactivation to remove unique constraint conflict
            await db.commit()
            print(f"DEBUG: Committed deactivation")
            
            # Step 2: Create new subscriptions
            for student in students:
                # Get subscription parameters based on type and student's group age
                subscription_params = get_subscription_params(
                    SubscriptionType(new_subscription_type),
                    group.age_group
                )
                
                new_subscription = Subscription(
                    student_id=student.id,
                    subscription_type=SubscriptionType(new_subscription_type),
                    start_date=date.today(),
                    is_active=True,
                    **subscription_params  # total_sessions, remaining_sessions, price, expiry_date
                )
                db.add(new_subscription)
            
            print(f"DEBUG: Created {len(students)} new subscriptions")
            await db.commit()
            print(f"DEBUG: Committed new subscriptions")
            
        except Exception as e:
            print(f"ERROR in subscription update: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            raise
    
    await db.refresh(group)
    print(f"DEBUG: Group refresh successful, returning response")
    
    return group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a group."""
    group = await check_group_access(group_id, current_user, db)
    
    await db.delete(group)
    await db.commit()
    
    return None


@router.get("/{group_id}/students", response_model=List[dict])
async def get_group_students(
    group_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all students in a group."""
    group = await check_group_access(group_id, current_user, db)
    
    result = await db.execute(
        select(Student)
        .where(Student.group_id == group_id)
        .order_by(Student.full_name)
    )
    students = result.scalars().all()
    
    return [
        {
            "id": str(student.id),
            "full_name": student.full_name,
            "birth_date": student.birth_date.isoformat(),
            "phone": student.phone,
            "is_active": student.is_active
        }
        for student in students
    ]
