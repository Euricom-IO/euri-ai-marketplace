---
name: euricom-word-template
version: 1.5.0
description: "Produce professional .docx documents in the Euricom brand template — Aptos fonts, brand colours, logo header, footer, cover page, TOC, callouts, quotes. Trigger when the user (1) mentions 'Euricom', 'huisstijl', 'onze template', 'brand template'; (2) asks to convert a document, PDF, markdown or text into the Euricom or company template, even without naming Euricom (e.g. 'zet dit in onze template', 'maak hier een nette versie van', 'apply our brand template'); (3) asks for any Euricom deliverable type — voorstel, whitepaper, PRD, architectuurdocument, AI-strategie, analyse, rapport, memo, meeting notes, governance document; or (4) uploads a .dotx/.docx and asks to apply it as a template. The Euricom template ships embedded in this skill's assets/ — do NOT ask the user to upload it before verifying via `find /mnt/skills`. Prefer this skill over the generic docx skill whenever Euricom branding is implicit or explicit, because only this one applies the correct fonts, colours and components."
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
  branded data tables with zebra striping and optional total rows,
  and **Inline Code** for file paths, commands, and keyboard
  shortcuts in body text. Notes, quote, and color picker are also
  Quick Parts in the .dotx for users who install it as a template
  (see the dedicated section below for the caveat about generated
  .docx files).
- **Languages**: follows the source language; Belgian-Dutch by default
  for new documents unless told otherwise.
- **Template**: based on the Euricom Generic Template that ships in
  `assets/Euricom_Generic_Template.dotx`. Multi-section structure with
  correct page numbering from page 1; Heading1 does not auto
  page-break.
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

### Multi-section structure

The Euricom template uses a **multi-section structure** to keep page
numbering clean:

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

**Single-section template fallback.** The build script also handles
single-section templates (an older shape that didn't separate cover
from content). If it sees only one `sectPr` it duplicates it and uses
the cover-flags-stripping path. This isn't actively used today but is
kept as defensive logic in case the template structure is ever
simplified again.

### The complete flow

```
user request
    │
    ▼
[locate template]  ──── prefer user-uploaded .dotx, fall back to assets/Euricom_Generic_Template.dotx
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
[present file via present_files]
```

## Locating the template (CHECK FIRST — DO NOT ASK)

**Critical**: before asking the user for anything, verify the template
yourself. The skill ships with the template embedded at a known path.
The reason this section is at the top of the workflow is that previous
runs have failed by asking the user to upload the template even though
it was already present in the skill folder — that wastes the user's
time and undermines trust in the skill.

### Step 1: locate the skill directory

Custom skills in Claude.ai are unpacked under `/mnt/skills/`. The
exact path depends on whether the skill is personal or org-provisioned,
so don't hard-code it. Find it dynamically:

```bash
find /mnt/skills -type f -name "Euricom_Generic_Template*.dotx" 2>/dev/null | head -5
```

This will return a path like:
- `/mnt/skills/user/euricom-word-template/assets/Euricom_Generic_Template.dotx` (personal upload), or
- `/mnt/skills/organization/euricom-word-template/assets/Euricom_Generic_Template.dotx` (Team/Enterprise provisioned)

**Capture that path and reuse it.** All subsequent build commands need
to point at this exact file. The wildcard in the `find` pattern lets
this also match older filenames like `Euricom_Generic_Template_v1_4.dotx`
in case an outdated copy of the skill is installed somewhere — just take
the first match.

### Step 2: prefer a user-uploaded template over the embedded one

If the user has uploaded a `.dotx` or `.docx` in the current chat
that looks like a Euricom template (filename contains `euricom` or
`template`, or the user explicitly says "use this template"), prefer
that over the embedded copy — it may be a newer revision. Check with:

```bash
ls /mnt/user-data/uploads/ 2>/dev/null
```

### Step 3: only ask for an upload if BOTH are missing

Only fall back to asking the user if **both** of the following are
true:

1. `find /mnt/skills -name "Euricom_Generic_Template*.dotx"` returned nothing
2. `/mnt/user-data/uploads/` does not contain a recognisable Euricom template

