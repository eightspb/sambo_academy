"""Comprehensive tests for subscriptions endpoints."""
import pytest
from httpx import AsyncClient
from datetime import date
from decimal import Decimal


class TestSubscriptionCreation:
    """Tests for creating subscriptions."""
    
    @pytest.mark.asyncio
    async def test_create_subscription_8_sessions(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_student
    ):
        """Test creating 8 sessions subscription."""
        data = {
            "student_id": str(test_student.id),
            "subscription_type": "8_sessions",
            "price": 4200.00,
            "start_date": "2025-10-01"
        }
        
        response = await client.post(
            "/api/subscriptions",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        assert result["subscription_type"] == "8_sessions"
        assert result["total_sessions"] == 8
        assert result["remaining_sessions"] == 8
        assert result["is_active"] == True
    
    @pytest.mark.asyncio
    async def test_create_subscription_12_sessions(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_student
    ):
        """Test creating 12 sessions subscription."""
        data = {
            "student_id": str(test_student.id),
            "subscription_type": "12_sessions",
            "price": 4800.00,
            "start_date": "2025-10-01"
        }
        
        response = await client.post(
            "/api/subscriptions",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        assert result["subscription_type"] == "12_sessions"
        assert result["total_sessions"] == 12
        assert result["remaining_sessions"] == 12
    
    @pytest.mark.asyncio
    async def test_create_subscription_with_custom_expiry(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_student
    ):
        """Test creating subscription with custom expiry date."""
        data = {
            "student_id": str(test_student.id),
            "subscription_type": "8_sessions",
            "price": 4200.00,
            "start_date": "2025-10-01",
            "expiry_date": "2025-12-31"
        }
        
        response = await client.post(
            "/api/subscriptions",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        assert result["expiry_date"] == "2025-12-31"


class TestSubscriptionRetrieval:
    """Tests for retrieving subscriptions."""
    
    @pytest.mark.asyncio
    async def test_get_student_subscriptions(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_student,
        db_session
    ):
        """Test getting all subscriptions for a student."""
        from app.models.subscription import Subscription, SubscriptionType
        
        # Create multiple subscriptions
        for i in range(2):
            subscription = Subscription(
                student_id=test_student.id,
                subscription_type=SubscriptionType.EIGHT_SESSIONS,
                total_sessions=8,
                remaining_sessions=8-i,
                price=Decimal("4200.00"),
                start_date=date(2025, 10+i, 1),
                expiry_date=date(2025, 12+i, 1),
                is_active=(i == 0)
            )
            db_session.add(subscription)
        
        await db_session.commit()
        
        response = await client.get(
            f"/api/subscriptions/student/{test_student.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)
        assert len(result) >= 2
        
        # Check that active subscription is first
        assert result[0]["is_active"] == True


class TestSubscriptionUpdate:
    """Tests for updating subscriptions."""
    
    @pytest.mark.asyncio
    async def test_update_subscription_remaining_sessions(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_student,
        db_session
    ):
        """Test updating remaining sessions."""
        from app.models.subscription import Subscription, SubscriptionType
        
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
        await db_session.refresh(subscription)
        
        update_data = {
            "remaining_sessions": 5
        }
        
        response = await client.put(
            f"/api/subscriptions/{subscription.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["remaining_sessions"] == 5
    
    @pytest.mark.asyncio
    async def test_deactivate_subscription(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_student,
        db_session
    ):
        """Test deactivating subscription."""
        from app.models.subscription import Subscription, SubscriptionType
        
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
        await db_session.refresh(subscription)
        
        update_data = {
            "is_active": False
        }
        
        response = await client.put(
            f"/api/subscriptions/{subscription.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["is_active"] == False


class TestSubscriptionDeletion:
    """Tests for deleting subscriptions."""
    
    @pytest.mark.asyncio
    async def test_delete_subscription(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_student,
        db_session
    ):
        """Test deleting subscription."""
        from app.models.subscription import Subscription, SubscriptionType
        from sqlalchemy import select
        
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
        await db_session.refresh(subscription)
        
        subscription_id = subscription.id
        
        response = await client.delete(
            f"/api/subscriptions/{subscription_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify deletion
        result = await db_session.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        deleted_sub = result.scalar_one_or_none()
        assert deleted_sub is None


class TestSubscriptionConstraints:
    """Tests for subscription business rules."""
    
    @pytest.mark.asyncio
    async def test_cannot_create_duplicate_active_subscription(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_student,
        db_session
    ):
        """Test that only one active subscription per student is allowed."""
        from app.models.subscription import Subscription, SubscriptionType
        
        # Create first active subscription
        subscription1 = Subscription(
            student_id=test_student.id,
            subscription_type=SubscriptionType.EIGHT_SESSIONS,
            total_sessions=8,
            remaining_sessions=8,
            price=Decimal("4200.00"),
            start_date=date(2025, 10, 1),
            expiry_date=date(2025, 12, 1),
            is_active=True
        )
        db_session.add(subscription1)
        await db_session.commit()
        
        # Try to create second active subscription
        data = {
            "student_id": str(test_student.id),
            "subscription_type": "8_sessions",
            "price": 4200.00,
            "start_date": "2025-10-01"
        }
        
        response = await client.post(
            "/api/subscriptions",
            json=data,
            headers=auth_headers
        )
        
        # Should fail due to unique constraint
        assert response.status_code in [400, 409, 500]  # Depending on error handling
