from __future__ import annotations

import abc
from typing import Sequence, List

from migration_lint import logger
from migration_lint.extractor.base import BaseExtractor
from migration_lint.extractor.model import ExtendedSourceDiff
from migration_lint.source_loader.base import BaseSourceLoader
from migration_lint.util.colors import green, red, yellow


# A migration ignore mark.
MANUALLY_IGNORE_ANNOTATION = "-- migration-lint: ignore"

CLASSIFICATION_LINK = "https://pandadoc.github.io/migration-lint/classification/"
IGNORE_LINK = "https://pandadoc.github.io/migration-lint/rules/#ignoring-statements"


class BaseLinter:
    """Base class for migration linters."""

    @abc.abstractmethod
    def lint(
        self,
        migration_sql: str,
        changed_files: List[ExtendedSourceDiff],
    ) -> List[str]:
        """Perform SQL migartion linting."""

        raise NotImplementedError()


class Analyzer:
    """Migrations analyzer."""

    def __init__(
        self,
        loader: BaseSourceLoader,
        extractor: BaseExtractor,
        linters: Sequence[BaseLinter],
    ) -> None:
        self.loader = loader
        self.extractor = extractor
        self.linters = linters

    def analyze(self) -> None:
        """Analyze migrations in files changed according to analyzer's source
        loader.
        """

        changed_files = self.loader.get_changed_files()
        metadata = self.extractor.create_metadata(changed_files)

        if not metadata.migrations:
            logger.info("Looks like you don't have any migration in MR.")
            return

        logger.info("")

        errors = []
        for migration in metadata.migrations:
            logger.info(green(f"Analyzing migration: {migration.path}\n"))

            if MANUALLY_IGNORE_ANNOTATION in migration.raw_sql:
                logger.info(yellow("Migration is ignored."))
                continue

            for linter in self.linters:
                errors.extend(
                    linter.lint(migration.raw_sql, metadata.changed_files),
                )

        logger.info("")

        if errors:
            logger.info(red("Errors found in migrations:\n"))
            for error in errors:
                logger.error(error)
            logger.info("")
            logger.info(
                f"See classification of statements if you need to fix: {CLASSIFICATION_LINK}"
            )
            logger.info(
                f"See how to ignore the linter for one migration: {IGNORE_LINK}"
            )
            exit(1)
        else:
            logger.info(green("Everything seems good!"))