In that rare case, say something like:

> "I can't find the Euricom template — neither in this skill's assets
> nor in your uploads. Can you upload the `.dotx` file so I can apply
> the styling?"

Do NOT ask the user to upload the template **before** running the
`find` command. If you find yourself drafting a "please upload"
message without having checked `/mnt/skills/` first, stop and check.

## Workflow for each scenario

### Scenario 1 — Convert existing content

When the user uploads a source file (or pastes content) and asks to
put it in the Euricom template:

1. **Read the source.** Use `extract-text` for `.docx`, `.odt`, `.epub`;
   `pdftotext` or the `pdf-reading` skill for `.pdf`; `cat` for `.md`
   or `.txt`. For very large sources, sample first to understand
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

4. **Apply surface-level tone of voice only.** This is a conversion,
   not a rewrite — the author's content, structure, argument, and
   voice stay intact. Only fix things that are objectively wrong or
   purely typographic:
   - Typos, dt-errors, wrong-word swaps (`hen/hun`, `then/than`).
   - Smart quotes (the renderer does this automatically — don't
     hand-encode).
   - Normalise capitalisation in headings to sentence case; drop
     trailing colons (`Inleiding:` → `Inleiding`).
   - Inconsistent terminology that's clearly a slip (the same
     concept spelled three different ways).
   - Non-breaking spaces between numbers and units (`5 GB`, `€ 100`).

   **Do not** rewrite sentences for shortness, swap "uitdaging" for
   "probleem", convert passive voice to active, or apply other style
   preferences from `references/tone-of-voice.md`. Those rules guide
   *new* content authored by the skill (Scenario 2). On a conversion,
   the author's voice wins.

5. **Decide on cover / TOC.** Roughly: cover and TOC for documents
   ≥ 8 pages or any external deliverable. Skip both for memos and
   short internal notes. See `references/document-types.md`.

6. **Discard the template's example content.** The embedded template
   contains its own "Werken met de Euricom template" handbook text as
   placeholder. The build script replaces the entire body, so this
   gets discarded automatically — but be careful never to copy any of
   that handbook prose into the new document.

7. **Proofread (see "Proofread before building" below).**

8. **Build, validate, present.**

9. **Invite further refinement (first conversion only).** After
   `present_files`, if this is the *first* conversion in the current
   conversation, add a short follow-up message inviting the user to
   ask for refinements. See "Invite further refinement" below for the
   exact wording and when to skip it. On subsequent conversions in
   the same chat, just deliver the file — no repeat invitation.

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

6. **Proofread (see "Proofread before building" below).**

7. **Build, validate, present.**

## Proofread before building

Before calling `build_from_template.py`, reread your composed body
critically once. This is a non-skippable step — it costs little and
catches the errors that are most embarrassing in a delivered .docx.

The pass applies regardless of language: Dutch source → proofread in
Dutch, English source → proofread in English, mixed → both. Match the
source's variant (Belgian-Dutch vs. Netherlands-Dutch; British vs.
American English) and stay consistent throughout.

**What to look for:**

- **Typos and missing letters.** Especially in headings, the cover
  title, and the first sentence of each chapter — the spots a reader
  hits first.
- **Verb agreement and Dutch dt-rule.** For Dutch: subject-verb
  agreement, correct dt-endings (`hij wordt`, `hij heeft geword*en*`,
  `verwacht` vs. `verwachtte`). For English: third-person -s and
  irregular past forms.
- **Wrong-word swaps.** Homophones and look-alikes: `dan/als`,
  `hen/hun`, `het/de`, `effect/affect`, `then/than`, `its/it's`,
  `their/there/they're`. These slip past most spellcheckers because
  each word is itself valid.
- **Inconsistent terminology.** If the document introduces a concept
  ("EPA", "macro-laag", "delivery manager"), use that exact spelling
  and casing everywhere. Don't drift to "Epa", "Macro-laag", or
  "Delivery Manager" mid-document.
- **Inconsistent capitalisation in headings.** The template uses
  sentence case for headings. Don't mix in title-case.
