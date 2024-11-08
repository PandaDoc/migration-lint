from typing import Optional, List

from sqlfluff.core.parser import BaseSegment, PositionMarker
from sqlfluff.dialects.dialect_ansi import StatementSegment

from migration_lint.sql.model import SegmentLocator


def find_matching_segment(
    segment: BaseSegment,
    locator: SegmentLocator,
    min_position: Optional[PositionMarker] = None,
    context: Optional[List[StatementSegment]] = None,
) -> Optional[BaseSegment]:
    """Find matching segment by the given locator starting with the given
    position.
    """

    for found in segment.recursive_crawl(locator.type):
        if (
            not locator.ignore_order
            and min_position
            and found.pos_marker
            and found.pos_marker < min_position
        ):
            continue
        attrs_match = True
        if locator.raw and locator.raw.upper() != found.raw.upper():
            attrs_match = False

        children_match = True
        if locator.children:
            min_position = None
            for child_locator in locator.children:
                child_found = find_matching_segment(
                    segment=found,
                    locator=child_locator,
                    min_position=min_position,
                )
                if (
                    not child_locator.inverted
                    and not child_found
                    or child_locator.inverted
                    and child_found
                ):
                    children_match = False
                if child_found:
                    min_position = child_found.pos_marker

        # unsafe segment still can be safe if paired with specific
        only_with_match = locator.only_with is None
        if locator.only_with and context:
            match_by_original = find_matching_segment(
                segment, locator.only_with.match_by
            )
            for context_statement in context:
                # searching in the same migration
                found_context_segment = find_matching_segment(
                    context_statement, locator.only_with.locator
                )
                if not found_context_segment:
                    continue

                # matching in context
                # (for example checking table that being created
                # is the same as being altered)
                match_by_context = find_matching_segment(
                    found_context_segment, locator.only_with.match_by
                )
                if (
                    match_by_original
                    and match_by_context
                    and match_by_original.raw_normalized()
                    == match_by_context.raw_normalized()
                ):
                    only_with_match = True

        if attrs_match and children_match and only_with_match:
            return found

    return None
