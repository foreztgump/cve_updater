import git


class GitModule:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.branch = "main"

    def clone_from_trickest(self):
        try:
            trickest_repo = git.Repo.clone_from(
                "https://github.com/trickest/cve.git",
                self.repo_path,
                branch=self.branch,
            )
            return trickest_repo
        except Exception as e:
            print(e)

    def clone_from_json(self):
        try:
            json_repo = git.Repo.clone_from(
                "https://github.com/foreztgump/cve_json.git",
                self.repo_path,
                branch=self.branch,
            )
        except:
            print("Repo already exists")

    def pull(self):
        repo = git.Repo(self.repo_path)
        repo.git.pull()

    def add(self):
        repo = git.Repo(self.repo_path)
        repo.git.add(".")  # add all files

    def commit(self, message):
        repo = git.Repo(self.repo_path)
        repo.git.commit("-m", message)
