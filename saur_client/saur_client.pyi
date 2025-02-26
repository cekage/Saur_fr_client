# (generated with --quick)

import logging
from typing import Any, Coroutine, Optional

SaurResponse = dict[str, Any]

# SaurResponseDelivery: NewType("SaurResponseDelivery", SaurResponse)
# SaurResponseLastKnow: NewType("SaurResponseLastKnow", SaurResponse)
# SaurResponseMonthly: NewType("SaurResponseMonthly", SaurResponse)
# SaurResponseWeekly: NewType("SaurResponseWeekly", SaurResponse)
# SaurResponseContracts: NewType("SaurResponseContracts", SaurResponse)

class SaurResponseDelivery(SaurResponse):
    pass

class SaurResponseLastKnow(SaurResponse):
    pass

class SaurResponseMonthly(SaurResponse):
    pass

class SaurResponseWeekly(SaurResponse):
    pass

class SaurResponseContracts(SaurResponse):
    pass

BASE_DEV: str
BASE_SAUR: str
ClientSession: Any
USER_AGENT: str
_LOGGER: logging.Logger

class SaurApiError(Exception):
    __doc__: str

class SaurClient:
    __doc__: str
    access_token: Optional[str]
    base_url: str
    clientId: str
    contracts_url: str
    default_section_id: str
    delivery_url: str
    dev_mode: bool
    headers: dict[str, str]
    last_url: str
    login: str
    monthly_url: str
    password: str
    session: type
    token_url: str
    weekly_url: str
    def __aenter__(self) -> Coroutine[Any, Any, Any]: ...
    def __aexit__(
        self, exc_type: None, exc_val: None, exc_tb: None
    ) -> Coroutine[Any, Any, None]: ...
    def __init__(
        self,
        login: str,
        password: str,
        unique_id: str = ...,
        clientId: str = ...,
        dev_mode: bool = ...,
        token: str = ...,
    ) -> None: ...
    def _async_request(
        self,
        method: str,
        url: str,
        payload: Optional[dict[str, Any]] = ...,
        max_retries: int = ...,
        backoff_factor: float = ...,
    ) -> Coroutine[Any, Any, dict[str, Any]]: ...
    def _authenticate(self) -> Coroutine[Any, Any, None]: ...
    def close_session(self) -> Coroutine[Any, Any, None]: ...
    def get_contracts(self) -> Coroutine[Any, Any, SaurResponseContracts]: ...
    def get_deliverypoints_data(
        self, section_id: Optional[str] = ...
    ) -> Coroutine[Any, Any, SaurResponseDelivery]: ...
    def get_lastknown_data(
        self, section_id: Optional[str] = ...
    ) -> Coroutine[Any, Any, SaurResponseLastKnow]: ...
    def get_monthly_data(
        self, year: int, month: int, section_id: Optional[str] = ...
    ) -> Coroutine[Any, Any, SaurResponseMonthly]: ...
    def get_weekly_data(
        self, year: int, month: int, day: int, section_id: Optional[str] = ...
    ) -> Coroutine[Any, Any, SaurResponseWeekly]: ...

def _build_auth_payload(login: str, password: str) -> dict[str, Any]: ...
def _execute_http_request(
    session,
    method: str,
    url: str,
    headers: dict[str, str],
    payload: Optional[dict[str, Any]] = ...,
) -> Coroutine[Any, Any, dict[str, Any]]: ...
def _process_auth_response(self: SaurClient, data: dict[str, Any]) -> None: ...
def _retry_authentication(
    self: SaurClient,
    err: SaurApiError,
    attempt: int,
    max_retries: int,
    headers: dict[str, str],
) -> Coroutine[Any, Any, bool]: ...
