import mindsdb_sdk
import subprocess
import os
import time

from octo.templates.query_dicts import using_dict, using_dict_all


class Mindsdb_Github:
    """Mindsdb class to interact with Mindsdb SDK"""

    def __init__(self):
        """
        Authenicating Mindsdb SDK with email and password
        """
        self.connection_string = "http://127.0.0.1:47334"

    def start_local(self):
        """
        Connect to local installation of mindsdb
        """
        # Run shell command to start the local mindsdb server
        command = "nohup python -m mindsdb > mindsdb.log 2>&1 &"
        subprocess.run(command, shell=True, check=True)

    def stop_local(self):
        """
        Stop local installation of mindsdb
        """
        # Run shell command to stop the local mindsdb server
        command = 'pkill -f "python"'
        subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL)

    def create_model(self, owner, repo, branch, all_files=False):
        project = self._get_project()

        if not all_files:
            using_dict["owner"] = owner
            using_dict["repo"] = repo
            using_dict["branch"] = branch
            using_dict["openai_api_key"], using_dict["github_token"] = self._get_keys()
            model = project.create_model(
                name=f"{owner}_{repo}".lower(),
                engine="llama_index",
                predict="answer",
                options=using_dict,
            )
        else:
            using_dict_all["owner"] = owner
            using_dict_all["repo"] = repo
            using_dict_all["branch"] = branch
            (
                using_dict_all["openai_api_key"],
                using_dict_all["github_token"],
            ) = self._get_keys()
            model = project.create_model(
                name=f"{owner}_{repo}".lower(),
                engine="llama_index",
                predict="answer",
                options=using_dict_all,
            )
        while True:
            if model.get_status() not in ("generating", "training"):
                break

        if model.get_status() == "error":
            return f"[bold][red]{model.data['error']}", True

        return f"[bold][green]Model created successfully", False

    def predict(self, df, owner, repo):
        project = self._get_project()
        model = project.get_model(f"{owner}_{repo}".lower())
        return model.predict(df)

    def _get_keys(self):
        """
        Get keys before model creation
        """
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        github_token = os.environ.get("GITHUB_TOKEN")

        if not openai_api_key or not github_token:
            raise Exception(
                "Please set OPENAI_API_KEY and GITHUB_TOKEN environment variables"
            )

        return openai_api_key, github_token

    def _get_project(self):
        try:
            server = mindsdb_sdk.connect(self.connection_string)
            project = server.get_project()
        except:
            time.sleep(10)
            server = mindsdb_sdk.connect(self.connection_string)
            project = server.get_project()
        return project


