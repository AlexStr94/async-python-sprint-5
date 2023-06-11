from fastapi import HTTPException, status


class DatabaseConnectionError(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE,
        detail: str = 'Database is unvailable',
        headers: dict = {"WWW-Authenticate": "Bearer"}
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers
        )


class UserAlreadyExist(Exception):
    pass


class FileDoesNotExist(Exception):
    pass

class FieldError(Exception):
    def __init__(self, field: str = '', *args, **kwargs):
        if field:
            self.message = f'Field {field} is required'
        else:
            self.message = 'Field error'
        
        super().__init__(self.message, *args, **kwargs)