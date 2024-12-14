

class UserIsBlocked(Exception):
    """
    Пользователь заблокирован
    """
    pass

class UserPasswordReset(Exception):
    """
    Необходимо сменить пароль
    """
    pass