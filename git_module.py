import os
from git import Repo
from dotenv import load_dotenv


class GitModule:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.branch = "main"

    def clone_from_trickest(self):
        try:
            Repo.clone_from(
                os.getenv("TRICKEST_REPO_URL"),
                self.repo_path,
                branch=self.branch,
            )
        except Exception as e:
            print(e)

    def clone_from_json(self):
        try:
            Repo.clone_from(
                os.getenv("JSON_REPO_URL"),
                self.repo_path,
                branch=self.branch,
            )
        except Exception as e:
            print(e)

    def pull(self):
        repo = Repo(self.repo_path)
        repo.git.pull()

    def add(self):
        repo = Repo(self.repo_path)
        repo.git.add("--all")  # add all files

    def commit(self, message):
        repo = Repo(self.repo_path)
        if changes := repo.git.diff("--cached", name_only=True):
            repo.git.commit("-m", message)
        else:
            print("No changes to commit")

    def push(self):
        repo = Repo(self.repo_path)
        repo.git.push()
