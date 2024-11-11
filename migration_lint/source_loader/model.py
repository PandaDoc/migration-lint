from dataclasses import dataclass
from typing import Optional


@dataclass
class SourceDiff:
    """An object describing a single changed file.

    - `path` -- the path to the file;
    - `old_path` -- the previous path to the file; differs from `path` if the
      file was renamed;
    - `diff` -- difference between versions (if present).
    """

    path: str
    old_path: str = ""
    diff: Optional[str] = None

    def __post_init__(self):
        if not self.old_path:
            self.old_path = self.path
