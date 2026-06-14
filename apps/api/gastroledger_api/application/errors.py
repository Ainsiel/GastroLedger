from dataclasses import dataclass
from typing import Literal

from gastroledger_api.application.identifiers import CorrelationId

ErrorCategory = Literal[
    "validation_error",
    "authentication_required",
    "forbidden",
    "not_found",
    "conflict",
    "unprocessable_exception",
    "rate_limited",
    "internal_error",
]


@dataclass(frozen=True)
class ErrorDetail:
    code: str
    detail: str
    field: str | None = None


@dataclass(frozen=True)
class ApplicationError(Exception):
    category: ErrorCategory
    code: str
    correlation_id: CorrelationId
    details: tuple[ErrorDetail, ...] = ()

