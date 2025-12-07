"""Public interface for the python_common_sample package."""

from .config import load_config, load_config_as
from .errors import OcSampleError, OcSampleUserError

__all__ = [
    "OcSampleError",
    "OcSampleUserError",
    "load_config",
    "load_config_as",
]
