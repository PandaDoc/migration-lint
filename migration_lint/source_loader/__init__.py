from migration_lint.source_loader.base import SourceLoader
from migration_lint.source_loader.local import LocalLoader
from migration_lint.source_loader.gitlab import GitlabBranchLoader, GitlabMRLoader

__all__ = (
    "SourceLoader",
    "LocalLoader",
    "GitlabBranchLoader",
    "GitlabMRLoader",
)
