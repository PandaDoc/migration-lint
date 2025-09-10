from __future__ import annotations

from typing import List

from migration_lint import logger
from migration_lint.analyzer.base import BaseLinter
from migration_lint.extractor.model import ExtendedSourceDiff
from migration_lint.sql.parser import classify_migration
from migration_lint.util.colors import blue, yellow


class PrimaryKeyLinter(BaseLinter):
    """
    Linter that checks if newly created tables have primary keys.

    This linter operates in dry-run mode by default, meaning it only logs
    warnings but doesn't cause the overall linting process to fail.
    """

    def __init__(self, dry_run: bool = True):
        """
        Initialize the PrimaryKeyLinter.

        Args:
            dry_run: If True, only log warnings without failing the linter.
                    If False, treat missing primary keys as errors.
        """
        self.dry_run = dry_run

    def lint(
        self,
        migration_sql: str,
        changed_files: List[ExtendedSourceDiff],
    ) -> List[str]:
        """Perform primary key validation on CREATE TABLE statements."""

        errors = []

        try:
            classification_result = classify_migration(migration_sql)

            create_table_statements = [
                (statement_sql, statement_type)
                for statement_sql, statement_type in classification_result
                if self._is_create_table_statement(statement_sql)
            ]

            tables_without_pk = []
            for statement_sql, _ in create_table_statements:
                table_name = self._extract_table_name_from_sql(statement_sql)
                if not self._sql_has_primary_key(statement_sql):
                    tables_without_pk.append({
                        'table_name': table_name or 'unknown',
                        'sql': statement_sql
                    })

            if tables_without_pk:
                if self.dry_run:
                    logger.info(yellow("\n🔍 Primary Key Check (dry-run mode):"))
                    for table_info in tables_without_pk:
                        logger.info(
                            yellow(
                                f"  ⚠️  Table '{table_info['table_name']}' "
                                f"created without a primary key:"
                            )
                        )
                        logger.info(blue(f"     {table_info['sql']}"))
                    logger.info(
                        yellow(
                            "  💡 Consider adding a primary key for better "
                            "performance and data integrity."
                        )
                    )
                else:
                    for table_info in tables_without_pk:
                        errors.append(
                            f"- Table '{table_info['table_name']}' is created "
                            f"without a primary key: {table_info['sql']}\n"
                            f"  Consider adding a primary key for better "
                            f"performance and data integrity."
                        )
            else:
                logger.info(
                    blue("✅ Primary Key Check: All created tables have primary keys.")
                )

        except Exception as e:
            logger.info(
                yellow(f"Primary Key Check: Could not analyze SQL - {str(e)}")
            )

        return errors

    def _is_create_table_statement(self, statement_sql: str) -> bool:
        """Check if a SQL statement is a CREATE TABLE statement."""
        normalized_sql = statement_sql.strip().upper()
        return normalized_sql.startswith("CREATE TABLE")

    def _extract_table_name_from_sql(self, statement_sql: str) -> str:
        """Extract table name from CREATE TABLE SQL statement."""
        try:
            import re

            # Match CREATE TABLE [IF NOT EXISTS] table_name
            match = re.search(
                r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([^\s\(]+)',
                statement_sql,
                re.IGNORECASE
            )
            if match:
                return match.group(1).strip('"`')
            return "unknown"
        except Exception:
            return "unknown"

    def _sql_has_primary_key(self, statement_sql: str) -> bool:
        """Check if CREATE TABLE SQL statement includes a primary key."""
        normalized_sql = statement_sql.upper()

        return "PRIMARY KEY" in normalized_sql
