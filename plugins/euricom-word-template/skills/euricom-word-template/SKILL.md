---
name: euricom-word-template
description: "Produce professional .docx documents in the Euricom brand template — Aptos fonts, brand colours, logo header, footer, cover page, TOC, callouts, quotes. Trigger when the user (1) mentions 'Euricom', 'huisstijl', 'onze template', 'brand template'; (2) asks to convert a document, PDF, markdown or text into the Euricom or company template, even without naming Euricom (e.g. 'zet dit in onze template', 'maak hier een nette versie van', 'apply our brand template'); (3) asks for any Euricom deliverable type — voorstel, whitepaper, PRD, architectuurdocument, AI-strategie, analyse, rapport, memo, meeting notes, governance document; or (4) points at a .dotx/.docx and asks to apply it as a template. The Euricom template ships bundled in this skill's assets/ directory — do NOT ask the user for a template file before checking that bundled path. Prefer this skill over the generic docx skill whenever Euricom branding is implicit or explicit, because only this one applies the correct fonts, colours and components."
license: Proprietary to Euricom. Use within Euricom only.
---

# Euricom Word template

## What this skill does

Two scenarios:

1. **Convert existing content into the Euricom template.** Source can
   be markdown, PDF, plain text, Word, or any other text format. The
   skill interprets the structure (headings, lists, tables, callouts,
   quotes) and emits a clean `.docx` that uses the template's styles
   instead of the source's formatting.

2. **Generate new documents from a prompt.** The user says "make me
   an AI-strategy document about X using the Euricom template" — the
   skill picks the appropriate document type (proposal, whitepaper,
   memo, etc.), drafts the content in the right tone of voice, and
   produces the `.docx`.

The output is always a real `.docx` file with all the template's
visual identity intact: Aptos / Aptos Display fonts, brand colours,
the Euricom logo in the page header, page numbering, and every
custom paragraph style.

## When the user asks "what can this skill do" / "help" / "about"

If the user asks anything like *"wat doet deze skill"*, *"help"*,
*"about"*, *"wat kan je met de Euricom-template"*, *"welke documenten
kan je maken"*, *"hoe gebruik ik dit"*, or any equivalent — DON'T
start producing a document. Instead, give a concise overview of what
the skill offers. A good answer covers:

- **Two modes**: convert existing content, or generate new from prompt.
- **Document types supported**: proposal (voorstel), whitepaper, PRD,
  architecture document, AI strategy, analysis/report, memo, meeting
  notes, governance document.
- **Components available**: cover page, table of contents,
  auto-numbered headings (H1–H3), bullets (2 levels), 4 note types
  (Tip / Alarm / Waarschuwing / Info), quote blocks with attribution,
  branded data tables with zebra striping and optional total rows.
- **Languages**: follows the source language; Belgian-Dutch by default
  for new documents unless told otherwise.
- **Template version**: based on Euricom Generic Template v1.1
  (multi-section structure with correct page numbering from page 1).
- **A short usage example**: "Upload a document and say 'zet dit in
  onze template', or describe what you want: 'maak een korte memo
  over X'."

Keep it under ~15 lines. Offer to demonstrate with a concrete example
if the user wants to try.

## How the build actually works

The single most important thing to understand:

> **Never build from scratch with `python-docx` or `docx-js`.** Those
> approaches drop or rewrite custom styles, lose the theme, lose the
> header/footer/logo, and produce something that looks generic. The
> only reliable way to preserve a complex template is to **copy the
> `.dotx` file and replace its `word/document.xml` body**.

That is what `scripts/build_from_template.py` does. The body XML it
consumes is assembled from helper functions in
`scripts/render_components.py` — these helpers emit the exact XML the
template's styles expect (paragraph references via `<w:pStyle
w:val="...">`, note tables with the right cell widths and hex colours,
the quote block with its 24pt left-border, the cover page anchoring
the logo via `rId8`, etc.).

### Multi-section template (v1.1+)

The Euricom template from v1.1 onwards uses a **multi-section
structure** to keep page numbering clean:

- **Section 1** (cover): empty header, empty footer, `pgNumType
  start=0`. The cover doesn't show a page number.
- **Section 2** (content): logo header, address-and-page-number
  footer, `pgNumType start=1`. The first content page is page 1.

`build_from_template.py` handles both sections automatically. The
caller doesn't need to think about sections — just compose a body and
the script places the section break where it belongs:

```
# Document WITH a cover page (whitepapers, reports, proposals):
python build_from_template.py --template ... --body ... --output ...

