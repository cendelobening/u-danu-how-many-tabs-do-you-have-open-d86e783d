#!/usr/bin/env python3
"""How Many Tabs Do You Have Open? — make.fun entry.

Writes one number (digits only, nothing else) to /output/entry.txt:
the honest count of open browser tabs. Pure stdlib, no network,
no reads outside this repository.
"""

import os
import stat
import sys
import tempfile

# The chosen count: 47 tabs. A lived-in number — research papers,
# docs, a few shops and videos, none of them ever closed.
TAB_COUNT = "47"
OUTPUT_NAME = "entry.txt"


def output_dir() -> str:
    """Honour MAKEFUN_OUTPUT_DIR when set, else /output."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def validate(text: str) -> None:
    """The gate: 1-5 characters, ASCII digits only, not only whitespace."""
    if not (1 <= len(text) <= 5):
        raise ValueError(f"entry must be 1-5 characters, got {len(text)}")
    # isdigit() alone would also accept non-ASCII digits; the gate wants
    # plain ASCII digits, so require isascii() too.
    if not text.isascii() or not text.isdigit():
        raise ValueError(f"entry must be ASCII digits only, got {text!r}")
    if not text.strip():
        raise ValueError("entry must not be only whitespace")


def main() -> int:
    try:
        validate(TAB_COUNT)
        out_dir = output_dir()
        os.makedirs(out_dir, exist_ok=True)
        target = os.path.join(out_dir, OUTPUT_NAME)
        data = TAB_COUNT.encode("utf-8")

        # Write via temp file in the same directory, then atomic replace.
        fd, tmp_path = tempfile.mkstemp(
            prefix=".entry.", suffix=".tmp", dir=out_dir
        )
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(data)
                fh.flush()
                os.fsync(fh.fileno())
            os.chmod(tmp_path, 0o644)
            os.replace(tmp_path, target)
        except BaseException:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

        # Read the file back and verify bytes + mode 0644, and that the
        # content on disk itself passes the gate.
        with open(target, "rb") as fh:
            actual = fh.read()
        if actual != data:
            raise ValueError(
                f"verification failed: file holds {actual!r}, expected {data!r}"
            )
        validate(actual.decode("utf-8"))
        mode = stat.S_IMODE(os.stat(target).st_mode)
        if mode != 0o644:
            raise ValueError(f"verification failed: mode is {oct(mode)}, not 0o644")
    except Exception as exc:  # noqa: BLE001 - any failure must exit non-zero
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
