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
        --template path/to/Euricom_Generic_Template.dotx \\
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
from typing import Optional


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


# Marker emitted by cover_page() to signal that the template's
# pre-designed cover should be kept in the output (with the values
# from the directive filled into its content controls).
#
# Form: <!-- EURICOM_COVER_DIRECTIVE:{"title":"…","subtitle":"…","meta":"…"} -->
COVER_DIRECTIVE_PATTERN = re.compile(
    r"<!-- EURICOM_COVER_DIRECTIVE:(\{.*?\}) -->"
)


def _find_top_level_sdt_spans(xml: str) -> list[tuple[int, int, str]]:
    """Return list of (start, end, tag_value) for every top-level
    <w:sdt> in the XML, properly handling nesting. SDTs can be nested
    in OOXML, so naive regex matching is unreliable — we walk the
    open/close events to find true boundaries.
    """
    events = []
    for m in re.finditer(r'<w:sdt>', xml):
        events.append(('open', m.start()))
    for m in re.finditer(r'</w:sdt>', xml):
        events.append(('close', m.start() + len('</w:sdt>')))
    events.sort(key=lambda e: e[1] if e[0] == 'open' else e[1])
    # Re-sort: open events use start position, close use start+len
    # so to sort by position-in-document use start of the marker
    events = []
    for m in re.finditer(r'<w:sdt>', xml):
        events.append(('open', m.start(), m.end()))
    for m in re.finditer(r'</w:sdt>', xml):
        events.append(('close', m.start(), m.end()))
    events.sort(key=lambda e: e[1])

    spans = []
    stack = []
    for kind, pos_start, pos_end in events:
        if kind == 'open':
            stack.append(pos_start)
        else:
            open_pos = stack.pop()
            if not stack:  # only record top-level
                sdt_xml = xml[open_pos:pos_end]
                tag_m = re.search(r'<w:tag w:val="([^"]*)"', sdt_xml[:600])
                tag = tag_m.group(1) if tag_m else ""
                spans.append((open_pos, pos_end, tag))
    return spans