# Document WITHOUT a cover page (memos, short notes):
# Same command — the build script detects the absence of a cover
# from the body content (no EURICOM_COVER_SECTION_BREAK marker) and
# grafts the logo header onto the content section automatically.
python build_from_template.py --template ... --body ... --output ...
```

The previous `--no-cover` flag is gone — the cover-or-not decision is
now derived from whether your body starts with a `cover_page(...)`
call (which emits a section-break marker) or not.

**Backwards compatible with v1.0 templates.** If you point the build
script at the old v1.0 template (single-section), it still works:
the single sectPr is duplicated and the cover-flags-stripping path
is used.

### The complete flow

```
user request
    │
    ▼
[locate template]  ──── prefer user-uploaded .dotx, fall back to assets/Euricom_Generic_Template_v1_1.dotx
    │
    ▼
[plan document structure]  ──── pick doc type, decide on cover/TOC, draft section outline
    │
    ▼
[assemble body XML]  ──── compose calls to heading(), paragraph(), bullet(), note(), quote(), table() in render_components.py
    │
    ▼
[build .docx]  ──── build_from_template.py copies template, swaps body, injects sectPrs in the right places,
                    rewrites content type from .dotx to .docx
    │
    ▼
[validate]  ──── validate_output.py parses every XML part to catch malformed output before the user sees it
    │
    ▼
[report output path to user]
```

## Locating the template (CHECK FIRST — DO NOT ASK)

**Critical**: before asking the user for anything, verify the template
yourself. The skill ships with the template bundled at a known path.
The reason this section is at the top of the workflow is that previous
runs have failed by asking the user for a template file even though it
was already present in the skill folder — that wastes the user's time
and undermines trust in the skill.

### Step 1: use the bundled template path

The template lives next to this `SKILL.md` at:

```
assets/Euricom_Generic_Template_v1_1.dotx
```

At runtime Claude Code installs the plugin under
`~/.claude/plugins/cache/...` and exposes its root via the
`${CLAUDE_PLUGIN_ROOT}` environment variable. Build the absolute path
from there:

```
${CLAUDE_PLUGIN_ROOT}/skills/euricom-word-template/assets/Euricom_Generic_Template_v1_1.dotx
```

Pass that path to `scripts/build_from_template.py --template ...`.

### Step 2: prefer a user-supplied template over the bundled one

If the user has explicitly pointed at their own `.dotx` or `.docx`
("use this template: C:\path\to\custom.dotx", or has just edited a
local copy), prefer that path over the bundled copy — it may be a
newer revision.

### Step 3: only ask for a template if the bundled file is missing

The bundled template is committed to this plugin, so its absence
signals a packaging problem rather than a missing user input. Verify
the file exists at the path in Step 1. If — and only if — it doesn't,
fall back to asking the user:

> "I can't find the bundled Euricom template at
> `${CLAUDE_PLUGIN_ROOT}/skills/euricom-word-template/assets/Euricom_Generic_Template_v1_1.dotx`.
> The plugin may be incomplete. Reinstall the plugin, or point me at a
> Euricom `.dotx` file so I can apply the styling."

Do NOT ask the user for a template **before** checking that bundled
path. If you find yourself drafting that message without having
checked the bundled location first, stop and check.

## Workflow for each scenario

### Scenario 1 — Convert existing content

When the user uploads a source file (or pastes content) and asks to
put it in the Euricom template:

1. **Read the source.** For `.md`, `.txt`, and other text formats, use
   the Read tool. For `.docx`, `.odt`, `.epub`, parse with `python-docx`
   or `pandoc`. For `.pdf`, use `pdftotext` (poppler-utils) or
   `pdfplumber`. For very large sources, sample first to understand
   structure, then read fully.

2. **Interpret the structure.** Map the source's organisation onto
   the template's vocabulary:
   - Source `# H1` / `## H2` / `### H3` → `Heading1` / `Heading2` / `Heading3`
   - Markdown `>` block-quote with attribution → `quote(...)`
   - Source admonitions/callouts (`> [!NOTE]`, `> [!WARNING]`, `Note:`,
     `⚠️ Tip:`) → `note("Info"/"Waarschuwing"/"Tip", ...)`
   - Markdown lists → `bullet(...)` at appropriate level
   - Markdown tables → `table(headers, rows)`
   - Code blocks → use `paragraph` with a monospace formatting
     fallback, or keep as inline `code` runs — the template does not
     define a dedicated code-block style, so a monospace `Normal`
     paragraph with light-gray background is acceptable

