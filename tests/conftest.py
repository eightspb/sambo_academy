"""Pytest configuration and fixtures."""
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from app.main import app
from app.database import Base, get_db
from app.core.security import create_access_token


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://sambo_user:sambo_password@db:5432/sambo_test"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Drop all tables after tests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> dict:
    """Create authentication headers for tests."""
    # Create test user token
    test_user_data = {"sub": "test@example.com", "user_id": "test-user-id"}
    token = create_access_token(test_user_data)
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_user(db_session):
    """Create test user."""
    from app.models.user import User
    from app.core.security import get_password_hash
    
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        full_name="Test User",
        is_admin=True
    )
    
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


@pytest.fixture
async def test_group(db_session, test_user):
    """Create test group."""
    from app.models.group import Group
    
    group = Group(
        name="Тестовая группа",
        age_group="senior",
        schedule_type="mon_wed_fri",
        skill_level="beginner",
        trainer_id=test_user.id
    )
    
    db_session.add(group)
    await db_session.commit()
    await db_session.refresh(group)
    
    return group


@pytest.fixture
async def test_student(db_session, test_group, test_user):
    """Create test student."""
    from app.models.student import Student
    from datetime import date
    
    student = Student(
        full_name="Тестовый Ученик",
        birth_date=date(2010, 1, 1),
        phone="+79991234567",
        email="student@test.com",
        group_id=test_group.id,
        trainer_id=test_user.id,
        is_active=True
    )
    
    db_session.add(student)
    await db_session.commit()
    await db_session.refresh(student)
    
    return student


@pytest.fixture
async def test_tournament(db_session, test_user):
    """Create test tournament."""
    from app.models.tournament import Tournament
    from datetime import date
    
    tournament = Tournament(
        name="Тестовый турнир",
        tournament_date=date(2025, 10, 15),
        location="Тестовый зал",
        description="Описание турнира",
        created_by=test_user.id
    )
    
    db_session.add(tournament)
    await db_session.commit()
    await db_session.refresh(tournament)
    
    return tournament


@pytest.fixture
def tournament_id(test_tournament) -> str:
    """Get tournament ID as string."""
    return str(test_tournament.id)


@pytest.fixture
def student_id(test_student) -> str:
    """Get student ID as string."""
    return str(test_student.id)


@pytest.fixture
async def test_participation(db_session, test_tournament, test_student):
    """Create test tournament participation."""
    from app.models.tournament import TournamentParticipation
    
    participation = TournamentParticipation(
        tournament_id=test_tournament.id,
        student_id=test_student.id,
        place=1,
        total_fights=5,
        wins=4,
        losses=1,
        weight_category="45-50kg"
    )
    
    db_session.add(participation)
    await db_session.commit()
    await db_session.refresh(participation)
    
    return participation


@pytest.fixture
def participation_id(test_participation) -> str:
    """Get participation ID as string."""
    return str(test_participation.id)
