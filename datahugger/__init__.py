from datahugger.api import get
from datahugger.api import info

__all__ = ["get", "info"]

try:
    from datahugger._version import __version__
    from datahugger._version import __version_tuple__
except ImportError:
    __version__ = "0.0.0"
    __version_tuple__ = (0, 0, 0)
