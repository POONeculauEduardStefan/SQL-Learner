from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def ok(data=None, status_code: int = 200, meta: dict | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({"success": True, "data": data}),
    )


def err(code: str, message: str, status_code: int = 400, details: dict | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({"success": False, "error": {"code": code, "message": message, "details": details}}),
    )
