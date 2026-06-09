#!/usr/bin/env python3
"""
render_components.py
====================

Python helpers that produce the exact WordprocessingML XML snippets
the Euricom template expects.

Why a renderer library instead of an XML template engine?
---------------------------------------------------------
The note callouts and quote blocks use very specific structures
(two-column tables, exact hex colors, exact cell widths) that are
both verbose and easy to mistype. Centralising them here means the
caller writes::

    note("Tip", "Twijfel je over de stijl? Clear eerst de opmaak.")

and gets back the correct ~80 lines of XML, every time.

All functions return strings. Compose them and write the result to
the body.xml file consumed by build_from_template.py.

Escaping
--------
All visible text is escaped via ``escape_text``: ``&``, ``<``, ``>``,
and ``"`` are converted to entities, and straight quotes/apostrophes
are upgraded to smart quotes (Belgian-Dutch professional typography
expects ``&#x201C;…&#x201D;`` for double quotes and ``&#x2019;`` for
apostrophes). If you have text that should NOT be smart-quoted (code,
URLs), pass ``smart=False``.

**Always pass plain UTF-8 text into the helpers.** Do NOT pre-encode
characters as XML entities (``&#x201C;``) or Python escapes
(``\u201C``) in your input strings — the helpers do that conversion
themselves. Pre-encoded input gets double-escaped: ``&#x201C;`` in
your input becomes ``&amp;#x201C;`` in the output, which Word renders
as the literal text ``&#x201C;`` rather than a smart quote. Write
``"quoted phrase"``, ``Keenan's book``, ``café`` — not their entity
equivalents. The validator catches this mistake on the output, but
catching it at the source is faster.
"""

from __future__ import annotations

import re
from typing import Iterable, List, Optional, Sequence, Tuple


# --------------------------------------------------------------------------- #
# Text escaping
# --------------------------------------------------------------------------- #

