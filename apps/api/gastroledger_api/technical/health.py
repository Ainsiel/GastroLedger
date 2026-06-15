from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["technical"])


class HealthResponse(BaseModel):
    service: Literal["api"]
    status: Literal["ok"]


@router.get(
    "/health",
    response_model=HealthResponse,
    operation_id="getApiHealth",
    summary="Check API readiness",
)
def health() -> HealthResponse:
    return HealthResponse(service="api", status="ok")
