"""Comprehensive tests for payments endpoints."""
import pytest
from httpx import AsyncClient
from datetime import date
from decimal import Decimal


class TestPaymentCreation:
    """Tests for creating payments."""
    
    @pytest.mark.asyncio
    async def test_create_payment_full(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_student,
        db_session
    ):
        """Test creating full payment."""
        from app.models.subscription import Subscription, SubscriptionType
        
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
        await db_session.refresh(subscription)
        
        data = {
            "student_id": str(test_student.id),
            "subscription_id": str(subscription.id),
            "amount": 4200.00,
            "payment_date": "2025-10-01",
            "payment_month": "2025-10-01",
            "payment_type": "full",
            "status": "paid",
            "notes": "Тестовая оплата"
        }
        
        response = await client.post(
            "/api/payments",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        assert result["amount"] == "4200.00"
        assert result["payment_type"] == "full"
        assert result["status"] == "paid"
    
    @pytest.mark.asyncio
    async def test_create_payment_partial(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_student,
        db_session
    ):
        """Test creating partial payment."""
        from app.models.subscription import Subscription, SubscriptionType
        
        subscription = Subscription(
            student_id=test_student.id,
            subscription_type=SubscriptionType.TWELVE_SESSIONS,
            total_sessions=12,
            remaining_sessions=12,
            price=Decimal("4200.00"),
            start_date=date(2025, 10, 1),
            expiry_date=date(2025, 12, 1),
            is_active=True
        )
        db_session.add(subscription)
        await db_session.commit()
        await db_session.refresh(subscription)
        
        data = {
            "student_id": str(test_student.id),
            "subscription_id": str(subscription.id),
            "amount": 2100.00,
            "payment_date": "2025-10-01",
            "payment_month": "2025-10-01",
            "payment_type": "partial",
            "status": "pending",
            "notes": "Частичная оплата"
        }
        
        response = await client.post(
            "/api/payments",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        assert result["amount"] == "2100.00"
        assert result["payment_type"] == "partial"
    
    @pytest.mark.asyncio
    async def test_create_payment_with_discount(
        self, 
        client: AsyncClient, 
        auth_headers: dict, 
        test_student,
        db_session
    ):
        """Test creating payment with discount."""
        from app.models.subscription import Subscription, SubscriptionType
        
        subscription = Subscription(
            student_id=test_student.id,
            subscription_type=SubscriptionType.EIGHT_SESSIONS,
            total_sessions=8,
            remaining_sessions=8,
            price=Decimal("3500.00"),
            start_date=date(2025, 10, 1),
            expiry_date=date(2025, 12, 1),
            is_active=True
        )
        db_session.add(subscription)
        await db_session.commit()
        await db_session.refresh(subscription)
        
        data = {
            "student_id": str(test_student.id),
            "subscription_id": str(subscription.id),
            "amount": 3500.00,
            "payment_date": "2025-10-01",
            "payment_month": "2025-10-01",
            "payment_type": "discount",
            "status": "paid",
            "notes": "Скидка 700₽"
        }
        
        response = await client.post(
            "/api/payments",
            json=data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        result = response.json()
        assert result["payment_type"] == "discount"
        assert "Скидка" in result["notes"]


class TestPaymentRetrieval:
    """Tests for retrieving payments."""
    
    @pytest.mark.asyncio
    async def test_get_monthly_payments(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        test_student,
        db_session
    ):
        """Test getting payments for specific month."""
        from app.models.payment import Payment, PaymentType, PaymentStatus
        
        # Create test payment
        payment = Payment(
            student_id=test_student.id,
            amount=Decimal("4200.00"),
            payment_date=date(2025, 10, 1),
            payment_month=date(2025, 10, 1),
            payment_type=PaymentType.FULL,
            status=PaymentStatus.PAID,
            notes="Test"
        )
        db_session.add(payment)
        await db_session.commit()
        
        response = await client.get(
            "/api/payments/month/2025/10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_get_unpaid_students(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        test_student
    ):
        """Test getting list of unpaid students."""
        response = await client.get(
            "/api/payments/unpaid-students?year=2025&month=10",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "year" in data
        assert "month" in data
        assert "total_unpaid" in data
        assert "students" in data
        assert isinstance(data["students"], list)


class TestPaymentUpdate:
    """Tests for updating payments."""
    
    @pytest.mark.asyncio
    async def test_update_payment_amount(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        test_student,
        db_session
    ):
        """Test updating payment amount."""
        from app.models.payment import Payment, PaymentType, PaymentStatus
        
        # Create payment
        payment = Payment(
            student_id=test_student.id,
            amount=Decimal("4200.00"),
            payment_date=date(2025, 10, 1),
            payment_month=date(2025, 10, 1),
            payment_type=PaymentType.FULL,
            status=PaymentStatus.PAID
        )
        db_session.add(payment)
        await db_session.commit()
        await db_session.refresh(payment)
        
        update_data = {
            "amount": 3800.00,
            "notes": "Скидка применена"
        }
        
        response = await client.put(
            f"/api/payments/{payment.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["amount"] == "3800.00"
        assert "Скидка" in result["notes"]
    
    @pytest.mark.asyncio
    async def test_update_payment_status(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        test_student,
        db_session
    ):
        """Test updating payment status."""
        from app.models.payment import Payment, PaymentType, PaymentStatus
        
        payment = Payment(
            student_id=test_student.id,
            amount=Decimal("4200.00"),
            payment_date=date(2025, 10, 1),
            payment_month=date(2025, 10, 1),
            payment_type=PaymentType.FULL,
            status=PaymentStatus.PENDING
        )
        db_session.add(payment)
        await db_session.commit()
        await db_session.refresh(payment)
        
        update_data = {
            "status": "paid"
        }
        
        response = await client.put(
            f"/api/payments/{payment.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "paid"


class TestPaymentDeletion:
    """Tests for deleting payments."""
    
    @pytest.mark.asyncio
    async def test_delete_payment(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        test_student,
        db_session
    ):
        """Test deleting payment."""
        from app.models.payment import Payment, PaymentType, PaymentStatus
        from sqlalchemy import select
        
        payment = Payment(
            student_id=test_student.id,
            amount=Decimal("4200.00"),
            payment_date=date(2025, 10, 1),
            payment_month=date(2025, 10, 1),
            payment_type=PaymentType.FULL,
            status=PaymentStatus.PAID
        )
        db_session.add(payment)
        await db_session.commit()
        await db_session.refresh(payment)
        
        payment_id = payment.id
        
        response = await client.delete(
            f"/api/payments/{payment_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 204
        
        # Verify deletion
        result = await db_session.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        deleted_payment = result.scalar_one_or_none()
        assert deleted_payment is None


class TestPaymentStatistics:
    """Tests for payment statistics."""
    
    @pytest.mark.asyncio
    async def test_get_payment_summary(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        test_student,
        db_session
    ):
        """Test getting payment statistics summary."""
        from app.models.payment import Payment, PaymentType, PaymentStatus
        
        # Create multiple payments
        for i in range(3):
            payment = Payment(
                student_id=test_student.id,
                amount=Decimal("4200.00"),
                payment_date=date(2025, 10, i+1),
                payment_month=date(2025, 10, 1),
                payment_type=PaymentType.FULL,
                status=PaymentStatus.PAID
            )
            db_session.add(payment)
        
        await db_session.commit()
        
        response = await client.get(
            "/api/payments/statistics/summary?year=2025",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, list)
