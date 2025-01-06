from fastapi import HTTPException, status


class BookingException(HTTPException):
    status_code = 500
    detail = ''
    
    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class UserCreateErrorException(BookingException):
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    detail='При создании пользователя произошла ошибка'

class GroupDeleteErrorException(BookingException):
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    detail='При удалении группы произошла ошибка'

class UserLoginAlreadyExistsException(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail='Пользователь с таким логином уже существует'

class UserEmailAlreadyExistsException(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail='Пользователь с таким email уже существует'

class UserIsBlocked(BookingException):
    status_code=status.HTTP_403_FORBIDDEN
    detail='пользователь заблокирован'

class IncorrectEmailOrPasswordException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail='Неверная почта или пароль'
    
class TokenExpiredException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail='Срок действия токена истек'
        
class TokenAbsentException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail='Токен отсутствует'
        
class IncorrectTokenFormatException(BookingException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail='Неверный формат токена'

class CannotAddDataToDatabase(BookingException):
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    detail='Не удалось добавить запись'
