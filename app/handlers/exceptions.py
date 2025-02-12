class HandlersBaseException(BaseException):
    pass


class NegativeAmountError(HandlersBaseException):
    """Исключение для случая, когда пользователь ввел отрицательную сумму"""
    pass

class NotEnoughBalanceError(HandlersBaseException):
    """Исключение для случая, когда у пользователя недостаточно средств"""
    pass

class ExceedsCreditLimitError(HandlersBaseException):
    """Исключение для случая, когда пользователь пытается взять кредит на сумму, превышающую лимит"""
    pass

class ExceedsDebtAmountError(HandlersBaseException):
    """Исключение для случая, когда пользователь пытается погасить кредит суммой, превышающей долг"""
    pass