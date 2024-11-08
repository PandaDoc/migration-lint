import os
from typing import Sequence

from migration_lint import logger
from migration_lint.source_loader.base import BaseSourceLoader
from migration_lint.source_loader.model import SourceDiff


class LocalLoader(BaseSourceLoader):
    """A loader to obtain files changed for local stashed files."""

    NAME = "local_git"

    def get_changed_files(self) -> Sequence[SourceDiff]:
        """Return a list of changed files."""

        from git import Repo

        logger.info("### Getting changed files for local stashed files")

        repo = Repo(os.getcwd())
        diffs = repo.head.commit.diff(None)
        add_or_change_diffs = [d for d in diffs if not d.deleted_file]

        logger.info("Files changed: ")
        logger.info("\n".join([f"- {d.a_path}" for d in add_or_change_diffs]))

        return [
            SourceDiff(old_path=diff.a_path, path=diff.b_path)
            for diff in add_or_change_diffs
        ]
