from fastapi import HTTPException, status


class CredentialException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        detail: str = 'Could not validate credentials',
        headers: dict = {"WWW-Authenticate": "Bearer"}
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers
        )