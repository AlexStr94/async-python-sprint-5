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


class FileError(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = 'Incorrect file',
        headers: dict = {"WWW-Authenticate": "Bearer"}
    ) -> None:
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers
        )


class FileTypeError(FileError):
    def __init__(
        self,
        detail: str = 'Incorrect file type',
    ) -> None:
        super().__init__(
            detail=detail,
        )


class FilePathError(FileError):
    def __init__(
        self,
        detail: str = 'Incorrect path or id',
    ) -> None:
        super().__init__(
            detail=detail,
        )