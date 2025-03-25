from __future__ import annotations

import os.path
import re
import subprocess
import sys
from io import StringIO
from collections import defaultdict
from typing import List, Dict, Optional

import migration_lint
from migration_lint.analyzer.base import BaseLinter
from migration_lint.extractor.model import ExtendedSourceDiff


class SquawkLinter(BaseLinter):
    """Squawk linter integration."""

    ignored_rules = [
        "ban-drop-column",  # Backward-incompatible, checked by compatibility analyzer.
        "ban-drop-table",  # Backward-incompatible, checked by compatibility analyzer.
        "adding-not-nullable-field",  # Backward-incompatible, checked by compatibility analyzer.
        "prefer-big-int",  # Deprecated.
        "prefer-identity",
        "prefer-timestamptz",
        "ban-drop-not-null",  # Dropping a NOT NULL constraint is safe but may break existing clients.
        "prefer-robust-stmts",  # TODO: Add transactions tracking.
        "transaction-nesting",  # TODO: Add transactions tracking.
    ]

    def __init__(
        self, config_path: Optional[str] = None, pg_version: Optional[str] = None
    ) -> None:
        bin_dir = os.path.join(migration_lint.__path__[0], "bin")
        self.config_path = config_path
        self.pg_version = pg_version
        if sys.platform == "linux":
            self.squawk = os.path.join(bin_dir, "squawk-linux-x86")
        elif sys.platform == "darwin":
            self.squawk = os.path.join(bin_dir, "squawk-darwin-arm64")
        else:
            raise RuntimeError(f"unsupported platform: {sys.platform}")

    def squawk_command(self, migration_sql: str) -> str:
        """Get squawk command."""
        exclude = f"--exclude={','.join(self.ignored_rules)}"
        config = f"--config={self.config_path}" if self.config_path else ""
        pg_version = f"--pg-version={self.pg_version}" if self.pg_version else ""

        return " ".join([self.squawk, exclude, config, pg_version]).strip()

    def lint(
        self,
        migration_sql: str,
        changed_files: List[ExtendedSourceDiff],
    ) -> List[str]:
        """Perform SQL migration linting."""

        output = subprocess.run(
            self.squawk_command(migration_sql),
            input=migration_sql.encode(),
            shell=True,
            stdout=subprocess.PIPE,
        ).stdout.decode("utf-8")

        # Reformat the output for brevity.

        statements: Dict[str, str] = {}
        error_msgs: Dict[str, List[str]] = defaultdict(list)

        key = None
        statement = None
        error_msg = None
        for line in output.splitlines():
            stmt_m = re.match(r"\s+\d+\s+\|\s(.*)", line)

            if line.startswith("stdin:"):
                if key is not None:
                    statements[key] = statement.getvalue()
                    error_msgs[key].append(error_msg.getvalue())

                key = line[: line.index(" ")]

                statement = None
                error_msg = StringIO()
                error_msg.write(f"  - squawk {line[line.index(' ') + 1:]}\n\n")

            elif stmt_m is not None:
                if statement is None:
                    statement = StringIO()
                    statement.write(f"- {stmt_m.group(1)}\n")
                else:
                    statement.write(f"  {stmt_m.group(1)}\n")

            elif line.startswith("  "):
                if error_msg is not None:
                    error_msg.write(f"  {line}\n")
        else:
            if key is not None:
                assert statement is not None
                assert error_msg is not None

                statements[key] = statement.getvalue()
                error_msgs[key].append(error_msg.getvalue())

        # Generate the errors.

        errors: List[str] = []

        error = StringIO()
        for key in statements:
            error.write(f"{statements[key]}\n")
            for msg in error_msgs[key]:
                error.write(msg)
            errors.append(error.getvalue())

            error = StringIO()

        if errors:
            errors.append(
                "squawk: find detailed examples and solutions for each rule at "
                "https://squawkhq.com/docs/rules"
            )

        return errors
