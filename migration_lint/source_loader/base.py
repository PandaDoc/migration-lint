from __future__ import annotations

import abc
from typing import Any, Sequence, cast, Dict

from migration_lint.source_loader.model import SourceDiff


class SourceLoader(type):
    """Metaclass for source loaders.

    This metaclass register all its instances in the registry.
    """

    source_loaders: Dict[str, SourceLoader] = {}

    def __new__(
        mcls,
        name: str,
        bases: tuple[SourceLoader, ...],
        classdict: Dict[str, Any],
    ) -> SourceLoader:
        cls = cast(SourceLoader, type.__new__(mcls, name, bases, classdict))

        if len(bases) > 0:
            # Not the base class.
            if not hasattr(cls, "NAME"):
                raise NotImplementedError(
                    f"source loader {cls.__name__} doesn't provide name",
                )

            mcls.source_loaders[cls.NAME] = cls

        return cls

    @classmethod
    def names(mcls) -> Sequence[str]:
        """Get the names of all registered source loaders."""

        return list(mcls.source_loaders.keys())

    @classmethod
    def get(mcls, name: str) -> SourceLoader:
        """Get a registered source loader by its name."""

        return mcls.source_loaders[name]


class BaseSourceLoader(metaclass=SourceLoader):
    """Base class for changes source files loader."""

    def __init__(self, only_new_files: bool, **kwargs: Any) -> None:
        self.only_new_files = only_new_files

    @abc.abstractmethod
    def get_changed_files(self) -> Sequence[SourceDiff]:
        """Return a list of changed files."""

        raise NotImplementedError()
