from migration_lint.analyzer.base import Analyzer
from migration_lint.analyzer.compat import CompatibilityLinter
from migration_lint.analyzer.primary_key import PrimaryKeyLinter
from migration_lint.analyzer.squawk import SquawkLinter

__all__ = (
    "Analyzer",
    "CompatibilityLinter",
    "SquawkLinter",
    "PrimaryKeyLinter",
)
