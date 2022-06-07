"""Repo class"""
from typing import Optional
from urllib.parse import urlencode

from requests import Response
from seafileapi import repo
from seafileapi_extended.files import SeafDir, SeafFile
from seafileapi.utils import raise_does_not_exist


class Repo(repo.Repo):
    """
    A seafile library
    """

    @raise_does_not_exist("The requested file does not exist")
    def get_file(self, path) -> Optional[SeafFile]:
        """Get the file object located in `path` in this repo.

        Return a :class:`SeafFile` object
        """
        assert path.startswith("/")
        try:
            url = f"/api2/repos/{self.id}/file/detail/"
            query = "?" + urlencode(dict(p=path))
            file_json = self.client.get(url + query).json()
            if "id" in file_json and "size" in file_json:
                return SeafFile(self, path, file_json["id"], file_json["size"])
        except Exception as error:
            print(error, flush=True)

    @raise_does_not_exist("The requested dir does not exist")
    def get_dir(self, path) -> Optional[SeafDir]:
        """Get the dir object located in `path` in this repo.

        Return a :class: `SeafDir` object
        """
        assert path.startswith("/")
        try:
            url = f"/api2/repos/{self.id}/dir/"
            query = "?" + urlencode(dict(p=path))
            response = self.client.get(url + query)
            dir_id = response.headers["oid"]
            dir_json = response.json()
            dir = SeafDir(self, path, dir_id)
            dir.load_entries(dir_json)
            return dir
        except Exception as error:
            print(error, flush=True)

    def delete(self) -> Response:
        """Remove this repo. Only the repo owner can do this"""
        response = self.client.delete(f"/api2/repos/{self.id}")
        if response:
            print(f"status deleted: {self.id} - {response.ok}")
        else:
            print(f"errors with delete {self.id}")
        return response
