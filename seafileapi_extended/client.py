"""Seafile api client class"""
from typing import Optional
import re
import requests
from requests import Response
from seafileapi import client
from seafileapi.utils import urljoin

from seafileapi_extended import SeafileAdmin
from seafileapi_extended.exceptions import AuthenticationError
from seafileapi_extended.groups import AdminGroups, Groups
from seafileapi_extended.ping import Ping
from seafileapi_extended.utils import is_ascii
from seafileapi.exceptions import ClientHttpError
from seafileapi_extended.repos import Repos
from sys import exit

request_filename_pattern = re.compile(b"filename\*=.*")

seahub_api_auth_token = 40


class SeafileApiClient(client.SeafileApiClient):
    """Wraps seafile web api"""

    def __init__(
        self,
        server: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        verify_ssl: bool = True,
    ):
        """Wraps various basic operations to interact with seahub http api."""
        super().__init__(server, username, password)
        self._token = token

        self.verify_ssl = verify_ssl
        self.default_timeout = 30
        self.repos = Repos(self)
        self.groups = Groups(self)
        self.admin_groups = AdminGroups(self)
        self.ping = Ping(self)
        self.admin = SeafileAdmin(self)

        if token is None:
            self._get_token()

    def _get_token(self):
        data = {"username": self.username, "password": self.password}
        url = urljoin(self.server, "/api2/auth-token/")
        try:
            with requests.post(
                url, data=data, verify=self.verify_ssl, timeout=self.default_timeout
            ) as response:
                if response.status_code != 200:
                    if response.status_code == 400:
                        resp_json = response.json()
                        if 'non_field_errors' in resp_json:
                            raise AuthenticationError(response.status_code, response.content)
                    raise ClientHttpError(response.status_code, response.content)
                try:
                    _token = response.json()
                except Exception as e:
                    print(e, flush=True)
                else:
                    self._token = _token.get("token", "")
                    if len(self._token) != seahub_api_auth_token:
                        exit("The length of seahub api auth token should be 40")
        except Exception as error:
            exit(error)

    def _rewrite_request(self, *args, **kwargs):
        def func(prepared_request):
            if "files" in kwargs:
                file = kwargs["files"].get("file", None)
                if file and isinstance(file[0], str):
                    filename = file[0]
                    if not is_ascii(filename):
                        filename = (filename + '"\r').encode("utf-8")
                        prepared_request.body = request_filename_pattern.sub(
                            b'filename="' + filename, prepared_request.body, count=1
                        )

            return prepared_request

        return func

    def _send_request(
        self, method: str, url: str, *args, **kwargs
    ) -> Optional[Response]:
        if not url.startswith("http"):
            url = urljoin(self.server, url)

        headers = kwargs.get("headers", {})
        headers.setdefault("Authorization", f"Token {self._token}")
        kwargs["headers"] = headers

        expected = kwargs.pop("expected", 200)
        if not hasattr(expected, "__iter__"):
            expected = (expected,)

        kwargs["auth"] = self._rewrite_request(
            *args, **kwargs
        )  # hack to rewrite post body

        kwargs["method"] = method
        kwargs["url"] = url
        kwargs["verify"] = self.verify_ssl
        kwargs["timeout"] = self.default_timeout
        try:
            response = requests.request(*args, **kwargs)
        except Exception as e:
            print(e, flush=True)
        else:
            if response.status_code not in expected:
                msg = "Expected %s, but get %s" % (
                    " or ".join(map(str, expected)),
                    response.status_code,
                )
                raise ClientHttpError(response.status_code, msg)
            return response

