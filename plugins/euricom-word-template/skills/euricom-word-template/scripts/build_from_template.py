#!/usr/bin/env python3
"""
build_from_template.py
=======================

Build a .docx from the Euricom template by copying the entire .dotx
(styles, theme, header, footer, logo, fonts) and swapping the body.

The critical insight: docx-js or python-docx built from scratch lose
all the visual identity baked into the template. The template-copy
approach keeps everything (styles, theme, header, footer, logo) intact
and only replaces the visible content.

Usage
-----
    python build_from_template.py \\
        --template path/to/Euricom_Generic_Template_v1_0.dotx \\
        --body path/to/body.xml \\
        --output path/to/output.docx

The body.xml file must contain the contents that belong INSIDE
<w:body>...</w:body> — that is, a sequence of <w:p>, <w:tbl>, etc.,
WITHOUT the <w:body> wrapper itself. The script handles wrapper,
namespaces, and final <w:sectPr> (taken from the original template
so margins/page setup/headers/footers all stay correct).

Why XML and not python-docx?
----------------------------
python-docx silently drops or rewrites custom styles and rarely
round-trips a complex template cleanly. Direct XML editing gives us
exact control. The XML we produce is small and predictable because
all the heavy lifting (styles, theme, numbering) already lives in the
template files we copy.
"""

import argparse
import re
import shutil
import sys
import zipfile
from pathlib import Path


def extract_sectprs(document_xml: str) -> list[str]:
    """Return every <w:sectPr> in the template's document.xml, in
    document order.

    The Euricom v1.1 template has a multi-section structure:
      - sectPr #1 (mid-document, inside a paragraph): ends section 1
        (the cover), with titlePg + pgNumType start=0 + headers/footers
        referencing the cover-specific layout.
      - sectPr #2 (trailing, at end of body): defines section 2
        (the content pages), with footer4 + pgNumType start=1.

    The v1.0 template had only one trailing sectPr. We support both:
    when the body has no cover, the second sectPr alone suffices;
    when the body has a cover, we inject the first sectPr at the
    cover-to-content transition.

    Returns the sectPr blocks as raw XML strings, including the
    <w:sectPr> opening tag and </w:sectPr> closing tag."""
    return re.findall(r"<w:sectPr\b.*?</w:sectPr>", document_xml, re.DOTALL)


# Marker string emitted by cover_page() to indicate where the
# cover-to-content section break should be inserted. Kept as a plain
# string (not XML) so it's easy to grep for and easy to replace.
SECTION_BREAK_MARKER = "<!-- EURICOM_COVER_SECTION_BREAK -->"


def cover_section_break_paragraph(cover_sectpr: str) -> str:
    """Build the paragraph that ends section 1 (cover) and starts
    section 2 (content). The sectPr lives INSIDE a paragraph's pPr —
    that's how Word marks a section break mid-document."""
    return (
        '<w:p>'
        '<w:pPr>'
        f'{cover_sectpr}'
        '</w:pPr>'
        '</w:p>'
    )


def extract_namespaces(document_xml: str) -> str:
    """Pull the namespace attributes from the <w:document ...> opening
    tag so the new document uses the same xmlns declarations as the
    template. This is necessary because the body content may reference
    namespaces like w14: that must be declared on the root element."""
    m = re.search(r"<w:document\b([^>]*?)>", document_xml)
    return m.group(1) if m else ' xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


def build_document_xml(body_xml: str, namespaces: str,
                       sectprs: list[str]) -> str:
    """Assemble a complete document.xml from the body fragment.

    Multi-section logic
    -------------------
    The Euricom v1.1 template defines two sections:
      - Section 1: cover page (titlePg, page-number start = 0).
      - Section 2: content pages (default header + footer4, page-number
        start = 1).

    If the body contains the cover-section-break marker, we inject the
    section-1 sectPr inside a paragraph at that position, and the
    section-2 sectPr at the end. If the body does NOT contain the
    marker (memo-style document with no cover), only the trailing
    section-2 sectPr is used and titlePg is stripped so the regular
    header (with logo) appears from page 1.

    For backwards compatibility with v1.0 templates (one sectPr only),
    we fall back to the single-section path."""
    # Strip wrappers that may have crept in
    body_xml = re.sub(r"<\?xml[^?]*\?>", "", body_xml).strip()
    body_xml = re.sub(r"^<w:body[^>]*>", "", body_xml).strip()
    body_xml = re.sub(r"</w:body>\s*$", "", body_xml).strip()

    has_marker = SECTION_BREAK_MARKER in body_xml

    if len(sectprs) >= 2 and has_marker:
        # v1.1 path: multi-section template + body has a cover.
        # First sectPr ends section 1 (cover), placed at the marker.
        # Second sectPr trails the body (section 2 = content).
        cover_sectpr = sectprs[0]
        content_sectpr = sectprs[-1]
        body_xml = body_xml.replace(
            SECTION_BREAK_MARKER,
            cover_section_break_paragraph(cover_sectpr),
        )
        trailing = content_sectpr
    elif has_marker:
        # v1.0 fallback: only one sectPr available, but body has a
        # marker. Use the single sectPr as the cover-ending one and
        # synthesize a content-section variant (no titlePg, page start
        # = 1) for the trailing position.
        single = sectprs[0] if sectprs else ""
        body_xml = body_xml.replace(
            SECTION_BREAK_MARKER,
            cover_section_break_paragraph(single),
        )
        trailing = _strip_cover_flags(single)
    else:
        # No marker: body has no cover (memo). We use the content-section
        # sectPr (the trailing one in a multi-section template) but
        # graft on any header references from the cover-section sectPr,
        # because the content section may not define its own logo
        # header. Without this, memo-style documents would have no
        # logo at the top of page 1.
        if len(sectprs) >= 2:
            content_sectpr = sectprs[-1]
            cover_sectpr = sectprs[0]
            trailing = _strip_cover_flags(
                _graft_header_references(content_sectpr, cover_sectpr)
            )
        else:
            # v1.0 fallback: only one sectPr → strip cover flags from it
            trailing = _strip_cover_flags(sectprs[0] if sectprs else "")

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f"<w:document{namespaces}>\n"
        "  <w:body>\n"
        f"{body_xml}\n"
        f"    {trailing}\n"
        "  </w:body>\n"
        "</w:document>\n"
    )


