---
name: euricom-word-template
version: 1.5.3
description: "Produce professional .docx documents in the Euricom brand template — Aptos fonts, brand colours, logo header, footer, cover page, TOC, callouts, quotes. Trigger when the user (1) mentions 'Euricom', 'huisstijl', 'onze template', 'brand template'; (2) asks to convert a document, PDF, markdown or text into the Euricom or company template, even without naming Euricom (e.g. 'zet dit in onze template', 'maak hier een nette versie van', 'apply our brand template'); (3) asks for any Euricom deliverable type — voorstel, whitepaper, PRD, architectuurdocument, AI-strategie, analyse, rapport, memo, meeting notes, governance document; or (4) uploads a .dotx/.docx and asks to apply it as a template. The Euricom template ships embedded in this skill's assets/ — do NOT ask the user to upload it before verifying via `find /mnt/skills`. Prefer this skill over the generic docx skill whenever Euricom branding is implicit or explicit, because only this one applies the correct fonts, colours and components."
license: Proprietary to Euricom. Use within Euricom only.
---

# Euricom Word template

This SKILL.md is the orchestration layer: it covers what to do and in
what order. The detailed reference material lives in `references/`
(catalogued under "Reference files" below) — read the relevant file
when you reach the step that needs it, rather than absorbing
everything upfront.

## What this skill does

Two scenarios:

1. **Convert existing content into the Euricom template.** Source can
   be markdown, PDF, plain text, Word, or any text format. The skill
   interprets the structure (headings, lists, tables, callouts, quotes)
   and emits a clean `.docx` that uses the template's styles instead of
   the source's formatting.
2. **Generate new documents from a prompt.** "Make an AI-strategy
   document about X using the Euricom template" — the skill picks the
   document type, drafts the content in the right tone of voice, and
   produces the `.docx`.

The output is always a real `.docx` with the template's visual identity
intact: Aptos / Aptos Display fonts, brand colours, the Euricom logo in
the page header, page numbering, and every custom paragraph style.

## When the user asks "what can this skill do" / "help" / "about"

If the user asks *"wat doet deze skill"*, *"help"*, *"about"*, *"welke
documenten kan je maken"*, *"hoe gebruik ik dit"*, or any equivalent —
DON'T start producing a document. Give a concise overview (under ~15
lines) covering:

- **Two modes**: convert existing content, or generate new from prompt.
- **Document types**: proposal (voorstel), whitepaper, PRD, architecture
  document, AI strategy, analysis/report, memo, meeting notes,
  governance document.
- **Components**: cover page, TOC, auto-numbered headings (H1–H3),
  bullets (2 levels), 4 note types (Tip / Alarm / Waarschuwing / Info),
  quote blocks with attribution, branded data tables with zebra
  striping and optional total rows, and Inline Code for paths, commands
  and shortcuts.
- **Languages**: follows the source language; Belgian-Dutch by default
  for new documents unless told otherwise.
- **Template**: the Euricom Generic Template in
  `assets/Euricom_Generic_Template.dotx`. Multi-section structure with
  clean page numbering; Heading1 does not auto page-break.
- **A short usage example**: "Upload a document and say 'zet dit in onze
  template', or describe what you want: 'maak een korte memo over X'."

Offer to demonstrate with a concrete example if the user wants to try.

## How the build works

The single most important rule:

> **Never build from scratch with `python-docx` or `docx-js`.** Those
> approaches drop or rewrite custom styles, lose the theme, lose the
> header/footer/logo, and produce something generic. The only reliable
> way to preserve a complex template is to **copy the `.dotx` and
> replace its `word/document.xml` body**.

That is what `scripts/build_from_template.py` does. The body XML it
consumes is assembled from helper functions in
`scripts/render_components.py` — these emit the exact XML the template's
styles expect (paragraph references via `<w:pStyle>`, note tables with
the right cell widths and hex colours, the quote block with its 24pt
left-border, the cover content controls, the documenttitle control,
etc.). `scripts/validate_output.py` then parses every XML part to catch
malformed output before the user sees it.

### The complete flow

