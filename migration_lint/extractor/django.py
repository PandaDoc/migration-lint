import re
import subprocess

from migration_lint import logger
from migration_lint.extractor.base import BaseExtractor


class DjangoExtractor(BaseExtractor):
    """Migrations extractor for Django migrations."""

    NAME = "django"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.command = "python manage.py sqlmigrate {app} {migration_name}"
        self.command = "make sqlmigrate app={app} migration={migration_name}"
        self.skip_lines = 2

    def is_migration(self, path: str) -> bool:
        """Check if the specified file is a migration."""

        return (
            "/migrations/" in path
            and path.endswith(".py")
            and "__init__.py" not in path
        )

    def is_allowed_with_backward_incompatible_migration(self, path: str) -> bool:
        """Check if the specified file changes are allowed with
        backward-incompatible migrations.
        """

        allowed_patterns = [
            r".*/models\.py",
            r".*/constants\.py",
            r".*/enums\.py",
            r".*/migrations/.*\.py",
            r"^(?!.*\.py).*$",
        ]
        for pattern in allowed_patterns:
            if re.match(pattern, path):
                return True

        return False

    def extract_sql(self, migration_path: str) -> str:
        """Extract raw SQL from the migration file."""

        parts = migration_path.split("/")
        file_name = parts[-1]
        app = parts[-3]
        migration_name = file_name.replace(".py", "")

        logger.info(
            f"Extracting sql for migration: app={app}, migration_name={migration_name}"
        )

        try:
            output = subprocess.check_output(
                self.command.format(app=app, migration_name=migration_name).split(" ")
            ).decode("utf-8")
        except subprocess.CalledProcessError:
            logger.error(
                f"Failed to extract SQL for migration app={app}, migration_name={migration_name}"
            )
            if self.ignore_extractor_fail:
                return ""
            raise
        return "\n".join(output.split("\n")[self.skip_lines :])
