"""Date and time helper utilities."""
from datetime import date, datetime, timedelta
from typing import Tuple


def get_month_range(year: int, month: int) -> Tuple[date, date]:
    """Get the first and last day of a month."""
    first_day = date(year, month, 1)
    
    # Get last day of month
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    return first_day, last_day


def get_year_range(year: int) -> Tuple[date, date]:
    """Get the first and last day of a year."""
    first_day = date(year, 1, 1)
    last_day = date(year, 12, 31)
    return first_day, last_day


def get_current_reporting_month() -> date:
    """Get the current reporting month (1st of current month)."""
    today = date.today()
    return date(today.year, today.month, 1)


def calculate_age(birth_date: date) -> int:
    """Calculate age from birth date."""
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age
