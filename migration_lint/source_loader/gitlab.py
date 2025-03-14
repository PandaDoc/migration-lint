import json
import os
from typing import Any, Sequence
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from migration_lint import logger
from migration_lint.source_loader.base import BaseSourceLoader
from migration_lint.source_loader.model import SourceDiff


class GitlabBranchLoader(BaseSourceLoader):
    """A loader to obtain files changed in the given branch comparing to
    master.
    """

    NAME = "gitlab_branch"

    def __init__(
        self,
        branch: str,
        project_id: str,
        gitlab_api_key: str,
        gitlab_instance: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.base_url = gitlab_instance
        self.branch = branch
        self.project_id = project_id
        self.gitlab_api_key = gitlab_api_key
        self.default_branch = os.environ.get("CI_DEFAULT_BRANCH", "master")

        if not self.branch or not self.project_id or not self.gitlab_api_key:
            raise RuntimeError(
                f"You must specify branch, project_id and gitlab_api_key "
                f"to use GitlabBranchLoader (branch={self.branch}, project_id={self.project_id}, "
                f"gitlab_api_key={self.gitlab_api_key})"
            )

    def get_changed_files(self) -> Sequence[SourceDiff]:
        """Return a list of changed files."""

        logger.info(
            f"### Getting changed files from {self.default_branch} <-> {self.branch}"
        )

        endpoint = f"projects/{self.project_id}/repository/compare?"
        query_params = f"from={self.default_branch}&to={self.branch}"
        url = urljoin(f"{self.base_url}/api/v4/", endpoint + query_params)
        req = Request(url, headers={"PRIVATE-TOKEN": self.gitlab_api_key})
        with urlopen(req) as resp:
            diffs = json.loads(resp.read().decode("utf-8"))["diffs"]

        return [
            SourceDiff(
                diff=diff["diff"],
                path=diff["new_path"],
                old_path=diff["old_path"],
            )
            for diff in diffs
            if not diff["deleted_file"]
            and (not self.only_new_files or self.only_new_files and diff["new_file"])
        ]


class GitlabMRLoader(BaseSourceLoader):
    """A loader to obtain files changed in the given MR."""

    NAME = "gitlab_mr"

    def __init__(
        self,
        mr_id: str,
        project_id: str,
        gitlab_api_key: str,
        gitlab_instance: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.base_url = gitlab_instance
        self.mr_id = mr_id
        self.project_id = project_id
        self.gitlab_api_key = gitlab_api_key

        if not self.mr_id or not self.project_id or not self.gitlab_api_key:
            raise RuntimeError(
                f"You must specify mr_id, project_id and gitlab_api_key "
                f"to use GitlabMRLoader (mr_id={self.mr_id}, project_id={self.project_id}, "
                f"gitlab_api_key={self.gitlab_api_key})"
            )

    def get_changed_files(self) -> Sequence[SourceDiff]:
        """Return a list of changed files."""

        logger.info(f"### Getting changed files from MR: {self.mr_id}")

        endpoint = f"projects/{self.project_id}/merge_requests/{self.mr_id}"
        url = urljoin(f"{self.base_url}/api/v4/", endpoint)
        req = Request(url, headers={"PRIVATE-TOKEN": self.gitlab_api_key})
        with urlopen(req) as resp:
            mr_info = json.loads(resp.read().decode("utf-8"))

        logger.info(f"MR link: {mr_info['web_url']}")

        endpoint = f"projects/{self.project_id}/merge_requests/{self.mr_id}/diffs"
        url = urljoin(f"{self.base_url}/api/v4/", endpoint)
        req = Request(url, headers={"PRIVATE-TOKEN": self.gitlab_api_key})
        with urlopen(req) as resp:
            diffs = json.loads(resp.read().decode("utf-8"))

        return [
            SourceDiff(
                diff=diff["diff"],
                path=diff["new_path"],
                old_path=diff["old_path"],
            )
            for diff in diffs
            if not diff["deleted_file"]
            and (not self.only_new_files or self.only_new_files and diff["new_file"])
        ]
