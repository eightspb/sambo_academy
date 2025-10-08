"""Attendance API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_, any_, case
from sqlalchemy.orm import selectinload
from typing import List
from datetime import date, datetime, timedelta
import uuid
from decimal import Decimal

from app.database import get_db
from app.models.user import User
from app.models.attendance import Attendance, AttendanceStatus
from app.models.student import Student
from app.models.subscription import Subscription, SubscriptionType
from app.models.group import Group
from app.models.payment import Payment
from app.models.settings import Settings
from app.constants import (
    SETTING_KEY_SUBSCRIPTION_8_SENIOR,
    SETTING_KEY_SUBSCRIPTION_8_JUNIOR,
    SETTING_KEY_SUBSCRIPTION_12_SENIOR,
    SETTING_KEY_SUBSCRIPTION_12_JUNIOR,
    DEFAULT_SUBSCRIPTION_8_SENIOR_PRICE,
    DEFAULT_SUBSCRIPTION_8_JUNIOR_PRICE,
    DEFAULT_SUBSCRIPTION_12_SENIOR_PRICE,
    DEFAULT_SUBSCRIPTION_12_JUNIOR_PRICE
)
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceMarkRequest,
    AttendanceUpdate,
    AttendanceResponse,
    AttendanceWithDetails
)
from app.core.security import get_current_user
from app.core.permissions import check_group_access

router = APIRouter(prefix="/api/attendance", tags=["attendance"])


@router.post("/mark", response_model=List[AttendanceResponse], status_code=status.HTTP_201_CREATED)
async def mark_attendance(
    attendance_data: AttendanceMarkRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark attendance for multiple students in a session. Updates existing records if found."""
    # Verify group access
    await check_group_access(attendance_data.group_id, current_user, db)
    
    session_date = attendance_data.session_date
    result_attendances = []
    
    for attendance_item in attendance_data.attendances:
        student_id = uuid.UUID(attendance_item["student_id"])
        status_value = attendance_item.get("status")  # Может быть None
        notes = attendance_item.get("notes")
        
        # Verify student belongs to group (primary or additional)
        result = await db.execute(
            select(Student).where(Student.id == student_id)
        )
        student = result.scalar_one_or_none()
        
        if not student:
            continue
        
        # Check if student belongs to this group (primary or additional)
        belongs_to_group = (
            student.group_id == attendance_data.group_id or
            (student.additional_group_ids and attendance_data.group_id in student.additional_group_ids)
        )
        
        if not belongs_to_group:
            continue
        
        # Check if attendance already exists for this student/group/date
        existing_result = await db.execute(
            select(Attendance).where(
                Attendance.student_id == student_id,
                Attendance.group_id == attendance_data.group_id,
                Attendance.session_date == session_date
            )
        )
        existing_attendance = existing_result.scalar_one_or_none()
        
        # Если status = None, удаляем существующую запись
        if status_value is None:
            if existing_attendance:
                await db.delete(existing_attendance)
            continue
        
        # Конвертируем в AttendanceStatus
        status_value = AttendanceStatus(status_value)
        
        if existing_attendance:
            # Update existing record
            old_status = existing_attendance.status
            existing_attendance.status = status_value
            existing_attendance.notes = notes
            existing_attendance.marked_by = current_user.id
            
            # If changing to TRANSFERRED, create partial payment for next month
            if old_status != AttendanceStatus.TRANSFERRED and status_value == AttendanceStatus.TRANSFERRED:
                # Get active subscription
                subscription_result = await db.execute(
                    select(Subscription).where(
                        Subscription.student_id == student_id,
                        Subscription.is_active == True
                    ).order_by(Subscription.created_at.desc()).limit(1)
                )
                subscription = subscription_result.scalars().first()
                
                if subscription:
                    # Get group
                    group_result = await db.execute(
                        select(Group).where(Group.id == attendance_data.group_id)
                    )
                    group = group_result.scalar_one_or_none()
                    
                    if group:
                        # Determine sessions count
                        sessions_count = 8 if subscription.subscription_type == SubscriptionType.EIGHT_SESSIONS else 12
                        
                        # Get standard price for this subscription from Settings
                        if subscription.subscription_type == SubscriptionType.EIGHT_SESSIONS:
                            if group.age_group == 'senior':
                                price_key = SETTING_KEY_SUBSCRIPTION_8_SENIOR
                                default_price = DEFAULT_SUBSCRIPTION_8_SENIOR_PRICE
                            else:
                                price_key = SETTING_KEY_SUBSCRIPTION_8_JUNIOR
                                default_price = DEFAULT_SUBSCRIPTION_8_JUNIOR_PRICE
                        else:  # TWELVE_SESSIONS
                            if group.age_group == 'senior':
                                price_key = SETTING_KEY_SUBSCRIPTION_12_SENIOR
                                default_price = DEFAULT_SUBSCRIPTION_12_SENIOR_PRICE
                            else:
                                price_key = SETTING_KEY_SUBSCRIPTION_12_JUNIOR
                                default_price = DEFAULT_SUBSCRIPTION_12_JUNIOR_PRICE
                        
                        # Get price from database
                        price_result = await db.execute(
                            select(Settings).where(Settings.key == price_key)
                        )
                        price_setting = price_result.scalar_one_or_none()
                        standard_price = int(price_setting.value) if price_setting else default_price
                        
                        # Check if there's an actual payment for current month
                        current_month = session_date.month
                        current_year = session_date.year
                        
                        existing_payment_result = await db.execute(
                            select(func.sum(Payment.amount)).where(
                                Payment.student_id == student_id,
                                Payment.month == current_month,
                                Payment.year == current_year
                            )
                        )
                        actual_paid_amount = existing_payment_result.scalar()
                        
                        # Use actual paid amount if exists, otherwise use standard price
                        base_price = Decimal(str(actual_paid_amount)) if actual_paid_amount else Decimal(str(standard_price))
                        session_cost = base_price / Decimal(str(sessions_count))
                        
                        # Calculate next month
                        next_month = session_date + relativedelta(months=1)
                        next_month = next_month.replace(day=1)
                        
                        # Create payment for next month
                        payment = Payment(
                            student_id=student_id,
                            subscription_type=subscription.subscription_type,
                            amount=session_cost,
                            standard_price=standard_price,
                            payment_date=next_month,
                            month=next_month.month,
                            year=next_month.year,
                            notes=f"Автоматическая компенсация за перенос от {session_date.strftime('%d.%m.%Y')}"
                        )
                        db.add(payment)
            
            result_attendances.append(existing_attendance)
        else:
            # Get active subscription for the student (most recent)
            subscription_result = await db.execute(
                select(Subscription).where(
                    Subscription.student_id == student_id,
                    Subscription.is_active == True
                ).order_by(Subscription.created_at.desc()).limit(1)
            )
            subscription = subscription_result.scalars().first()
            
            # Create new attendance record
            new_attendance = Attendance(
                student_id=student_id,
                group_id=attendance_data.group_id,
                session_date=session_date,
                status=status_value,
                subscription_id=subscription.id if subscription else None,
                marked_by=current_user.id,
                notes=notes
            )
            
            db.add(new_attendance)
            
            # Update subscription if present and not transferred
            if subscription and status_value == AttendanceStatus.PRESENT:
                if subscription.remaining_sessions > 0:
                    subscription.remaining_sessions -= 1
                    if subscription.remaining_sessions == 0:
                        subscription.is_active = False
            
            # Create partial payment for next month if transferred
            if status_value == AttendanceStatus.TRANSFERRED and subscription:
                # Get group to determine age group
                group_result = await db.execute(
                    select(Group).where(Group.id == attendance_data.group_id)
                )
                group = group_result.scalar_one_or_none()
                
                if group:
                    # Determine sessions count
                    sessions_count = 8 if subscription.subscription_type == SubscriptionType.EIGHT_SESSIONS else 12
                    
                    # Get standard price for this subscription from Settings
                    if subscription.subscription_type == SubscriptionType.EIGHT_SESSIONS:
                        if group.age_group == 'senior':
                            price_key = SETTING_KEY_SUBSCRIPTION_8_SENIOR
                            default_price = DEFAULT_SUBSCRIPTION_8_SENIOR_PRICE
                        else:
                            price_key = SETTING_KEY_SUBSCRIPTION_8_JUNIOR
                            default_price = DEFAULT_SUBSCRIPTION_8_JUNIOR_PRICE
                    else:  # TWELVE_SESSIONS
                        if group.age_group == 'senior':
                            price_key = SETTING_KEY_SUBSCRIPTION_12_SENIOR
                            default_price = DEFAULT_SUBSCRIPTION_12_SENIOR_PRICE
                        else:
                            price_key = SETTING_KEY_SUBSCRIPTION_12_JUNIOR
                            default_price = DEFAULT_SUBSCRIPTION_12_JUNIOR_PRICE
                    
                    # Get price from database
                    price_result = await db.execute(
                        select(Settings).where(Settings.key == price_key)
                    )
                    price_setting = price_result.scalar_one_or_none()
                    standard_price = int(price_setting.value) if price_setting else default_price
                    
                    # Check if there's an actual payment for current month
                    current_month = session_date.month
                    current_year = session_date.year
                    
                    existing_payment_result = await db.execute(
                        select(func.sum(Payment.amount)).where(
                            Payment.student_id == student_id,
                            Payment.month == current_month,
                            Payment.year == current_year
                        )
                    )
                    actual_paid_amount = existing_payment_result.scalar()
                    
                    # Use actual paid amount if exists, otherwise use standard price
                    base_price = Decimal(str(actual_paid_amount)) if actual_paid_amount else Decimal(str(standard_price))
                    session_cost = base_price / Decimal(str(sessions_count))
                    
                    # Calculate next month (first day of next month)
                    next_month = session_date + relativedelta(months=1)
                    next_month = next_month.replace(day=1)
                    
                    # Create payment for next month
                    payment = Payment(
                        student_id=student_id,
                        subscription_type=subscription.subscription_type,
                        amount=session_cost,
                        standard_price=standard_price,
                        payment_date=next_month,
                        month=next_month.month,
                        year=next_month.year,
                        notes=f"Автоматическая компенсация за перенос от {session_date.strftime('%d.%m.%Y')}"
                    )
                    db.add(payment)
            
            result_attendances.append(new_attendance)
    
    await db.commit()
    
    # Refresh all attendances
    for attendance in result_attendances:
        await db.refresh(attendance)
    
    return result_attendances