def fill_content_control(xml: str, tag: str, new_text: str) -> str:
    """Replace the visible text inside an SDT (content control) identified
    by its w:tag value. Leaves the SDT structure, properties, alias, and
    paragraph styles intact — only the visible text runs are replaced.

    Strategy:
      1. Locate the top-level SDT with the matching tag.
      2. Within its <w:sdtContent>, find the first <w:t> element.
      3. Replace that <w:t>'s text with new_text.
      4. Remove any additional <w:t> elements in the same sdtContent
         (placeholders that were spread over multiple runs).

    If the tag is not found, returns the XML unchanged.
    """
    spans = _find_top_level_sdt_spans(xml)
    for start, end, found_tag in spans:
        if found_tag != tag:
            continue
        sdt_xml = xml[start:end]

        # Isolate sdtContent
        content_open = sdt_xml.find('<w:sdtContent>')
        content_close = sdt_xml.rfind('</w:sdtContent>')
        if content_open == -1 or content_close == -1:
            return xml  # malformed — leave alone
        content_open_end = content_open + len('<w:sdtContent>')
        content_xml = sdt_xml[content_open_end:content_close]

        # Escape new text for XML
        safe = (new_text.replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;"))

        # Replace first <w:t...>...</w:t> with our new text,
        # then strip all other <w:t> elements.
        first_t = re.search(r'<w:t\b[^>]*>.*?</w:t>', content_xml, re.DOTALL)
        if first_t:
            new_t = f'<w:t xml:space="preserve">{safe}</w:t>'
            content_xml = (content_xml[:first_t.start()] + new_t
                           + content_xml[first_t.end():])
            # Now remove any remaining w:t elements (other than our new one)
            # We use a different replacement string to avoid removing the one
            # we just inserted: rebuild by splitting on our marker.
            sentinel = "<<<KEEP_THIS_W_T>>>"
            content_xml = content_xml.replace(new_t, sentinel, 1)
            content_xml = re.sub(r'<w:t\b[^>]*>.*?</w:t>', '',
                                 content_xml, flags=re.DOTALL)
            content_xml = content_xml.replace(sentinel, new_t, 1)

        # Reassemble
        new_sdt = (sdt_xml[:content_open_end]
                   + content_xml
                   + sdt_xml[content_close:])
        return xml[:start] + new_sdt + xml[end:]

    return xml  # tag not found


def parse_cover_directive(body_xml: str) -> tuple[Optional[dict], str]:
    """Pull the cover directive from the body XML if present.

    Returns (directive_dict or None, body_xml_without_directive).
    """
    import json
    m = COVER_DIRECTIVE_PATTERN.search(body_xml)
    if not m:
        return None, body_xml
    payload = m.group(1).replace("&#45;&#45;", "--")
    try:
        directive = json.loads(payload)
    except json.JSONDecodeError as e:
        print(f"Warning: malformed cover directive ({e}); cover will be omitted",
              file=sys.stderr)
        directive = None
    body_clean = COVER_DIRECTIVE_PATTERN.sub("", body_xml, count=1)
    return directive, body_clean


def extract_namespaces(document_xml: str) -> str:
    """Pull the namespace attributes from the <w:document ...> opening
    tag so the new document uses the same xmlns declarations as the
    template. This is necessary because the body content may reference
    namespaces like w14: that must be declared on the root element."""
    m = re.search(r"<w:document\b([^>]*?)>", document_xml)
    return m.group(1) if m else ' xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'


def _extract_cover_block(template_doc_xml: str) -> tuple[str, str]:
    """Split the template's document.xml into (cover_block, rest_block).

    cover_block: everything from <w:body> opening (exclusive) up to and
                 including the first inline section break paragraph
                 (the paragraph that contains the cover's <w:sectPr>).
    rest_block:  everything after that, up to but excluding </w:body>
                 and any trailing sectPr.

    The trailing sectPr (the one directly under <w:body>) is NOT part
    of rest_block — it's handled separately as the content-section
    sectPr.

    Returns ("", body_without_trailing_sectpr) if no inline section
    break is found (e.g. v1.0 single-section template).
    """
    body_open = template_doc_xml.find("<w:body>")
    body_close = template_doc_xml.rfind("</w:body>")
    body_inner = template_doc_xml[body_open + len("<w:body>"):body_close]

    # Strip the trailing sectPr (the one not enclosed in a paragraph;
    # it sits directly under <w:body>). Use a pattern that excludes
    # the closing </w:sectPr> from the inner content to ensure we
    # match only the LAST sectPr in body_inner, not the first one
    # consuming everything up to the end.
    trailing_sectpr_match = re.search(
        r"<w:sectPr\b(?:(?!</w:sectPr>).)*?</w:sectPr>\s*$",
        body_inner,
        re.DOTALL,
    )
    if trailing_sectpr_match:
        body_inner = body_inner[:trailing_sectpr_match.start()]

    # Find the first sectPr remaining — this should be the inline one
    # (inside a paragraph's pPr), which marks the end of the cover.
    inline_sectpr = re.search(
        r"<w:sectPr\b[^>]*>.*?</w:sectPr>",
        body_inner,
        re.DOTALL,
    )
    if not inline_sectpr:
        # No inline section break: this is a single-section template
        # (v1.0 style) with no separate cover. Treat whole body as
        # "rest" and signal no cover block by returning empty.
        return "", body_inner

    # Walk back from the sectPr to find the enclosing <w:p ...> opener.
    # Look for both attributed (<w:p ...>) and bare (<w:p>) forms.
    p_open_attrs = body_inner.rfind("<w:p ", 0, inline_sectpr.start())
    p_open_bare = body_inner.rfind("<w:p>", 0, inline_sectpr.start())
    p_open = max(p_open_attrs, p_open_bare)
    if p_open == -1:
        # Defensive: sectPr not inside a paragraph — shouldn't happen
        # since we stripped the trailing one, but just in case.
        return "", body_inner

    # Walk forward from the sectPr to find the matching </w:p>.
    p_close = body_inner.find("</w:p>", inline_sectpr.end())
    if p_close == -1:
        return "", body_inner
    p_close_end = p_close + len("</w:p>")

    cover_block = body_inner[:p_close_end]
    rest_block = body_inner[p_close_end:]
    return cover_block, rest_block


def build_document_xml(body_xml: str, namespaces: str,
                       sectprs: list[str],
                       template_doc_xml: str) -> str:
    """Assemble a complete document.xml from the generated body fragment.

    Cover handling (template v1.2+)
    -------------------------------
    The template ships with a designed cover page that contains content
    controls for the title, subtitle, and meta line. The skill does NOT
    rebuild the cover — instead:

      - If the body contains a EURICOM_COVER_DIRECTIVE marker (emitted
        by render_components.cover_page()), the template's cover block
        is prepended to the generated body, with the content controls
        filled in from the directive's values. Result: the output
        cover is visually identical to what a human user would produce
        by manually editing the .dotx.

      - If no directive is present, the cover is omitted entirely. The
        document starts with the generated body content directly. The
        trailing content-section sectPr is used (no separate cover
        section).

    Section breaks
    --------------
    When a cover is present, the cover block from the template
    already contains the inline section break (the boundary between
    cover and content). We just need to append the trailing content
    sectPr at the end of the body.

    When no cover is present, we strip cover-specific flags
    (titlePg, pgNumType=0) from the trailing sectPr so page 1 gets
    the regular header and numbering.
    """
    # Strip wrappers that may have crept in
    body_xml = re.sub(r"<\?xml[^?]*\?>", "", body_xml).strip()
    body_xml = re.sub(r"^<w:body[^>]*>", "", body_xml).strip()
    body_xml = re.sub(r"</w:body>\s*$", "", body_xml).strip()

    # Parse cover directive (if any)
    directive, body_xml = parse_cover_directive(body_xml)

    # Determine the trailing sectPr (always present)
    if len(sectprs) >= 2:
        content_sectpr = sectprs[-1]
    elif sectprs:
        content_sectpr = sectprs[0]
    else:
        content_sectpr = ""

    if directive is not None:
        # Cover present: extract template's cover block, fill in SDTs.
        cover_block, _ = _extract_cover_block(template_doc_xml)

        # Fill the four content controls
        cover_block = fill_content_control(cover_block, "covertitle",
                                           directive.get("title", ""))
        cover_block = fill_content_control(cover_block, "coversubtitle",
                                           directive.get("subtitle", ""))
        cover_block = fill_content_control(cover_block, "covermeta",
                                           directive.get("meta", ""))

        # The documenttitle SDT lives in the rest of the document
        # (page 3 area). Fill it in the body_xml too — but only if
        # the body_xml is empty / minimal. In practice the body_xml
        # is fully Claude-generated and won't contain a documenttitle
        # SDT. The documenttitle in the template's rest block is
        # therefore irrelevant for generated content. Skipping it.

        # Trailing: use content sectPr as-is (cover block has its own
        # inline section break already)
        trailing = content_sectpr

        assembled_body = f"{cover_block}\n{body_xml}"
    else:
        # No cover: skip the template's cover block entirely.
        # Strip cover flags from the trailing sectPr so page 1 gets
        # the regular header / numbering.
        if len(sectprs) >= 2:
            cover_sectpr = sectprs[0]
            trailing = _strip_cover_flags(
                _graft_header_references(content_sectpr, cover_sectpr)
            )
        else:
            trailing = _strip_cover_flags(content_sectpr)

        assembled_body = body_xml

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f"<w:document{namespaces}>\n"
        "  <w:body>\n"
        f"{assembled_body}\n"
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
    new_document_xml = build_document_xml(body_xml, namespaces, sectprs,
                                          template_doc_xml=original_doc)

    # Copy all files from template to output, replacing document.xml.
    # Three additional fixes happen here:
    #
    #   1. [Content_Types].xml — a .dotx declares document.xml as a
    #      template content type; a .docx must declare it as a document.
    #      Without this fix, Word opens the output but warns / refuses
    #      to save.
    #
    #   2. docProps/app.xml — the .dotx carries a <Template> element
    #      pointing to itself (e.g. "Euricom_Generic_Template.dotx").
    #      If we leave that intact, Word on iPhone/iOS (and sometimes on
    #      Mac) shows a "this document is linked to another file" warning
    #      every time the file is opened. We blank out that field so the
    #      output document looks like a self-contained .docx.
    #
    #   3. word/settings.xml — two changes:
    #      a) Defensively strip any <w:attachedTemplate> element. The
    #         Euricom template doesn't currently include one, but
    #         if a future revision does, it would re-introduce
    #         the same link warning.
    #      b) Add <w:updateFields w:val="false"/> so Word doesn't show
    #         the "fields may refer to other files. Update?" dialog
    #         every time the document opens. Without this, users tend
    #         to click "No" (the wording reads as a security warning)
    #         and end up with the TOC placeholder text instead of an
    #         actual TOC. The TOC placeholder we generate tells the
    #         user how to populate it manually (right-click → F9).
    #
    # Together these make the output behave like a freshly-created Word
    # document on every platform, including iOS where the warning is
    # most visible.
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
                elif item == "docProps/app.xml":
                    text = data.decode("utf-8")
                    # Empty the <Template>...</Template> element so Word
                    # doesn't treat the .docx as linked to the .dotx.
                    # We deliberately keep the element present (just empty)
                    # because some Office versions complain about missing
                    # standard properties; an empty value is universally safe.
                    text = re.sub(
                        r"<Template>[^<]*</Template>",
                        "<Template></Template>",
                        text,
                    )
                    data = text.encode("utf-8")
                elif item == "word/settings.xml":
                    text = data.decode("utf-8")
                    # Strip any <w:attachedTemplate .../> reference.
                    # Matches both self-closing and paired forms.
                    text = re.sub(
                        r"<w:attachedTemplate\b[^/]*/>",
                        "",
                        text,
                    )
                    text = re.sub(
                        r"<w:attachedTemplate\b[^>]*>.*?</w:attachedTemplate>",
                        "",
                        text,
                        flags=re.DOTALL,
                    )
                    # Add <w:updateFields w:val="false"/> so Word does NOT
                    # show the "this document contains fields that may
                    # refer to other files. Update?" dialog every time
                    # the document opens.
                    #
                    # Why this dialog appears in our docs: the TOC field
                    # is dynamic and Word defensively asks whether to
                    # refresh it on open. Many users read the wording
                    # as a security warning and click "No", leaving them
                    # with the placeholder text instead of a real TOC.
                    #
                    # With updateFields=false:
                    #   - No dialog on open (good UX).
                    #   - The TOC stays as placeholder until the user
                    #     right-clicks → "Update Field" (or F9). The
                    #     placeholder text we emit from toc() explicitly
                    #     instructs the user to do this.
                    #   - Same workflow continues to work after the user
                    #     adds/edits chapters: right-click + F9 updates.
                    #     This matches the "human in the loop" model:
                    #     the skill provides a starting point; the user
                    #     finalises.
                    #
                    # If <w:updateFields> already exists in settings,
                    # replace its value. Otherwise insert one right
                    # after the <w:settings ...> opening tag.
                    if re.search(r"<w:updateFields\b", text):
                        text = re.sub(
                            r'<w:updateFields\s+w:val="[^"]*"\s*/>',
                            '<w:updateFields w:val="false"/>',
                            text,
                        )
                    else:
                        text = re.sub(
                            r"(<w:settings\b[^>]*>)",
                            r'\1<w:updateFields w:val="false"/>',
                            text,
                            count=1,
                        )
                    data = text.encode("utf-8")
                zout.writestr(item, data)

    print(f"Built {output_path} ({output_path.stat().st_size:,} bytes)")


def main() -> int:
    p = argparse.ArgumentParser(description="Build a .docx from the Euricom template")
    p.add_argument("--template", required=True, type=Path,
                   help="Path to Euricom_Generic_Template.dotx (or another .dotx/.docx)")
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
