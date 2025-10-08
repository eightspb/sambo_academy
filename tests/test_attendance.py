"""Comprehensive tests for attendance endpoints."""
import pytest
from httpx import AsyncClient
from datetime import date, datetime
from decimal import Decimal


class TestAttendanceMarking:
    """Tests for marking attendance."""
    
    @pytest.mark.asyncio
    async def test_mark_attendance_present(self, client: AsyncClient, auth_headers: dict, test_student, test_group):
        """Test marking student as present."""
        data = {
            "group_id": str(test_group.id),
            "session_date": "2025-10-07",
            "attendances": [
                {
                    "student_id": str(test_student.id),
                    "status": "present",
                    "notes": None
                }
            ]
        }
        
        response = await client.post(
            "/api/attendance/mark",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        assert len(result) == 1
        assert result[0]["status"] == "present"
    
    @pytest.mark.asyncio
    async def test_mark_attendance_absent(self, client: AsyncClient, auth_headers: dict, test_student, test_group):
        """Test marking student as absent."""
        data = {
            "group_id": str(test_group.id),
            "session_date": "2025-10-08",
            "attendances": [
                {
                    "student_id": str(test_student.id),
                    "status": "absent",
                    "notes": "Болен"
                }
            ]
        }
        
        response = await client.post(
            "/api/attendance/mark",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        assert len(result) == 1
        assert result[0]["status"] == "absent"
        assert result[0]["notes"] == "Болен"
    
    @pytest.mark.asyncio
    async def test_mark_attendance_transferred(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_student, 
        test_group,
        db_session
    ):
        """Test marking student as transferred - creates payment for next month."""
        from app.models.subscription import Subscription, SubscriptionType
        from app.models.payment import Payment
        
        # Create subscription first
        subscription = Subscription(
            student_id=test_student.id,
            subscription_type=SubscriptionType.EIGHT_SESSIONS,
            total_sessions=8,
            remaining_sessions=8,
            price=Decimal("4200.00"),
            start_date=date(2025, 10, 1),
            expiry_date=date(2025, 12, 1),
            is_active=True
        )
        db_session.add(subscription)
        await db_session.commit()
        
        data = {
            "group_id": str(test_group.id),
            "session_date": "2025-10-07",
            "attendances": [
                {
                    "student_id": str(test_student.id),
                    "status": "transferred",
                    "notes": None
                }
            ]
        }
        
        response = await client.post(
            "/api/attendance/mark",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        assert len(result) == 1
        assert result[0]["status"] == "transferred"
        
        # Check that payment was created for next month
        from sqlalchemy import select
        payments_result = await db_session.execute(
            select(Payment).where(Payment.student_id == test_student.id)
        )
        payments = payments_result.scalars().all()
        
        # Should have created a partial payment
        assert len(payments) > 0
        partial_payment = payments[0]
        assert partial_payment.payment_type.value == "partial"
        assert partial_payment.status.value == "pending"
        assert "перенос" in partial_payment.notes.lower()
    
    @pytest.mark.asyncio
    async def test_mark_attendance_null_status_removes_record(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_student, 
        test_group,
        db_session
    ):
        """Test that null status removes existing attendance record."""
        from app.models.attendance import Attendance, AttendanceStatus
        from app.models.user import User
        from sqlalchemy import select
        
        # Get test user
        user_result = await db_session.execute(select(User).limit(1))
        user = user_result.scalar_one()
        
        # Create attendance first
        attendance = Attendance(
            student_id=test_student.id,
            group_id=test_group.id,
            session_date=date(2025, 10, 09),
            status=AttendanceStatus.PRESENT,
            marked_by=user.id
        )
        db_session.add(attendance)
        await db_session.commit()
        
        # Now mark with null status
        data = {
            "group_id": str(test_group.id),
            "session_date": "2025-10-09",
            "attendances": [
                {
                    "student_id": str(test_student.id),
                    "status": None,
                    "notes": None
                }
            ]
        }
        
        response = await client.post(
            "/api/attendance/mark",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        
        # Check that attendance was deleted
        result = await db_session.execute(
            select(Attendance).where(
                Attendance.student_id == test_student.id,
                Attendance.session_date == date(2025, 10, 9)
            )
        )
        deleted_attendance = result.scalar_one_or_none()
        assert deleted_attendance is None
    
    @pytest.mark.asyncio
    async def test_mark_attendance_invalid_student_id(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_group
    ):
        """Test marking attendance with invalid student ID."""
        data = {
            "group_id": str(test_group.id),
            "session_date": "2025-10-07",
            "attendances": [
                {
                    "student_id": "invalid-uuid",
                    "status": "present",
                    "notes": None
                }
            ]
        }
        
        response = await client.post(
            "/api/attendance/mark",
            json=data,
            headers=auth_headers
        )
        
        # Should still return 201 but skip invalid student
        assert response.status_code == 201
        result = response.json()
        assert len(result) == 0  # No attendances created
    
    @pytest.mark.asyncio
    async def test_mark_attendance_invalid_status(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_student, 
        test_group
    ):
        """Test marking attendance with invalid status."""
        data = {
            "group_id": str(test_group.id),
            "session_date": "2025-10-07",
            "attendances": [
                {
                    "student_id": str(test_student.id),
                    "status": "invalid_status",
                    "notes": None
                }
            ]
        }
        
        response = await client.post(
            "/api/attendance/mark",
            json=data,
            headers=auth_headers
        )
        
        # Should still return 201 but skip invalid status
        assert response.status_code == 201
        result = response.json()
        assert len(result) == 0


class TestAttendanceRetrieval:
    """Tests for retrieving attendance data."""
    
    @pytest.mark.asyncio
    async def test_get_attendance_by_date(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_student, 
        test_group,
        db_session
    ):
        """Test getting attendance for specific date."""
        response = await client.get(
            f"/api/attendance/date/{test_group.id}/2025-10-07",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)
        
        # Should include test student
        student_found = any(s["student_id"] == str(test_student.id) for s in result)
        assert student_found
    
    @pytest.mark.asyncio
    async def test_get_attendance_invalid_date_format(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_group
    ):
        """Test getting attendance with invalid date format."""
        response = await client.get(
            f"/api/attendance/date/{test_group.id}/invalid-date",
            headers=auth_headers
        )
        
        assert response.status_code == 400


class TestAttendanceStatistics:
    """Tests for attendance statistics."""
    
    @pytest.mark.asyncio
    async def test_get_group_detail_statistics(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_group,
        test_student,
        db_session
    ):
        """Test getting detailed group attendance calendar."""
        response = await client.get(
            f"/api/attendance/statistics/group-detail/{test_group.id}?year=2025&month=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "group_id" in data
        assert "group_name" in data
        assert "year" in data
        assert "month" in data
        assert "training_dates" in data
        assert "students" in data
        
        # Check values
        assert data["year"] == 2025
        assert data["month"] == 10
        assert isinstance(data["training_dates"], list)
        assert isinstance(data["students"], list)
        
        # Check student data structure
        if len(data["students"]) > 0:
            student = data["students"][0]
            assert "student_id" in student
            assert "full_name" in student
            assert "attendance" in student
            assert isinstance(student["attendance"], list)
