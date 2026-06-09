# Proofreading checklist — Euricom Word template

Before calling `build_from_template.py`, reread your composed body
critically once. This is a non-skippable step — it costs little and
catches the errors that are most embarrassing in a delivered .docx.

The pass applies regardless of language: Dutch source → proofread in
Dutch, English source → proofread in English, mixed → both. Match the
source's variant (Belgian-Dutch vs. Netherlands-Dutch; British vs.
American English) and stay consistent throughout.

## What to look for

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

## How to do it

Do not just glance at the body string. Read it in sequence as a reader
would, top to bottom, and fix errors directly in the compose script
(the source of truth) — not in the resulting XML. Recompose, then
build.

If you find more than a handful of issues, that's a signal to slow
down on the next draft rather than fix-and-ship.
