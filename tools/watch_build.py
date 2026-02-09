#!/usr/bin/env python3
"""Simple file watcher for order.life FastSite.

Runs build.py whenever files change under:
- templates/
- static/
- content/
- build.py

No external deps (polling).
"""

from __future__ import annotations

import os
import sys
import time
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WATCH_PATHS = [
    ROOT / "build.py",
    ROOT / "templates",
    ROOT / "static",
    ROOT / "content",
]

# Ignore generated output + large exports
IGNORE_DIRS = {"site", ".git", "node_modules", "__pycache__"}
IGNORE_SUFFIXES = {".xml"}


def iter_files():
    for p in WATCH_PATHS:
        if p.is_file():
            yield p
        elif p.is_dir():
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
                for fn in files:
                    fp = Path(root) / fn
                    if fp.suffix in IGNORE_SUFFIXES:
                        continue
                    yield fp


def snapshot_mtimes() -> dict[Path, float]:
    snap = {}
    for f in iter_files():
        try:
            snap[f] = f.stat().st_mtime
        except FileNotFoundError:
            pass
    return snap


def changed(prev: dict[Path, float], cur: dict[Path, float]) -> bool:
    if prev.keys() != cur.keys():
        return True
    for k, v in cur.items():
        if prev.get(k) != v:
            return True
    return False


def run_build() -> int:
    print("\n[watch_build] change detected -> running: python3 build.py", flush=True)
    t0 = time.time()
    p = subprocess.run([sys.executable, str(ROOT / "build.py")])
    dt = time.time() - t0
    print(f"[watch_build] build exit={p.returncode} in {dt:.1f}s", flush=True)
    return p.returncode


def main():
    interval = float(os.environ.get("WATCH_BUILD_INTERVAL", "1.0"))
    prev = snapshot_mtimes()
    print("[watch_build] watching for changes...", flush=True)

    # Initial build (optional)
    if os.environ.get("WATCH_BUILD_INITIAL", "1") == "1":
        run_build()
        prev = snapshot_mtimes()

    while True:
        time.sleep(interval)
        cur = snapshot_mtimes()
        if changed(prev, cur):
            run_build()
            prev = snapshot_mtimes()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[watch_build] stopped", flush=True)
        sys.exit(0)