3. **Restructure if needed.** The source structure is a starting
   point, not a constraint. Consult `references/document-types.md` for
   the conventional shape of each document type. Common
   restructurings:
   - Add a "Samenvatting" H1 at the top of long documents that lack one.
   - Consolidate scattered recommendations into a final "Aanbevelingen" H1.
   - Re-bucket H4+ source headings into the H1–H3 ceiling.
   - Convert inline "let op:" / "belangrijk:" prose to Note callouts.

4. **Apply tone of voice.** Mirror the source's language but clean up
   per `references/tone-of-voice.md`: smart quotes, normalised
   capitalisation in headings (sentence case, no trailing colons),
   Belgian-Dutch conventions if the source is Dutch.

5. **Decide on cover / TOC.** Roughly: cover and TOC for documents
   ≥ 8 pages or any external deliverable. Skip both for memos and
   short internal notes. See `references/document-types.md`.

6. **Discard the template's example content.** The embedded template
   contains its own "Werken met de Euricom template" handbook text as
   placeholder. The build script replaces the entire body, so this
   gets discarded automatically — but be careful never to copy any of
   that handbook prose into the new document.

7. **Build, validate, present.**

### Scenario 2 — Generate a new document from a prompt

When the user asks for a new document ("make me a whitepaper on X",
"draft a proposal for client Y"):

1. **Identify the document type.** Use the cues in
   `references/document-types.md`. If genuinely ambiguous, ask one
   clarifying question — don't guess between very different shapes
   (proposal vs. internal memo).

2. **Plan the outline first.** Before writing prose, sketch H1s and
   note where notes / quotes / tables would land. This is where the
   document type's blueprint earns its keep.

3. **Draft section by section.** For each H1: write 2–4 short
   paragraphs, add an H2/H3 only if the section genuinely splits
   into sub-topics. Use bullets for lists; use a table for parallel
   structured data; use a note for emphasis on a single point.

4. **Respect the budgets.** Max one to two notes per page. At most
   one or two quotes per document. Tables stay under ~4 columns.

5. **Cover / TOC by document length.** Estimate length from the
   outline: a typical H1 + 3 short paragraphs = roughly half a page.
   10+ H1s usually means cover and TOC are warranted.

6. **Build, validate, present.**

## Reference files

Read these as needed; don't try to absorb them all upfront.

- `references/styles-reference.md` — full catalogue of style IDs, when
  to use each, theme colour palette.
- `references/components-reference.md` — every component (notes,
  quotes, tables, cover, TOC) with its Python helper signature,
  rationale, and examples.
- `references/document-types.md` — structural blueprints for the
  common Euricom document types and length-based decisions on cover
  and TOC.
- `references/tone-of-voice.md` — Belgian-Dutch writing conventions,
  typographic habits, words to avoid.

## Quick Parts in the output

The Euricom template defines six Quick Parts in the "Euricom" gallery
category (`Note - Tip`, `Note - Alarm`, `Note - Waarschuwing`,
`Note - Info`, `Color Picker`, `Quote`). Because the build script
copies the entire `.dotx` and only swaps the body, the glossary
containing these Quick Parts **survives intact** in every output
`.docx`.

This means anyone who opens a generated document in Word can insert
the same branded components manually via **Insert → Quick Parts →
Building Blocks Organizer → category Euricom**. No additional work
needed in the skill — it's a side effect of the template-copy
architecture.

If you're adding new content to an existing document and want the
note/quote rendering to be byte-identical to what users get via
the Quick Parts UI, use the helpers in `render_components.py`
(`note(...)`, `quote(...)`). They produce the same visual output.

## Common pitfalls

### Never pre-encode characters in your input strings

The helpers in `render_components.py` already handle all character
encoding for you. **Pass plain UTF-8 text into the helpers — never
pre-encode anything.**

Specifically:

- Pass `"quoted phrase"` — NOT `&#x201C;quoted phrase&#x201D;` and
  NOT `\u201Cquoted phrase\u201D`. `escape_text` will convert the
  straight quotes to typographic ones automatically.
- Pass `"Keenan's book"` — NOT `Keenan&#x2019;s book`. The
  apostrophe is upgraded to a curly one automatically.
- Pass `"café"` or `"één"` — NOT `caf&#xE9;` or `&#xE9;&#xE9;n`.
  Accented characters work fine in UTF-8 source code; they don't
  need to be entities.

