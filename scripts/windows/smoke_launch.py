"""Launch a packaged GUI executable as a startup smoke test.

The launch is considered healthy when the process is still running at the end of
the grace window (it is then terminated) or has already exited cleanly with code 0.
An early non-zero exit is treated as a startup failure.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the launch smoke test."""

    parser = argparse.ArgumentParser(
        prog="smoke_launch.py",
        description="Launch a packaged executable and verify it starts cleanly.",
    )
    parser.add_argument(
        "--exe-path",
        required=True,
        help="Path to the packaged executable to launch.",
    )
    parser.add_argument(
        "--grace-seconds",
        type=int,
        default=12,
        help="Survival window, in seconds, before a healthy process is terminated.",
    )
    return parser.parse_args(argv)


def isolated_environment(exe_path: Path) -> dict[str, str]:
    """Return a child environment with offscreen Qt and isolated runtime dirs."""

    profile_root = Path(tempfile.gettempdir()) / f"smoke-{exe_path.stem}"
    config_dir = profile_root / "config"
    data_dir = profile_root / "data"
    temp_dir = profile_root / "temp"
    for directory in (config_dir, data_dir, temp_dir):
        directory.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.update(
        {
            "QT_QPA_PLATFORM": "offscreen",
            "CONFIG_DIR": str(config_dir),
            "DATA_DIR": str(data_dir),
            "APPDATA": str(data_dir),
            "LOCALAPPDATA": str(data_dir),
            "TEMP": str(temp_dir),
            "TMP": str(temp_dir),
        }
    )
    return env


def smoke_launch(exe_path: Path, grace_seconds: int) -> int:
    """Launch the executable and return a process exit code for the smoke test."""

    if not exe_path.is_file():
        print(f"ERROR: executable not found: {exe_path}", file=sys.stderr)
        return 1

    env = isolated_environment(exe_path)
    print(
        f"Launching {exe_path} (offscreen) with a {grace_seconds}s survival window..."
    )
    process = subprocess.Popen([str(exe_path)], env=env)

    deadline = time.monotonic() + max(0, grace_seconds)
    while time.monotonic() < deadline:
        exit_code = process.poll()
        if exit_code is not None:
            if exit_code != 0:
                print(
                    f"ERROR: executable exited early with code {exit_code}.",
                    file=sys.stderr,
                )
                return 1
            print("Executable exited cleanly with code 0.")
            return 0
        time.sleep(0.25)

    print(
        "Executable still running after grace window; launch is healthy. Terminating."
    )
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the launch smoke test from command-line arguments."""

    args = parse_args(argv)
    return smoke_launch(Path(args.exe_path), int(args.grace_seconds))


if __name__ == "__main__":
    raise SystemExit(main())
