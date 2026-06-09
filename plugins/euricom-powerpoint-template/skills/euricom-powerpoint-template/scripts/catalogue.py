#!/usr/bin/env python3
"""
catalogue.py - print what the active Euricom template offers, so you can
decide BEFORE building: reuse a Components Library slide when one fits, else
build on a base layout. Always run this first.

    python catalogue.py            # uses the newest uploaded template
    python catalogue.py <file>     # or a specific .pptx
"""
import sys
from build_deck import Deck


def main():
    d = Deck(sys.argv[1] if len(sys.argv) > 1 else None)
    print(f"Template : {d.template_path}")
    print(f"Canvas   : x={d.canvas['x']} y={d.canvas['y']} "
          f"w={d.canvas['w']} h={d.canvas['h']} (inches)\n")

    print("BASE LIBRARY (clone + refill for standard slides)")
    base = d.base_examples()
    if not base:
        print("  (none found - the engine will instantiate bare layouts)")
    for role, notes in base.items():
        first = notes.splitlines()[0].strip() if notes else "(no notes)"
        print(f"  - {role:8s}: {first}")
    print()

    print("COMPONENTS LIBRARY (clone + refill for richer slides)")
    cat = d.library()
    if not cat:
        print("  (empty)")
    for c in cat:
        print(f"  [{c['index']}] {c['label']}")
        if c["notes"]:
            for line in c["notes"].splitlines()[1:]:
                if line.strip():
                    print(f"          {line.strip()}")


if __name__ == "__main__":
    main()
