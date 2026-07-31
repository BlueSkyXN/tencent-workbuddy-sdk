#!/usr/bin/env python3
"""Inventory OpenAPI paths/operations for coverage checks."""

from __future__ import annotations

import argparse
import hashlib
import re
from collections import defaultdict
from pathlib import Path

PATH_RE = re.compile(r"^  '?(?P<path>/[^:'\s]+)'?:\s*$")
METHOD_RE = re.compile(r"^    (get|post|put|delete|patch):\s*$")
SUMMARY_RE = re.compile(r"^      summary:\s*(.+)$")


def domain_for(path: str) -> str:
    if "/openapi/skill-categories" in path:
        return "skill_categories"
    if "/openapi/skills" in path:
        return "skills"
    if "/openapi/expert-categories" in path:
        return "expert_categories"
    if "/openapi/experts" in path:
        return "experts"
    if "/openapi/models" in path:
        return "models"
    if "/openapi/groups" in path:
        return "groups"
    if "/openapi/usage" in path:
        return "usage"
    if "/openapi/license" in path:
        return "licenses"
    if "/openapi/members" in path:
        return "members"
    if "/dashboard" in path or "/metrics" in path:
        return "analytics"
    if "/users" in path:
        return "users"
    if path.endswith("/info") or re.search(r"/enterprises/\{enterpriseId\}/license$", path):
        return "enterprise"
    return "unclassified"


def inventory(path: Path) -> None:
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    lines = text.splitlines()
    ops: list[tuple[str, str, str]] = []
    i = 0
    while i < len(lines):
        m = PATH_RE.match(lines[i])
        if not m:
            i += 1
            continue
        pth = m.group("path")
        j = i + 1
        while j < len(lines) and not PATH_RE.match(lines[j]):
            mm = METHOD_RE.match(lines[j])
            if mm:
                method = mm.group(1).upper()
                summary = ""
                for k in range(j + 1, min(j + 40, len(lines))):
                    if METHOD_RE.match(lines[k]) or PATH_RE.match(lines[k]):
                        break
                    sm = SUMMARY_RE.match(lines[k])
                    if sm:
                        summary = sm.group(1).strip()
                ops.append((method, pth, summary))
            j += 1
        i = j if j > i else i + 1

    print(f"file: {path}")
    print(f"bytes: {len(raw)}")
    print(f"sha256: {hashlib.sha256(raw).hexdigest()}")
    print(f"paths: {len({p for _, p, _ in ops})}")
    print(f"operations: {len(ops)}")
    by: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for op in ops:
        by[domain_for(op[1])].append(op)
    for dom in sorted(by, key=lambda d: (-len(by[d]), d)):
        print(f"\n## {dom} ({len(by[dom])})")
        for method, pth, summary in by[dom]:
            print(f"- {method:4} {pth}  # {summary}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("yaml_path", type=Path)
    args = ap.parse_args()
    inventory(args.yaml_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
