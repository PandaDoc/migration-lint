from __future__ import annotations

import dataclasses
from typing import Optional, List


@dataclasses.dataclass
class SegmentLocator:
    """A locator object used to find segments.

    - `type` -- string used to match the type of operation (see sqlfluff types);
    - `raw` -- string used to match segment by raw SQL;
    - `children` -- list of locators used to match descendant segments (on any
      level);
    - `inverted` --- flag to perform an "inverted" match; works only for
      children, so it's actually "segment that doesn't contain specific
      descendant".
    - `ignore_order` --- by default linter looks for keywords in order,
      use this flag to search regardless
    - `only_with` --- if statement comes with this statement in one migration, it's safe,
      for example if we create table and add foreign key in one migration, it's safe,
      if we add foreign key on existing big table - it's not.
    """

    type: str
    raw: Optional[str] = None
    children: Optional[List[SegmentLocator]] = None
    inverted: bool = False
    ignore_order: bool = False
    only_with: Optional[ConditionalMatch] = None


@dataclasses.dataclass
class KeywordLocator(SegmentLocator):
    """A locator object used to find segments by keyword."""

    type: str = "keyword"


@dataclasses.dataclass
class ConditionalMatch:
    """
    An object to segment by condition
    (for example CREATE TABLE and ALTER TABLE for the same table).
    See sql/rules.py for examples.

    - `locator` -- what segment to look for.
    - `match_by` -- how to match two segments (by table name, column name etc);
    """

    locator: SegmentLocator
    match_by: SegmentLocator
