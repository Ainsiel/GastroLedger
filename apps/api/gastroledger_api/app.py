from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from gastroledger_api.runtime import configure_logging

configure_logging()

app = FastAPI(title="GastroLedger API", version="0.0.0")


class HealthResponse(BaseModel):
    service: Literal["api"]
    status: Literal["ok"]


@app.get("/health", response_model=HealthResponse, tags=["technical"])
def health() -> HealthResponse:
    return HealthResponse(service="api", status="ok")

