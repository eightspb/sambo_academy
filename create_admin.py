"""Script to create the first admin user."""
import asyncio
from getpass import getpass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal, engine, Base
from app.models.user import User
from app.core.security import get_password_hash


async def create_admin_user():
    """Create an admin user interactively."""
    print("=== Создание администратора ===\n")
    
    # Collect user information
    username = input("Имя пользователя: ").strip()
    email = input("Email: ").strip()
    full_name = input("Полное имя: ").strip()
    password = getpass("Пароль: ")
    password_confirm = getpass("Подтвердите пароль: ")
    
    # Validate input
    if not all([username, email, full_name, password]):
        print("\n❌ Ошибка: Все поля обязательны для заполнения")
        return
    
    if password != password_confirm:
        print("\n❌ Ошибка: Пароли не совпадают")
        return
    
    if len(password) < 8:
        print("\n❌ Ошибка: Пароль должен быть не менее 8 символов")
        return
    
    if len(password.encode('utf-8')) > 72:
        print("\n❌ Ошибка: Пароль слишком длинный (максимум 72 байта)")
        print("   Используйте более короткий пароль (до 72 символов)")
        return
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create admin user
    async with AsyncSessionLocal() as session:
        try:
            # Check if user already exists
            result = await session.execute(
                select(User).where(User.username == username)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"\n❌ Ошибка: Пользователь с именем '{username}' уже существует")
                return
            
            # Check if email already exists
            result = await session.execute(
                select(User).where(User.email == email)
            )
            existing_email = result.scalar_one_or_none()
            
            if existing_email:
                print(f"\n❌ Ошибка: Пользователь с email '{email}' уже существует")
                return
            
            # Create new admin user
            admin_user = User(
                username=username,
                email=email,
                full_name=full_name,
                hashed_password=get_password_hash(password),
                is_admin=True,
                is_active=True
            )
            
            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)
            
            print("\n✅ Администратор успешно создан!")
            print(f"   ID: {admin_user.id}")
            print(f"   Имя пользователя: {admin_user.username}")
            print(f"   Email: {admin_user.email}")
            print(f"   Полное имя: {admin_user.full_name}")
            print("\nТеперь вы можете войти в систему с этими учетными данными.")
            
        except Exception as e:
            print(f"\n❌ Ошибка при создании пользователя: {e}")
            await session.rollback()


def main():
    """Run the admin creation script."""
    asyncio.run(create_admin_user())


if __name__ == "__main__":
    main()
