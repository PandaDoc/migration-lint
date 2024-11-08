import enum

from migration_lint.util.colors import grey, green, red, yellow


class StatementType(str, enum.Enum):
    """Types of migration statements."""

    IGNORED = "ignored"
    BACKWARD_COMPATIBLE = "backward_compatible"
    BACKWARD_INCOMPATIBLE = "backward_incompatible"
    DATA_MIGRATION = "data_migration"
    RESTRICTED = "restricted"
    UNSUPPORTED = "unsupported"

    @property
    def colorized(self):
        if self is StatementType.IGNORED:
            return grey(self)
        elif self is StatementType.BACKWARD_COMPATIBLE:
            return green(self)
        elif self is StatementType.BACKWARD_INCOMPATIBLE:
            return red(self)
        elif self is StatementType.DATA_MIGRATION:
            return red(self)
        elif self is StatementType.RESTRICTED:
            return yellow(self)
        elif self is StatementType.UNSUPPORTED:
            return red(self)
