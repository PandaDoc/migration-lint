from __future__ import annotations

from typing import List
from unittest import mock

import pytest

from migration_lint.analyzer import Analyzer, CompatibilityLinter
from migration_lint.extractor.model import (
    ExtendedSourceDiff,
    Migration,
    MigrationsMetadata,
)
from migration_lint.sql.constants import StatementType

FAKE_STATEMENT = "fake sql"


def get_analyzer(
    changed_files: List[ExtendedSourceDiff],
    migrations: List[Migration],
):
    analyzer = Analyzer(
        loader=mock.MagicMock(),
        extractor=mock.MagicMock(),
        linters=[CompatibilityLinter()],
    )
    analyzer.extractor.create_metadata.return_value = MigrationsMetadata(
        migrations=migrations,
        changed_files=changed_files,
    )
    return analyzer


def test_analyze_no_errors():
    analyzer = get_analyzer(
        changed_files=[ExtendedSourceDiff("one")],
        migrations=[Migration("one", "")],
    )
    with mock.patch(
        "migration_lint.analyzer.compat.classify_migration"
    ) as classify_mock, mock.patch(
        "migration_lint.analyzer.base.logger.info"
    ) as logger_mock:
        classify_mock.return_value = [
            (FAKE_STATEMENT, StatementType.BACKWARD_COMPATIBLE)
        ]
        analyzer.analyze()

        logger_mock.assert_called_with("\x1b[1;32mEverything seems good!\x1b[0m")


def test_analyze_ignore_migration():
    analyzer = get_analyzer(
        changed_files=[ExtendedSourceDiff("one")],
        migrations=[
            Migration(
                "one",
                "CREATE INDEX idx ON table_name (column_name); -- migration-lint: ignore",
            ),
        ],
    )
    with mock.patch("migration_lint.analyzer.base.logger.info") as logger_mock:
        analyzer.analyze()

        logger_mock.assert_any_call("\x1b[33;21mMigration is ignored.\x1b[0m")


def test_analyze_no_migrations():
    analyzer = get_analyzer(
        changed_files=[ExtendedSourceDiff("one")],
        migrations=[],
    )
    with mock.patch(
        "migration_lint.analyzer.compat.classify_migration"
    ) as classify_mock, mock.patch(
        "migration_lint.analyzer.base.logger.info"
    ) as logger_mock:
        classify_mock.return_value = []
        analyzer.analyze()

        logger_mock.assert_called_with("Looks like you don't have any migration in MR.")


def test_analyze_unsupported():
    analyzer = get_analyzer(
        changed_files=[ExtendedSourceDiff("one")],
        migrations=[Migration("one", "")],
    )
    with mock.patch(
        "migration_lint.analyzer.compat.classify_migration"
    ) as classify_mock, mock.patch(
        "migration_lint.analyzer.base.logger.error"
    ) as logger_mock:
        classify_mock.return_value = [(FAKE_STATEMENT, StatementType.UNSUPPORTED)]
        with pytest.raises(SystemExit):
            analyzer.analyze()

        logger_mock.assert_called_with(
            f"- Statement can't be identified: {FAKE_STATEMENT}"
        )


def test_analyze_restricted():
    analyzer = get_analyzer(
        changed_files=[ExtendedSourceDiff("one")],
        migrations=[Migration("one", "")],
    )
    with mock.patch(
        "migration_lint.analyzer.compat.classify_migration"
    ) as classify_mock, mock.patch(
        "migration_lint.analyzer.base.logger.error"
    ) as logger_mock:
        classify_mock.return_value = [(FAKE_STATEMENT, StatementType.RESTRICTED)]
        with pytest.raises(SystemExit):
            analyzer.analyze()

        logger_mock.assert_has_calls(
            [
                mock.call(
                    "- There are restricted statements in migration\n\t"
                    "Check squawk output below for details\n\t"
                    "Also check the doc to fix it: https://coda.io/d/"
                    "Application-Platform_dRYCqoVEASR/DB-migrations-classification_suAoY#_luZp5\n"
                )
            ]
        )


def test_analyze_incompatible():
    analyzer = get_analyzer(
        changed_files=[
            ExtendedSourceDiff("one", "one", ""),
            ExtendedSourceDiff("two", "two", ""),
        ],
        migrations=[Migration("", "")],
    )
    with mock.patch(
        "migration_lint.analyzer.compat.classify_migration"
    ) as classify_mock, mock.patch(
        "migration_lint.analyzer.base.logger.error"
    ) as logger_mock:
        classify_mock.return_value = [
            (FAKE_STATEMENT, StatementType.BACKWARD_INCOMPATIBLE)
        ]
        with pytest.raises(SystemExit):
            analyzer.analyze()

        logger_mock.assert_has_calls(
            [
                mock.call(
                    (
                        "- You have backward incompatible operations, "
                        "which is not allowed with changes in following files:"
                        "\n\t- one\n\t- two"
                        "\n\n\tPlease, separate changes in different merge requests.\n"
                    )
                )
            ]
        )


def test_analyze_incompatible_with_allowed_files():
    analyzer = get_analyzer(
        changed_files=[
            ExtendedSourceDiff(
                "one", "one", "", allowed_with_backward_incompatible=True
            ),
        ],
        migrations=[Migration("one", "")],
    )
    with mock.patch(
        "migration_lint.analyzer.compat.classify_migration"
    ) as classify_mock, mock.patch(
        "migration_lint.analyzer.base.logger.info"
    ) as logger_mock:
        classify_mock.return_value = [
            (FAKE_STATEMENT, StatementType.BACKWARD_INCOMPATIBLE)
        ]
        analyzer.analyze()

        logger_mock.assert_called_with("\x1b[1;32mEverything seems good!\x1b[0m")


def test_analyze_data_migration():
    analyzer = get_analyzer(
        changed_files=[
            ExtendedSourceDiff(
                "one", "one", "", allowed_with_backward_incompatible=True
            ),
            ExtendedSourceDiff(
                "two", "two", "", allowed_with_backward_incompatible=True
            ),
        ],
        migrations=[Migration("one", "")],
    )
    with mock.patch(
        "migration_lint.analyzer.compat.classify_migration"
    ) as classify_mock, mock.patch(
        "migration_lint.analyzer.base.logger.error"
    ) as logger_mock:
        classify_mock.return_value = [
            (FAKE_STATEMENT, StatementType.DATA_MIGRATION),
            (FAKE_STATEMENT, StatementType.BACKWARD_INCOMPATIBLE),
        ]
        with pytest.raises(SystemExit):
            analyzer.analyze()

        logger_mock.assert_has_calls(
            [
                mock.call(
                    (
                        f"- Seems like you have data migration along with schema migration: {FAKE_STATEMENT}"
                        "\n\n\tPlease, separate changes in different merge requests.\n"
                    )
                )
            ]
        )