**What happens if you do pre-encode:** `escape_text` sees the `&`
in `&#x201C;` as a literal ampersand and escapes it to `&amp;`,
turning your intended `&#x201C;` (which Word would render as `"`)
into `&amp;#x201C;` (which Word renders as the literal text
`&#x201C;`). The reader then sees raw hex codes scattered through
the document — a confusing and embarrassing bug.

The validator (`validate_output.py`) detects this pattern in the
output and will fail the build with a clear message. If you see
that error, search your body-composition script for any `&#x` or
`\u` escapes and replace them with the actual character.

### Use single-quoted Python strings when the content contains double quotes

Python lets you delimit strings with either `'...'` or `"..."`. When
the content of a string contains double quotes (very common in Dutch
prose), prefer `'...'` as the delimiter so you don't have to escape
each one:

```python
# Good
paragraph('De klant zegt "we hebben een team nodig" en bedoelt ...')

# Awkward (every internal quote needs escaping)
paragraph("De klant zegt \"we hebben een team nodig\" en bedoelt ...")
```

This keeps the Python source readable and avoids accidentally
breaking string boundaries.

### Don't add `page_break()` before `Heading1`

The template's `Heading1` style has **built-in page-break-before**
behaviour: every H1 starts on a fresh page automatically (see
`references/styles-reference.md`). Adding a manual `page_break()`
right before an H1 produces a double break — one extra blank page
between every chapter.

```python
# Wrong — produces an extra blank page before every chapter
paragraph("..."),
page_break(),
heading("New chapter", 1),

# Right — the style handles the break
paragraph("..."),
heading("New chapter", 1),
```

`page_break()` is still useful, but only for forcing a break that
the styles would not produce on their own — for example, mid-chapter
before a large table, or to keep a quote on its own page. If the
break you want is "start the next chapter on a new page", do
nothing; the H1 style already does it.

## Hard rules from the template itself

These come from the template's own self-documentation and apply to
every document the skill produces:

- **No manual formatting when a style exists.** Never set font, size,
  colour, or spacing directly to simulate a heading or note —
  reference the style by ID.
- **Maximum heading depth: H3.** If the structure wants H4 or deeper,
  restructure instead.
- **Maximum bullet depth: 2 levels.** Split or restructure if you
  need three.
- **Notes are semantic, not decorative.** Pick the right type (Tip,
  Alarm, Waarschuwing, Info) for what the note actually conveys.
  Don't use a Tip just because you like the green.
- **One to two notes per page maximum.**
- **Cover and TOC are for documents ≥ 8 pages or external
  deliverables.** Skip both for memos and quick notes.
- **The meta line on the cover ("voor"-vermelding) is always
  uppercase.** `VOOR EURICOM`, `CONFIDENTIEEL`, `VOOR <CLIENT>`.
- **No version number inside the document body.** Versioning lives in
  the filename suffix (`v0.1`, `v1.0`, `v1.1`, `v2.0`).
- **File naming.** When the user asks for a filename, follow:
  `<Documentnaam> v<version>.docx` — e.g. `AI-strategie_2026 v0.1.docx`.
  Default to `v0.1` for drafts; the user can rename.

## Output handling

- **Where to write.** Final `.docx` goes to a path the user has
  specified, or — if they haven't — to the current working directory.
  Use a meaningful filename per the naming convention above. Confirm
  the destination with the user when in doubt rather than overwriting
  an existing file silently.
- **Validate before reporting.** Run `scripts/validate_output.py` on
  the produced file and only surface it to the user if it passes. If
  validation fails, surface the error and try to fix it rather than
  handing over a broken file.
- **Report succinctly.** Tell the user the absolute path of the
  generated file in one or two sentences. Don't paste the whole
  document content back — they have the file.

## Example end-to-end

User: *"Maak een korte memo voor het management over de keuze om
GitHub Copilot Enterprise breed uit te rollen. Gebruik onze Euricom
template."*

Skill thinking:
- Document type: **Memo** (user said "korte" + "memo").
- Length: ~1–2 pages. → **No cover, no TOC.**
- Structure: Title + H1Intro + Aanleiding + Voorstel + Implicaties +
  Volgende stappen.
- Language: Dutch (Belgian-Flemish, U-vorm given management audience).
- Notes: probably one Waarschuwing about cost or licensing pitfalls.

Skill produces body XML composing those pieces, calls
`build_from_template.py`, validates, presents
`GitHub_Copilot_uitrol_memo v0.1.docx`.
