# Authoring guide and common pitfalls — Euricom Word template

Detailed authoring guidance that supports the workflow in `SKILL.md`.
Read the relevant part when you reach it; you don't need to absorb it
all upfront.

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

## Never pre-encode characters in your input strings

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

## Use single-quoted Python strings when the content contains double quotes

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

## Don't insert page breaks proactively

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
