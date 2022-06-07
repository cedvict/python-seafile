"""Exceptions class"""
from seafileapi.exceptions import ClientHttpError


class AuthenticationError(ClientHttpError):
    """Authentication error occurred while retrieving access token"""


class UserExisted(Exception):
    pass


class GroupExisted(Exception):
    pass