@router.get("/group/{group_id}", response_model=List[AttendanceWithDetails])
async def get_group_attendance(
    group_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get attendance history for a group."""
    # Verify group access
    await check_group_access(group_id, current_user, db)
    
    result = await db.execute(
        select(Attendance, Student.full_name, Student.group_id)
        .join(Student, Attendance.student_id == Student.id)
        .where(Attendance.group_id == group_id)
        .order_by(Attendance.session_date.desc())
    )
    
    attendance_records = result.all()
    
    return [
        AttendanceWithDetails(
            **attendance.__dict__,
            student_name=student_name,
            group_name=str(group_id)
        )
        for attendance, student_name, _ in attendance_records
    ]


@router.get("/student/{student_id}", response_model=List[AttendanceResponse])
async def get_student_attendance(
    student_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get attendance history for a student."""
    # Verify student access
    from app.core.permissions import check_student_access
    await check_student_access(student_id, current_user, db)
    
    result = await db.execute(
        select(Attendance)
        .where(Attendance.student_id == student_id)
        .order_by(Attendance.session_date.desc())
    )
    attendances = result.scalars().all()
    
    return attendances


@router.put("/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(
    attendance_id: uuid.UUID,
    attendance_data: AttendanceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an attendance record."""
    result = await db.execute(select(Attendance).where(Attendance.id == attendance_id))
    attendance = result.scalar_one_or_none()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    # Verify access through group
    await check_group_access(attendance.group_id, current_user, db)
    
    # Update fields
    update_data = attendance_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(attendance, field, value)
    
    await db.commit()
    await db.refresh(attendance)
    
    return attendance


@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attendance(
    attendance_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an attendance record."""
    result = await db.execute(select(Attendance).where(Attendance.id == attendance_id))
    attendance = result.scalar_one_or_none()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    # Verify access through group
    await check_group_access(attendance.group_id, current_user, db)
    
    await db.delete(attendance)
    await db.commit()
    
    return None


@router.get("/date/{group_id}/{session_date}")
async def get_attendance_by_date(
    group_id: uuid.UUID,
    session_date: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get attendance records for a specific group and date."""
    from datetime import datetime
    
    # Verify group access
    await check_group_access(group_id, current_user, db)
    
    # Parse date string
    try:
        date_obj = datetime.strptime(session_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Get all students in the group (including those with this group as additional)
    students_result = await db.execute(
        select(Student).where(
            and_(
                or_(
                    Student.group_id == group_id,
                    group_id == any_(Student.additional_group_ids)
                ),
                Student.is_active == True
            )
        ).order_by(Student.full_name)
    )
    students = students_result.scalars().all()
    
    # Get attendance records for this date
    attendance_result = await db.execute(
        select(Attendance).where(
            Attendance.group_id == group_id,
            Attendance.session_date == date_obj
        )
    )
    attendances = attendance_result.scalars().all()
    
    # Create a map of student_id -> attendance
    attendance_map = {str(a.student_id): a for a in attendances}
    
    # Build response with all students
    result = []
    for student in students:
        attendance = attendance_map.get(str(student.id))
        # Check if this is a bonus group (not primary group)
        is_bonus_group = student.group_id != group_id
        
        result.append({
            'student_id': str(student.id),
            'full_name': student.full_name,
            'birth_date': student.birth_date.isoformat(),
            'status': attendance.status.value if attendance else None,
            'attendance_id': str(attendance.id) if attendance else None,
            'notes': attendance.notes if attendance else None,
            'is_bonus_group': is_bonus_group
        })
    
    return result


@router.get("/statistics/summary")
async def get_attendance_statistics(
    year: int = None,
    month: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get attendance statistics by groups and overall."""
    from datetime import date
    from app.models.group import Group
    
    # Use current year/month if not specified
    if year is None:
        year = date.today().year
    if month is None:
        month = date.today().month
    
    # Get all groups
    groups_result = await db.execute(select(Group))
    groups = groups_result.scalars().all()
    
    group_stats = []
    total_sessions = 0
    total_present = 0
    total_absent = 0
    total_transferred = 0
    
    for group in groups:
        # Count attendances by status for this group
        stats_query = await db.execute(
            select(
                func.count(Attendance.id).label('total'),
                func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label('present'),
                func.sum(case((Attendance.status == AttendanceStatus.ABSENT, 1), else_=0)).label('absent'),
                func.sum(case((Attendance.status == AttendanceStatus.TRANSFERRED, 1), else_=0)).label('transferred')
            )
            .where(
                Attendance.group_id == group.id,
                func.extract('year', Attendance.session_date) == year,
                func.extract('month', Attendance.session_date) == month
            )
        )
        
        stats = stats_query.first()
        total = int(stats[0] or 0)
        present = int(stats[1] or 0)
        absent = int(stats[2] or 0)
        transferred = int(stats[3] or 0)
        
        if total > 0:  # Only include groups with sessions
            attendance_rate = (present / total * 100) if total > 0 else 0
            
            group_stats.append({
                'group_id': str(group.id),
                'group_name': group.name,
                'total_sessions': total,
                'present': present,
                'absent': absent,
                'transferred': transferred,
                'attendance_rate': round(attendance_rate, 2)
            })
            
            total_sessions += total
            total_present += present
            total_absent += absent
            total_transferred += transferred
    
    overall_rate = (total_present / total_sessions * 100) if total_sessions > 0 else 0
    
    return {
        'year': year,
        'month': month,
        'groups': group_stats,
        'overall': {
            'total_sessions': total_sessions,
            'present': total_present,
            'absent': total_absent,
            'transferred': total_transferred,
            'attendance_rate': round(overall_rate, 2)
        }
    }


@router.get("/statistics/group-detail/{group_id}")
async def get_group_attendance_detail(
    group_id: uuid.UUID,
    year: int = None,
    month: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed attendance calendar for a specific group."""
    from calendar import monthrange
    
    # Verify group access
    await check_group_access(group_id, current_user, db)
    
    # Use current year/month if not specified
    if year is None:
        year = date.today().year
    if month is None:
        month = date.today().month
    
    # Get group info
    group_result = await db.execute(select(Group).where(Group.id == group_id))
    group = group_result.scalar_one_or_none()
    
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    
    # Determine training days based on schedule_type
    training_days = []
    if group.schedule_type.value == 'mon_wed_fri':
        training_days = [0, 2, 4]  # Monday, Wednesday, Friday
    elif group.schedule_type.value == 'tue_thu':
        training_days = [1, 3]  # Tuesday, Thursday
    else:
        # Default to all weekdays if unknown type
        training_days = [0, 1, 2, 3, 4]
    
    # Get all training dates in the month
    _, last_day = monthrange(year, month)
    training_dates = []
    
    for day in range(1, last_day + 1):
        current_date = date(year, month, day)
        if current_date.weekday() in training_days:
            training_dates.append(current_date)
    
    # Get all active students in the group
    students_result = await db.execute(
        select(Student).where(
            and_(
                or_(
                    Student.group_id == group_id,
                    group_id == any_(Student.additional_group_ids)
                ),
                Student.is_active == True
            )
        ).order_by(Student.full_name)
    )
    students = students_result.scalars().all()
    
    # Get all attendance records for this group and month
    attendances_result = await db.execute(
        select(Attendance).where(
            and_(
                Attendance.group_id == group_id,
                func.extract('year', Attendance.session_date) == year,
                func.extract('month', Attendance.session_date) == month
            )
        )
    )
    attendances = attendances_result.scalars().all()
    
    # Build attendance map: student_id -> {date -> status}
    attendance_map = {}
    for att in attendances:
        if att.student_id not in attendance_map:
            attendance_map[att.student_id] = {}
        attendance_map[att.student_id][att.session_date] = att.status.value
    
    # Build response
    students_data = []
    for student in students:
        student_attendance = []
        for training_date in training_dates:
            status = attendance_map.get(student.id, {}).get(training_date, None)
            student_attendance.append({
                'date': training_date.isoformat(),
                'day': training_date.day,
                'status': status  # 'present', 'absent', 'transferred', or None
            })
        
        students_data.append({
            'student_id': str(student.id),
            'full_name': student.full_name,
            'attendance': student_attendance
        })
    
    return {
        'group_id': str(group.id),
        'group_name': group.name,
        'year': year,
        'month': month,
        'training_dates': [d.isoformat() for d in training_dates],
        'students': students_data
    }
