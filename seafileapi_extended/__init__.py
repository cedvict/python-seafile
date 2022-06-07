"""Seafile api client"""
from seafileapi.client import Groups
from seafileapi.exceptions import ClientHttpError, OperationError, DoesNotExist
from seafileapi.group import Group
from seafileapi.repo import RepoRevision

from seafileapi_extended.admin import SeafileAdmin
from seafileapi_extended.client import SeafileApiClient
from seafileapi_extended.exceptions import UserExisted, GroupExisted
from seafileapi_extended.files import SeafDir, SeafFile
from seafileapi_extended.repo import Repo
from seafileapi_extended.repos import Repos
from seafileapi_extended.utils import is_ascii

__version__ = "1.0.0"


__all__ = [
    SeafileAdmin.__name__,
    Groups.__name__,
    Group.__name__,
    ClientHttpError.__name__,
    OperationError.__name__,
    DoesNotExist.__name__,
    RepoRevision.__name__,
    SeafileApiClient.__name__,
    SeafDir.__name__,
    SeafFile.__name__,
    Repo.__name__,
    Repos.__name__,
]


def connect(
    server: str, username: str, password: str, token=None, verify_ssl=True
) -> SeafileApiClient:
    """
    Connect to seafile server
    """
    api_client = SeafileApiClient(server, username, password, token, verify_ssl)
    return api_client