- **Punctuation spacing.** No space before `:`, `;`, `.`, `,`, `?`,
  `!`. One space after. Em-dashes (`—`) have spaces around them in
  Dutch and English alike, in line with the template's tone guide.
- **Duplicate words.** "de de", "the the", "is is" — easy to miss
  while writing, jarring to read.
- **Numbering and references.** If text says "in hoofdstuk 3 …",
  hoofdstuk 3 must actually exist and be about what the reference
  claims.
- **Names and proper nouns.** Author names, product names, client
  names — these are the costliest errors. Double-check spelling.

**How to do it.** Do not just glance at the body string. Read it in
sequence as a reader would, top to bottom, and fix errors directly in
the compose script (the source of truth) — not in the resulting XML.
Recompose, then build.

If you find more than a handful of issues, that's a signal to slow
down on the next draft rather than fix-and-ship.

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

## Invite further refinement

Conversions (Scenario 1) end with a short follow-up message that
invites the user to ask for further refinements. The goal is to help
new users discover what's possible without being pushy — many users
don't realise they can iterate on the converted document.

**When to send it:** only after the *first* conversion in a given
conversation. Track whether this is the first conversion by looking
at the conversation history — if there's no prior `present_files`
call for a converted .docx, this is the first. Subsequent conversions
in the same chat just deliver the file with no extra message.

**When to skip it entirely:**
- Generation flow (Scenario 2). Claude already authored the document
  applying the full tone-of-voice; the invitation would be redundant.
- The user has explicitly indicated they want no follow-up ("just
  convert it", "no commentary").
- The user is clearly an experienced user of the skill (they've used
  it across earlier conversations, they're using technical
  vocabulary about the skill, etc.).

**Where it goes:** as a short message *after* the `present_files`
call, not before. The file is the deliverable; this is the friendly
suggestion alongside it.

**Wording:** roughly the following, adapted to the source language
(Dutch / English) and lightly varied so it doesn't read like a canned
response. Keep it short — four examples, no more.

> Het bestand staat klaar. Vraag me gerust om verfijningen —
> bijvoorbeeld:
> — de tone-of-voice scherper maken (kortere zinnen, actieve stem)
> — iets toevoegen of inkorten
> — de structuur herzien (volgorde van hoofdstukken, extra samenvatting)
> — specifieke termen of zinnen anders verwoorden

English equivalent:

> The file is ready. Feel free to ask for refinements — for example:
> — tighten the tone of voice (shorter sentences, active voice)
> — add to or trim the content
> — restructure (reorder chapters, add a summary)
> — rephrase specific terms or sentences

The four examples are deliberate: tone-of-voice, content, structure,
phrasing. They cover the spectrum of useful follow-ups without
overwhelming a new user.



## Quick Parts: a property of the .dotx, not of generated documents

The template ships six user-facing Quick Parts: `Note - Tip`,
`Note - Waarschuwing`, `Note - Alarm`, `Note - Info`, and
`Color Picker` in the **Euricom** category, plus `Quote` in **General**.
All six live in the `AutoText` gallery of the template's glossary.

**Important:** these are available to a Word user only if the
`.dotx` is loaded as a template — either as the active document
template, or as a global template (File → Options → Add-ins →
Manage: Templates → Go → Add the Euricom `.dotx`). They are **not**
visible in the Building Blocks Organizer when opening a generated
`.docx`, even though the glossary XML is physically present inside
the file. This is Word's own design: Building Blocks are sourced
from loaded templates, not from the current document.

This is documented by Microsoft: Building Blocks can only be saved
in a template (document template or global template). Saving a
.dotx-with-Quick-Parts as .docx — which is essentially what the
build script does, content-type-wise — drops the user's access to
those Quick Parts even though the data survives in the zip.

**Practical guidance for users who want the Quick Parts:**

> Install the Euricom template once as a global template. In Word:
> File → Options → Add-ins → bottom-of-screen Manage dropdown →
> Templates → Go → Add → select `Euricom_Generic_Template.dotx`.
> From then on, Insert → Quick Parts → Building Blocks Organizer
> shows the six Euricom blocks in every Word session.

**What the skill does about this**: nothing special. The build
script doesn't try to preserve UI-level Quick Parts in the output
.docx, because it can't — that's not how Word resolves Building
Blocks. The skill renders notes, quotes, and tables programmatically
via the helpers in `render_components.py`. The output of those
helpers is byte-equivalent to what a human gets by inserting the
Quick Part manually, so a generated document looks identical to
one assembled by hand.

## Inline Code in body text

For file paths, filenames, environment variables, commands, keyboard
shortcuts, and short menu/UI fragments, use the `InlineCodeChar`
character style (Aptos Mono, dark teal text, light teal background,
11pt). Compose runs via the `inline_code(text)` helper inside a
`rich_paragraph(...)` or `bullet_rich(...)` call:

```python
from render_components import rich_paragraph, bullet_rich, inline_code

# Inline code in lopende tekst
rich_paragraph([
    ("Open de Verkenner en plak ", {}),
    inline_code("%APPDATA%\\Microsoft\\Word\\STARTUP"),
    (" in de adresbalk. Kopieer ", {}),
    inline_code("Euricom_Generic_Template.dotx"),
    (" naar deze map.", {}),
])

# Inline code in een bullet
bullet_rich([
    ("Bestandsnamen — ", {}),
    inline_code("package.json"),
    (", ", {}),
    inline_code("README.md"),
    (".", {}),
])
```

**Apply to:** file paths (`C:\Users\jdoe\Documents`,
`~/Library/Preferences`), filenames
(`Euricom_Generic_Template.dotx`), env vars (`%APPDATA%`, `$HOME`),
commands (`git status`), shortcuts (`Ctrl+Alt+V`), and short UI
fragments the reader must recognise verbatim
(`Invoegen → Snelonderdelen`).

**Don't apply to:** whole sentences (if a sentence is "code", it
wants a different structure), prose where you just want emphasis
(use italic), or to highlight terminology in a definition list (use
bold instead).

