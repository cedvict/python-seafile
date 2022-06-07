"""Seafile api client"""
from seafileapi_extended.admin import SeafileAdmin
from seafileapi_extended.client import SeafileApiClient
from seafileapi_extended.exceptions import (
    UserExisted,
    GroupExisted,
    ClientHttpError,
    OperationError,
    DoesNotExist,
)
from seafileapi_extended.group import Group, AdminGroup, GroupMember
from seafileapi_extended.groups import Groups, AdminGroups
from seafileapi_extended.files import SeafDir, SeafFile
from seafileapi_extended.repo import Repo, RepoRevision
from seafileapi_extended.repos import Repos


__version__ = "1.0.5"


__all__ = [
    SeafileAdmin.__name__,
    AdminGroups.__name__,
    Groups.__name__,
    AdminGroup.__name__,
    Group.__name__,
    GroupMember.__name__,
    ClientHttpError.__name__,
    UserExisted.__name__,
    GroupExisted.__name__,
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
    api_client = SeafileApiClient(
        server,
        username,
        password,
        token,
        verify_ssl,
    )
    return api_client
