import re
import subprocess
from io import StringIO
from functools import lru_cache

from migration_lint import logger
from migration_lint.extractor.base import BaseExtractor


class AlembicExtractor(BaseExtractor):
    """Migrations extractor for Alembic migrations."""

    NAME = "alembic"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command = "make sqlmigrate"

    def is_migration(self, path: str) -> bool:
        """Check if the specified file is a migration."""

        return (
            "/migrations/versions/" in path
            and path.endswith(".py")
            and "__init__.py" not in path
        )

    def is_allowed_with_backward_incompatible_migration(self, path: str) -> bool:
        """Check if the specified file changes are allowed with
        backward-incompatible migrations.
        """

        allowed_patterns = [
            r".*/tables\.py",
            r".*/constants\.py",
            r".*/enums\.py",
            r".*/migrations/versions/.*\.py",
            r"^(?!.*\.py).*$",
        ]
        for pattern in allowed_patterns:
            if re.match(pattern, path):
                return True

        return False

    def extract_sql(self, migration_path: str) -> str:
        """Extract raw SQL from the migration file."""

        file_name = migration_path.split("/")[-1]
        parts = file_name.split("_")
        version = parts[1]

        logger.info(f"Extracting sql for migration: version={version}")

        migrations_sql = self._get_migrations_sql()

        try:
            return migrations_sql[version]
        except KeyError:
            logger.error(
                f"Couldn't find info about migration with version={version} "
                f"in alembic offline mode output"
            )
            return ""

    @lru_cache(maxsize=1)
    def _get_migrations_sql(self):
        """Get raw SQL for all migrations."""

        try:
            lines = (
                subprocess.check_output(self.command.split(" "))
                .decode("utf-8")
                .split("\n")
            )
        except subprocess.CalledProcessError:
            logger.error("Failed to extract SQL for migrations")
            return {}

        migrations_sql = {}

        current_migration = None
        current_migration_sql = StringIO()

        for line in lines:
            m = re.match(r"-- Running upgrade \w* -> (\w*)", line)
            if m is not None:
                if current_migration is not None:
                    migrations_sql[current_migration] = (
                        current_migration_sql.getvalue().strip("\n")
                    )

                current_migration = m.group(1)
                current_migration_sql = StringIO()

            elif "alembic_version" in line:
                continue

            else:
                current_migration_sql.write(f"{line}\n")

        else:
            if current_migration is not None:
                migrations_sql[current_migration] = (
                    current_migration_sql.getvalue().strip("\n")
                )

        return migrations_sql