import json
from unittest import mock

import pytest

from migration_lint.source_loader.gitlab import GitlabBranchLoader, GitlabMRLoader


def test_gitlab_branch_loader():
    loader = GitlabBranchLoader(
        branch="branch_name",
        project_id="000",
        gitlab_api_key="key",
        gitlab_instance="https://gitlab.example.com",
        only_new_files=True,
    )

    with mock.patch("migration_lint.source_loader.gitlab.urlopen") as urlopen_mock:
        urlopen_mock().__enter__().read.return_value = json.dumps(
            {
                "diffs": [
                    {
                        "new_path": "a.py",
                        "old_path": None,
                        "diff": "",
                        "deleted_file": False,
                        "new_file": True,
                    },
                    {
                        "new_path": None,
                        "old_path": "c.py",
                        "diff": "",
                        "deleted_file": True,
                        "new_file": False,
                    },
                    {
                        "new_path": "d.py",
                        "old_path": "d.py",
                        "diff": "",
                        "deleted_file": False,
                        "new_file": False,
                    },
                ]
            }
        ).encode("utf-8")

        changed_files = loader.get_changed_files()

        assert len(changed_files) == 1
        assert changed_files[0].path == "a.py"
        assert (
            urlopen_mock.call_args_list[1].args[0].full_url
            == "https://gitlab.example.com/api/v4/projects/000/repository/compare?from=master&to=branch_name"
        )


def test_gitlab_branch_loader_on_changed_files():
    loader = GitlabBranchLoader(
        branch="branch_name",
        project_id="000",
        gitlab_api_key="key",
        gitlab_instance="https://gitlab.example.com",
        only_new_files=False,
    )

    with mock.patch("migration_lint.source_loader.gitlab.urlopen") as urlopen_mock:
        urlopen_mock().__enter__().read.return_value = json.dumps(
            {
                "diffs": [
                    {
                        "new_path": "a.py",
                        "old_path": None,
                        "diff": "",
                        "deleted_file": False,
                        "new_file": True,
                    },
                    {
                        "new_path": None,
                        "old_path": "c.py",
                        "diff": "",
                        "deleted_file": True,
                        "new_file": False,
                    },
                    {
                        "new_path": "d.py",
                        "old_path": "d.py",
                        "diff": "",
                        "deleted_file": False,
                        "new_file": False,
                    },
                ]
            }
        ).encode("utf-8")

        changed_files = loader.get_changed_files()

        assert len(changed_files) == 2
        assert changed_files[0].path == "a.py"
        assert (
            urlopen_mock.call_args_list[1].args[0].full_url
            == "https://gitlab.example.com/api/v4/projects/000/repository/compare?from=master&to=branch_name"
        )
        assert changed_files[1].path == "d.py"


def test_gitlab_branch_loader_not_configured():
    with pytest.raises(RuntimeError):
        GitlabBranchLoader(
            branch=None,
            project_id=None,
            gitlab_api_key=None,
            gitlab_instance=None,
            only_new_files=True,
        )


def test_gitlab_mr_loader():
    loader = GitlabMRLoader(
        mr_id="100",
        project_id="000",
        gitlab_api_key="key",
        gitlab_instance="https://gitlab.example.com",
        only_new_files=True,
    )

    with mock.patch("migration_lint.source_loader.gitlab.urlopen") as urlopen_mock:
        urlopen_mock().__enter__().read.side_effect = [
            json.dumps({"web_url": "fake mr url"}).encode("utf-8"),
            json.dumps(
                [
                    {
                        "new_path": "a.py",
                        "old_path": None,
                        "diff": "",
                        "deleted_file": False,
                        "new_file": True,
                    },
                    {
                        "new_path": None,
                        "old_path": "c.py",
                        "diff": "",
                        "deleted_file": True,
                        "new_file": False,
                    },
                    {
                        "new_path": "d.py",
                        "old_path": "d.py",
                        "diff": "",
                        "deleted_file": False,
                        "new_file": False,
                    },
                ]
            ).encode("utf-8"),
        ]

        changed_files = loader.get_changed_files()

        assert len(changed_files) == 1
        assert changed_files[0].path == "a.py"
        assert (
            urlopen_mock.call_args_list[1].args[0].full_url
            == "https://gitlab.example.com/api/v4/projects/000/merge_requests/100"
        )
        assert (
            urlopen_mock.call_args_list[2].args[0].full_url
            == "https://gitlab.example.com/api/v4/projects/000/merge_requests/100/diffs"
        )


def test_gitlab_mr_loader_on_changed_files():
    loader = GitlabMRLoader(
        mr_id="100",
        project_id="000",
        gitlab_api_key="key",
        gitlab_instance="https://gitlab.example.com",
        only_new_files=False,
    )

    with mock.patch("migration_lint.source_loader.gitlab.urlopen") as urlopen_mock:
        urlopen_mock().__enter__().read.side_effect = [
            json.dumps({"web_url": "fake mr url"}).encode("utf-8"),
            json.dumps(
                [
                    {
                        "new_path": "a.py",
                        "old_path": None,
                        "diff": "",
                        "deleted_file": False,
                        "new_file": True,
                    },
                    {
                        "new_path": None,
                        "old_path": "c.py",
                        "diff": "",
                        "deleted_file": True,
                        "new_file": False,
                    },
                    {
                        "new_path": "d.py",
                        "old_path": "d.py",
                        "diff": "",
                        "deleted_file": False,
                        "new_file": False,
                    },
                ]
            ).encode("utf-8"),
        ]

        changed_files = loader.get_changed_files()

        assert len(changed_files) == 2
        assert changed_files[0].path == "a.py"
        assert (
            urlopen_mock.call_args_list[1].args[0].full_url
            == "https://gitlab.example.com/api/v4/projects/000/merge_requests/100"
        )
        assert (
            urlopen_mock.call_args_list[2].args[0].full_url
            == "https://gitlab.example.com/api/v4/projects/000/merge_requests/100/diffs"
        )

        assert changed_files[1].path == "d.py"


def test_gitlab_mr_loader_not_configured():
    with pytest.raises(RuntimeError):
        GitlabMRLoader(
            mr_id=None,
            project_id=None,
            gitlab_api_key=None,
            gitlab_instance=None,
            only_new_files=True,
        )
