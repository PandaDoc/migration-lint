import os

from migration_lint import logger
from migration_lint.analyzer import Analyzer, CompatibilityLinter, SquawkLinter
from migration_lint.extractor import Extractor
from migration_lint.source_loader import SourceLoader, LocalLoader
from migration_lint.django.extractor.django_management import DjangoManagementExtractor  # noqa

from django.core.management.base import BaseCommand

from migration_lint.util.env import get_bool_env


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--loader",
            dest="loader_type",
            type=str,
            choices=SourceLoader.names(),
            default=os.getenv("LOADER_TYPE", LocalLoader.NAME),
            help="loader type (where to take source files changes)",
        )
        parser.add_argument(
            "--only-new-files",
            dest="only_new_files",
            action="store_true",
            default=get_bool_env("ONLY_NEW_FILES", True),
            help="lint only new files, ignore changes in existing files",
        )
        parser.add_argument(
            "--gitlab-instance",
            dest="gitlab_instance",
            type=str,
            default=os.getenv("CI_SERVER_URL"),
            help="GitLab instance instance (protocol://host:port)",
        )
        parser.add_argument(
            "--project-id",
            dest="project_id",
            type=str,
            default=os.getenv("CI_PROJECT_ID"),
            help="GitLab project id (repo)",
        )
        parser.add_argument(
            "--gitlab-api-key",
            dest="gitlab_api_key",
            type=str,
            default=os.getenv("CI_DEPLOY_GITLAB_TOKEN"),
            help="api key for GitLab API",
        )
        parser.add_argument(
            "--branch",
            dest="branch",
            type=str,
            default=os.getenv(
                "CI_MERGE_REQUEST_SOURCE_BRANCH_NAME", os.getenv("CI_COMMIT_BRANCH")
            ),
            help="branch to compare",
        )
        parser.add_argument(
            "--mr-id",
            dest="mr_id",
            type=str,
            default=os.getenv("CI_MERGE_REQUEST_ID"),
            help="integer merge request id",
        )
        parser.add_argument(
            "--squawk-config-path",
            dest="squawk_config_path",
            type=str,
            default=os.getenv("MIGRATION_LINTER_SQUAWK_CONFIG_PATH"),
            help="squawk config path",
        )

    def handle(self, loader_type, squawk_config_path, **options):
        logger.info("Start analysis..")

        loader = SourceLoader.get(loader_type)(**options)
        extractor = Extractor.get("django_management")(**options)
        analyzer = Analyzer(
            loader=loader,
            extractor=extractor,
            linters=[CompatibilityLinter(), SquawkLinter(squawk_config_path)],
        )
        analyzer.analyze()
