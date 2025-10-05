"""Settings API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.settings import Settings
from app.schemas.settings import SettingsCreate, SettingsUpdate, SettingsResponse, SubscriptionPrices
from app.core.security import get_current_admin_user
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

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=List[SettingsResponse])
async def get_all_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get all settings (admin only)."""
    result = await db.execute(
        select(Settings).order_by(Settings.key)
    )
    settings = result.scalars().all()
    return settings


@router.get("/prices", response_model=SubscriptionPrices)
async def get_subscription_prices(
    db: AsyncSession = Depends(get_db)
):
    """Get subscription prices (public endpoint)."""
    # Get prices for all types
    price_keys = [
        SETTING_KEY_SUBSCRIPTION_8_SENIOR,
        SETTING_KEY_SUBSCRIPTION_8_JUNIOR,
        SETTING_KEY_SUBSCRIPTION_12_SENIOR,
        SETTING_KEY_SUBSCRIPTION_12_JUNIOR
    ]
    
    prices = {}
    defaults = {
        SETTING_KEY_SUBSCRIPTION_8_SENIOR: DEFAULT_SUBSCRIPTION_8_SENIOR_PRICE,
        SETTING_KEY_SUBSCRIPTION_8_JUNIOR: DEFAULT_SUBSCRIPTION_8_JUNIOR_PRICE,
        SETTING_KEY_SUBSCRIPTION_12_SENIOR: DEFAULT_SUBSCRIPTION_12_SENIOR_PRICE,
        SETTING_KEY_SUBSCRIPTION_12_JUNIOR: DEFAULT_SUBSCRIPTION_12_JUNIOR_PRICE
    }
    
    for key in price_keys:
        result = await db.execute(
            select(Settings).where(Settings.key == key)
        )
        setting = result.scalar_one_or_none()
        prices[key] = int(setting.value) if setting else defaults[key]
    
    return SubscriptionPrices(**prices)


@router.get("/{key}", response_model=SettingsResponse)
async def get_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Get a specific setting by key (admin only)."""
    result = await db.execute(
        select(Settings).where(Settings.key == key)
    )
    setting = result.scalar_one_or_none()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting with key '{key}' not found"
        )
    
    return setting


@router.post("", response_model=SettingsResponse, status_code=status.HTTP_201_CREATED)
async def create_setting(
    setting_data: SettingsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new setting (admin only)."""
    # Check if setting already exists
    result = await db.execute(
        select(Settings).where(Settings.key == setting_data.key)
    )
    existing_setting = result.scalar_one_or_none()
    
    if existing_setting:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Setting with key '{setting_data.key}' already exists"
        )
    
    new_setting = Settings(**setting_data.model_dump())
    
    db.add(new_setting)
    await db.commit()
    await db.refresh(new_setting)
    
    return new_setting


@router.put("/{key}", response_model=SettingsResponse)
async def update_setting(
    key: str,
    setting_data: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update a setting (admin only)."""
    result = await db.execute(
        select(Settings).where(Settings.key == key)
    )
    setting = result.scalar_one_or_none()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting with key '{key}' not found"
        )
    
    # Update fields
    update_data = setting_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(setting, field, value)
    
    await db.commit()
    await db.refresh(setting)
    
    return setting


@router.put("/prices/update", response_model=SubscriptionPrices)
async def update_subscription_prices(
    prices: SubscriptionPrices,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update subscription prices (admin only)."""
    price_settings = [
        (SETTING_KEY_SUBSCRIPTION_8_SENIOR, prices.subscription_8_senior_price, SETTING_DESC_SUBSCRIPTION_8_SENIOR),
        (SETTING_KEY_SUBSCRIPTION_8_JUNIOR, prices.subscription_8_junior_price, SETTING_DESC_SUBSCRIPTION_8_JUNIOR),
        (SETTING_KEY_SUBSCRIPTION_12_SENIOR, prices.subscription_12_senior_price, SETTING_DESC_SUBSCRIPTION_12_SENIOR),
        (SETTING_KEY_SUBSCRIPTION_12_JUNIOR, prices.subscription_12_junior_price, SETTING_DESC_SUBSCRIPTION_12_JUNIOR),
    ]
    
    for key, value, description in price_settings:
        result = await db.execute(
            select(Settings).where(Settings.key == key)
        )
        setting = result.scalar_one_or_none()
        
        if setting:
            setting.value = str(value)
        else:
            setting = Settings(
                key=key,
                value=str(value),
                description=description,
                is_system=True
            )
            db.add(setting)
    
    await db.commit()
    
    return prices
