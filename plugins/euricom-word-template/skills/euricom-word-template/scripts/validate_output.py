#!/usr/bin/env python3
"""
validate_output.py
==================

Quick sanity check for a generated .docx: it parses every XML file in
the zip with the standard library and reports the first parse error if
any. This catches malformed XML (unbalanced tags, bad escapes) BEFORE
the user opens the file in Word and sees a generic 'file is corrupt'
dialog.

Also confirms that key template assets survived the build: theme,
styles, header2 (with logo), footer2, and the relationships file.

Finally, scans document.xml for double-encoded entity patterns
(``&amp;#x...;``) — a common authoring mistake where the body-composition
script pre-encoded characters as entities instead of passing plain text
to escape_text. The reader sees those literal codes in the document if
this isn't caught.

Usage:  python validate_output.py path/to/output.docx
"""

import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


REQUIRED_PARTS = [
    "word/document.xml",
    "word/styles.xml",
    "word/theme/theme1.xml",
    "word/_rels/document.xml.rels",
    "[Content_Types].xml",
]

# Headers and footers may be named header1.xml, header2.xml, header3.xml
# depending on which template version is in use. We require at least one
# of each rather than a specific filename.
REQUIRED_PART_PATTERNS = [
    (re.compile(r"^word/header\d+\.xml$"), "header (any number)"),
    (re.compile(r"^word/footer\d+\.xml$"), "footer (any number)"),
]


# Pattern for double-encoded XML entities. When a body-composition script
# writes "&#x201C;" into a string that's then passed to escape_text, the
# leading "&" gets escaped to "&amp;", producing "&amp;#x201C;" in the
# final XML. Word renders that as the literal text "&#x201C;" rather than
# a smart quote — a confusing, embarrassing bug that's invisible until
# the user opens the document.
DOUBLE_ENCODED = re.compile(r"&amp;#x[0-9A-Fa-f]+;")


def validate(path: Path) -> int:
    if not path.exists():
        print(f"Error: file not found: {path}")
        return 1

    try:
        zf = zipfile.ZipFile(path)
    except zipfile.BadZipFile as e:
        print(f"Error: not a valid zip/docx file: {e}")
        return 1

    names = set(zf.namelist())
    errors = []

    # Check required parts exist (exact names)
    for part in REQUIRED_PARTS:
        if part not in names:
            errors.append(f"Missing required part: {part}")

    # Check required part patterns (header / footer with any number)
    for pattern, description in REQUIRED_PART_PATTERNS:
        if not any(pattern.match(n) for n in names):
            errors.append(f"Missing required part matching: {description}")

    # Parse every XML file
    for name in zf.namelist():
        if not name.endswith(".xml") and not name.endswith(".rels"):
            continue
        try:
            ET.fromstring(zf.read(name))
        except ET.ParseError as e:
            errors.append(f"XML parse error in {name}: {e}")

    # Spot-check that document.xml is a docx document, not a dotx template
    ct = zf.read("[Content_Types].xml").decode("utf-8")
    if "wordprocessingml.template.main+xml" in ct and "wordprocessingml.document.main+xml" not in ct:
        errors.append(
            "[Content_Types].xml still declares document.xml as a template "
            "(dotx). Word may refuse to save edits. The build script should "
            "rewrite this content type."
        )

    # Detect double-encoded entities in document.xml
    if "word/document.xml" in names:
        doc_xml = zf.read("word/document.xml").decode("utf-8")
        matches = DOUBLE_ENCODED.findall(doc_xml)
        if matches:
            unique = sorted(set(matches))
            sample = ", ".join(unique[:5])
            errors.append(
                f"Double-encoded XML entities found in document.xml "
                f"({len(matches)} occurrence(s), {len(unique)} unique: {sample}). "
                f"This means the body-composition script pre-encoded characters "
                f"as XML entities (e.g. '&#x201C;') instead of passing plain "
                f"text. The reader will see raw hex codes instead of smart "
                f"quotes / accented characters. Fix: replace pre-encoded "
                f"entities in your input strings with actual UTF-8 characters "
                f"and let escape_text do the conversion."
            )

    if errors:
        print(f"VALIDATION FAILED ({len(errors)} issue(s)):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"OK: {path} ({path.stat().st_size:,} bytes, {len(names)} parts)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate_output.py path/to/output.docx", file=sys.stderr)
        sys.exit(2)
    sys.exit(validate(Path(sys.argv[1])))