def _graft_header_references(target_sectpr: str, source_sectpr: str) -> str:
    """Copy <w:headerReference> elements from source into target.

    Used for the memo-style scenario: the content section may not
    define its own headers (the template assumes you go through a
    cover first), but a memo skips the cover. To keep the logo on
    page 1, we lift the default-type headerReference from the
    cover-section sectPr and prepend it to the content sectPr.

    Idempotent — if target already has header references, they win
    (we only add ones that aren't there yet)."""
    if not target_sectpr or not source_sectpr:
        return target_sectpr
    existing_types = set(re.findall(
        r'<w:headerReference[^/]*w:type="([^"]+)"', target_sectpr
    ))
    refs_to_add = []
    for m in re.finditer(
        r'<w:headerReference[^/]*?/>', source_sectpr
    ):
        ref = m.group(0)
        type_match = re.search(r'w:type="([^"]+)"', ref)
        if type_match and type_match.group(1) not in existing_types:
            # Only "default" headers are useful for a content section
            # without a cover. "first" headers are intentionally empty
            # in the template (designed for the cover), so skipping
            # them is what we want.
            if type_match.group(1) == "default":
                refs_to_add.append(ref)
    if not refs_to_add:
        return target_sectpr
    # Insert just after the opening <w:sectPr ...> tag
    return re.sub(
        r"(<w:sectPr\b[^>]*>)",
        r"\1\n      " + "\n      ".join(refs_to_add),
        target_sectpr,
        count=1,
    )


def _strip_cover_flags(sectpr: str) -> str:
    """Remove cover-specific flags from a sectPr so it behaves like a
    content section. Used in two cases:
      - v1.0 template + no cover: the single sectPr originally had
        titlePg and pgNumType=0 (cover-aware); strip both so page 1
        gets the regular header and is numbered as 1.
      - v1.0 template + cover: the trailing position needs a content-
        style sectPr even though only one was defined in the template.
    """
    if not sectpr:
        return ""
    sectpr = re.sub(r"<w:titlePg\s*/>", "", sectpr)
    sectpr = re.sub(r"<w:titlePg\b[^>]*></w:titlePg>", "", sectpr)
    sectpr = re.sub(r'<w:pgNumType[^/]*w:start="0"[^/]*/>',
                    '<w:pgNumType w:start="1"/>', sectpr)
    return sectpr


def build_docx(template_path: Path, body_xml_path: Path,
               output_path: Path) -> None:
    """Copy the template, replace word/document.xml with the new body,
    and write to output_path as a valid .docx.

    The body is expected to come from ``render_components.body(...)``,
    which inserts a section-break marker after any ``cover_page()``
    call. This script handles the rest:
      - v1.1 templates (multi-section): both sectPr's are placed
        correctly — cover sectPr at the marker, content sectPr at end.
      - v1.0 templates (single-section): the single sectPr is split
        into a cover-style copy at the marker and a content-style copy
        at end.
      - Body with no cover (no marker): the trailing sectPr alone is
        used, with cover-specific flags stripped so page 1 gets the
        regular header and is numbered 1.

    The previous ``with_cover`` parameter is no longer needed —
    presence of the marker in the body XML is now the signal."""
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    if not body_xml_path.exists():
        raise FileNotFoundError(f"Body XML not found: {body_xml_path}")

    body_xml = body_xml_path.read_text(encoding="utf-8")

    with zipfile.ZipFile(template_path) as zin:
        original_doc = zin.read("word/document.xml").decode("utf-8")

    namespaces = extract_namespaces(original_doc)
    sectprs = extract_sectprs(original_doc)
    new_document_xml = build_document_xml(body_xml, namespaces, sectprs)

    # Copy all files from template to output, replacing document.xml.
    # Also fix [Content_Types].xml: a .dotx declares document.xml as
    # a template content type; a .docx must declare it as a document.
    # Without this fix, Word opens the output but warns / refuses to save.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(template_path) as zin:
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.namelist():
                data = zin.read(item)
                if item == "word/document.xml":
                    data = new_document_xml.encode("utf-8")
                elif item == "[Content_Types].xml":
                    text = data.decode("utf-8")
                    # Replace dotx template content type with docx document content type
                    text = text.replace(
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml",
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml",
                    )
                    data = text.encode("utf-8")
                zout.writestr(item, data)

    print(f"Built {output_path} ({output_path.stat().st_size:,} bytes)")


def main() -> int:
    p = argparse.ArgumentParser(description="Build a .docx from the Euricom template")
    p.add_argument("--template", required=True, type=Path,
                   help="Path to Euricom_Generic_Template_v1_0.dotx (or another .dotx/.docx)")
    p.add_argument("--body", required=True, type=Path,
                   help="Path to body.xml — content inside <w:body> without the wrapper")
    p.add_argument("--output", required=True, type=Path,
                   help="Path for the output .docx file")
    args = p.parse_args()

    try:
        build_docx(args.template, args.body, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
