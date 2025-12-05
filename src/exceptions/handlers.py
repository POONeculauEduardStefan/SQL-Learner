from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.exceptions.exceptions import AppException


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exc_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": {
                "status_code": exc.status_code, "message": exc.message, "details": exc.details
            }},
        )

    @app.exception_handler(RequestValidationError)
    async def app_exc_handler(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            errors.append({
                "field": error["loc"][-1],
                "message": error["msg"]
            })

        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "status_code": 422,
                    "message": "Validation error",
                    "details": errors
                }
            }
        )
