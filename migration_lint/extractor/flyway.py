from migration_lint.extractor.raw_sql import RawSqlExtractor


class FlywayExtractor(RawSqlExtractor):
    """Migrations extractor for Flyway migrations."""

    NAME = "flyway"

    def is_migration(self, path: str) -> bool:
        """Check if the specified file is a migration."""

        return "/db/migration/" in path and path.endswith(".sql")

    def is_allowed_with_backward_incompatible_migration(self, path: str) -> bool:
        """Check if the specified file changes are allowed with
        backward-incompatible migrations.
        """

        return self.is_migration(path)
