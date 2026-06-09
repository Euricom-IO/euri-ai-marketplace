# Slide logic

How to turn a message into the right slide, and how to structure a deck. The
per-layout filling rules below are distilled from the template's own Base
Library notes - read them live with `python scripts/catalogue.py`.

## Choosing a slide per message

For each thing you want to say, decide in this order:

1. Is it a **chapter break**? -> `section` (dark). Keep its title in sync with
   the agenda.
2. Is it a **single strong statement / customer quote**? -> `quote` (sparingly).
3. Does a **Components Library** entry fit (e.g. an agenda / table of
   contents)? -> `use_component`.
4. Is it **a few parallel points**? -> `cards` with an icon each, or
   `icon_list` (a rich, full-height alternative to bullets). Use plain
   `content` bullets only for genuinely list-like detail.
5. Is it **structured**? -> a `components.py` builder on `content_blank`:
   numbers -> `kpi_row`; one core message -> `statement`; steps -> `process_flow`;
   time -> `timeline`; two options -> `comparison`; levels -> `maturity`;
   tabular -> `data_table`.
6. Is it **a genuine decision or risk**? -> a semantic `note` (succes / info /
   waarschuwing / risico): a slim rounded semantic bar + icon + label, light and
   slide-native. Use sparingly — at most one per slide, often none; for an
   informational aside prefer a `statement` with one semantic-coloured word.
   Placement is automatic: a `note` stacks **below** any content already on the
   slide and is skipped when the canvas is full, so it never overlaps a builder
   or another note. Pass an explicit `y=` only when you want to force a
   position.

Design the richest fitting form, not the easiest: give one idea per slide a
strong visual anchor, add an icon where a builder supports it, fill the content
area, and vary the composition so consecutive slides don't look alike. You are
not limited to the component library - build what the message needs, within the
brand.

## Framing the deck (three dials)

Before building, settle three dials and let them steer the choices. In a chat,
always ask: a one-line "I understood your material — a few questions to be sure",
then the three dials as three separate multiple-choice questions plus an open
fourth ("Wil je nog iets toevoegen?" — Nee / free text); pre-select on each what
the prompt and content imply. In a non-interactive run, infer them instead (see
SKILL.md step 0). Guidance in the user's prompt outweighs everything: explicit
prompt instruction > what the source implies > skill defaults, stays in force for
the whole build, and is never overridden by the answers.

- **Visual richness (sober ◄► rich) — the anchor:** richer -> more
  `cards(style="tonal")` and `style="accent"`, more `statement`, icons on most
  slides; soberer -> mostly plain white/steel cards and restrained composition.
  Steel stays the default body either way.
- **Afwisseling (consistent ◄► afwisselend):** variation *across* slides, not
  richness within one. Consistent -> a small set of layouts, the same card
  treatment, a calm repetitive rhythm; afwisselend -> switch builders and card
  styles slide-to-slide (`kpi_row`/`cards`/`statement`/`icon_list`,
  `cap`/`tonal`/`accent`). Rich-but-consistent and sober-but-afwisselend are both
  valid, which is why it is its own dial.
- **Text density (little ◄► lots):** more text -> `icon_list`, fuller card
  bodies, the odd bullet `content`, denser tables; less text -> headline + one
  visual per slide, short bodies, more slides. Usually the clearest from the
  source itself.

Semantic colour (succes / info / waarschuwing / risico) is not a dial: use it
only at a genuine risk / win / decision, sparing by default. It still works in
ALL forms — a `note`, a semantic `color=` on a KPI/statement, a coloured word or
icon — always one accent per slide and never a large fill.

Card colour lives in the *style*, not new hues: `cap`/`fluo` (the default fluo
top cap), `tonal` (midnight tints per card), `accent` (one hero card), `plain`
(no green). One treatment per slide.

## Deck structure

- Start with the **cover** (dark).
- Optionally an **agenda** (Components Library) right after.
- Group content under **section** dividers; keep section titles consistent with
  the agenda.
- Alternate **steel** and **white** content slides for rhythm; lean towards
  steel. The dark cover/sections/closing give the dark contrast, so you rarely
  need extra dark content slides.
- **Always close with a dark closing slide** (`section`-style dark) as the final
  slide: a short, contextual sign-off — a thank-you, the core takeaway, a call to
  action, or contact details — chosen to fit the deck and kept on-brand. A
  `quote` may come just before it, but the last slide is dark.

## Per-layout filling rules

**Cover** - `eyebrow` = presentation type, e.g. "SOLUTION PROPOSAL — VOOR
[KLANT/EURICOM/INTERN/PUBLIEK]". `title` = presentation title; if it runs to two
lines the tagline/intro sit a little lower (handled). `subtitle` = a short
tagline / emotional pay-off (renders fluo). `intro` = one or two sentences of
context (steel colour). `date` = today's date (steel). `author` = presenter.

**Content (steel & white)** - `eyebrow` = context; can name the chapter and bind
several slides. `title` = slide title, NEVER more than one line. The body may be
bullets OR be replaced by any visual (KPIs, cards, timeline, charts, table).
Left-align by default; centre when a design benefits. Leaving the right side
emptier is fine. White elements: shadow on white, none on steel.

**Section** - `eyebrow` = section number/label (e.g. "DEEL 03"); your choice of
prefix, kept consistent across the deck and the agenda. `title` = section title
(in sync with the agenda). `description` = a sentence summarising the section.

**Quote** - `quote` = the statement. `author` + `role`. Use sparingly.

**Agenda (component)** - a table; add/remove rows. The agenda and its title may
be reworded to the context (e.g. "Inhoud", or a creative framing).

## Language & tone

Default to the user's language (usually Dutch for Euricom). Keep titles short,
eyebrows in caps
