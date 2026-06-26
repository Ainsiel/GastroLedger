from typing import Protocol, TypeVar

from gastroledger_api.application.contracts import ApplicationResult, RequestEnvelope

InputT = TypeVar("InputT", contravariant=True)
OutputT = TypeVar("OutputT", covariant=True)


class Interactor(Protocol[InputT, OutputT]):
    async def execute(self, request: RequestEnvelope[InputT]) -> ApplicationResult[OutputT]: ...

