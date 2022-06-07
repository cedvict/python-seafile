"""Repo class"""
from typing import Optional
from urllib.parse import urlencode

from requests import Response
from seafileapi import repo
from seafileapi.exceptions import DoesNotExist

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

    @staticmethod
    def create_from_repo_id(client, repo_id):
        url = "/api2/repos/%s/" % (repo_id,)
        resp = client.get(url).json()
        param = {
            "repo_name": resp["name"],
            "repo_desc": resp["desc"],
            "encrypted": resp["encrypted"],
            "owner": resp["owner"],
            "perm": resp["permission"]
        }
        return Repo(client, repo_id, **param)

    def get_name(self):
        return self.name

    def is_exist_dir(self, path):
        """
        Determine whether the path exists
        :param path:
        :return:
        """
        exist = False
        try:
            dir = self.get_dir(path, False)
            if dir:
                exist = True
        except DoesNotExist:
            pass

        return exist

    def _share_operation(self, operation, share_type, users=None, group_id=None, permission=None):
        """Manage sharing on this repo
        :param operation: Can be 'share' or 'unshare'
        :param share_type: Type of share, can be 'personal', 'group' or 'public'.
                           If personal, then users param must be specified.
                           If group, then group_id param must be specified.
       :param users: String, list or tuple of usernames/email addresses
       :param group_id: String group id from Seafile
       :param permission: String, 'r' or 'rw'
        """
        url = '/api2/shared-repos/' + self.id + '/'
        if share_type not in ['personal', 'group', 'public']:
            raise ValueError('Invalid share type: {}'.format(share_type))
        if share_type == 'personal' and (users is None or len(users) == 0):
            raise ValueError('Invalid users supplied for personal share: {}'.format(users))
        if share_type == 'group' and group_id is None:
            raise ValueError('Invalid group_id for group share: {}'.format(group_id))
        if permission not in ['r', 'rw']:
            raise ValueError('Invalid permission: {}'.format(permission))
        if isinstance(users, (list, tuple)):
            users = ','.join(users)
        query = '?' + urlencode(dict(share_type=share_type, users=users, group_id=group_id, permission=permission))
        if operation == 'share':
            resp = self.client.put(url + query)
        elif operation == 'unshare':
            query = '?' + urlencode(dict(share_type=share_type, user=users, group_id=group_id, permission=permission))
            resp = self.client.delete(url + query)
        else:
            raise ValueError('Invalid share operation: {}'.format(operation))

    def share(self, share_type, users=None, group_id=None, permission=None):
        self._share_operation('share', share_type=share_type, users=users, group_id=group_id, permission=permission)

    def unshare(self, share_type, users=None, group_id=None, permission=None):
        if isinstance(users, (list, tuple)):
            # Unshare operation does not accept a list of users, only a single user
            raise TypeError('Unshare operation only accepts one user at a time')
        self._share_operation('unshare', share_type=share_type, users=users, group_id=group_id, permission=permission)

    ## Operations only the repo owner can do:

    def update(self, name=None, desc=None):
        """Update the name and/or description of this repo. Only the repo owner can do
        this.
        """
        url = '/api2/repos/' + self.id + '/?op=rename'
        params = dict(repo_name=self.name)
        self.client.post(url, data=params)

    def share_folder(self,path, share_type, users=None, group_id=None, permission=None):
        '''
        :param path:        [string]
        :param share_type:  [string] one of values: 'user', 'group' or 'public'.
        :param users:       [string] email
        :param group_id:    [int]
        :param permission:  [string] one of values: 'r' , 'rw'
        :return:
        '''
        return self._share_folder_operation('share',path, share_type=share_type, users=users, group_id=group_id, permission=permission)

    def unshare_folder(self,path, share_type, users=None, group_id=None, permission=None):
        '''
        :param path:        [string]
        :param share_type:  [string] one of values: 'user', 'group' or 'public'.
        :param users:       [string] email
        :param group_id:    [int]
        :param permission:  [string] one of values: 'r' , 'rw'
        :return:
        '''
        return self._share_folder_operation('unshare',path, share_type=share_type, users=users, group_id=group_id, permission=permission)

    def list_shares(self, path=None, share_type=None):
        url = '/api2/repos/' + self.id + '/dir/shared_items/?' + urlencode(dict(p=path))
        if path is None:
            path = '/'
        if share_type not in ['user', 'group', 'public']:
            raise ValueError('Invalid share type: {}'.format(share_type))

        params = {'p': path, 'share_type': share_type}
        resp = self.client.get(url, params=params, expected=[200]).json()
        return resp

    def _share_folder_operation(self, operation, path, share_type, users=None, group_id=None, permission=None):
        """Manage sharing on this folder
        :param operation: Can be 'share' or 'unshare'
        :param share_type: Type of share, can be 'personal', 'group' or 'public'.
                           If personal, then users param must be specified.
                           If group, then group_id param must be specified.
       :param users: String, list or tuple of usernames/email addresses
       :param group_id: String group id from Seafile
       :param permission: String, 'r' or 'rw'
        """

        # /api2/repos/{repo-id}/dir/shared_items/?p={path}
        url = '/api2/repos/' + self.id + '/dir/shared_items/?' + urlencode(dict(p=path))

        if share_type not in ['user', 'group', 'public']:
            raise ValueError('Invalid share type: {}'.format(share_type))
        if share_type == 'personal' and users is None or len(users) == 0:
            raise ValueError('Invalid users supplied for personal share: {}'.format(users))
        if share_type == 'group' and group_id is None:
            raise ValueError('Invalid group_id for group share: {}'.format(group_id))
        if permission not in ['r', 'rw']:
            raise ValueError('Invalid permission: {}'.format(permission))

        if isinstance(users, (list, tuple)):
            users = ','.join(users)

        param =dict(share_type=share_type, username=users, group_id=group_id, permission=permission)
        # query = '?' + urlencode(dict(share_type=share_type, users=users, group_id=group_id, permission=permission))

        if operation == 'share':
            resp = self.client.put(url = url,data = param)
        elif operation == 'unshare':
            query = '&' + urlencode(param)
            resp = self.client.delete(url + query)
        else:
            raise ValueError('Invalid share operation: {}'.format(operation))

        return resp
