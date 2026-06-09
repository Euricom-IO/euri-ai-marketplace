# Changelog

All notable changes to the **euricom-word-template** skill. Versions
refer to the skill itself, not to the embedded `.dotx` template. The
template has its own version history, tracked in this file under each
skill release where it changed (the embedded .dotx is the file
`assets/Euricom_Generic_Template.dotx` regardless of its internal
revision).

The skill follows semantic versioning: MAJOR.MINOR.PATCH. MAJOR for
breaking API changes, MINOR for new features or convention changes,
PATCH for fixes.

## [1.5.3] — 2026-05-29

### Changed

- **Embedded template: `Title` style spacing-before reduced from 24pt
  to 10pt** (`w:before` 480 → 200 twips in `word/styles.xml`). This
  tightens the gap above the DocumentTitle on the first content page;
  `spacing after` (600 / 30pt), font size, colour, and all other style
  properties are unchanged. Only the `Title` paragraph style is
  affected — the cover title uses `ECCoverTitle` and is untouched. All
  36 template parts (theme, logo, headers, footers, numbering) are
  preserved. Scripts are unchanged.

## [1.5.2] — 2026-05-29

### Changed

- **SKILL.md refactored for progressive disclosure** — reduced from 727
  to 350 lines (well under the 500-line review gate) by moving detailed
  material into `references/`, with short pointers left in place. No
  behaviour change: the scripts, helpers, build contract, and generated
  output are byte-identical to 1.5.1. SKILL.md is now a lean
  orchestration layer; the detail lives where it is easier to maintain.
