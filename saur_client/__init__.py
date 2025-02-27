"""Package SaurClient."""

try:
    from ._version import __version__
except ImportError:
    # Pour les cas où le package n'est pas installé via setuptools
    __version__ = "0.0.0+unknown"

from .saur_client import (
    SaurApiError,
    SaurClient,
    SaurResponse,
    SaurResponseContracts,
    SaurResponseDelivery,
    SaurResponseLastKnow,
    SaurResponseMonthly,
    SaurResponseWeekly,
)

__all__ = [
    "SaurApiError",
    "SaurClient",
    "SaurResponse",
    "SaurResponseContracts",
    "SaurResponseDelivery",
    "SaurResponseLastKnow",
    "SaurResponseMonthly",
    "SaurResponseWeekly",
]
