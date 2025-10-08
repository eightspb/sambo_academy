"""Comprehensive tests for students endpoints."""
import pytest
from httpx import AsyncClient
from datetime import date


class TestStudentCreation:
    """Tests for creating students."""
    
    @pytest.mark.asyncio
    async def test_create_student(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_group,
        test_user
    ):
        """Test creating new student."""
        data = {
            "full_name": "Новый Ученик",
            "birth_date": "2012-05-15",
            "phone": "+79991234567",
            "email": "new@student.com",
            "group_id": str(test_group.id),
            "trainer_id": str(test_user.id),
            "is_active": True
        }
        
        response = await client.post(
            "/api/students",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        assert result["full_name"] == "Новый Ученик"
        assert result["is_active"] == True
    
    @pytest.mark.asyncio
    async def test_create_student_with_additional_groups(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_group,
        test_user,
        db_session
    ):
        """Test creating student with additional groups."""
        from app.models.group import Group
        
        # Create second group
        group2 = Group(
            name="Дополнительная группа",
            age_group="senior",
            schedule_type="tue_thu",
            skill_level="experienced",
            trainer_id=test_user.id
        )
        db_session.add(group2)
        await db_session.commit()
        await db_session.refresh(group2)
        
        data = {
            "full_name": "Ученик с доп группами",
            "birth_date": "2010-03-20",
            "phone": "+79991234568",
            "group_id": str(test_group.id),
            "additional_group_ids": [str(group2.id)],
            "trainer_id": str(test_user.id),
            "is_active": True
        }
        
        response = await client.post(
            "/api/students",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        assert len(result["additional_group_ids"]) == 1


class TestStudentRetrieval:
    """Tests for retrieving students."""
    
    @pytest.mark.asyncio
    async def test_get_all_students(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        test_student
    ):
        """Test getting all students."""
        response = await client.get(
            "/api/students",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_get_students_by_group(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        test_student,
        test_group
    ):
        """Test getting students filtered by group."""
        response = await client.get(
            f"/api/students?group_id={test_group.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)
        
        # All students should belong to test_group
        for student in result:
            assert student["group_id"] == str(test_group.id)
    
    @pytest.mark.asyncio
    async def test_get_active_students_only(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        test_student,
        db_session
    ):
        """Test getting only active students."""
        from app.models.student import Student
        
        # Create inactive student
        inactive_student = Student(
            full_name="Неактивный Ученик",
            birth_date=date(2010, 1, 1),
            phone="+79991234569",
            group_id=test_student.group_id,
            trainer_id=test_student.trainer_id,
            is_active=False
        )
        db_session.add(inactive_student)
        await db_session.commit()
        
        response = await client.get(
            "/api/students?is_active=true",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # All returned students should be active
        for student in result:
            assert student["is_active"] == True
    
    @pytest.mark.asyncio
    async def test_get_student_by_id(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        test_student
    ):
        """Test getting specific student by ID."""
        response = await client.get(
            f"/api/students/{test_student.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["id"] == str(test_student.id)
        assert result["full_name"] == test_student.full_name


class TestStudentUpdate:
    """Tests for updating students."""
    
    @pytest.mark.asyncio
    async def test_update_student_info(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        test_student
    ):
        """Test updating student information."""
        update_data = {
            "phone": "+79999999999",
            "email": "updated@email.com",
            "notes": "Обновленная информация"
        }
        
        response = await client.put(
            f"/api/students/{test_student.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["phone"] == "+79999999999"
        assert result["email"] == "updated@email.com"
    
    @pytest.mark.asyncio
    async def test_deactivate_student(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        test_student
    ):
        """Test deactivating student."""
        update_data = {
            "is_active": False
        }
        
        response = await client.put(
            f"/api/students/{test_student.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["is_active"] == False
    
    @pytest.mark.asyncio
    async def test_move_student_to_another_group(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        test_student,
        test_user,
        db_session
    ):
        """Test moving student to different group."""
        from app.models.group import Group
        
        # Create new group
        new_group = Group(
            name="Новая группа",
            age_group="senior",
            schedule_type="mon_wed_fri",
            skill_level="experienced",
            trainer_id=test_user.id
        )
        db_session.add(new_group)
        await db_session.commit()
        await db_session.refresh(new_group)
        
        update_data = {
            "group_id": str(new_group.id)
        }
        
        response = await client.put(
            f"/api/students/{test_student.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["group_id"] == str(new_group.id)


class TestStudentDeletion:
    """Tests for deleting students."""
    
    @pytest.mark.asyncio
    async def test_delete_student(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        test_group,
        test_user,
        db_session
    ):
        """Test deleting student."""
        from app.models.student import Student
        from sqlalchemy import select
        
        # Create student to delete
        student = Student(
            full_name="Удаляемый Ученик",
            birth_date=date(2010, 1, 1),
            phone="+79991234570",
            group_id=test_group.id,
            trainer_id=test_user.id,
            is_active=True
        )
        db_session.add(student)
        await db_session.commit()
        await db_session.refresh(student)
        
        student_id = student.id
        
        response = await client.delete(
            f"/api/students/{student_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify deletion
        result = await db_session.execute(
            select(Student).where(Student.id == student_id)
        )
        deleted_student = result.scalar_one_or_none()
        assert deleted_student is None
