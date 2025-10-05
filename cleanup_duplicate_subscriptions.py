#!/usr/bin/env python3
"""
Скрипт для очистки дублирующихся активных абонементов.
Для каждого студента оставляет только ОДИН самый новый активный абонемент.
"""
import asyncio
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.subscription import Subscription
from app.models.student import Student
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://sambo_user:sambo_password@db:5432/sambo_academy")


async def cleanup_duplicate_subscriptions():
    """Очистка дублирующихся активных абонементов."""
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        print("\n" + "="*60)
        print("ОЧИСТКА ДУБЛИРУЮЩИХСЯ АКТИВНЫХ АБОНЕМЕНТОВ")
        print("="*60 + "\n")
        
        # Получить всех студентов
        students_result = await session.execute(select(Student))
        students = students_result.scalars().all()
        
        total_deactivated = 0
        students_with_duplicates = 0
        
        for student in students:
            # Получить все активные абонементы студента
            active_subs_result = await session.execute(
                select(Subscription)
                .where(
                    Subscription.student_id == student.id,
                    Subscription.is_active == True
                )
                .order_by(Subscription.start_date.desc())
            )
            active_subs = active_subs_result.scalars().all()
            
            if len(active_subs) > 1:
                students_with_duplicates += 1
                print(f"\n👤 Студент: {student.full_name}")
                print(f"   📊 Найдено активных абонементов: {len(active_subs)}")
                
                # Оставляем только первый (самый новый)
                newest_sub = active_subs[0]
                print(f"   ✅ Оставляем: {newest_sub.subscription_type.value} (начало: {newest_sub.start_date})")
                
                # Деактивируем остальные
                for old_sub in active_subs[1:]:
                    print(f"   ❌ Деактивируем: {old_sub.subscription_type.value} (начало: {old_sub.start_date})")
                    old_sub.is_active = False
                    total_deactivated += 1
        
        # Сохраняем изменения
        await session.commit()
        
        print("\n" + "="*60)
        print("ИТОГИ ОЧИСТКИ")
        print("="*60)
        print(f"Всего студентов проверено: {len(students)}")
        print(f"Студентов с дубликатами: {students_with_duplicates}")
        print(f"Абонементов деактивировано: {total_deactivated}")
        print("="*60 + "\n")
        
        # Проверка результата
        print("Проверка результата...")
        check_result = await session.execute(
            select(Student.id, func.count(Subscription.id))
            .join(Subscription, Subscription.student_id == Student.id)
            .where(Subscription.is_active == True)
            .group_by(Student.id)
            .having(func.count(Subscription.id) > 1)
        )
        remaining_duplicates = check_result.all()
        
        if remaining_duplicates:
            print(f"⚠️  ВНИМАНИЕ: Осталось студентов с дубликатами: {len(remaining_duplicates)}")
        else:
            print("✅ УСПЕШНО: У всех студентов теперь по 1 активному абонементу!")
    
    await engine.dispose()


if __name__ == "__main__":
    print("\n🚀 Запуск скрипта очистки...\n")
    asyncio.run(cleanup_duplicate_subscriptions())
    print("\n✅ Скрипт завершен!\n")
