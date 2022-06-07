"""Seafile Dir, File class"""
from __future__ import annotations

import io
import os
import posixpath
import re
from typing import Optional

from seafileapi.utils import querystr, utf8lize

from seafileapi import files


class _SeafDirentBase(files._SeafDirentBase):
    """Base class for :class:`SeafFile` and :class:`SeafDir`.

    It provides implementation of their common operations.
    """

    def get_share_link(
        self,
        can_edit=False,
        can_download=True,
        password=None,
        expire_days=None,
        direct_link=True,
    ) -> Optional[str]:
        """
        Return share link
        """
        url = "/api/v2.1/share-links/"
        post_data = {
            "repo_id": self.repo.id,
            "path": self.path,
            "permissions": {"can_edit": can_edit, "can_download": can_download},
        }
        if password:
            post_data["password"] = password
        if expire_days:
            post_data["expire_days"] = expire_days
        response = self.client.post(url, data=post_data)
        if response:
            try:
                data = response.json()
                link = data["link"]
                if direct_link:
                    link = link + "?dl=1"
                return link
            except Exception as e:
                print(e, flush=True)


class SeafDir(_SeafDirentBase, files.SeafDir):

    def share_to_user(self, email, permission):
        url = f'/api2/repos/{self.repo.id}/dir/shared_items/' + querystr(p=self.path)
        putdata = {
            'share_type': 'user',
            'username': email,
            'permission': permission
        }
        response = self.client.put(url, data=putdata)
        if response:
            return response.status_code == 200
        else:
            print(f'errors with share: {email}, {permission}')

    def upload(
        self,
        file_data: str | bytes,
        filename: str,
        relative_path: str = "",
        replace=False,
    ):
        """Upload a file to this folder.

        :param:file_data :class:`File` like object
        :param:filename The name of the file

        Return a :class:`SeafFile` object of the newly uploaded file.
        """
        if isinstance(file_data, str):
            file_data = io.BytesIO(file_data.encode("utf-8"))
        upload_url = self._get_upload_link()
        payload = {
            "file": (filename, file_data),
            "parent_dir": self.path,
            "replace": 1 if replace else 0,
            "relative_path": relative_path,
        }
        self.client.post(upload_url, files=payload)
        return self.repo.get_file(posixpath.join(self.path, relative_path, filename))

    def upload_local_file(
        self, filepath, name=None, relative_path: str = "", replace=False
    ):
        """Upload a file to this folder.

        :param: filepath The path to the local file
        :param: name The name of this new file. If None, the name of the local file would be used.

        Return a :class:`SeafFile` object of the newly uploaded file.
        """
        name = name or os.path.basename(filepath)
        with open(filepath, "rb") as fp:
            return self.upload(fp, name, relative_path, replace)

    def _get_upload_link(self):
        url = f"/api2/repos/{self.repo.id}/upload-link/" + querystr(p=self.path)
        resp = self.client.get(url)
        return re.match(r'"(.*)"', resp.text).group(1)

    def _load_dirent(self, dirent_json):
        dirent_json = utf8lize(dirent_json)
        path = posixpath.join(self.path, dirent_json["name"])
        if dirent_json["type"] == "file":
            return SeafFile(self.repo, path, dirent_json["id"], dirent_json["size"])
        else:
            return SeafDir(self.repo, path, dirent_json["id"], 0)


class SeafFile(_SeafDirentBase, files.SeafFile):
    isdir = False