Five inline-code fragments in one paragraph reads as noise. If you
find yourself reaching for that density, restructure into a bullet
list with one code fragment per bullet, or into a table with two
columns (description + code).

## Writing a Quick Parts installation guide

Users who want the in-template Quick Parts available in Word's UI
must install the `.dotx` as a global template — a one-time per-laptop
action (see the Quick Parts section above for the underlying reason).
Generated documents that explain this should include both Windows and
macOS paths. The canonical version of the instructions lives in the
v1.7 template's own styleguide content under "Quick Parts activeren
in Word". When asked to write or update this guide, follow that
structure: a one-paragraph intro, then a Windows section with two
routes (STARTUP-folder + Word-instellingen), then a macOS section
with two routes (Word-instellingen + Startup-folder), with a
`Waarschuwing`-note after each platform explaining the limitation of
the secondary route. Use `InlineCodeChar` for every file path,
filename, and shortcut throughout.

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

### Don't insert page breaks proactively

In the Euricom template, `Heading1` does **NOT** auto-break to a new
page. This is intentional: document density varies, and forced breaks
before every chapter often produce ugly half-empty pages. Where to
break is an editorial decision the human author makes, not the skill.

**The only page break the skill emits automatically is the one after
the TOC** (built into `toc()`). Anywhere else, do not call
`page_break()` "for safety" between chapters.

```python
# Wrong — author hasn't asked for breaks; let the flow happen
heading("Hoofdstuk 1", 1),
paragraph("..."),
page_break(),               # ← don't do this
heading("Hoofdstuk 2", 1),

# Right — the flow continues naturally
heading("Hoofdstuk 1", 1),
paragraph("..."),
heading("Hoofdstuk 2", 1),  # H1 does NOT auto-break
```

**When `page_break()` IS appropriate:**

- Forcing a break before an oversized table that would split
  awkwardly across pages
- Isolating a full-page quote or image
- Author has explicitly asked to break at a specific spot

These are editorial exceptions, not defaults.

## Hard rules from the template itself

These come from the Euricom template's own styleguide (the canonical
reference is the v1.7 .dotx itself, which documents these rules in its
embedded styleguide content). Every document the skill produces must
respect them.

### Styling and formatting

