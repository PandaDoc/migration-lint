from __future__ import annotations

import abc
from typing import Any, Sequence, cast, Dict

from migration_lint.source_loader.model import SourceDiff
from migration_lint.extractor.model import (
    ExtendedSourceDiff,
    Migration,
    MigrationsMetadata,
)


class Extractor(type):
    """Metaclass for migrations extractors.

    This metaclass registers all its instances in the registry.
    """

    extractors: Dict[str, Extractor] = {}

    def __new__(
        mcls,
        name: str,
        bases: tuple[Extractor, ...],
        classdict: dict[str, Any],
    ) -> Extractor:
        cls = cast(Extractor, type.__new__(mcls, name, bases, classdict))

        if len(bases) > 0:
            # Not the base class.
            if not hasattr(cls, "NAME"):
                raise NotImplementedError(
                    f"extractor {cls.__name__} doesn't provie name",
                )

            mcls.extractors[cls.NAME] = cls

        return cls

    @classmethod
    def names(mcls) -> Sequence[str]:
        """Get the names of all registered extractors."""

        return list(mcls.extractors.keys())

    @classmethod
    def get(mcls, name: str) -> Extractor:
        """Get a registered extractor by its name."""

        return mcls.extractors[name]


class BaseExtractor(metaclass=Extractor):
    """Base class for migrations extractor."""

    def __init__(self, **kwargs) -> None:
        self.ignore_extractor_fail = kwargs.get("ignore_extractor_fail")
        self.ignore_extractor_not_found = kwargs.get("ignore_extractor_not_found")

    def create_metadata(
        self,
        changed_files: Sequence[SourceDiff],
    ) -> MigrationsMetadata:
        """Create migrations metadata by the list of changed files."""

        metadata = MigrationsMetadata()
        for changed_file in changed_files:
            path = changed_file.path

            metadata.changed_files.append(
                ExtendedSourceDiff.of_source_diff(
                    changed_file,
                    self.is_allowed_with_backward_incompatible_migration(path),
                ),
            )

            if self.is_migration(path):
                metadata.migrations.append(
                    Migration(path=path, raw_sql=self.extract_sql(path)),
                )

        return metadata

    @abc.abstractmethod
    def is_migration(self, path: str) -> bool:
        """Check if the specified file is a migration."""

        raise NotImplementedError()

    @abc.abstractmethod
    def is_allowed_with_backward_incompatible_migration(self, path: str) -> bool:
        """Check if the specified file changes are allowed with
        backward-incompatible migrations.
        """

        raise NotImplementedError()

    @abc.abstractmethod
    def extract_sql(self, migration_path: str) -> str:
        """Extract raw SQL from the migration file."""

        raise NotImplementedError()
