#!/usr/bin/env python3
"""Prepare the full English AIOS test handoff without provider calls."""

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
sys.path.insert(0, str(PACKAGE / "pruefungen/englische-pilotuebergabe-0-2-0"))
from prepare_pilot import main

if __name__ == "__main__":
    main(guide=PACKAGE / "docs/english-full-test.md", clients=["claude-code", "codex"],
         destination=HERE, archive_name="aios-0.2.0-dev-en-full-test.zip",
         manifest_name="TEST-MANIFEST.json", status_label="full English AIOS development test package",
         exercise_lifecycle=True)
