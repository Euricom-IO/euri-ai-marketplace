---
name: euricom-powerpoint-template
description: >-
  Produce professional .pptx presentations in the Euricom brand - Montserrat,
  brand colours, dark cover/section slides, content slides, quote slide, and an
  automatic page number. Trigger when the user (1) mentions 'Euricom' together
  with a presentation, deck, slides, or pitch; (2) asks to build, generate, or
  draft a PowerPoint/presentation/deck and Euricom branding is implied (e.g.
  'maak een presentatie', 'zet dit in een deck', 'bouw hier slides van', 'maak
  er een pitch van'); (3) asks to convert a document, notes, or outline into
  Euricom slides; or (4) uploads a Euricom PowerPoint template and asks to build
  on it. Works as a design system: a small set of master layouts plus a reusable
  Components Library, not a pile of one-off slides. Prefer this skill over the
  generic pptx skill whenever Euricom branding is implicit or explicit.
---

# Euricom PowerPoint Template

Generate branded `.pptx` decks that look hand-made by the same designer and stay
fully editable. The skill works from the Euricom template (it ships in
`assets/`, and the newest file the user uploads is used automatically).

> ## ⛔ ALWAYS START HERE — frame the deck first
>
> Before generating ANY slide, frame the deck on three dials: **visual richness**
> (sober ◄► rich), **afwisseling** (consistent ◄► afwisselend), and **text
> density** (little ◄► lots). Richness is the anchor; afwisseling refines it (how
> much the look varies slide-to-slide); density is mostly content-driven.
>
> **In an interactive chat, always ask — even when the content seems clear.**
> Open with one line that shows you understood the material ("Ik heb je [bron]
> begrepen — voor de zekerheid stel ik je nog enkele vragen"), then ask the three
> dials as **three separate multiple-choice questions** (never one combined
> question), plus a fourth, open one — *"Wil je nog iets toevoegen?"* — with a
> "Nee" option and room for free text. Use what the prompt and content imply to
> pre-select the recommended option on each dial, so confirming is one click.
> Wait for the answers before building.
>
> **The prompt outweighs everything and stays sticky.** Precedence, strongest
> first: (1) an explicit instruction in the user's prompt, (2) what the source
> implies, (3) skill defaults. A dial the user pinned in the prompt is the
> pre-selected answer and, once confirmed, holds for every later choice — the
> questions confirm and refine, they never override what the user explicitly
> stated.
>
> **In a non-interactive run** (scheduled task / flow) never block: infer all
> three dials, state the assumptions, and build.

## Mental model: clone a reference, then refill

The template is the single source of truth and is self-documenting. It carries
three native PowerPoint sections:

- **Base Library** - one filled, annotated example per master layout (cover /
  content-steal / content-white / section / quote). The speaker notes of each
  example explain how to fill it.
- **Components Library** - richer, composed reusable slides (e.g. an agenda
  table). Notes describe each component's purpose and how to adapt it.
- **Sample Presentation** - scratch space, ignored.

There is ONE consistent operation: **clone a reference slide and refill it.**
Cloning inherits everything the designer baked in - exact placeholder
formatting, the automatic page number, table styling - so you never rebuild the
theme and the output always matches the brand.

## Design rich, don't bullet

The biggest quality lever is composition. A title + bullet list is the
soberest possible slide; reach for it last, not first. For each slide, give one
clear idea a strong visual anchor and make the content fill the area:

- **Numbers** -> `kpi_row` (big figures, optional icons), not bullets.
- **A few parallel points** -> `cards` WITH an icon each, or `icon_list`
  (a rich, full-height alternative to bullets).
- **Cards carry the fluo top cap by default.** `cards(...)` now renders the
  Euricom standard boxed card: a subtle border with a rounded fluo-green top cap
  (matches the design system's card pages) — so the green accent shows without
  asking. `cards(style="tonal")` fills each card with a different midnight tint
  (deep -> muted teal) for a richer set; `cards(style="accent", accent=i)`
  makes one midnight 'hero' card stand out; `cards(style="plain")` is the sober
  no-green look. Pick ONE treatment per slide; never combine.
- **One core message** -> `statement` (a large takeaway with a fluo accent).
- **A point that needs real attention** (a genuine decision or risk) -> a
  semantic `note` (succes / info / waarschuwing / risico): a slim rounded
  semantic bar + icon + label, light and slide-native. Use sparingly — at
  most one per slide, often none. For an informational aside, prefer a
  `statement` with one semantic-coloured word over a note. Notes auto-stack
  and are skipped when the canvas is full, so they never overlap.
- **Steps / phases** -> `process_flow`; **time** -> `timeline`; **two options**
  -> `comparison`; **levels** -> `maturity`; **tabular data** -> `data_table`.
- **People** -> `team` (circular photos + name/role/body); **photos / moments**
  -> `image_grid` (rounded, cover-cropped photo grid, optionally beside a text
  column).
- Reserve `content(body=[...])` bullets for genuinely list-like detail, and even
  then prefer `icon_list`.

Add a relevant icon wherever a builder accepts one (`icons.NAMES`,
`icons.suggest("growth")`). Vary the composition across the deck so consecutive
content slides don't blur together — how far you push this is the *afwisseling*
dial (step 0). Fill the content area; leaving the right side a bit open is fine,
a half-empty slide is not.

## Workflow (follow in order)

0. **Frame the deck first.** Before building anything, settle the three dials
   below. **In a chat, always ask** — even when the content looks clear. Open
   with one line that shows you understood the material ("Ik heb je [bron]
   begrepen — voor de zekerheid stel ik je nog enkele vragen"), then put the
   three dials as **three separate multiple-choice questions** (not one combined
   question) and add a fourth, open question — *"Wil je nog iets toevoegen?"* —
   with a "Nee" option and free text. Pre-select on each dial the option the
   prompt and content imply, so confirming is one click; then wait for the
   answers. **In a non-interactive run**, infer the dials and state the
   assumption instead of blocking. Precedence everywhere, strongest first: an
   explicit instruction in the user's prompt > what the source implies > skill
   defaults — and a prompt instruction stays in force for every later choice; the
   questions confirm and refine, they never override it.

   - **Visual richness — sober ◄────► rich? (anchor)** Sober = mostly white/steel
     content slides, restrained composition, the occasional accent. Rich =
     tonal-midnight cards, accent/hero cards, statements, icons on most slides,
     more dark contrast. Maps to: how often to reach for `cards(style="tonal")`
     / `style="accent"`, `statement`, and icons. (Steel stays the default body
     even when rich — see "Rhythm and design notes".)
   - **Afwisseling — consistent ◄────► afwisselend?** This is variation *across*
     slides, not richness *within* one. Consistent = lean on a small set of
     layouts and keep the same card treatment for a calm, predictable rhythm;
     repetition is fine, even desirable. Afwisselend = actively switch builders
     and card styles slide-to-slide (`kpi_row` → `cards` → `statement` →
     `icon_list`, and `cap` → `tonal` → `accent`) for a lively rhythm. A deck can
     be rich but consistent (lots of decoration, same shape every slide) or sober
     but afwisselend (light slides that each look different) — that's why it is a
     separate dial. Maps to: how widely to vary builders and card styles over the
     deck. (The baseline "consecutive slides shouldn't blur together" still holds
     at the consistent end; this dial sets how far past that you push.)
   - **Text density — little ◄────► lots?** Little = headline + one visual per
     slide, short card bodies, more slides. Lots = fuller bodies, `icon_list`,
     occasional bullet `content`, denser tables. Usually the clearest from the
     source itself (a dense document → lots; loose bullets → little), so it is
     often inferable rather than asked. Maps to: builder choice and how much text
     each card/row carries.

   Semantic colour (succes / info / waarschuwing / risico) is not a dial: use it
   only where the content has a genuine risk, win or decision, sparing by
   default. It works in ALL forms (a `note`, a semantic `color=` on a
   KPI/statement, a coloured word or icon), always one accent per slide and never
   a large fill.

   Translate the settled dials into a small plan (which styles, how much
   variation, how much text) and keep to it so the deck feels deliberate, not
   random.

1. **Read the catalogue first.** Run `python scripts/catalogue.py`. It prints
   the content area, the Base Library roles (with their filling notes), and the
   Components Library entries (with their notes). ALWAYS look here before
   inventing a slide.

2. **For each slide you need, decide:**
   - Does a **Components Library** entry fit the message? If yes, reuse it:
     `d.use_component("<label or keyword>")`, then refill (`set_title`,
     `set_table_rows`, or edit the returned slide).
   - Otherwise build on a **base layout**: `d.cover(...)`, `d.section(...)`,
     `d.quote(...)`, or `d.content_blank(...)` + a `components.py` builder
     (see "Design rich, don't bullet" above).
   - Use plain `d.content(..., variant="white"|"steel")` bullets only for
     genuinely list-like content.
   - Follow the per-layout notes (read via `catalogue.py`): content titles are
     never more than one line; the eyebrow can carry the chapter/context; the
     cover intro and date use the steel colour.

3. **Lists use the built-in bullet list.** When you do use `d.content`, it fills
   the layout's native bullet list (level-1 string, or `(level, text)` for
   nesting; `lead=` adds a non-bulleted intro line) so a human can edit it.

4. **Compose a small Python script** that imports `build_deck` and
   `components`, builds the slides, and calls `d.save("/mnt/user-data/outputs/
   <Name>-v01.pptx")`. See `references/usage-examples.md`.

   **Speaker notes are recommended, not required.** Where they help, pass
   `notes="..."` to any slide factory (`cover`/`section`/`content`/
   `content_blank`/`quote`) or call `d.set_notes(slide, "...")` for a component
   slide. Keep them short spoken cues — 2-4 sentences: the slide's core message,
   what to say out loud, and the one figure or transition to land. They live in
   the notes pane, never on the slide. Since the on-slide text stays lean (we
   design, we don't bullet), notes are a good home for supporting detail and
   phrasing — but a short deck that doesn't need them is fine, and the validator
   no longer insists.

5. **Validate, then render-QA.** Run `python scripts/validate_deck.py <out>`
   (must PASS), then render to images and LOOK at every slide; fix overflow or
   overlap and re-render. Only then present the file with `present_files`.

## What the engine handles for you

- Auto-selects the newest uploaded template; falls back to `assets/`.
- Removes the Base/Components/Sample originals and the section list from output.
- Reads the content area from the red rectangle on the content example and
  removes that rectangle from output.
- Clones the page-number placeholder so layout-built slides are numbered (the
  cover stays unnumbered, by design).
- White cards get a subtle shadow on white slides and no shadow on steel slides.
- Cloned slides start with an EMPTY notes pane (template instructions don't
  leak), so `notes=`/`set_notes` writes a clean speaker-notes block.

## Rhythm and design notes

- Alternate steel and white content slides for rhythm (the dark cover, sections
  and closing provide the dark contrast). Lean towards steel.
- **Always end the deck with a dark closing slide** — a `section`-style dark
  slide as the final slide. Fill it from context: a short sign-off such as a
  thank-you, the core takeaway, a call to action, or contact details, kept
  on-brand (one fluo accent at most, no large fill). A `quote` may come just
  before it, but the last slide is dark.
- Use the quote slide sparingly.
- Give one idea per slide a strong anchor and let it fill the area; whitespace
  on the right is fine, a half-empty slide is not. Left-align by default, centre
  when a design benefits from it.

## References

- `references/brand-reference.md` - palette, fonts, fluo-green and semantic
  colour rules, background rules.
- `references/layouts-reference.md` - the master layouts, placeholder roles, and
  the Base Library clone-and-refill model.
- `references/components-reference.md` - the Components Library convention and
  the free-drawn component builders.
- `references/slide-logic.md` - how to choose a slide per message, deck
  structure, and the per-layout filling rules distilled from the template notes.
- `references/usage-examples.md` - copy-paste compose scripts.

## Environment

`pip install python-pptx` is the only dependency. The skill reads the template
from `assets/` (or the newest one the user uploads) and writes the finished deck
to the outputs folder.
