"""Repos class"""
from seafileapi_extended import SeafDir
from seafileapi_extended.repo import Repo
from seafileapi_extended.utils import raise_does_not_exist
from urllib.parse import urlencode


class Repos(object):
    def __init__(self, client):
        self.client = client

    def create_repo(self, name, desc, password=None):
        data = {"name": name}
        if password:
            data["passwd"] = password
        response = self.client.post("/api2/repos/", data=data).json()
        try:
            data = response.json()
            if "repo_id" in data:
                return self.get_repo(data["repo_id"])
            return response
        except Exception as error:
            print(error, flush=True)

    @raise_does_not_exist("The requested library does not exist")
    def get_repo(self, repo_id):
        """Get the repo which has the id `repo_id`.

        Raises :exc:`DoesNotExist` if no such repo exists.
        """

        try:
            response = self.client.get(f"/api2/repos/{repo_id}").json()
            repo_json = response.json()
            return Repo.from_json(self.client, repo_json)
        except Exception as error:
            print(error, flush=True)

    def list_repos(self, type=None):
        query = ""
        if type:
            query = "?" + urlencode(dict(type=type))

        try:
            response = self.client.get(f"/api2/repos/{query}")
            repos_json = response.json()
            return [Repo.from_json(self.client, j) for j in repos_json]
        except Exception as e:
            print(e, flush=True)

    @raise_does_not_exist("The requested library does not exist")
    def get_repo_by_name(self, name):
        """
        Get the repo which the name
        :param name:    [string]
        :return:    [Repo|None]
        """

        # important: Only return one repo for  multiple repos with the same.
        repos_list = self.list_repos()
        for repo in repos_list:
            repo_name = repo.get_name()  # .decode()
            if repo_name == name:
                return repo

        return None

    def list_shared_folders(self, shared_email=None):
        """
        List Shared Folders
        :param  shared_email [string|None]
            According to the email to filter on the Shared folder. if None then no filter.
        :return:    [list(SeafDir)]
        """

        repos_json = self.client.get("/api/v2.1/shared-folders/").json()
        shared_folders = []

        for t_folder in repos_json:

            seaf_dir_obj = SeafDir.create_from_shared_folder(t_folder, self.client)

            t_user_email = t_folder.get("user_email", None)

            if shared_email:
                if t_user_email == shared_email:
                    shared_folders.append(seaf_dir_obj)
            else:
                shared_folders.append(seaf_dir_obj)

        return shared_folders
