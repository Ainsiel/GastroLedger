from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def problem_response(
    status: int,
    code: str,
    correlation_id: str,
    errors: list[dict[str, str]],
    *,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "type": code,
            "title": "The request could not be completed",
            "status": status,
            "correlationId": correlation_id,
            "errors": errors,
        },
        headers=headers,
    )


def configure_problem_handlers(application: FastAPI) -> None:
    @application.exception_handler(RequestValidationError)
    async def validation_problem(
        _request: Request, error: RequestValidationError
    ) -> JSONResponse:
        details: list[dict[str, str]] = []
        for item in error.errors():
            location = [str(part) for part in item["loc"] if part != "body"]
            details.append(
                {
                    "field": ".".join(location),
                    "code": str(item["type"]),
                    "detail": "review field",
                }
            )
        return problem_response(
            422,
            "platform.validation_error",
            str(uuid4()),
            details,
        )
