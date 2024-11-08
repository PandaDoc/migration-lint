from __future__ import annotations

from io import StringIO
from typing import List

from migration_lint import logger
from migration_lint.analyzer.base import BaseLinter
from migration_lint.extractor.model import ExtendedSourceDiff
from migration_lint.sql.constants import StatementType
from migration_lint.sql.parser import classify_migration
from migration_lint.util.colors import blue


DOCS_URL = "https://pandadoc.github.io/migration-lint/classification/"


class CompatibilityLinter(BaseLinter):
    f"""
    Custom linter that checks backward compatibility
    based on migrations classification.

    See {DOCS_URL} for details.
    """

    def lint(
        self,
        migration_sql: str,
        changed_files: List[ExtendedSourceDiff],
        report_restricted: bool = False,
    ) -> List[str]:
        """Perform SQL migration linting."""

        errors = []

        classification_result = classify_migration(migration_sql)

        statement_types = set()
        logger.info(blue("Migration contains statements:\n"))
        for statement_sql, statement_type in classification_result:
            statement_types.add(statement_type)
            logger.info(f"- {statement_type.colorized}: {statement_sql}")

            if statement_type == StatementType.UNSUPPORTED:
                errors.append(f"- Statement can't be identified: {statement_sql}")

            if statement_type == StatementType.RESTRICTED and report_restricted:
                errors.append(
                    (
                        f"- Statement is restricted to use: {statement_sql}."
                        f"\n\tCheck the doc to do this correctly: {DOCS_URL}.\n"
                    )
                )

        if StatementType.RESTRICTED in statement_types and not report_restricted:
            errors.append(
                (
                    "- There are restricted statements in migration"
                    "\n\tCheck squawk output below for details"
                    f"\n\tAlso check the doc to fix it: {DOCS_URL}\n"
                )
            )

        if StatementType.BACKWARD_INCOMPATIBLE in statement_types:
            not_allowed_files = [
                file.path
                for file in changed_files
                if not file.allowed_with_backward_incompatible
            ]
            if not_allowed_files:
                error = StringIO()
                error.write(
                    (
                        "- You have backward incompatible operations, "
                        "which is not allowed with changes in following files:"
                    )
                )
                for file_name in not_allowed_files:
                    error.write(f"\n\t- {file_name}")
                error.write(
                    "\n\n\tPlease, separate changes in different merge requests.\n"
                )

                errors.append(error.getvalue())

        if StatementType.DATA_MIGRATION in statement_types and (
            StatementType.BACKWARD_COMPATIBLE in statement_types
            or StatementType.BACKWARD_INCOMPATIBLE in statement_types
        ):
            statement_sql = [
                r[0]
                for r in classification_result
                if r[1] == StatementType.DATA_MIGRATION
            ][0]
            errors.append(
                (
                    f"- Seems like you have data migration along with schema migration: {statement_sql}"
                    "\n\n\tPlease, separate changes in different merge requests.\n"
                )
            )

        return errors
