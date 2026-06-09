# Components reference — Euricom Word template

Every component below has a Python helper in `scripts/render_components.py`.
**Always use the helper** rather than hand-writing XML — the helpers
encode the exact structure (cell widths, hex colours, font sizes) the
template expects.

## Quick map: situation → component

| Situation | Component | Helper |
|---|---|---|
| Document title (the `documenttitle` content control, Title style) | Title | `title("...")` |
| Chapter heading | Heading 1 | `heading("...", 1)` |
| Section / sub-section | Heading 2 / 3 | `heading("...", 2)` / `heading("...", 3)` |
| Italic intro under a chapter title | H1 Intro | `h1_intro("...")` |
| Regular paragraph | Normal | `paragraph("...")` |
| First-level bullet | Bullet 1 | `bullet("...", 1)` |
| Second-level bullet | Bullet 2 | `bullet("...", 2)` |
| Actionable tip / shortcut / best practice | Note (Tip) | `note("Tip", "...")` |
| Critical, time-sensitive warning | Note (Alarm) | `note("Alarm", "...")` |
| Caution / things to watch out for | Note (Waarschuwing) | `note("Waarschuwing", "...")` |
| Supporting info / context / reference | Note (Info) | `note("Info", "...")` |
| Vision quote / key message with attribution | Quote | `quote("...", author="...", role="...")` |
| Comparison table / data table | Table | `table(headers, rows)` |
| Cover page | Cover | `cover_page(title, subtitle, meta)` |
| Table of contents | TOC | `toc(levels=2)` |
| Hard page break | Page break | `page_break()` |

## Note callouts

**Purpose.** Notes pull a single point of attention out of the reading
flow without breaking it. The template defines four semantic types,
each with a distinct accent colour.

**Budget.** The template's own guidance: **one to two notes per page,
maximum**. More than that and they lose their visual punch and start
to feel cluttered. If a document has many things worth flagging,
prefer to integrate them into the prose or restructure into a
dedicated "Aandachtspunten" subsection.

**Choosing the right type:**

- **Tip** — proactive suggestion, shortcut, or "did you know" that
  helps the reader work smarter. Example: *"Twijfel je of de stijl
  correct staat? Clear eerst de opmaak."*
- **Alarm** — critical condition; failing to act has serious
  consequences (security, data loss, downtime). Use sparingly; if
  every note is an Alarm, none of them are.
- **Waarschuwing** — caution; something can go wrong if mishandled.
  Use for caveats and gotchas.
- **Info** — neutral aside; context or background that helps
  comprehension but isn't required to act. The catch-all when the
  others don't fit.

**Custom title.** Pass `title="..."` to override the default label.
The template does this for things like *"Geen tekstuele suffixen"*
(styled as a Waarschuwing but titled descriptively).

## Quote blocks

**Purpose.** Quotes give vision statements, principles, or key
messages typographic weight. They are a heavy visual element — use
them deliberately, typically **once or twice per document, never
back-to-back**.

**Structure:**
- Body text is italicised, 12pt, with a thick steel-gray left bar.
- Optional attribution row: bold name + italic "– role".
- The helper adds smart-quote characters automatically.

**Example:**

```python
quote(
    "AI-adoptie is geen project maar een evolutie. Organisaties die "
    "vandaag investeren in een gestructureerd framework bouwen niet "
    "alleen productiviteit, maar ook een duurzaam AI gedreven "
    "engineeringmodel.",
    author="Wim Van Hoye",
    role="Managing Director",
)
```

## Tables

**Purpose.** Structured, comparable data. Avoid using tables for
layout (sidebars, callouts) — that's what notes and quotes are for.

**Styling — delegated to the template.** Tables use the
``EuricomDataTable`` style defined in the template. This style
provides:
- Subtle borders (`#DCE5E6`, 2pt) — lighter than the previous manual approach
- Header row: bold white text on Midnight `#014046` background
- Body rows: zebra striping with `#F1F5F6` (Light Steel Gray) on
  alternating rows
- Optional last row: bold with `#D3E0E3` fill — intended for totals
- Compact cell padding (45 DXA top/bottom in the body, 57 in header)
- Aptos 10pt body text

The `table()` helper does **not** set fills, borders, or padding
directly — Word applies them automatically via the style. This is
the same rule that applies to paragraphs: prefer the style over
inline formatting.

**Helper signature:**
```python
table(headers, rows, col_widths=None, last_row_is_total=False)
```

**The `last_row_is_total` flag.** Set this to `True` when the final
row of your table is a sum, total, or summary row. The template
will then render it bold with the light-blue accent background,
giving the reader an immediate visual cue that this row is
different from the others.

```python
# Example: requirements estimation table with a total row
table(
    headers=["#", "Requirement", "Days", "Deviation"],
    rows=[
        ["1", "Bin verwijderen", "2 dagen", "1 dag"],
        ["2", "Locatie opvragen", "1,5 dag", "0,5 dag"],
        # ... more rows ...
        ["", "TOTAAL", "47,5 dagen", "12 dagen"],   # ← becomes a total row
    ],
    col_widths=[1000, 4500, 1750, 1706],
    last_row_is_total=True,
)
```

