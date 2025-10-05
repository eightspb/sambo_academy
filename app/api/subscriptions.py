"""Subscriptions API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import timedelta
import uuid

from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionType
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    SubscriptionUsage
)
from app.core.security import get_current_user
from app.core.permissions import check_student_access

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])


@router.post("", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new subscription for a student."""
    # Verify student access
    student = await check_student_access(subscription_data.student_id, current_user, db)
    
    # Determine total sessions based on subscription type
    total_sessions = 8 if subscription_data.subscription_type == SubscriptionType.EIGHT_SESSIONS else 12
    
    # Calculate expiry date (default 30 days from start)
    if not subscription_data.expiry_date:
        expiry_date = subscription_data.start_date + timedelta(days=30)
    else:
        expiry_date = subscription_data.expiry_date
    
    new_subscription = Subscription(
        student_id=subscription_data.student_id,
        subscription_type=subscription_data.subscription_type,
        total_sessions=total_sessions,
        remaining_sessions=total_sessions,
        price=subscription_data.price,
        start_date=subscription_data.start_date,
        expiry_date=expiry_date,
        is_active=True
    )
    
    db.add(new_subscription)
    await db.commit()
    await db.refresh(new_subscription)
    
    return new_subscription


@router.get("/student/{student_id}", response_model=List[SubscriptionResponse])
async def get_student_subscriptions(
    student_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all subscriptions for a student."""
    # Verify student access
    await check_student_access(student_id, current_user, db)
    
    result = await db.execute(
        select(Subscription)
        .where(Subscription.student_id == student_id)
        .order_by(Subscription.created_at.desc())
    )
    subscriptions = result.scalars().all()
    
    return subscriptions


@router.put("/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: uuid.UUID,
    subscription_data: SubscriptionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a subscription."""
    result = await db.execute(select(Subscription).where(Subscription.id == subscription_id))
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Verify student access
    await check_student_access(subscription.student_id, current_user, db)
    
    # Update fields
    update_data = subscription_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(subscription, field, value)
    
    await db.commit()
    await db.refresh(subscription)
    
    return subscription


@router.get("/{subscription_id}/usage", response_model=SubscriptionUsage)
async def get_subscription_usage(
    subscription_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get subscription usage statistics."""
    result = await db.execute(select(Subscription).where(Subscription.id == subscription_id))
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Verify student access
    await check_student_access(subscription.student_id, current_user, db)
    
    used_sessions = subscription.total_sessions - subscription.remaining_sessions
    usage_percentage = (used_sessions / subscription.total_sessions * 100) if subscription.total_sessions > 0 else 0
    
    return SubscriptionUsage(
        subscription_id=subscription.id,
        total_sessions=subscription.total_sessions,
        remaining_sessions=subscription.remaining_sessions,
        used_sessions=used_sessions,
        usage_percentage=round(usage_percentage, 2)
    )


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(
    subscription_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a subscription."""
    result = await db.execute(select(Subscription).where(Subscription.id == subscription_id))
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Verify student access
    await check_student_access(subscription.student_id, current_user, db)
    
    await db.delete(subscription)
    await db.commit()
    
    return None