def escape_text(text: str, smart: bool = True) -> str:
    """Escape XML special characters. Optionally convert straight quotes
    to typographic (curly) quotes — the Euricom template uses smart
    quotes throughout its examples."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if smart:
        # Apostrophe (always curly right single quote)
        text = text.replace("'", "&#x2019;")
        # Double quotes: alternate open/close. Simpler heuristic: opening
        # quote after whitespace or start of string, closing otherwise.
        out = []
        in_quote = False
        for ch in text:
            if ch == '"':
                out.append("&#x201D;" if in_quote else "&#x201C;")
                in_quote = not in_quote
            else:
                out.append(ch)
        text = "".join(out)
    else:
        text = text.replace('"', "&quot;").replace("'", "&apos;")
    return text


# --------------------------------------------------------------------------- #
# Basic paragraph builders
# --------------------------------------------------------------------------- #

def paragraph(text: str = "", style: Optional[str] = None,
              bold: bool = False, italic: bool = False) -> str:
    """A paragraph with optional style and inline formatting.
    Empty text = empty paragraph (use sparingly; the template's styles
    already handle spacing, so blank paragraphs are usually unneeded)."""
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    if not text:
        return f"<w:p>{style_xml}</w:p>"
    run_props = []
    if bold:
        run_props.append("<w:b/>")
    if italic:
        run_props.append("<w:i/>")
    rpr = f"<w:rPr>{''.join(run_props)}</w:rPr>" if run_props else ""
    return (
        f"<w:p>{style_xml}"
        f"<w:r>{rpr}<w:t xml:space=\"preserve\">{escape_text(text)}</w:t></w:r>"
        "</w:p>"
    )


def heading(text: str, level: int = 1) -> str:
    """Heading 1-3. Levels 1-3 are the only ones the template encourages;
    higher levels exist but make documents harder to scan."""
    if not 1 <= level <= 3:
        raise ValueError(f"Heading level must be 1, 2, or 3 (got {level})")
    return paragraph(text, style=f"Heading{level}")


def title(text: str) -> str:
    """Document title — the big ``Title``-styled heading at the top of
    the content (page 3 of a cover+TOC document, page 1 of a cover-less
    memo).

    Unlike earlier versions, this does NOT emit a plain ``Title``
    paragraph. It emits a directive that ``build_from_template.py``
    turns into the template's real ``documenttitle`` **content control**
    (an SDT with the ``Title`` style inside), placed at exactly this
    position in the body. Call it where the title should appear: right
    after ``toc(...)`` in a cover document, or at the very top in a
    cover-less memo.

    Relationship to the cover title
    -------------------------------
    The template has two separate title content controls:

    - ``covertitle`` — on the cover page, filled from ``cover_page(...)``.
    - ``documenttitle`` — the one this helper produces.

    They are independent fields: editing one in Word does NOT change the
    other (they are not linked). Their *content* should normally match,
    so in a cover document pass the same string you passed to
    ``cover_page(title=...)``.

    Robustness
    ----------
    In a cover document you may omit ``title()`` entirely — the build
    script then fills the ``documenttitle`` control automatically from
    the cover title, so the DocumentTitle is never left empty. If you do
    call ``title()``, your text wins and it is placed exactly where you
    put the call.
    """
    import json
    payload = json.dumps({"title": text}, ensure_ascii=False)
    # Encode -- so it can't appear inside an XML comment (forbidden).
    safe = payload.replace("--", "&#45;&#45;")
    return f"<!-- EURICOM_DOCTITLE_DIRECTIVE:{safe} -->"


def h1_intro(text: str) -> str:
    """The 'H1 Intro' style: italicised lead paragraph under an H1.
    Use sparingly — only when it adds genuine context."""
    return paragraph(text, style="H1Intro")


def bullet(text: str, level: int = 1) -> str:
    """Bullet at level 1 or 2. The template's Bullet1/Bullet2 styles
    handle indentation and the bullet glyph via numbering.

    For bullets that need inline formatting (e.g. inline code), use
    ``bullet_rich(...)`` instead."""
    if level not in (1, 2):
        raise ValueError(f"Bullet level must be 1 or 2 (got {level})")
    return paragraph(text, style=f"Bullet{level}")


def rich_paragraph(runs: Sequence[Tuple[str, dict]], style: Optional[str] = None) -> str:
    """Paragraph with multiple runs of different formatting.

    Each run is a (text, props) tuple. Recognised props keys:

    - ``bold``: bool — apply ``<w:b/>``
    - ``italic``: bool — apply ``<w:i/>``
    - ``color``: hex string without ``#`` (e.g. ``"014046"``)
    - ``size``: half-points (e.g. 20 = 10pt)
    - ``rstyle``: character style ID (e.g. ``"InlineCodeChar"``) — applied
      via ``<w:rStyle w:val="..."/>``. Most useful for inline code, but
      works for any character style defined in the template.

    Combine ``rstyle`` with the others if you want to override individual
    properties on top of the character style; usually you should not need
    to. For inline code in particular, prefer ``inline_code(text)`` over
    constructing the run dict by hand."""
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    runs_xml = []
    for text, props in runs:
        rpr_items = []
        if "rstyle" in props:
            rpr_items.append(f'<w:rStyle w:val="{props["rstyle"]}"/>')
        if props.get("bold"):
            rpr_items.append("<w:b/>")
        if props.get("italic"):
            rpr_items.append("<w:i/>")
        if "color" in props:
            rpr_items.append(f'<w:color w:val="{props["color"]}"/>')
        if "size" in props:
            rpr_items.append(f'<w:sz w:val="{props["size"]}"/>')
        rpr = f"<w:rPr>{''.join(rpr_items)}</w:rPr>" if rpr_items else ""
        runs_xml.append(
            f'<w:r>{rpr}<w:t xml:space="preserve">{escape_text(text)}</w:t></w:r>'
        )
    return f"<w:p>{style_xml}{''.join(runs_xml)}</w:p>"


def inline_code(text: str) -> Tuple[str, dict]:
    """Produce a run-tuple for inline code, using the template's
    ``InlineCodeChar`` character style (Aptos Mono, dark teal, light teal
    background, 11pt).

    This returns a ``(text, props)`` tuple meant to be embedded in a
    ``rich_paragraph(...)`` or ``bullet_rich(...)`` call alongside plain
    text tuples. Example::

        rich_paragraph([
            ("Open the path ", {}),
            inline_code("%APPDATA%\\\\Microsoft\\\\Word\\\\STARTUP"),
            (" in Explorer.", {}),
        ])

    Apply to file paths, filenames, environment variables, commands,
    keyboard shortcuts, and short menu items the reader must recognise
    in a UI. Use sparingly — five code fragments in one paragraph reads
    as noise. See SKILL.md for the full guideline."""
    return (text, {"rstyle": "InlineCodeChar"})


def bullet_rich(runs: Sequence[Tuple[str, dict]], level: int = 1) -> str:
    """Bullet paragraph (Bullet1/Bullet2) with mixed-formatting runs
    inside. The standard ``bullet(text)`` only accepts plain text; when
    you need a bullet that contains an ``inline_code(...)`` run or other
    formatting, use this instead. Example::

        bullet_rich([
            ("Bestandsnamen — ", {}),
            inline_code("Euricom_Generic_Template.dotx"),
            (".", {}),
        ])
    """
    if level not in (1, 2):
        raise ValueError(f"Bullet level must be 1 or 2 (got {level})")
    return rich_paragraph(runs, style=f"Bullet{level}")



# --------------------------------------------------------------------------- #
# Page break
# --------------------------------------------------------------------------- #

def page_break() -> str:
    """Hard page break — wraps the break in a paragraph as required
    by the spec (a standalone break is invalid).

    **Page-break philosophy in the Euricom template (v1.4+):**

    The Heading1 style does NOT auto-break to a new page. This is
    deliberate: documents have varying density, and forcing a page
    break before every chapter often produces ugly half-empty pages.
    The author is the only one who knows where a break genuinely
    improves readability.

    **Rules for the skill:**

    - The skill emits at most ONE automatic page break: the one
      immediately after the TOC (see `toc()`). This mirrors the
      manual template's design where the first chapter starts on
      a fresh page after the TOC.
    - Anywhere else, the skill does NOT insert page breaks
      proactively. Do not call `page_break()` between chapters
      "for safety" — let the natural flow happen.
    - If you (the human author reviewing a generated document) want
      a break at a specific spot, insert it manually in Word, or
      ask the skill to insert one at a named location.

    **When `page_break()` IS appropriate to call from code:**

    - Forcing a break before an oversized table that would
      otherwise split awkwardly across pages
    - Isolating a full-page quote or image
    - Separating clearly distinct sections of a long document where
      the author has explicitly asked for it

    These are exceptions, not defaults."""
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


# --------------------------------------------------------------------------- #
# Note callouts (Tip / Alarm / Waarschuwing / Info)
# --------------------------------------------------------------------------- #

# Exact colors extracted from the template. Strip = the thin left
# coloured bar; bg = the filled note body; title_color = the bold
# title text. Keys are the exact note labels rendered to the reader.
NOTE_STYLES = {
    "Tip":           {"strip": "00FF00", "bg": "F1F5F6", "title_color": "014046"},
    "Alarm":         {"strip": "E80F0F", "bg": "FEF0F0", "title_color": "E80F0F"},
    "Waarschuwing":  {"strip": "E9AB0C", "bg": "FEF9EC", "title_color": "E9AB0C"},
    "Info":          {"strip": "5C7B7E", "bg": "F1F5F6", "title_color": "014046"},
}


def note(kind: str, body: str, title: Optional[str] = None) -> str:
    """Render a callout. `kind` ∈ {Tip, Alarm, Waarschuwing, Info}.
    `title` defaults to `kind` (so a Tip is titled "Tip"); override
    for cases like 'Geen tekstuele suffixen' (a 'Waarschuwing'-styled
    note with a more descriptive title).

    Returns a 2-column borderless table that matches the template's
    Quick Part exactly."""
    if kind not in NOTE_STYLES:
        raise ValueError(
            f"Unknown note kind {kind!r}. "
            f"Must be one of: {', '.join(NOTE_STYLES)}"
        )
    s = NOTE_STYLES[kind]
    display_title = title if title is not None else kind

    return f'''<w:tbl>
  <w:tblPr>
    <w:tblW w:w="8956" w:type="dxa"/>
    <w:tblBorders>
      <w:top w:val="single" w:sz="4" w:space="0" w:color="auto"/>
      <w:left w:val="single" w:sz="4" w:space="0" w:color="auto"/>
      <w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/>
      <w:right w:val="single" w:sz="4" w:space="0" w:color="auto"/>
      <w:insideH w:val="single" w:sz="4" w:space="0" w:color="auto"/>
      <w:insideV w:val="single" w:sz="4" w:space="0" w:color="auto"/>
    </w:tblBorders>
    <w:tblCellMar><w:left w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar>
    <w:tblLook w:val="04A0"/>
  </w:tblPr>
  <w:tblGrid><w:gridCol w:w="125"/><w:gridCol w:w="8831"/></w:tblGrid>
  <w:tr>
    <w:tc>
      <w:tcPr>
        <w:tcW w:w="125" w:type="dxa"/>
        <w:tcBorders>
          <w:top w:val="none" w:sz="0" w:space="0" w:color="FFFFFF"/>
          <w:left w:val="none" w:sz="0" w:space="0" w:color="FFFFFF"/>
          <w:bottom w:val="none" w:sz="0" w:space="0" w:color="FFFFFF"/>
          <w:right w:val="none" w:sz="0" w:space="0" w:color="FFFFFF"/>
        </w:tcBorders>
        <w:shd w:val="clear" w:color="auto" w:fill="{s['strip']}"/>
        <w:tcMar><w:top w:w="0" w:type="dxa"/><w:left w:w="0" w:type="dxa"/><w:bottom w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tcMar>
      </w:tcPr>
      <w:p/>
    </w:tc>
    <w:tc>
      <w:tcPr>
        <w:tcW w:w="8831" w:type="dxa"/>
        <w:tcBorders>
          <w:top w:val="none" w:sz="0" w:space="0" w:color="FFFFFF"/>
          <w:left w:val="none" w:sz="0" w:space="0" w:color="FFFFFF"/>
          <w:bottom w:val="none" w:sz="0" w:space="0" w:color="FFFFFF"/>
          <w:right w:val="none" w:sz="0" w:space="0" w:color="FFFFFF"/>
        </w:tcBorders>
        <w:shd w:val="clear" w:color="auto" w:fill="{s['bg']}"/>
        <w:tcMar><w:top w:w="85" w:type="dxa"/><w:left w:w="113" w:type="dxa"/><w:bottom w:w="85" w:type="dxa"/><w:right w:w="113" w:type="dxa"/></w:tcMar>
      </w:tcPr>
      <w:p>
        <w:r>
          <w:rPr><w:b/><w:bCs/><w:color w:val="{s['title_color']}"/><w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr>
          <w:t xml:space="preserve">{escape_text(display_title)}</w:t>
        </w:r>
      </w:p>
      <w:p>
        <w:pPr><w:spacing w:line="264" w:lineRule="auto"/></w:pPr>
        <w:r>
          <w:rPr><w:color w:val="1D252D" w:themeColor="text1"/><w:szCs w:val="22"/></w:rPr>
          <w:t xml:space="preserve">{escape_text(body)}</w:t>
        </w:r>
      </w:p>
    </w:tc>
  </w:tr>
</w:tbl>
<w:p/>'''


# --------------------------------------------------------------------------- #
# Quote block
# --------------------------------------------------------------------------- #

def quote(text: str, author: Optional[str] = None, role: Optional[str] = None) -> str:
    """A Euricom-style quote: italic body with a thick steel-gray left
    border, optionally followed by bold author + italic role.

    The quotation marks (&#x201C; / &#x201D;) are added automatically
    around the body, matching the template example."""
    body_text = escape_text(text)
    # Add curly quotes around the body if not already present
    if not body_text.startswith("&#x201C;"):
        body_text = f"&#x201C;{body_text}&#x201D;"

    attribution_row = ""
    if author:
        author_x = escape_text(author)
        if role:
            role_x = escape_text(role)
            attribution = (
                f'<w:r><w:rPr><w:b/><w:bCs/><w:color w:val="1D252D" w:themeColor="text1"/>'
                f'<w:sz w:val="20"/><w:szCs w:val="22"/></w:rPr>'
                f'<w:t xml:space="preserve">{author_x}</w:t></w:r>'
                f'<w:r><w:rPr><w:color w:val="1D252D" w:themeColor="text1"/>'
                f'<w:sz w:val="20"/></w:rPr><w:t xml:space="preserve"> </w:t></w:r>'
                f'<w:r><w:rPr><w:i/><w:iCs/><w:color w:val="1D252D" w:themeColor="text1"/>'
                f'<w:sz w:val="20"/></w:rPr>'
                f'<w:t xml:space="preserve">&#x2013; {role_x}</w:t></w:r>'
            )
        else:
            attribution = (
                f'<w:r><w:rPr><w:b/><w:bCs/><w:color w:val="1D252D" w:themeColor="text1"/>'
                f'<w:sz w:val="20"/></w:rPr>'
                f'<w:t xml:space="preserve">{author_x}</w:t></w:r>'
            )
        attribution_row = f'''
  <w:tr>
    <w:tc>
      <w:tcPr><w:tcW w:w="8933" w:type="dxa"/></w:tcPr>
      <w:p><w:pPr><w:spacing w:before="120"/></w:pPr>{attribution}</w:p>
    </w:tc>
  </w:tr>'''

    return f'''<w:tbl>
  <w:tblPr>
    <w:tblStyle w:val="TableGrid"/>
    <w:tblW w:w="8933" w:type="dxa"/>
    <w:tblBorders>
      <w:top w:val="none" w:sz="0" w:space="0" w:color="auto"/>
      <w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>
      <w:bottom w:val="none" w:sz="0" w:space="0" w:color="auto"/>
      <w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>
      <w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/>
      <w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>
    </w:tblBorders>
    <w:tblCellMar><w:left w:w="170" w:type="dxa"/><w:right w:w="142" w:type="dxa"/></w:tblCellMar>
    <w:tblLook w:val="04A0"/>
  </w:tblPr>
  <w:tblGrid><w:gridCol w:w="8933"/></w:tblGrid>
  <w:tr>
    <w:tc>
      <w:tcPr>
        <w:tcW w:w="8933" w:type="dxa"/>
        <w:tcBorders>
          <w:left w:val="single" w:sz="24" w:space="0" w:color="CBD9DA" w:themeColor="accent4"/>
        </w:tcBorders>
      </w:tcPr>
      <w:p>
        <w:pPr><w:spacing w:after="0" w:line="360" w:lineRule="exact"/></w:pPr>
        <w:r>
          <w:rPr><w:i/><w:iCs/><w:color w:val="1D252D" w:themeColor="text1"/><w:sz w:val="24"/></w:rPr>
          <w:t xml:space="preserve">{body_text}</w:t>
        </w:r>
      </w:p>
    </w:tc>
  </w:tr>{attribution_row}
</w:tbl>
<w:p/>'''


# --------------------------------------------------------------------------- #
# Tables (general purpose)
# --------------------------------------------------------------------------- #

def table(headers: Sequence[str], rows: Sequence[Sequence[str]],
          col_widths: Optional[Sequence[int]] = None,
          last_row_is_total: bool = False) -> str:
    """A Euricom-branded data table.

    Uses the template's ``EuricomDataTable`` style, which means:
    - The template — not this helper — controls borders (DCE5E6, 2pt),
      header fill (Midnight #014046 with white bold text), zebra
      striping on body rows (#F1F5F6 on alternating rows), and last-row
      emphasis (bold with #D3E0E3 fill, intended for totals).
    - This keeps tables consistent with every other Euricom document
      regardless of who builds them and follows the template's own
      rule: prefer styles over manual formatting.

    Parameters
    ----------
    headers
        Header row labels. Become the first row, styled by the template
        via ``firstRow`` (bold white on dark Midnight).
    rows
        Body rows. Each must have the same length as ``headers``.
    col_widths
        Per-column widths in DXA (1440 = 1 inch). If omitted, columns
        are split evenly across 8956 DXA. **Minimum 1000 DXA for short
        columns** (counters, single-word headers); below that, Word
        breaks bold header text across two lines.
    last_row_is_total
        Set ``True`` when the last row is a total / summary that should
        be visually distinct (bold, light background). The template's
        ``lastRow`` style does this automatically once we enable the
        ``lastRow`` flag in ``tblLook``.

    Note on banding
    ---------------
    Row banding (zebra striping) is **on by default** in the template
    style. If you ever need to disable it for a specific table (e.g.
    a tiny 2-row reference table where stripes look fussy), the call
    site needs custom XML — we don't expose that here because we have
    yet to see a real Euricom case for it.
    """
    if not headers:
        raise ValueError("Table needs at least a header row")
    n_cols = len(headers)
    for i, r in enumerate(rows):
        if len(r) != n_cols:
            raise ValueError(
                f"Row {i} has {len(r)} cells but headers have {n_cols}"
            )

    total_width = 8956
    if col_widths is None:
        base = total_width // n_cols
        col_widths = [base] * (n_cols - 1) + [total_width - base * (n_cols - 1)]
    else:
        if len(col_widths) != n_cols:
            raise ValueError("col_widths must match number of headers")
        total_width = sum(col_widths)

    def cell(text: str, width: int, is_total_row: bool = False) -> str:
        # Body cells delegate all styling to the table style. The total
        # row gets bold + a light accent fill INLINE in addition to the
        # tblStylePr lastRow rule, because some renderers (LibreOffice,
        # certain Word-on-the-web versions) don't fully implement the
        # lastRow conditional. Word desktop handles both paths and
        # they're idempotent — no double application.
        if is_total_row:
            shading = '<w:shd w:val="clear" w:color="auto" w:fill="D3E0E3"/>'
            run_props = '<w:rPr><w:b/><w:bCs/></w:rPr>'
        else:
            shading = ""
            run_props = ""
        return (
            f'<w:tc>'
            f'<w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>{shading}</w:tcPr>'
            f'<w:p><w:r>{run_props}<w:t xml:space="preserve">{escape_text(text)}</w:t></w:r></w:p>'
            f'</w:tc>'
        )

    def row(values: Sequence[str], is_total_row: bool = False) -> str:
        cells = "".join(cell(v, w, is_total_row) for v, w in zip(values, col_widths))
        return f"<w:tr>{cells}</w:tr>"

    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in col_widths)

    # Build the header row separately so we can flag it as repeating.
    # When a table breaks across pages, Word and LibreOffice both
    # check for <w:tblHeader/> in the row properties to know whether
    # to repeat the row as a header on each new page. Without this,
    # the visual header appears only on the first page — but some
    # renderers leave an empty row at the top of subsequent pages
    # where the header "would" be, which looks like a bug.
    header_cells = "".join(cell(v, w, is_total_row=False)
                           for v, w in zip(headers, col_widths))
    header_row = f'<w:tr><w:trPr><w:tblHeader/></w:trPr>{header_cells}</w:tr>'

    # Body rows. The last row is optionally the totals row.
    body_rows = []
    for i, r in enumerate(rows):
        is_last = last_row_is_total and (i == len(rows) - 1)
        body_rows.append(row(r, is_total_row=is_last))
    rows_xml = header_row + "".join(body_rows)

    # tblLook flags tell Word which conditional formats from the table
    # style to apply:
    #   firstRow="1"       → apply header styling to row 1 (Midnight + white bold)
    #   lastRow="1"        → apply lastRow styling (bold + light fill) — for totals
    #   firstColumn="0"    → no special first-column treatment
    #   lastColumn="0"     → no special last-column treatment
    #   noHBand="0"        → enable horizontal banding (zebra stripes)
    #   noVBand="1"        → disable vertical banding
    # The "04A0" hex value is the bitmask Word uses for "firstRow + noVBand";
    # we override it conditionally for the totals case ("06A0" adds lastRow).
    last_row_flag = 'w:lastRow="1"' if last_row_is_total else 'w:lastRow="0"'
    look_hex = "06A0" if last_row_is_total else "04A0"

    return f'''<w:tbl>
  <w:tblPr>
    <w:tblStyle w:val="EuricomDataTable"/>
    <w:tblW w:w="{total_width}" w:type="dxa"/>
    <w:tblLook w:val="{look_hex}" w:firstRow="1" {last_row_flag} w:firstColumn="0" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/>
  </w:tblPr>
  <w:tblGrid>{grid}</w:tblGrid>
  {rows_xml}
</w:tbl>
<w:p/>'''


# --------------------------------------------------------------------------- #
# Cover page
# --------------------------------------------------------------------------- #

def cover_page(title: str, subtitle: Optional[str] = None,
               meta: Optional[str] = None) -> str:
    """Signal to the build script that the document should keep the
    template's cover page, with the three content controls filled in.

    Starting from template v1.3, the cover is not built from scratch
    by this helper. Instead, the template ships with a pre-designed
    cover containing three content controls (tags: ``covertitle``,
    ``coversubtitle``, ``covermeta``) plus a fourth control
    ``documenttitle`` on page 3. The build script
    (``build_from_template.py``) finds those controls and replaces
    their inner text with the values passed here.

    This matches how human users work with the template: they open
    the .dotx, click on the cover placeholders, and type. The skill
    does exactly the same — only programmatically. Result: documents
    generated by the skill look identical to documents created
    manually from the template.

    To OMIT the cover entirely (no cover page in the output), simply
    do not call this function. The build script will then strip the
    entire cover section from the template, leaving content to start
    on page 1.

    Parameters
    ----------
    title : str
        Replaces both the covertitle (on the cover) and the
        documenttitle (on page 3) controls with this value.
    subtitle : str, optional
        Replaces the coversubtitle control. If omitted, the control
        is left empty.
    meta : str, optional
        Replaces the covermeta control. Always rendered uppercase
        per Euricom convention. If omitted, the control is left empty.
    """
    # Embed the values as a hidden directive that the build script
    # parses out. Each value is JSON-encoded to survive any XML-special
    # characters cleanly. The marker is a comment so it's invisible in
    # any intermediate processing and easy to grep for.
    import json
    payload = json.dumps({
        "title": title,
        "subtitle": subtitle or "",
        "meta": (meta or "").upper(),
    }, ensure_ascii=False)
    # Encode to avoid -- inside the comment (XML forbids it).
    safe = payload.replace("--", "&#45;&#45;")
    return f"<!-- EURICOM_COVER_DIRECTIVE:{safe} -->"


# --------------------------------------------------------------------------- #
# Table of contents
# --------------------------------------------------------------------------- #

def toc(title: str = "Inhoud", levels: int = 2,
        entries: Optional[Sequence[str]] = None) -> str:
    """Insert a table-of-contents field. Word builds the actual entries
    on first open; until then a placeholder shows.

    `levels` controls TOC depth (template recommends 2 by default,
    3 for technical documents). `title` is the heading above the TOC.

    `entries` is an optional list of H1 chapter titles. When provided,
    each title is pre-rendered as a TOC1 paragraph inside the field's
    result region. This gives readers something to see immediately
    (useful in iOS Quick Look, Pages, or any viewer that doesn't auto-
    update fields), while Word still treats the whole block as a TOC
    field and replaces it with a full, page-numbered TOC on F9 /
    "Update Field". Pass only H1 titles in order — the live TOC will
    add H2 entries and page numbers itself.

    The title uses ``Heading1`` with a direct-formatting override that
    suppresses auto-numbering (``<w:numPr><w:numId w:val="0"/></w:numPr>``
    sets numbering to "none" for this paragraph only). This matches the
    Euricom v1.4+ template convention: the TOC title is a real H1 for
    consistency in look and outline, but not numbered (so the first
    actual chapter gets number 1, not 2).

    A page break is emitted immediately after the TOC. This is the ONE
    place in the document where the skill inserts a page break
    automatically — the template's design assumes the TOC sits on its
    own page, with the first chapter starting on the next page.
    Everywhere else, authors should add `page_break()` themselves
    only where the layout truly requires it.

    The TOC instruction "TOC \\o '1-N' \\h \\z \\u" is the standard Word
    field code:
      \\o "1-N" = use headings level 1 through N
      \\h       = make entries hyperlinks
      \\z       = hide tab leader/page numbers when in Web Layout
      \\u       = use the document outline level
    """
    # Build the field-result region. Either a single placeholder line,
    # or the F9 update hint followed by one TOC1 paragraph per supplied
    # chapter title. Numbers are prefixed explicitly into the text
    # because the TOC1 style is flat by design (no auto-numbering), so
    # without a prefix the placeholder would render unnumbered. The F9
    # hint is rendered in italics with a leading marker to make it
    # visually distinct from real TOC entries — once F9 runs, the whole
    # block is replaced anyway.
    if entries:
        result_paragraphs = "\n".join(
            f'''  <w:p>
    <w:pPr><w:pStyle w:val="TOC1"/></w:pPr>
    <w:r><w:t xml:space="preserve">{i}. {escape_text(entry)}</w:t></w:r>
  </w:p>'''
            for i, entry in enumerate(entries, start=1)
        )
        result_region = f'''  <w:r>
    <w:fldChar w:fldCharType="separate"/>
  </w:r>
  <w:p>
    <w:pPr><w:pStyle w:val="TOC1"/></w:pPr>
    <w:r>
      <w:rPr><w:i/><w:iCs/><w:color w:val="808080"/></w:rPr>
      <w:t xml:space="preserve">&#x270E; Rechtsklik hier en kies "Veld bijwerken" (F9) om de inhoudstafel te genereren of bij te werken.</w:t>
    </w:r>
  </w:p>
{result_paragraphs}
  <w:p>
    <w:r>
      <w:fldChar w:fldCharType="end"/>
    </w:r>
  </w:p>'''
    else:
        result_region = '''  <w:r>
    <w:fldChar w:fldCharType="separate"/>
  </w:r>
  <w:r>
    <w:rPr><w:i/><w:iCs/><w:color w:val="808080"/></w:rPr>
    <w:t xml:space="preserve">&#x270E; Rechtsklik hier en kies "Veld bijwerken" (F9) om de inhoudstafel te genereren of bij te werken.</w:t>
  </w:r>
  <w:r>
    <w:fldChar w:fldCharType="end"/>
  </w:r>'''

    return f'''<w:p>
  <w:pPr>
    <w:pStyle w:val="Heading1"/>
    <w:numPr><w:ilvl w:val="0"/><w:numId w:val="0"/></w:numPr>
  </w:pPr>
  <w:r><w:t xml:space="preserve">{escape_text(title)}</w:t></w:r>
</w:p>
<w:p>
  <w:r>
    <w:fldChar w:fldCharType="begin"/>
  </w:r>
  <w:r>
    <w:instrText xml:space="preserve"> TOC \\o "1-{levels}" \\h \\z \\u </w:instrText>
  </w:r>
{result_region}
</w:p>
{page_break()}
<!-- EURICOM_AFTER_TOC -->'''


# --------------------------------------------------------------------------- #
# Convenience: assemble a body fragment from a list of pieces
# --------------------------------------------------------------------------- #

def body(*pieces: str) -> str:
    """Join component fragments into a single body XML string.
    Each piece is already a complete <w:p>, <w:tbl>, etc."""
    return "\n".join(p for p in pieces if p)
