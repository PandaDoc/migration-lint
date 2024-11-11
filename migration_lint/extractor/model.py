from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from migration_lint.source_loader.model import SourceDiff


@dataclass
class Migration:
    """A database migration file representation.

    - path -- path to the migration file;
    - raw_sql -- raw SQL representation of the migration.
    """

    path: str
    raw_sql: str


@dataclass
class ExtendedSourceDiff(SourceDiff):
    """An object desribing a single changed file.

    - `path` -- the path to the file;
    - `old_path` -- the previous path to the file; differs from `path` if the
      file was renamed;
    - `diff` -- difference between versions (if present).
    - `allowed_with_backward_incompatible` -- is this file is allowed with
      backward-incompatible migrations.
    """

    allowed_with_backward_incompatible: bool = False

    @classmethod
    def of_source_diff(
        cls,
        source_diff: SourceDiff,
        allowed_with_backward_incompatible,
    ) -> ExtendedSourceDiff:
        """Create an instance by the given source diff."""

        return cls(
            path=source_diff.path,
            old_path=source_diff.old_path,
            diff=source_diff.diff,
            allowed_with_backward_incompatible=allowed_with_backward_incompatible,
        )


@dataclass
class MigrationsMetadata:
    """Migrations metadata.

    - `changed_files` -- a list of changed files;
    - `migrations` -- a list of migrations.
    """

    changed_files: List[ExtendedSourceDiff] = field(default_factory=list)
    migrations: List[Migration] = field(default_factory=list)
