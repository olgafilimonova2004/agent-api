from functools import wraps
from http import HTTPStatus

from asyncpg.exceptions import (
    ForeignKeyViolationError,
    NotNullViolationError,
    PostgresError,
    UndefinedColumnError,
    UniqueViolationError,
)
from fastapi.exceptions import HTTPException
from loguru import logger


class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=HTTPStatus.NOT_FOUND, detail=detail)


class BadRequestError(HTTPException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=HTTPStatus.BAD_REQUEST, detail=detail)


class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=HTTPStatus.UNAUTHORIZED, detail=detail)


class RoleAcessError(HTTPException):
    def __init__(self, detail: str = "Uncorrect role"):
        super().__init__(status_code=HTTPStatus.FORBIDDEN, detail=detail)


class InternalServerError(HTTPException):
    def __init__(self, detail: str = "Internal Server Error"):
        super().__init__(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=detail)


class ConflictError(HTTPException):
    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=HTTPStatus.CONFLICT, detail=detail)


class TimeoutError(HTTPException):
    def __init__(self, detail: str = "Timeout"):
        super().__init__(status_code=HTTPStatus.GATEWAY_TIMEOUT, detail=detail)


def asyncpg_errors_decorator(func):
    @wraps(func)
    async def inner(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except NotNullViolationError as e:
            raise ConflictError(detail=f"Not null relations: {e}")
        except ForeignKeyViolationError as e:
            raise NotFoundError(detail=f"Object not found: {e}")
        except UndefinedColumnError as e:
            raise NotFoundError(detail=f"Object not found: {e}")
        except UniqueViolationError as e:
            raise BadRequestError(
                detail=f"Object with property relation already exist: {e}"
            )
        except PostgresError as e:
            logger.exception(e)
            raise InternalServerError(detail=f"Unknown server error: {e}")

    return inner
