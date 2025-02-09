from aiohttp.client import ClientSession
from typing import (
    Iterator,
    Optional,
)


def _build_auth_payload(login: str, password: str) -> dict[str, typing.Any]: ...


async def _execute_http_request(
    session: ClientSession,
    method: str,
    url: str,
    headers: dict[str, str],
    payload: Optional[dict[str, Any]] = ...
) -> dict[str, Any]: ...


def _process_auth_response(self: SaurClient, data: dict[str, typing.Any]) -> None: ...


async def _retry_authentication(
    self: SaurClient,
    err: SaurApiError,
    attempt: int,
    max_retries: int,
    headers: dict[str, str]
) -> bool: ...


class SaurClient:
    async def __aexit__(self, exc_type: None, exc_val: None, exc_tb: None) -> Iterator[None]: ...
    def __init__(self, login: str, password: str, unique_id: str = ..., dev_mode: bool = ..., token: str = ...) -> None: ...
    async def _async_request(
        self,
        method: str,
        url: str,
        payload: Optional[dict[str, Any]] = ...,
        max_retries: int = ...,
        backoff_factor: float = ...
    ) -> dict[str, Any]: ...
    async def _authenticate(self) -> None: ...
    async def close_session(self) -> None: ...
    async def get_deliverypoints_data(self) -> SaurResponseDelivery: ...
