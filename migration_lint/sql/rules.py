from typing import List

from migration_lint.sql.model import ConditionalMatch, KeywordLocator, SegmentLocator

BACKWARD_INCOMPATIBLE_OPERATIONS: List[SegmentLocator] = [
    SegmentLocator(type="drop_sequence_statement"),
    # TODO: drop constraints first?
    SegmentLocator(type="drop_table_statement"),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ALTER"),
            KeywordLocator(raw="COLUMN"),
            KeywordLocator(raw="DROP"),
            KeywordLocator(raw="DEFAULT"),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ALTER"),
            KeywordLocator(raw="COLUMN"),
            KeywordLocator(raw="SET"),
            KeywordLocator(raw="NOT"),
            KeywordLocator(raw="NULL"),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ADD"),
            KeywordLocator(raw="COLUMN"),
            KeywordLocator(raw="PRIMARY"),
            KeywordLocator(raw="KEY"),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ADD"),
            KeywordLocator(raw="CONSTRAINT"),
            KeywordLocator(raw="PRIMARY"),
            KeywordLocator(raw="KEY"),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="DROP"),
            KeywordLocator(raw="COLUMN"),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="RENAME"),
            KeywordLocator(raw="COLUMN"),
        ],
    ),
    SegmentLocator(type="truncate_table"),
    SegmentLocator(type="drop_type_statement"),
]

BACKWARD_COMPATIBLE_OPERATIONS: List[SegmentLocator] = [
    SegmentLocator(
        type="create_index_statement", children=[KeywordLocator(raw="CONCURRENTLY")]
    ),
    SegmentLocator(
        type="drop_index_statement", children=[KeywordLocator(raw="CONCURRENTLY")]
    ),
    SegmentLocator(
        type="alter_index_statement", children=[KeywordLocator(raw="RENAME")]
    ),
    SegmentLocator(
        type="reindex_statement_segment", children=[KeywordLocator(raw="CONCURRENTLY")]
    ),
    SegmentLocator(type="create_sequence_statement"),
    SegmentLocator(type="alter_sequence_statement"),
    SegmentLocator(type="create_table_statement"),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ADD"),
            KeywordLocator(raw="COLUMN"),
            KeywordLocator(raw="NOT", inverted=True),
            KeywordLocator(raw="NULL"),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ALTER"),
            KeywordLocator(raw="COLUMN"),
            KeywordLocator(raw="DROP"),
            KeywordLocator(raw="NOT"),
            KeywordLocator(raw="NULL"),
        ],
    ),
    # it's ok to do "SET NOT NULL" only after explicit "VALIDATE CONSTRAINT"
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ALTER"),
            KeywordLocator(raw="COLUMN"),
            KeywordLocator(raw="SET"),
            KeywordLocator(raw="NOT"),
            KeywordLocator(raw="NULL"),
        ],
        only_with=ConditionalMatch(
            SegmentLocator(
                type="alter_table_statement",
                children=[
                    KeywordLocator(raw="VALIDATE"),
                    KeywordLocator(raw="CONSTRAINT"),
                ],
            ),
            match_by=SegmentLocator(type="table_reference"),
        ),
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ADD"),
            KeywordLocator(raw="COLUMN"),
            KeywordLocator(raw="NOT"),
            KeywordLocator(raw="NULL"),
            KeywordLocator(raw="DEFAULT", ignore_order=True),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ALTER"),
            KeywordLocator(raw="COLUMN"),
            KeywordLocator(raw="SET"),
            KeywordLocator(raw="DEFAULT"),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ADD"),
            KeywordLocator(raw="CONSTRAINT"),
            KeywordLocator(raw="UNIQUE"),
            KeywordLocator(raw="USING"),
            KeywordLocator(raw="INDEX"),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ADD"),
            KeywordLocator(raw="CONSTRAINT"),
        ],
        only_with=ConditionalMatch(
            locator=SegmentLocator(type="create_table_statement"),
            match_by=SegmentLocator(type="table_reference"),
        ),
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ALTER"),
            KeywordLocator(raw="COLUMN"),
            KeywordLocator(raw="DROP"),
            KeywordLocator(raw="NOT"),
            KeywordLocator(raw="NULL"),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="DROP"),
            KeywordLocator(raw="CONSTRAINT"),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ADD"),
            KeywordLocator(raw="CONSTRAINT"),
            KeywordLocator(raw="NOT"),
            KeywordLocator(raw="VALID"),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="VALIDATE"),
            KeywordLocator(raw="CONSTRAINT"),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ADD"),
            KeywordLocator(raw="FOREIGN"),
            KeywordLocator(raw="KEY"),
            KeywordLocator(raw="NOT"),
            KeywordLocator(raw="VALID"),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ADD"),
            KeywordLocator(raw="FOREIGN"),
            KeywordLocator(raw="KEY"),
        ],
        only_with=ConditionalMatch(
            locator=SegmentLocator(type="create_table_statement"),
            match_by=SegmentLocator(type="table_reference"),
        ),
    ),
    # change type to text is always safe
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ALTER"),
            KeywordLocator(raw="COLUMN"),
            KeywordLocator(raw="TYPE"),
            SegmentLocator(type="data_type", raw="TEXT"),
        ],
    ),
    # basic ADD COLUMN is default to NULL, so it's safe
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ADD"),
            KeywordLocator(raw="COLUMN"),
            KeywordLocator(raw="NOT", inverted=True),
            KeywordLocator(raw="NULL", inverted=True),
            KeywordLocator(raw="PRIMARY", inverted=True),
            KeywordLocator(raw="KEY", inverted=True),
            KeywordLocator(raw="IDENTITY", inverted=True),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ALTER"),
            KeywordLocator(raw="COLUMN"),
            KeywordLocator(raw="ADD"),
            KeywordLocator(raw="GENERATED"),
            KeywordLocator(raw="IDENTITY"),
        ],
    ),
    SegmentLocator(type="create_statistics_statement"),
    SegmentLocator(type="analyze_statement"),
    SegmentLocator(type="reset_statement"),
    SegmentLocator(type="create_type_statement"),
    SegmentLocator(
        type="alter_type_statement",
        children=[
            KeywordLocator(raw="ADD"),
            KeywordLocator(raw="VALUE"),
        ],
    ),
    SegmentLocator(
        type="insert_statement",
        children=[SegmentLocator(type="table_reference", raw="alembic_version")],
    ),
    SegmentLocator(
        type="update_statement",
        children=[SegmentLocator(type="table_reference", raw="alembic_version")],
    ),
    SegmentLocator(type="create_function_statement"),
    SegmentLocator(type="drop_function_statement"),
    SegmentLocator(type="create_trigger"),
    SegmentLocator(type="drop_trigger"),
]

