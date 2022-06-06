"""Repos class"""
from seafileapi.repo import Repo
from seafileapi.utils import raise_does_not_exist
from urllib.parse import urlencode
from typing import Optional


class Repos(object):
    def __init__(self, client: "SeafileApiClient"):
        self.client = client

    def create_repo(self, name, password=None):
        data = {"name": name}
        if password:
            data["passwd"] = password
        response = self.client.post("/api2/repos/", data=data).json()
        try:
            data = response.json()
            if "repo_id" in data:
                return self.get_repo(data["repo_id"])
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
