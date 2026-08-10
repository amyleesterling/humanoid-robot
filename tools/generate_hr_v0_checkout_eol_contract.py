#!/usr/bin/env python3
"""Generate an exact Windows checkout EOL contract from the controlled worktree.

The repository historically contains hash-bound text artifacts whose expected
working-tree bytes use both LF and CRLF.  Git's machine-level autocrlf setting
must not decide those bytes.  This generator records only the exceptions to the
project-wide LF default and preserves the five deliberately mixed files as
opaque bytes.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ATTRS = ROOT / ".gitattributes"
BEGIN = "# BEGIN GENERATED CHECKOUT EOL CONTRACT"
END = "# END GENERATED CHECKOUT EOL CONTRACT"
LINE_RE = re.compile(r"^i/(\S+)\s+w/(\S+)\s+attr/.*?\t(.*)$")


def quote(path: str) -> str:
    return json.dumps(path, ensure_ascii=False)


def main() -> None:
    result = subprocess.run(
        ["git", "ls-files", "--eol"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    crlf: list[str] = []
    mixed: list[str] = []
    for raw in result.stdout.splitlines():
        match = LINE_RE.match(raw)
        if not match:
            raise SystemExit(f"unparsed git ls-files --eol row: {raw!r}")
        _index_eol, worktree_eol, path = match.groups()
        if path == ".gitattributes":
            continue
        if worktree_eol == "crlf":
            crlf.append(path)
        elif worktree_eol == "mixed":
            mixed.append(path)

    existing = ATTRS.read_text(encoding="utf-8")
    if BEGIN in existing or END in existing:
        if existing.count(BEGIN) != 1 or existing.count(END) != 1:
            raise SystemExit("malformed generated EOL contract markers")
        prefix, remainder = existing.split(BEGIN, 1)
        _old, suffix = remainder.split(END, 1)
        existing = prefix.rstrip() + "\n" + suffix.lstrip("\n")

    block = [
        BEGIN,
        f"# {len(crlf)} exact CRLF paths; generated from controlled working bytes.",
        *(f"{quote(path)} text eol=crlf" for path in sorted(crlf)),
        f"# {len(mixed)} exact mixed-EOL paths are preserved byte-for-byte.",
        *(f"{quote(path)} -text" for path in sorted(mixed)),
        END,
    ]
    ATTRS.write_text(existing.rstrip() + "\n\n" + "\n".join(block) + "\n", encoding="utf-8", newline="\n")
    print(f"checkout EOL contract: {len(crlf)} CRLF paths / {len(mixed)} mixed paths")


if __name__ == "__main__":
    main()