- **Three new reference files** hold the relocated content:
  - `references/proofreading.md` — the full pre-build proofreading
    checklist (was the body of "Proofread before building").
  - `references/authoring-and-pitfalls.md` — the Inline Code guide and
    the common pitfalls (never pre-encode characters, single-quoted
    Python strings, don't insert page breaks proactively).
  - `references/quick-parts.md` — why Quick Parts are a property of the
    `.dotx` rather than generated documents, plus the installation-guide
    structure.
- **SKILL.md sections condensed**: the "Hard rules", "How the build
  works", "Workflow", "Proofread", and "Invite further refinement"
  sections were tightened to their essential rules, each pointing to the
  relevant reference file for the rationale and examples. A consolidated
  "Reference files" section now lists all seven references.

### Notes

- This release is documentation-only. `render_components.py`,
  `build_from_template.py`, `validate_output.py`, and the embedded
  `.dotx` are unchanged from 1.5.1. The 1.5.1 DocumentTitle fix is fully
  preserved (the rule lives in the condensed "Hard rules" section and
  the full explanation in `references/components-reference.md`).
- Motivation: an external skill review flagged an *older* SKILL.md
  (162 lines, python-docx-based, not referencing the bundle). That
  version was already superseded; this refactor brings the current,
  correct SKILL.md back under the line-count gate while keeping the
  bundle-first, XML-based approach.

## [1.5.1] — 2026-05-29

### Fixed

- **DocumentTitle (the `Title`-styled `documenttitle` content control)
  was not reliably set.** Previously `title("...")` emitted a plain
  `Title` paragraph and the template's `documenttitle` content control
  was discarded entirely — so the title on page 3 (cover+TOC documents)
  or page 1 (cover-less documents) depended on Claude remembering to
  call `title()` and was missing whenever it was forgotten. The build
  now always produces the real `documenttitle` content control:
  - `title("...")` emits a directive that the build script turns into
    the template's `documenttitle` SDT (Title style) **at the position
    where `title()` was called** — so placing it after `toc(...)` keeps
    the title on the first content page.
  - **Safety net:** in a cover document, if no `title()` was emitted,
    the build fills the `documenttitle` control automatically from the
    cover title and positions it just after the TOC (via a new
    `<!-- EURICOM_AFTER_TOC -->` anchor that `toc()` now emits). The
    DocumentTitle is therefore never left empty.
- **Both title content controls are now filled.** The template's
  `covertitle` (cover) and `documenttitle` (content) are separate,
  non-linked fields. The build fills both with the same content — the
  cover title from `cover_page(...)` and the document title from
  `title(...)` (or, as a fallback, also from the cover title). Editing
  one in Word does not change the other; they are intentionally not
  auto-synchronised.

### Changed

- `render_components.title(text)` no longer returns a `Title` paragraph;
  it returns an `EURICOM_DOCTITLE_DIRECTIVE` marker. The signature and
  intent are unchanged — callers still call `title("My title")` — but
  the output is now the proper content control. No other helper
  signatures changed.
- `render_components.toc(...)` appends an internal `EURICOM_AFTER_TOC`
  marker after its trailing page break. The marker is consumed and
  stripped by the build script and never appears in the output.
- `build_from_template.py` gained `extract_documenttitle_sdt(...)` and
  the document-title placement / safety-net logic in
  `build_document_xml`. The embedded `.dotx` template is unchanged.

## [1.5.0] — 2026-05-26

This release combines several months of template iterations (v1.4 →
v1.7) with new API helpers for inline code. It's a single deployment
step: the previously drafted 1.5.0 with v1.6 was never installed, so
this supersedes it.

### Added

- **`inline_code(text)` helper** in `render_components.py`. Produces
  a `(text, props)` tuple keyed for the new `InlineCodeChar`
  character style. Use inside `rich_paragraph(...)` or
  `bullet_rich(...)` to wrap file paths, filenames, environment
  variables, commands, keyboard shortcuts, and short menu/UI
  fragments. Aptos Mono, dark teal text, light teal background, 11pt.
- **`bullet_rich(runs, level)` helper**. The existing `bullet(text)`
  only accepts plain text; `bullet_rich` accepts the same
  `(text, props)` tuples that `rich_paragraph` does, so bullets can
  contain inline code or other formatted runs without falling back to
  bullet-glyph-in-prose hacks.
- **`rstyle` prop on `rich_paragraph` runs**. Lets a single run
  reference a character style by ID — e.g. `{"rstyle":
  "InlineCodeChar"}`. The `inline_code(...)` helper is the
  recommended way to produce these tuples; this prop is the
  underlying mechanism if you need a different character style.

### Changed

- **Embedded template upgraded to v1.7** (ships as the unversioned
  `assets/Euricom_Generic_Template.dotx`). User-visible changes since
  v1.4:
  - **Bullet 1 line height raised from 240 to 280 twips** (~17% more
    breathing room). Bullet 2 unchanged.
  - **Quick Parts in the template's glossary**: `Note - Tip`,
    `Note - Waarschuwing`, `Note - Alarm`, `Note - Info`, and
    `Color Picker` in the Euricom category, plus `Quote` in General.
    Caveat: these are only visible in Word's Building Blocks
    Organizer when the .dotx is loaded as a template (global template
    or attached). They do not appear when a user opens a generated
    `.docx`, even though the glossary XML is physically embedded.
    Word resolves Building Blocks from loaded templates, not from the
    current document. Helpers like `note(...)` and `quote(...)`
    produce visually identical output regardless, so generated docs
    look the same as hand-assembled ones.
  - **`InlineCode` (paragraph) and `InlineCodeChar` (character)
    styles** added to the template. Linked styles, so applying one
    in Word switches between paragraph and inline mode naturally.
    Aptos Mono, dark teal `#014046`, light teal `#F1F5F6`
    background, 11pt.
  - **Multi-section structure expanded** in v1.7 (extra headers and
    footers per section). Transparent to the build script — it copies
    all headerN/footerN files unchanged.
- **Single canonical template in `assets/`.** Previously the folder
  shipped multiple .dotx versions (v1.1, v1.3, v1.4) and SKILL.md
  pointed to v1.1. None of the older copies were actively used by the
  build script. Now `assets/` holds exactly one file:
  `Euricom_Generic_Template.dotx`. The `find` pattern in SKILL.md
  still uses `Euricom_Generic_Template*.dotx` so a stale install with
  an older filename is tolerated.
- **SKILL.md "Hard rules" section rewritten** to reflect the v1.7
  template's own styleguide. Notable updates:
  - Concrete list of forbidden manual formatting (font sizes, manual
    colours, empty paragraphs for spacing, whole-paragraph bold).
  - Explicit rule: **use bulleted lists, not numbered lists** —
    headings already provide numbering in the document outline.
  - New "Inline Code" rules block: when to apply `InlineCodeChar`,
    the "use sparingly" guideline, and a prohibition on faking the
    style with ad-hoc run properties.
- **SKILL.md cleaned up** to remove hardcoded version references:
  - Help block no longer says "based on v1.4".
  - "Multi-section template (v1.1+)" section rewritten as
    "Multi-section structure" — explains build-script capability, not
    template versioning.
  - Page-break historical note about v1.1/v1.2/v1.3 removed.
  - Quick Parts section corrected: previous wording promised Quick
    Parts "survive intact" into generated documents, which was
    technically true at XML level but misleading at user-visible
    level. Now states the actual behaviour and the workaround
    (install .dotx as global template).
- **New SKILL.md section "Inline Code in body text"** with concrete
  examples of `rich_paragraph` + `inline_code` and
  `bullet_rich` + `inline_code` composition.
- **New SKILL.md section "Writing a Quick Parts installation guide"**.
  Points to v1.7's own styleguide content as the canonical reference
  for the Windows + macOS install instructions, so future generations
  of that guide stay consistent.
- **Build script docstring and `--template` help text** use the
  unversioned filename.

### Notes

- The 1.4 → 1.5 jump deliberately stays within MINOR. New helpers
  are additive; no existing function changed signature or behaviour.
  Documents built against 1.4 still build identically against 1.5,
  modulo the template-level changes (bullet spacing, Quick Parts
  presence in the glossary, new styles available).
- Filename convention for *output* documents (`<Name>-v01.docx`,
  etc.) is unaffected.

## [1.4.0] — 2026-05-26

### Added
- New workflow step in Scenario 1 (conversion): after `present_files`,
  if this is the *first* conversion in the conversation, Claude sends
  a short follow-up message inviting refinements with four concrete
  examples (tone-of-voice, content, structure, phrasing). Helps new
  users discover what's possible without being pushy. Skipped on
  subsequent conversions in the same chat, on the generation flow, and
  when the user has signalled they don't want commentary. Added as a
  dedicated section "Invite further refinement" in `SKILL.md`.

## [1.3.0] — 2026-05-26

### Changed
- **Tone-of-voice scope clarified.** The full style guide (sentence
  length, active voice, words to avoid, etc.) applies only when the
  skill *authors* a document (Scenario 2). On *conversions*
  (Scenario 1), the author's voice is the ground truth — only
  surface-level fixes are applied: typos, smart quotes, sentence-case
  headings, non-breaking spaces, obvious terminology inconsistencies.
  Sentence rewrites and word substitutions are off the table on
  conversions.
- Scenario 1 step 4 in `SKILL.md` rewritten to enumerate the limited
  set of allowed corrections and explicitly forbid stylistic
  rewriting.
- `references/tone-of-voice.md` gained a "When these rules apply"
  section at the top so the scope is visible from the first paragraph.

## [1.2.0] — 2026-05-26

### Added
- New mandatory workflow step **"Proofread before building"**, inserted
  between draft and build in both scenarios. Claude rereads the
  composed body in the source language (Dutch or English) before
  generating the .docx, catching typos, dt-errors, wrong-word swaps,
  inconsistent terminology, and similar surface issues that a
  mechanical spellchecker would miss. Added as a dedicated section
  in `SKILL.md` with a checklist.

## [1.1.0] — 2026-05-26

### Added
- `toc()` now accepts an optional `entries` parameter. When supplied
  with a list of H1 chapter titles, the TOC field gets pre-rendered
  content: a styled F9 update hint followed by one TOC1 paragraph
  per chapter, with explicit number prefixes (`1.`, `2.`, ...). This
  makes the placeholder readable in iOS Quick Look, Pages, and any
  other viewer that doesn't auto-update fields, while Word still
  treats the whole block as a TOC field and replaces it on F9.
- The F9 hint is rendered in italic grey (#808080) with a leading
  pencil glyph (✎) so it's visually distinct from real TOC entries.

### Changed
- **File naming convention tightened for iOS compatibility.** The
  recommended pattern is now `<Documentnaam>-v<NN>.docx` (no spaces,
  no dots other than the extension, two-digit version). The previous
  pattern (`<Documentnaam> v<version>.docx`, e.g. `... v0.1.docx`)
  produced files that preview as blank in the iOS Files app — Quick
  Look stumbles on the space and the dotted version. Word desktop
  was unaffected, so the bug surfaced late.
- Corrected an outdated reference to "Euricom Generic Template v1.1"
  in the skill help block — the skill is tuned for v1.4+.

### Notes
- The `.dotx` template files in `assets/` are unchanged in this
  release. Only the skill scripts and documentation were updated.

## [1.0.0] — earlier

Initial versioned baseline. Covered:
- `cover_page`, `toc`, `heading` (H1–H3), `paragraph`, `h1_intro`,
  `bullet`, `note` (Tip/Alarm/Waarschuwing/Info), `quote`, `table`,
  `page_break`, `body`, `title`.
- Multi-section template structure with correct page numbering from
  page 1 (template v1.1+).
- Heading1 no-auto-break behaviour (template v1.4+).
- `build_from_template.py` and `validate_output.py` scripts.
