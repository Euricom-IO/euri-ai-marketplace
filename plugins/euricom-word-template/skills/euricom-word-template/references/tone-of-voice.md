# Tone of voice — Euricom documents

This is the writing style baked into the template's own example text.
When the source language is Dutch (Flemish/Belgian-Dutch), follow it
closely. When the source is another language (English, French),
mirror these principles in that language — clarity, restraint, and
respect for the reader translate.

## When these rules apply (and when they don't)

This guide is for **new content authored by the skill** (Scenario 2 in
`SKILL.md` — generating a document from a prompt). There Claude is the
author and the full guide applies: sentence length, active voice,
words to avoid, the lot.

For **conversions of existing content** (Scenario 1) the rules are
much narrower. The author's voice is the ground truth; the skill's job
is to apply Euricom's *visual* identity, not to rewrite their prose.
On a conversion, apply only the surface-level items: smart quotes,
sentence-case headings, non-breaking spaces, fixing obvious typos and
inconsistent terminology. Leave sentence length, voice, word choice,
and paragraph structure as the author wrote them — even if some
phrasing isn't what this guide would recommend for new content.

If a user explicitly asks "rewrite this in our tone of voice", treat
that as Scenario 2 on existing material: the full guide applies.

## Core principles

The template's own description of itself is the best summary:

> *Professioneel, rustig en onderhoudbaar.*

Three words doing real work:

- **Professioneel** — accurate, well-structured, no slang, no jokes.
- **Rustig** — calm pacing, short sentences, no exclamation marks, no
  superlatives. White space and styles do the visual work; the prose
  doesn't have to shout.
- **Onderhoudbaar** — sentences and sections can be edited or moved
  without rewriting everything around them. Avoid sprawling
  paragraphs that bury one idea inside another.

## Belgian-Dutch specifics

When writing in Dutch, prefer Flemish/Belgian conventions over the
Netherlands variant:

- **U** by default for external/client audiences, **je/jij** for internal
  collaborative documents. When in doubt, U is safer.
- Belgian-Dutch vocabulary: *appartement* (not *flat*), *gsm* (not
  *mobieltje*), *binnenkort* (not *binnen kort*), *bij voorkeur* (not
  *bij voorkeur uit*).
- Numbers in prose follow the European convention: *€ 1.500,00* with
  a comma decimal and a period thousands separator. The euro symbol
  precedes the amount with a non-breaking space.
- Dates: *14 maart 2026* in prose, ISO `2026-03-14` in tables and
  file metadata.

## Sentence-level habits

- **Concrete verbs over abstract nouns.** "Wij optimaliseren het proces"
  → "Wij maken het proces sneller en eenvoudiger."
- **Active voice unless the actor doesn't matter.** "De architectuur
  werd ontworpen door het team" → "Het team ontwierp de architectuur."
- **Short sentences.** Aim for 15–20 words on average. A sentence over
  30 words usually wants to be two sentences.
- **One idea per paragraph.** If you can't summarise a paragraph in
  one sentence, it's doing too much.

## Words and phrases to avoid

| Avoid | Why | Use instead |
|---|---|---|
| *uitdaging* (overused) | Drained of meaning | *probleem*, *vraagstuk*, *moeilijkheid* — pick the one that's true |
| *synergie* | Empty corporate-speak | Describe the actual interaction |
| *leveraged*, *unlocked*, *empowered* | English jargon in Dutch | Plain Dutch verbs |
| *Wij geloven dat...* (without basis) | Performative | Replace with the evidence |
| *innovatief / disruptief* (as adjective for self) | Self-praise | Let the work speak |
| Excessive exclamation marks | Tone-deaf in formal context | Almost never use them |

## Typographic conventions

- **Smart quotes always.** Apostrophes and quotation marks should be
  curly (`'`, `'`, `"`, `"`) — the renderer handles this for you when
  you pass plain text.
- **En-dash** (`–`) for ranges (*2025–2026*) and parenthetical asides
  (`– zoals hierboven beschreven –`). Em-dashes (`—`) are uncommon in
  Dutch; prefer en-dash with spaces.
- **Non-breaking spaces** between numbers and units (`5 GB`, `€ 100`),
  between a name and a Roman numeral (`Wim II`), and before percent
  signs (`75 %`).

## Length calibration

| Document length | What this means in practice |
|---|---|
| Memo (1–3 pages) | Cut anything that isn't load-bearing. One idea per H1. |
| Short analysis (4–7 pages) | Add a "Samenvatting" only if the doc has a recommendation; otherwise let the structure speak. |
| Report / whitepaper (≥ 8 pages) | Always lead with an executive summary. The reader should be able to make a decision after reading just the H1Intros under each chapter. |

## When the source is English

If the user uploads English content and asks for Euricom-template
output, **don't translate unless they ask.** Keep the English; just
restructure it through the template. The styles, fonts, colours, and
components are language-agnostic.

If the user explicitly asks for translation, translate to the same
register: professional, calm, Belgian-Dutch by default unless they
specify Netherlands-Dutch.

## When the source is messy

Inherited content (PDFs of scanned docs, OCR'd material, hastily
written markdown) often has:

- Inconsistent capitalisation in headings (ALL CAPS sometimes, Title
  Case other times). **Normalise to sentence case** — the template's
  Heading1 style handles its own visual weight.
- Trailing colons on headings (`Inleiding:`). Drop them.
- Run-on paragraphs from PDF extraction. Re-paragraph at natural
  topic shifts.
- Bullet markers in prose (`* foo * bar`). Convert to actual bullets.
- Random bold or italics from PDF parsing. Strip unless they carry
  meaning (terms being defined, names of things).

The goal isn't to preserve every artefact of the source — it's to
produce a clean Euricom document the reader can use.
