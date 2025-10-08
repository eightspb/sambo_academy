"""Payments API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract
from typing import List
from decimal import Decimal
import uuid

from app.database import get_db
from app.models.user import User
from app.models.payment import Payment, PaymentStatus
from app.models.student import Student
from app.schemas.payment import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
    PaymentWithDetails,
    MonthlyPaymentSummary
)
from app.core.security import get_current_user
from app.core.permissions import check_student_access
from app.utils.date_helpers import get_month_range

router = APIRouter(prefix="/api/payments", tags=["payments"])


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Register a new payment."""
    # Verify student access
    await check_student_access(payment_data.student_id, current_user, db)
    
    new_payment = Payment(**payment_data.model_dump())
    
    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)
    
    return new_payment


@router.get("/student/{student_id}", response_model=List[PaymentResponse])
async def get_student_payments(
    student_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all payments for a student."""
    # Verify student access
    await check_student_access(student_id, current_user, db)
    
    result = await db.execute(
        select(Payment)
        .where(Payment.student_id == student_id)
        .order_by(Payment.payment_date.desc())
    )
    payments = result.scalars().all()
    
    return payments


@router.get("/month/{year}/{month}", response_model=List[PaymentWithDetails])
async def get_monthly_payments(
    year: int,
    month: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all payments for a specific month."""
    first_day, last_day = get_month_range(year, month)
    
    # Build query based on user role - get active subscription for each student
    from app.models.subscription import Subscription
    
    # Subquery to get active subscription type for each student
    active_sub_subquery = (
        select(Subscription.student_id, Subscription.subscription_type)
        .where(Subscription.is_active == True)
        .distinct(Subscription.student_id)
        .order_by(Subscription.student_id, Subscription.start_date.desc())
        .subquery()
    )
    
    query = (
        select(Payment, Student.full_name, active_sub_subquery.c.subscription_type)
        .join(Student, Payment.student_id == Student.id)
        .outerjoin(active_sub_subquery, Student.id == active_sub_subquery.c.student_id)
        .where(and_(
            Payment.payment_month >= first_day,
            Payment.payment_month <= last_day
        ))
    )
    
    if not current_user.is_admin:
        query = query.where(Student.trainer_id == current_user.id)
    
    result = await db.execute(query.order_by(Payment.payment_date.desc()))
    payment_records = result.all()
    
    return [
        PaymentWithDetails(
            **payment.__dict__,
            student_name=student_name,
            subscription_type=subscription_type.value if subscription_type else None
        )
        for payment, student_name, subscription_type in payment_records
    ]


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: uuid.UUID,
    payment_data: PaymentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a payment."""
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Verify student access
    await check_student_access(payment.student_id, current_user, db)
    
    # Update fields
    update_data = payment_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(payment, field, value)
    
    await db.commit()
    await db.refresh(payment)
    
    return payment


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a payment."""
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Verify student access
    await check_student_access(payment.student_id, current_user, db)
    
    await db.delete(payment)
    await db.commit()
    
    return None


@router.get("/statistics/summary", response_model=List[MonthlyPaymentSummary])
async def get_payment_statistics(
    year: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get payment statistics grouped by month."""
    from datetime import date
    
    # Use current year if not specified
    if year is None:
        year = date.today().year
    
    # Build query
    from sqlalchemy import Integer, case
    
    query = (
        select(
            extract('year', Payment.payment_month).label('year'),
            extract('month', Payment.payment_month).label('month'),
            func.sum(Payment.amount).label('total_amount'),
            func.count(Payment.id).label('payment_count'),
            func.sum(case((Payment.status == PaymentStatus.PAID, 1), else_=0)).label('paid_count'),
            func.sum(case((Payment.status == PaymentStatus.PENDING, 1), else_=0)).label('pending_count'),
            func.sum(case((Payment.status == PaymentStatus.OVERDUE, 1), else_=0)).label('overdue_count')
        )
        .where(extract('year', Payment.payment_month) == year)
    )
    
    if not current_user.is_admin:
        query = query.join(Student, Payment.student_id == Student.id).where(Student.trainer_id == current_user.id)
    
    query = query.group_by(
        extract('year', Payment.payment_month),
        extract('month', Payment.payment_month)
    ).order_by(
        extract('month', Payment.payment_month)
    )
    
    result = await db.execute(query)
    stats = result.all()
    
    return [
        MonthlyPaymentSummary(
            year=int(year_val),
            month=int(month_val),
            total_amount=Decimal(total or 0),
            payment_count=int(count or 0),
            paid_count=int(paid or 0),
            pending_count=int(pending or 0),
            overdue_count=int(overdue or 0)
        )
        for year_val, month_val, total, count, paid, pending, overdue in stats
    ]


@router.get("/unpaid-students")
async def get_unpaid_students(
    year: int = None,
    month: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of students who haven't paid for specified month."""
    from datetime import date
    from app.models.group import Group
    
    # Use current year/month if not specified
    if year is None:
        year = date.today().year
    if month is None:
        month = date.today().month
    
    # Get first day of the month
    first_day = date(year, month, 1)
    
    # Get all active students
    students_query = select(Student, Group.name).join(
        Group, Student.group_id == Group.id
    ).where(Student.is_active == True)
    
    if not current_user.is_admin:
        students_query = students_query.where(Student.trainer_id == current_user.id)
    
    students_result = await db.execute(students_query)
    all_students = students_result.all()
    
    unpaid_students = []
    
    for student, group_name in all_students:
        # Check if student has payment for this month
        payment_check = await db.execute(
            select(Payment).where(
                Payment.student_id == student.id,
                Payment.payment_month == first_day,
                Payment.status == PaymentStatus.PAID
            )
        )
        
        payment = payment_check.scalars().first()
        
        if not payment:
            # Get active subscription to determine expected amount
            subscription_query = select(Subscription).where(
                Subscription.student_id == student.id,
                Subscription.is_active == True
            ).order_by(Subscription.start_date.desc())
            subscription_result = await db.execute(subscription_query)
            active_subscription = subscription_result.scalars().first()
            
            # Calculate expected amount based on subscription
            expected_amount = Decimal('0')
            if active_subscription:
                expected_amount = active_subscription.price
            
            unpaid_students.append({
                'student_id': str(student.id),
                'full_name': student.full_name,
                'group_name': group_name,
                'phone': student.phone,
                'email': student.email,
                'debt_amount': float(expected_amount)
            })
    
    return {
        'year': year,
        'month': month,
        'total_unpaid': len(unpaid_students),
        'students': unpaid_students
    }
