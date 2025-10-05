"""Tests for statistics endpoints."""
import pytest
from httpx import AsyncClient
from datetime import date, datetime


class TestAttendanceStatistics:
    """Tests for attendance statistics endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_attendance_statistics_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful retrieval of attendance statistics."""
        year = 2025
        month = 10
        
        response = await client.get(
            f"/api/attendance/statistics/summary?year={year}&month={month}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "year" in data
        assert "month" in data
        assert "groups" in data
        assert "overall" in data
        
        # Check values
        assert data["year"] == year
        assert data["month"] == month
        assert isinstance(data["groups"], list)
        
        # Check overall stats
        overall = data["overall"]
        assert "total_sessions" in overall
        assert "present" in overall
        assert "absent" in overall
        assert "transferred" in overall
        assert "attendance_rate" in overall
        
        # Check types
        assert isinstance(overall["total_sessions"], int)
        assert isinstance(overall["attendance_rate"], (int, float))
    
    @pytest.mark.asyncio
    async def test_get_attendance_statistics_default_params(self, client: AsyncClient, auth_headers: dict):
        """Test attendance statistics with default year/month."""
        response = await client.get(
            "/api/attendance/statistics/summary",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should use current year/month as default
        current_date = date.today()
        assert data["year"] == current_date.year
        assert data["month"] == current_date.month
    
    @pytest.mark.asyncio
    async def test_get_attendance_statistics_group_structure(self, client: AsyncClient, auth_headers: dict):
        """Test group statistics structure."""
        response = await client.get(
            "/api/attendance/statistics/summary?year=2025&month=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check each group has required fields
        for group in data["groups"]:
            assert "group_id" in group
            assert "group_name" in group
            assert "total_sessions" in group
            assert "present" in group
            assert "absent" in group
            assert "transferred" in group
            assert "attendance_rate" in group
            
            # Check attendance rate is between 0 and 100
            assert 0 <= group["attendance_rate"] <= 100


class TestPaymentStatistics:
    """Tests for payment statistics endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_payment_statistics_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful retrieval of payment statistics."""
        year = 2025
        
        response = await client.get(
            f"/api/payments/statistics/summary?year={year}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be a list of monthly summaries
        assert isinstance(data, list)
        
        # Check structure of each month
        for month_data in data:
            assert "year" in month_data
            assert "month" in month_data
            assert "total_amount" in month_data
            assert "payment_count" in month_data
            assert "paid_count" in month_data
            assert "pending_count" in month_data
            assert "overdue_count" in month_data
            
            # Check types
            assert isinstance(month_data["year"], int)
            assert isinstance(month_data["month"], int)
            assert isinstance(month_data["payment_count"], int)
            
            # Month should be between 1 and 12
            assert 1 <= month_data["month"] <= 12
    
    @pytest.mark.asyncio
    async def test_get_payment_statistics_default_year(self, client: AsyncClient, auth_headers: dict):
        """Test payment statistics with default year."""
        response = await client.get(
            "/api/payments/statistics/summary",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should use current year as default
        if len(data) > 0:
            current_year = date.today().year
            assert all(item["year"] == current_year for item in data)


class TestUnpaidStudents:
    """Tests for unpaid students endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_unpaid_students_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful retrieval of unpaid students."""
        year = 2025
        month = 10
        
        response = await client.get(
            f"/api/payments/unpaid-students?year={year}&month={month}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "year" in data
        assert "month" in data
        assert "total_unpaid" in data
        assert "students" in data
        
        # Check values
        assert data["year"] == year
        assert data["month"] == month
        assert isinstance(data["students"], list)
        assert isinstance(data["total_unpaid"], int)
        
        # total_unpaid should match students list length
        assert data["total_unpaid"] == len(data["students"])
    
    @pytest.mark.asyncio
    async def test_get_unpaid_students_structure(self, client: AsyncClient, auth_headers: dict):
        """Test structure of unpaid students data."""
        response = await client.get(
            "/api/payments/unpaid-students?year=2025&month=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check each student has required fields
        for student in data["students"]:
            assert "student_id" in student
            assert "full_name" in student
            assert "group_name" in student
            assert "phone" in student
            assert "email" in student
            
            # Check types
            assert isinstance(student["student_id"], str)
            assert isinstance(student["full_name"], str)
    
    @pytest.mark.asyncio
    async def test_get_unpaid_students_default_params(self, client: AsyncClient, auth_headers: dict):
        """Test unpaid students with default year/month."""
        response = await client.get(
            "/api/payments/unpaid-students",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should use current year/month as default
        current_date = date.today()
        assert data["year"] == current_date.year
        assert data["month"] == current_date.month
    
    @pytest.mark.asyncio
    async def test_get_unpaid_students_unauthorized(self, client: AsyncClient):
        """Test unpaid students without authentication."""
        response = await client.get("/api/payments/unpaid-students")
        
        # Should require authentication
        assert response.status_code == 401


class TestTournamentDuplicatePrevention:
    """Tests for tournament duplicate participant prevention."""
    
    @pytest.mark.asyncio
    async def test_add_duplicate_participant_fails(self, client: AsyncClient, auth_headers: dict, tournament_id: str, student_id: str):
        """Test that adding duplicate participant fails."""
        # Add participant first time
        participant_data = {
            "student_id": student_id,
            "place": 1,
            "total_fights": 5,
            "wins": 4,
            "losses": 1,
            "weight_category": "45-50kg"
        }
        
        response1 = await client.post(
            f"/api/tournaments/{tournament_id}/participants",
            json=participant_data,
            headers=auth_headers
        )
        
        assert response1.status_code == 201
        
        # Try to add same participant again
        response2 = await client.post(
            f"/api/tournaments/{tournament_id}/participants",
            json=participant_data,
            headers=auth_headers
        )
        
        # Should fail with 400
        assert response2.status_code == 400
        assert "уже добавлен" in response2.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_update_participant_success(self, client: AsyncClient, auth_headers: dict, tournament_id: str, participation_id: str):
        """Test successful participant update."""
        update_data = {
            "place": 2,
            "total_fights": 6,
            "wins": 5,
            "losses": 1
        }
        
        response = await client.put(
            f"/api/tournaments/{tournament_id}/participants/{participation_id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check updated values
        assert data["place"] == 2
        assert data["total_fights"] == 6
        assert data["wins"] == 5
    
    @pytest.mark.asyncio
    async def test_delete_participant_success(self, client: AsyncClient, auth_headers: dict, tournament_id: str, participation_id: str):
        """Test successful participant deletion."""
        response = await client.delete(
            f"/api/tournaments/{tournament_id}/participants/{participation_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify participant is deleted
        get_response = await client.get(
            f"/api/tournaments/{tournament_id}/results",
            headers=auth_headers
        )
        
        assert get_response.status_code == 200
        results = get_response.json()
        
        # Participation should not be in results
        assert not any(r["id"] == participation_id for r in results)