```
user request
    │
    ▼
[locate template]  ──── prefer user-uploaded .dotx, fall back to assets/Euricom_Generic_Template.dotx
    │
    ▼
[plan structure]  ──── pick doc type, decide on cover/TOC, draft section outline
    │
    ▼
[assemble body XML]  ──── compose heading(), paragraph(), bullet(), note(), quote(), table(), title() in render_components.py
    │
    ▼
[build .docx]  ──── build_from_template.py copies the template, swaps the body, injects sectPrs, fills content controls, rewrites the content type from .dotx to .docx
    │
    ▼
[validate]  ──── validate_output.py parses every XML part
    │
    ▼
[present file via present_files]
```

### Multi-section structure

The template uses a multi-section structure to keep page numbering
clean: section 1 (cover) has an empty header/footer and `pgNumType
start=0` (no page number on the cover); section 2 (content) carries the
logo header, the address-and-page-number footer, and `pgNumType
start=1` (first content page is page 1).

`build_from_template.py` handles this automatically. The caller just
composes a body; the script places the section break where it belongs.
The cover-or-not decision is derived from whether the body starts with
a `cover_page(...)` call (which emits a section-break marker) or not —
there is no `--no-cover` flag. The script also tolerates an older
single-section template shape as defensive fallback.

```
# Same command whether or not the body contains a cover_page(...):
python build_from_template.py --template ... --body ... --output ...
```

## Locating the template (CHECK FIRST — DO NOT ASK)

Before asking the user for anything, verify the template yourself. The
skill ships with it embedded. Previous runs failed by asking the user
to upload a template that was already present — that wastes time and
undermines trust.

**Step 1 — locate the skill directory.** Custom skills unpack under
`/mnt/skills/`; the exact path varies (personal vs. org-provisioned),
so find it dynamically:

```bash
find /mnt/skills -type f -name "Euricom_Generic_Template*.dotx" 2>/dev/null | head -5
```

Capture that path and reuse it for all build commands. The wildcard
also matches older filenames (e.g. `..._v1_4.dotx`); take the first
match.

