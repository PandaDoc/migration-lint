from migration_lint.extractor.base import BaseExtractor


class RawSqlExtractor(BaseExtractor):
    """Migrations extractor for SQL files migrations."""

    NAME = "raw_sql"

    def is_migration(self, path: str) -> bool:
        """Check if the specified file is a migration."""

        return path.endswith(".sql")

    def is_allowed_with_backward_incompatible_migration(self, path: str) -> bool:
        """Check if the specified file changes are allowed with
        backward-incompatible migrations.
        """

        return self.is_migration(path)

    def extract_sql(self, migration_path: str) -> str:
        """Extract raw SQL from the migration file."""

        try:
            with open(migration_path, "r") as f:
                return f.read()
        except:
            if self.ignore_extractor_fail:
                return ""
            raise
