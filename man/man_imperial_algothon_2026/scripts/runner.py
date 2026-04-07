"""Bazel runner dispatcher — cross-platform gateway for algothon-2026 run targets.

Each ``sh_binary``/``py_binary`` gateway target in BUILD.bazel passes a single
positional argument (``backtest`` | ``submit`` | ``jupyter`` | ``docker_build``
| ``docker_jupyter`` | ``docker_down``) as ``args = ["<action>"]``.  This
script reads that argument, enriches ``sys.argv`` from the environment, then
either calls the engine's ``main()`` in-process (zero overhead, shared
interpreter) or shells out for Docker / Jupyter operations.

Environment variables forwarded from the calling shell:
    TEAM_NAME      Team identifier for submission naming.   (default: algothon_team)
    ROUND_NUMBER   Hackathon round number.                  (default: 1)
    RISK_AVERSION  MVO risk-aversion lambda λ.              (default: 2.0)
    BLEND_ALPHA    TSMOM/XSMOM blend coefficient α.         (default: 0.7)
    DATA_DIR       Path to CSV data directory.              (default: data/sample)
    OUTPUT_DIR     Submission output directory.             (default: submissions)

Usage (via Bazel — do not invoke directly):
    bazel run //:backtest
    bazel run //:submit -- --round 2
    bazel run //:jupyter
    bazel run //:docker_build
    bazel run //:docker_jupyter
    bazel run //:docker_down

Cross-platform notes:
    * Pure Python — works identically on Windows 11, Linux, and macOS.
    * No dependency on MSYS2, Cygwin, or any POSIX shell.
    * Docker/Jupyter sub-commands use ``subprocess`` so they inherit the
      caller's PATH and environment transparently.

Author: Algothon 2026 Team
"""

# Copyright 2026 Man Group Algothon Team. All rights reserved.

from __future__ import annotations

import os
import subprocess
import sys
from typing import Final

# ---------------------------------------------------------------------------
# Environment resolution helpers
# ---------------------------------------------------------------------------

def _env(key: str, default: str) -> str:
    """Return the environment variable *key*, falling back to *default*."""
    return os.environ.get(key, default)


def _base_engine_argv(action_flag: str | None = None) -> list[str]:
    """Build the ``sys.argv`` list forwarded to :func:`execution.engine.main`.

    Args:
        action_flag: Optional CLI flag to prepend (e.g. ``"--backtest"``).

    Returns:
        List of string arguments suitable for ``sys.argv`` assignment.
    """
    argv: list[str] = [
        "algothon",
        "--data-dir",     _env("DATA_DIR",       "data/sample"),
        "--team",         _env("TEAM_NAME",       "algothon_team"),
        "--round",        _env("ROUND_NUMBER",    "1"),
        "--risk-aversion",_env("RISK_AVERSION",   "2.0"),
        "--blend-alpha",  _env("BLEND_ALPHA",     "0.7"),
        "--output-dir",   _env("OUTPUT_DIR",      "submissions"),
    ]
    if action_flag:
        argv.append(action_flag)
    # Append any extra args passed after `--` on the bazel run command-line
    argv.extend(sys.argv[2:])
    return argv


# ---------------------------------------------------------------------------
# Action dispatch table
# ---------------------------------------------------------------------------

_DOCKER_COMMANDS: Final[dict[str, list[str]]] = {
    "docker_build":   ["docker", "compose", "build"],
    "docker_jupyter": ["docker", "compose", "up", "jupyter"],
    "docker_down":    ["docker", "compose", "down"],
}


def _dispatch(action: str) -> int:
    """Route *action* to the appropriate handler.

    Args:
        action: One of ``backtest``, ``submit``, ``jupyter``,
                ``docker_build``, ``docker_jupyter``, ``docker_down``.

    Returns:
        Process exit code (0 = success).
    """
    if action == "backtest":
        from execution.engine import main as _engine_main  # noqa: PLC0415
        sys.argv = _base_engine_argv("--backtest")
        return _engine_main()

    if action == "submit":
        from execution.engine import main as _engine_main  # noqa: PLC0415
        sys.argv = _base_engine_argv()  # no --backtest flag → submission only
        return _engine_main()

    if action == "jupyter":
        return subprocess.call(
            ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser"],
        )

    if action in _DOCKER_COMMANDS:
        return subprocess.call(_DOCKER_COMMANDS[action])

    print(
        f"[runner] Unknown action: '{action}'.  "
        "Valid actions: backtest submit jupyter docker_build docker_jupyter docker_down",
        file=sys.stderr,
    )
    return 1


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    """Parse the action argument and dispatch.

    Returns:
        Exit code forwarded to the OS.
    """
    if len(sys.argv) < 2:
        print("[runner] No action provided.", file=sys.stderr)
        return 1
    return _dispatch(sys.argv[1])


if __name__ == "__main__":
    sys.exit(main())