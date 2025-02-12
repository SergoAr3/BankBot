import enum


class TransactionType(str, enum.Enum):
    PURCHASE = "purchase"
    CREDIT = "credit"
    DEPOSIT = "deposit"
    SUBSCRIPTION = "subscription"
    TRANSFER = 'transfer'


class CreditJobType(str, enum.Enum):
    DEBT_REMINDER = 'debt_reminder'
    BLOCK_USER = 'block_user'


class ScheduledJobType:
    CREDIT = 'credit'
    DEPOSIT = 'deposit'
