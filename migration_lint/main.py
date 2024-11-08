import os

import click

from migration_lint import logger
from migration_lint.analyzer import Analyzer, CompatibilityLinter, SquawkLinter
from migration_lint.extractor import Extractor, DjangoExtractor
from migration_lint.source_loader import SourceLoader, LocalLoader


@click.command()
# Base setup
@click.option(
    "--loader",
    "loader_type",
    help="loader type (where to take source files changes)",
    type=click.Choice(SourceLoader.names(), case_sensitive=False),
    default=os.getenv("LOADER_TYPE", LocalLoader.NAME),
)
@click.option(
    "--extractor",
    "extractor_type",
    help="extractor type (how to extract SQL from migrations)",
    type=click.Choice(Extractor.names(), case_sensitive=False),
    default=os.getenv("EXTRACTOR", DjangoExtractor.NAME),
)
# gitlab-specific arguments
@click.option(
    "--project-id",
    help="GitLab project id (repo)",
    default=os.getenv("CI_PROJECT_ID"),
)
@click.option(
    "--gitlab-instance",
    help="GitLab instance instance (protocol://host:port)",
    default=os.getenv("CI_SERVER_FQDN"),
)
@click.option(
    "--gitlab-api-key",
    help="api key for GitLab API",
    default=os.getenv("CI_DEPLOY_GITLAB_TOKEN"),
)
@click.option(
    "--branch",
    help="branch to compare",
    default=os.getenv(
        "CI_MERGE_REQUEST_SOURCE_BRANCH_NAME", os.getenv("CI_COMMIT_BRANCH")
    ),
)
@click.option(
    "--mr-id",
    help="integer merge request id",
    default=os.getenv("CI_MERGE_REQUEST_ID"),
)
def main(loader_type: str, extractor_type: str, **kwargs) -> None:
    logger.info("Start analysis..")

    loader = SourceLoader.get(loader_type)(**kwargs)
    extractor = Extractor.get(extractor_type)(**kwargs)
    analyzer = Analyzer(
        loader=loader,
        extractor=extractor,
        linters=[CompatibilityLinter(), SquawkLinter()],
    )
    analyzer.analyze()


if __name__ == "__main__":
    main()