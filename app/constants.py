"""Application constants and default values."""

# ==================== SUBSCRIPTION PRICES ====================
# Default subscription prices (in rubles)

# Senior groups (Старшие группы)
DEFAULT_SUBSCRIPTION_8_SENIOR_PRICE = 4200
DEFAULT_SUBSCRIPTION_12_SENIOR_PRICE = 4800

# Junior groups (Младшие группы)
DEFAULT_SUBSCRIPTION_8_JUNIOR_PRICE = 3800
DEFAULT_SUBSCRIPTION_12_JUNIOR_PRICE = 4200


# ==================== SETTINGS KEYS ====================
# Keys for settings stored in database
SETTING_KEY_SUBSCRIPTION_8_SENIOR = "subscription_8_senior_price"
SETTING_KEY_SUBSCRIPTION_8_JUNIOR = "subscription_8_junior_price"
SETTING_KEY_SUBSCRIPTION_12_SENIOR = "subscription_12_senior_price"
SETTING_KEY_SUBSCRIPTION_12_JUNIOR = "subscription_12_junior_price"


# ==================== SETTINGS DESCRIPTIONS ====================
SETTING_DESC_SUBSCRIPTION_8_SENIOR = "Стоимость абонемента на 8 занятий для старших"
SETTING_DESC_SUBSCRIPTION_8_JUNIOR = "Стоимость абонемента на 8 занятий для младших"
SETTING_DESC_SUBSCRIPTION_12_SENIOR = "Стоимость абонемента на 12 занятий для старших"
SETTING_DESC_SUBSCRIPTION_12_JUNIOR = "Стоимость абонемента на 12 занятий для младших"


# ==================== PAGINATION ====================
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 1000


# ==================== SESSION ====================
SESSION_VALIDITY_DAYS = 30
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 72  # bcrypt limitation


# ==================== SUBSCRIPTION TYPES ====================
SUBSCRIPTION_TYPE_8_SESSIONS = "8_sessions"
SUBSCRIPTION_TYPE_12_SESSIONS = "12_sessions"


# ==================== GROUP TYPES ====================
AGE_GROUP_SENIOR = "senior"
AGE_GROUP_JUNIOR = "junior"

SCHEDULE_TYPE_MON_WED_FRI = "mon_wed_fri"
SCHEDULE_TYPE_TUE_THU = "tue_thu"

SKILL_LEVEL_BEGINNER = "beginner"
SKILL_LEVEL_EXPERIENCED = "experienced"


# ==================== ATTENDANCE STATUS ====================
ATTENDANCE_STATUS_PRESENT = "present"
ATTENDANCE_STATUS_ABSENT = "absent"
ATTENDANCE_STATUS_EXCUSED = "excused"
ATTENDANCE_STATUS_LATE = "late"


# ==================== PAYMENT STATUS ====================
PAYMENT_STATUS_PAID = "paid"
PAYMENT_STATUS_PENDING = "pending"
PAYMENT_STATUS_OVERDUE = "overdue"


# ==================== PAYMENT TYPES ====================
PAYMENT_TYPE_CASH = "cash"
PAYMENT_TYPE_CARD = "card"
PAYMENT_TYPE_TRANSFER = "transfer"