RESTRICTED_OPERATIONS: List[SegmentLocator] = [
    SegmentLocator(
        type="create_index_statement",
        children=[KeywordLocator(raw="CONCURRENTLY", inverted=True)],
    ),
    SegmentLocator(
        type="drop_index_statement",
        children=[KeywordLocator(raw="CONCURRENTLY", inverted=True)],
    ),
    SegmentLocator(
        type="reindex_statement_segment",
        children=[KeywordLocator(raw="CONCURRENTLY", inverted=True)],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ADD"),
            KeywordLocator(raw="CONSTRAINT"),
            KeywordLocator(raw="UNIQUE"),
            KeywordLocator(raw="USING", inverted=True),
            KeywordLocator(raw="INDEX", inverted=True),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="RENAME"),
            KeywordLocator(raw="COLUMN", inverted=True),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ALTER"),
            KeywordLocator(raw="COLUMN"),
            KeywordLocator(raw="TYPE"),
            SegmentLocator(type="data_type", raw="TEXT", inverted=True),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ADD"),
            KeywordLocator(raw="CONSTRAINT"),
            KeywordLocator(raw="NOT", inverted=True),
            KeywordLocator(raw="VALID", inverted=True),
            KeywordLocator(raw="USING", inverted=True),
            KeywordLocator(raw="INDEX", inverted=True),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ADD"),
            KeywordLocator(raw="FOREIGN"),
            KeywordLocator(raw="KEY"),
            KeywordLocator(raw="NOT", inverted=True),
            KeywordLocator(raw="VALID", inverted=True),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ADD"),
            KeywordLocator(raw="COLUMN"),
            KeywordLocator(raw="NOT"),
            KeywordLocator(raw="NULL"),
            KeywordLocator(raw="DEFAULT", inverted=True, ignore_order=True),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ADD"),
            KeywordLocator(raw="COLUMN"),
            KeywordLocator(raw="PRIMARY"),
            KeywordLocator(raw="KEY"),
        ],
    ),
    SegmentLocator(
        type="alter_table_statement",
        children=[
            KeywordLocator(raw="ADD"),
            KeywordLocator(raw="COLUMN"),
            KeywordLocator(raw="GENERATED"),
            KeywordLocator(raw="IDENTITY"),
        ],
    ),
]

DATA_MIGRATION_OPERATIONS = [
    SegmentLocator(type="update_statement"),
    SegmentLocator(type="insert_statement"),
    SegmentLocator(type="delete_statement"),
]

IGNORED_OPERATIONS = [
    SegmentLocator(type="select_statement"),
    SegmentLocator(type="set_statement"),
    SegmentLocator(
        type="transaction_statement", children=[KeywordLocator(raw="BEGIN")]
    ),
    SegmentLocator(type="transaction_statement", children=[KeywordLocator(raw="END")]),
    SegmentLocator(
        type="transaction_statement", children=[KeywordLocator(raw="COMMIT")]
    ),
]
