from datahugger.api import get
from datahugger.api import info
from datahugger.api import parse_resource_identifier
from datahugger.base import DownloadResult
from datahugger.exceptions import DOIError
from datahugger.exceptions import RepositoryNotSupportedError

__all__ = [
    "get",
    "info",
    "parse_resource_identifier",
    "DownloadResult",
    "DOIError",
    "RepositoryNotSupportedError",
]

try:
    from datahugger._version import __version__
    from datahugger._version import __version_tuple__
except ImportError:
    __version__ = "0.0.0"
    __version_tuple__ = (0, 0, 0)
