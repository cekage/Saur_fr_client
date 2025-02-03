"""Package SaurClient."""

try:
    from ._version import __version__
except ImportError:
    __version__ = (
        "0.0.0+unknown"  # Pour les cas où le package n'est pas installé via setuptools
    )

from .saur_client import SaurClient
