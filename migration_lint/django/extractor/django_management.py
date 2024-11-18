import os.path

from migration_lint import logger
from migration_lint.extractor.django import DjangoExtractor

import django.apps
from django.core.management import call_command, CommandError


class DjangoManagementExtractor(DjangoExtractor):
    """Migrations extractor for Django migrations for management command."""

    NAME = "django_management"

    def extract_sql(self, migration_path: str) -> str:
        """Extract raw SQL from the migration file."""

        parts = migration_path.split("/")
        file_name = parts[-1]
        app = parts[-3]
        migration_name = file_name.replace(".py", "")

        # handle subapp app name
        for app_config in django.apps.apps.get_app_configs():
            app_path = os.path.relpath(app_config.path, ".")
            app_migrations_path = os.path.join(app_path, "migrations")
            if migration_path.startswith(app_migrations_path):
                app = app_config.label
                break

        logger.info(
            f"Extracting sql for migration: app={app}, migration_name={migration_name}"
        )

        try:
            return call_command("sqlmigrate", app, migration_name)
        except CommandError:
            logger.error(
                f"Failed to extract SQL for migration app={app}, migration_name={migration_name}"
            )
            return ""
