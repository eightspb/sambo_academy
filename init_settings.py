"""Script to initialize default settings."""
import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal, engine, Base
from app.models.settings import Settings
from app.constants import (
    DEFAULT_SUBSCRIPTION_8_SENIOR_PRICE,
    DEFAULT_SUBSCRIPTION_8_JUNIOR_PRICE,
    DEFAULT_SUBSCRIPTION_12_SENIOR_PRICE,
    DEFAULT_SUBSCRIPTION_12_JUNIOR_PRICE,
    SETTING_KEY_SUBSCRIPTION_8_SENIOR,
    SETTING_KEY_SUBSCRIPTION_8_JUNIOR,
    SETTING_KEY_SUBSCRIPTION_12_SENIOR,
    SETTING_KEY_SUBSCRIPTION_12_JUNIOR,
    SETTING_DESC_SUBSCRIPTION_8_SENIOR,
    SETTING_DESC_SUBSCRIPTION_8_JUNIOR,
    SETTING_DESC_SUBSCRIPTION_12_SENIOR,
    SETTING_DESC_SUBSCRIPTION_12_JUNIOR,
)


async def init_settings():
    """Initialize default settings."""
    print("=== Инициализация настроек ===\n")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        try:
            # Default subscription prices from constants
            default_settings = [
                {
                    "key": SETTING_KEY_SUBSCRIPTION_8_SENIOR,
                    "value": str(DEFAULT_SUBSCRIPTION_8_SENIOR_PRICE),
                    "description": SETTING_DESC_SUBSCRIPTION_8_SENIOR,
                    "is_system": True
                },
                {
                    "key": SETTING_KEY_SUBSCRIPTION_8_JUNIOR,
                    "value": str(DEFAULT_SUBSCRIPTION_8_JUNIOR_PRICE),
                    "description": SETTING_DESC_SUBSCRIPTION_8_JUNIOR,
                    "is_system": True
                },
                {
                    "key": SETTING_KEY_SUBSCRIPTION_12_SENIOR,
                    "value": str(DEFAULT_SUBSCRIPTION_12_SENIOR_PRICE),
                    "description": SETTING_DESC_SUBSCRIPTION_12_SENIOR,
                    "is_system": True
                },
                {
                    "key": SETTING_KEY_SUBSCRIPTION_12_JUNIOR,
                    "value": str(DEFAULT_SUBSCRIPTION_12_JUNIOR_PRICE),
                    "description": SETTING_DESC_SUBSCRIPTION_12_JUNIOR,
                    "is_system": True
                }
            ]
            
            added_count = 0
            for setting_data in default_settings:
                # Check if setting already exists
                result = await session.execute(
                    select(Settings).where(Settings.key == setting_data["key"])
                )
                existing_setting = result.scalar_one_or_none()
                
                if existing_setting:
                    print(f"⚠️  {setting_data['key']} - уже существует (текущее значение: {existing_setting.value})")
                    continue
                
                # Create new setting
                new_setting = Settings(**setting_data)
                session.add(new_setting)
                added_count += 1
                print(f"✅ {setting_data['key']} = {setting_data['value']} - создано")
            
            await session.commit()
            
            if added_count > 0:
                print(f"\n🎉 Успешно создано {added_count} настроек!")
            else:
                print(f"\n✅ Все настройки уже инициализированы!")
            
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            await session.rollback()
            raise


def main():
    """Run the initialization script."""
    asyncio.run(init_settings())


if __name__ == "__main__":
    main()
