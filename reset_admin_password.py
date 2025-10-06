"""Script to reset admin password."""
import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash


async def reset_admin_password(username: str, new_password: str):
    """Reset admin password."""
    async with AsyncSessionLocal() as session:
        try:
            # Find user
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print(f"❌ Пользователь '{username}' не найден")
                return False
            
            # Update password
            user.hashed_password = get_password_hash(new_password)
            await session.commit()
            
            print(f"✅ Пароль для пользователя '{username}' успешно изменен!")
            print(f"   Email: {user.email}")
            print(f"   Новый пароль: {new_password}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            await session.rollback()
            return False


async def main():
    if len(sys.argv) < 3:
        print("Использование: python reset_admin_password.py <username> <new_password>")
        print("Пример: python reset_admin_password.py admin admin123")
        return
    
    username = sys.argv[1]
    new_password = sys.argv[2]
    
    await reset_admin_password(username, new_password)


if __name__ == "__main__":
    asyncio.run(main())
