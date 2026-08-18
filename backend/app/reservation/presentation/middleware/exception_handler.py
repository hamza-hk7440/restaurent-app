from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from reservation.domain.exceptions.domain_exceptions import DomainException


def register_reservation_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainException)
    async def handle_domain_exception(_: Request, exc: DomainException):
        return JSONResponse(
            status_code=400,
            content={"detail": exc.message, "error_code": exc.error_code},
        )