- **Use the template's styles. Never simulate them with manual
  formatting.** This is the single most important rule. Concretely,
  the following are forbidden anywhere in generated documents:
  - Setting a specific font size (e.g. 14pt) to fake a heading —
    reference `Heading1` / `Heading2` / `Heading3` instead.
  - Setting a specific colour by hand for emphasis — use the styles
    (`InlineCode`, note callouts, etc.) that already carry the right
    brand colour.
  - Adding empty paragraphs to create spacing between sections —
    paragraph styles already include the correct `spacing` values.
  - Applying bold or italic to whole paragraphs for emphasis. Use it
    on a phrase inside a paragraph if needed, never to substitute for
    a heading or a callout.
- **Maximum heading depth: H3.** If the structure wants H4 or deeper,
  restructure instead — split into more H1's, or fold the deepest
  level into prose.
- **Maximum bullet depth: 2 levels.** Split or restructure if you
  need three.

### Bullets and lists

- **Use bulleted lists, not numbered lists.** Headings already provide
  numbering in the document outline; an extra numbered list on top is
  redundant and visually noisy. If you need to convey order in a
  bulleted list, write `Eerst …`, `Daarna …`, `Tot slot …` in the
  bullet text. The one exception is step-by-step procedures where the
  step number is itself meaningful (e.g. "Step 3 must happen after
  Step 2") — even there, prefer prose like "Stap 3:" written into the
  bullet text over Word's auto-numbering, because auto-numbering does
  not survive copy-paste across documents reliably.
- **Keep bullets short, content-rich, and few.** A bullet list with
  twelve entries is usually a sign that the content wants a table or
  prose, not a list.

### Inline Code

- **Use `InlineCodeChar` for: file paths, filenames, environment
  variables, commands, keyboard shortcuts, and short menu/UI
  fragments** the reader must recognise verbatim. Apply via the
  `inline_code(text)` helper inside `rich_paragraph(...)` or
  `bullet_rich(...)`.
- **Use it sparingly.** Five code fragments in one paragraph reads as
  noise and destroys the contrast that gives the style its meaning.
  If a whole sentence is code, extract the essence or use a code
  paragraph instead.
- **Don't fake it.** Never apply Aptos Mono + dark teal + light
  background as ad-hoc run properties to simulate the style — that
  detaches it from the central definition and breaks find-by-style
  workflows for editors.

### Notes

- **Notes are semantic, not decorative.** Pick the right type (Tip,
  Alarm, Waarschuwing, Info) for what the note actually conveys.
  Don't use a Tip just because you like the green.
- **One to two notes per page maximum.**

### Cover, TOC, and metadata

- **Cover and TOC are for documents ≥ 8 pages or external
  deliverables.** Skip both for memos and quick notes.
- **The meta line on the cover ("voor"-vermelding) is always
  uppercase.** `VOOR EURICOM`, `CONFIDENTIEEL`, `VOOR <CLIENT>`.
- **No version number inside the document body.** Versioning lives in
  the filename suffix (`v0.1`, `v1.0`, `v1.1`, `v2.0`).
- **File naming.** When the user asks for a filename, follow:
  `<Documentnaam>-v<NN>.docx` — e.g. `AI-strategie-2026-v01.docx`.
  Default to `v01` for drafts; the user can rename.
  **No spaces and no dots in the filename** (other than the single
  `.docx` extension). Spaces and dotted versions like `v0.1` break
  iOS Quick Look — files preview as blank from the Files app even
  though Word desktop opens them fine. Use hyphens for separation
  and a digits-only version suffix (`v01`, `v10`, `v11`, `v20`).

## Output handling

- **Where to write.** Final `.docx` goes to `/mnt/user-data/outputs/`
  with a meaningful filename (per the naming convention above).
- **Validate before presenting.** Run `validate_output.py` and only
  call `present_files` if it passes. If validation fails, surface the
  error to the user and try to fix it rather than presenting a broken
  file.
- **Present succinctly.** Use `present_files` to expose the file, with
  a one-or-two-sentence summary of what was produced. Don't paste the
  whole document content back to the user — they have the file.

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