**Step 2 — prefer a user-uploaded template.** If the user uploaded a
`.dotx`/`.docx` in this chat that looks like a Euricom template
(filename contains `euricom`/`template`, or they said "use this
template"), prefer it — it may be newer. Check `ls
/mnt/user-data/uploads/`.

**Step 3 — only ask if BOTH are missing.** Ask for an upload only when
the `find` returned nothing AND uploads has no recognisable template.
Never draft a "please upload" message before running the `find`.

## Workflow for each scenario

### Scenario 1 — Convert existing content

1. **Read the source.** `extract-text` for `.docx`/`.odt`/`.epub`;
   `pdftotext` or the `pdf-reading` skill for `.pdf`; `cat` for
   `.md`/`.txt`. Sample large sources first, then read fully.
2. **Interpret the structure.** Map the source onto the template's
   vocabulary: `# / ## / ###` → `Heading1/2/3`; `>` block-quote with
   attribution → `quote(...)`; admonitions (`> [!NOTE]`, `Note:`, `⚠️
   Tip:`) → `note("Info"/"Waarschuwing"/"Tip", ...)`; lists →
   `bullet(...)`; tables → `table(headers, rows)`. The template has no
   dedicated code-block style — a monospace `Normal` paragraph with a
   light-gray background is acceptable.
3. **Restructure if needed.** The source structure is a starting point.
   Consult `references/document-types.md`. Common moves: add a
   "Samenvatting" H1 to long documents that lack one; consolidate
   recommendations into a final "Aanbevelingen" H1; re-bucket H4+ into
   the H1–H3 ceiling; convert inline "let op:"/"belangrijk:" prose into
   Note callouts.
4. **Apply surface-level tone of voice only.** This is a conversion,
   not a rewrite — the author's content, structure, argument, and voice
   stay intact. Fix only the objectively wrong or purely typographic:
   typos, dt-errors, wrong-word swaps; smart quotes (automatic — don't
   hand-encode); sentence-case headings with no trailing colon;
   clear terminology slips; non-breaking spaces between numbers and
   units. **Do not** shorten sentences, swap words for style, or apply
   other rules from `references/tone-of-voice.md` (those guide *new*
   content only). On a conversion, the author's voice wins.
5. **Decide on cover / TOC.** Cover and TOC for documents ≥ 8 pages or
   any external deliverable; skip both for memos and short notes. See
   `references/document-types.md`.
6. **Discard the template's example content.** The embedded template
   contains its own "Werken met de Euricom template" handbook text as
   placeholder. The build script replaces the entire body, so it is
   dropped automatically — never copy any of that handbook prose into
   the new document.
7. **Proofread** (see "Proofread before building").
8. **Build, validate, present.**
9. **Invite refinement** (first conversion only — see "Invite further
   refinement").

### Scenario 2 — Generate a new document from a prompt

1. **Identify the document type** using `references/document-types.md`.
   If genuinely ambiguous between very different shapes (proposal vs.
   internal memo), ask one clarifying question.
2. **Plan the outline first.** Sketch H1s and note where notes / quotes
   / tables would land before writing prose.
3. **Draft section by section.** Per H1: 2–4 short paragraphs; add an
   H2/H3 only if the section genuinely splits. Bullets for lists, a
   table for parallel structured data, a note for emphasis on a single
   point.
4. **Respect the budgets.** One to two notes per page; at most one or
   two quotes per document; tables under ~4 columns.
5. **Cover / TOC by length.** Estimate from the outline (an H1 + 3
   short paragraphs ≈ half a page). 10+ H1s usually warrants cover and
   TOC.
6. **Proofread**, then **build, validate, present.**

## Proofread before building

Before calling `build_from_template.py`, reread your composed body once
as a reader would, top to bottom, and fix errors in the compose script
(the source of truth), not in the XML. This is non-skippable. The full
checklist — dt-rule, wrong-word swaps, terminology and casing
consistency, punctuation spacing, names — is in
`references/proofreading.md`. Proofread in the source's language and
variant. If you find more than a handful of issues, slow down on the
next draft rather than fix-and-ship.

## Invite further refinement

After the *first* conversion (Scenario 1) in a conversation, follow the
`present_files` call with a short message inviting refinements — it
helps new users discover they can iterate. Send it only once per chat
and **skip** it for: the generation flow (Scenario 2), users who said
they want no commentary, and clearly experienced users. Keep it short,
four examples, adapted to the source language (the English equivalent
mirrors this):

> Het bestand staat klaar. Vraag me gerust om verfijningen —
> bijvoorbeeld:
> — de tone-of-voice scherper maken (kortere zinnen, actieve stem)
> — iets toevoegen of inkorten
> — de structuur herzien (volgorde van hoofdstukken, extra samenvatting)
> — specifieke termen of zinnen anders verwoorden

The four axes are deliberate: tone-of-voice, content, structure,
phrasing.

## Hard rules from the template itself

These come from the template's own styleguide (canonical reference: the
v1.7 `.dotx` styleguide content). Every document must respect them.

**Styling.** Use the template's styles; never simulate them with manual
formatting. Forbidden anywhere: faking a heading with a font size
instead of `Heading1/2/3`; setting a colour by hand instead of using
the styles that carry the brand colour; empty paragraphs for spacing
(styles already carry the right `spacing`); whole-paragraph bold/italic
for emphasis (use it on a phrase, never as a substitute for a heading
or callout). Maximum heading depth **H3**; maximum bullet depth **2
levels** — restructure if you need more.

**Bullets.** Use bulleted lists, not numbered lists — headings already
provide outline numbering. Convey order in the bullet text (`Eerst …`,
`Daarna …`, `Tot slot …`). Keep bullets short and few; a twelve-entry
list usually wants a table or prose.

**Notes.** Semantic, not decorative — pick the type (Tip, Alarm,
Waarschuwing, Info) that matches the meaning, not the colour you like.
One to two notes per page maximum.

**Inline Code.** Use `InlineCodeChar` (via `inline_code(...)`) for file
paths, filenames, env vars, commands, shortcuts, and short UI fragments
the reader must recognise verbatim. Use it sparingly and never fake the
style with ad-hoc run properties. Full guidance and examples:
`references/authoring-and-pitfalls.md`.

**Title fields — fill both.** The template has two independent,
non-linked title content controls: **CoverTitle** (cover) and
**DocumentTitle** (the `Title`-styled heading at the top of the
content — page 3 in a cover+TOC document, page 1 in a memo). They hold
the **same content** but do not auto-sync. Pass the title to
`cover_page(title=...)` and call `title("...")` with the same string,
placed **after** `toc(...)`. In a cover document you may omit `title()`
— the build fills the DocumentTitle from the cover title automatically
and positions it after the TOC, so it is never empty. In a cover-less
memo, always call `title("...")` yourself. `title()` emits the real
`documenttitle` content control, not a plain paragraph. See
`references/components-reference.md` for the full explanation.

**Cover, TOC, metadata.** Cover and TOC for documents ≥ 8 pages or
external deliverables; skip for memos. The cover meta line
("voor"-vermelding) is always uppercase (`VOOR EURICOM`,
`CONFIDENTIEEL`, `VOOR <CLIENT>`). No version number in the document
body — versioning lives in the filename.

**File naming.** `<Documentnaam>-v<NN>.docx` — e.g.
`AI-strategie-2026-v01.docx`. Default to `v01`. **No spaces and no dots**
(other than the `.docx` extension): spaces and dotted versions like
`v0.1` make files preview as blank in iOS Quick Look. Use hyphens and a
digits-only suffix (`v01`, `v10`, `v20`).

**Page breaks.** Don't insert them proactively — `Heading1` does not
auto-break, and the only automatic break is the one after the TOC. See
`references/authoring-and-pitfalls.md` for when a manual `page_break()`
is warranted.

**Never pre-encode characters.** Pass plain UTF-8 text into the helpers;
they handle smart quotes and entities. Pre-encoding double-escapes and
leaks raw hex codes into the document. Details and the validator check:
`references/authoring-and-pitfalls.md`.

## Reference files

Read the relevant one when you reach the step that needs it.

- `references/styles-reference.md` — full catalogue of style IDs, when
  to use each, theme colour palette.
- `references/components-reference.md` — every component (notes, quotes,
  tables, cover, TOC, the two title fields) with its helper signature,
  rationale, and examples.
- `references/document-types.md` — structural blueprints for the common
  Euricom document types and length-based cover/TOC decisions.
- `references/tone-of-voice.md` — Belgian-Dutch writing conventions,
  typographic habits, words to avoid (applies to *new* content).
- `references/proofreading.md` — the pre-build proofreading checklist.
- `references/authoring-and-pitfalls.md` — Inline Code guide and the
  common pitfalls (pre-encoding, quoting, page breaks).
- `references/quick-parts.md` — why Quick Parts are a property of the
  `.dotx` (not generated docs) and how to write the installation guide.

## Output handling

- **Where to write.** Final `.docx` to `/mnt/user-data/outputs/` with a
  meaningful filename (per the naming convention above).
- **Validate before presenting.** Run `validate_output.py`; only call
  `present_files` if it passes. On failure, surface the error and fix
  it rather than presenting a broken file.
- **Present succinctly.** Expose the file via `present_files` with a
  one-or-two-sentence summary. Don't paste the document content back.

## Example end-to-end

User: *"Maak een korte memo voor het management over de keuze om GitHub
Copilot Enterprise breed uit te rollen. Gebruik onze Euricom template."*

Skill thinking:
- Document type: **Memo** ("korte" + "memo"). Length ~1–2 pages → **no
  cover, no TOC**.
- Structure: `title()` + H1Intro + Aanleiding + Voorstel + Implicaties +
  Volgende stappen.
- Language: Dutch (Belgian-Flemish, U-vorm for a management audience).
- Notes: probably one Waarschuwing about cost or licensing pitfalls.

Skill composes the body, calls `build_from_template.py`, validates, and
presents `GitHub-Copilot-uitrol-memo-v01.docx`.