**Guidance:**
- Keep column count low (2–4 is comfortable; 5+ becomes hard to scan).
- Avoid merged cells; they don't reflow well on mobile or in Web Layout.
- Headers should be short — full sentences belong in the body.
- **Minimum column width for narrow columns: ~1000 DXA (~18mm).**
  Below this, Word can break short words and even small numbers across
  lines because the header row uses bold Aptos which is wider than the
  body font (so "Stap" becomes "St ap"). When a column will hold short
  values (a counter, a step number, a single short word), give it at
  least 1000 DXA. The 750 DXA figure that "feels safe" for body text
  is too narrow for headers.

## Cover page

**When to include one.** The template's own rule: **roughly eight
pages or more, or any external deliverable.** For short memos,
internal notes, or quick analyses, skip the cover entirely — it adds
ceremony without value.

**Composition.**
- `title`: main document title (no period at end).
- `subtitle`: optional one-liner describing what it is or what it's
  for. Keep under ~80 characters.
- `meta`: the "voor"-line, **always uppercase**. Common values:
  `VOOR EURICOM`, `VOOR INTERN`, `CONFIDENTIEEL`, or
  `VOOR <CLIENT NAME>` (e.g. `VOOR KRÊFEL`).

**The logo** is anchored automatically when `include_logo=True`
(default). It reuses `rId8` from the template's relationships, so the
image data is already embedded — no need to ship a separate PNG.

## Document title (CoverTitle vs DocumentTitle)

The template has **two distinct title content controls**, and both
should be filled with the same text:

- **CoverTitle** (`covertitle`) — the large title on the cover page.
  Filled from the `title=` argument of `cover_page(...)`.
- **DocumentTitle** (`documenttitle`) — the `Title`-styled heading at
  the top of the actual content: page 3 in a cover+TOC document, page 1
  in a cover-less memo. Produced by `title("...")`.

They are **separate, non-linked fields**: in Word, editing one does not
change the other. The skill fills both at build time so their content
matches, but nothing keeps them in sync afterwards — that is by design.

**How to fill them.**

- In a cover document, pass the same string to both:
  `cover_page(title="X", ...)` and `title("X")`. Place the `title("X")`
  call **after** `toc(...)` so the DocumentTitle lands on the first
  content page.
- You may **omit `title()` in a cover document** — the build script
  then fills the DocumentTitle automatically from the cover title, and
  positions it right after the TOC. This is a safety net: the
  DocumentTitle is never left empty just because `title()` was
  forgotten. Calling `title()` explicitly is still preferred when you
  want full control over its position or want different text.
- In a **cover-less** document (memo, short note) there is no cover
  title to fall back on, so call `title("...")` yourself at the top of
  the body to get a DocumentTitle on page 1.

`title("...")` does not emit a plain paragraph; it emits the template's
real `documenttitle` content control, so the generated title is
identical to what a human gets by typing into the template's page-3
placeholder.

## Table of contents

**When to include one.** Same rule as the cover: roughly eight pages
or more. For shorter documents, the TOC creates more noise than
navigation value.

**Depth.** Default is `levels=2` (H1 + H2). For technical or
reference-style documents with deep structure, `levels=3` is
appropriate. Avoid `levels=4` or deeper — if the doc needs that much
nesting, the structure itself is the problem.

**Behaviour.** The TOC field is a Word *field* — Word builds the
actual entries when the user first opens the document and chooses
"Update Field" (or automatically, depending on settings). Until then,
a placeholder line is shown. This is normal and expected.

## Composing a document

A typical body assembly looks like:

```python
from render_components import (
    cover_page, toc, title, heading, h1_intro, paragraph,
    bullet, note, quote, table, body
)

doc = body(
    cover_page(
        title="AI-strategie 2026",
        subtitle="Roadmap voor verantwoorde AI-adoptie",
        meta="VOOR EURICOM",
    ),
    toc(levels=2),
    title("AI-strategie 2026"),  # same text as the cover title; lands on the first content page

    heading("Inleiding", 1),
    h1_intro("Deze nota schetst de Euricom-aanpak voor AI-adoptie in 2026."),
    paragraph("AI-tools zijn de afgelopen twee jaar verschoven van ..."),

    heading("Vier pijlers", 1),
    bullet("Mensen — opleiding, governance, verantwoordelijkheid", 1),
    bullet("Tools — selectie, integratie, security", 1),
    bullet("Processen — prompts, reviews, audit trails", 1),
    bullet("Data — kwaliteit, eigenaarschap, naleving", 1),

    note(
        "Tip",
        "Begin met één pilot per pijler. Schaal pas op zodra meetbare "
        "resultaten bevestigen dat de aanpak werkt."
    ),

    heading("Voorbeeld-roadmap", 1),
    table(
        headers=["Kwartaal", "Pijler", "Mijlpaal"],
        rows=[
            ["Q1", "Mensen", "AI-fluency training voor alle engineers"],
            ["Q2", "Tools", "Centraal beheerde licenties live"],
            ["Q3", "Processen", "Prompt-review workflow gepubliceerd"],
            ["Q4", "Data", "Datakwaliteit-audit afgerond"],
        ],
    ),

    quote(
        "AI is geen project maar een evolutie.",
        author="Wim Van Hoye", role="Managing Director",
    ),
)
```

The resulting `doc` string is what you write to `body.xml` for
`build_from_template.py` to consume.
