# Changelog - euricom-powerpoint-template

Tracks the skill and the bundled template version. The skill always prefers the
newest template the user uploads; the bundled `assets/` copy is the fallback.

## v1.1.0 - always-ask framing, mandatory dark closing slide

- **Framing now always asks in a chat.** A test showed the skill skipping or
  collapsing the dials into one combined question; instead it now opens with a
  one-line "I understood your material — to be sure, a few questions", then asks
  the three dials as **three separate multiple-choice questions**, never one
  combined question.
- **Added a fourth, open question:** *"Wil je nog iets toevoegen?"* with a "Nee"
  option and free text, so the user can add anything the dials don't capture.
- **Per-dial skip replaced by pre-selection.** What the prompt/content implies no
  longer skips a question; it pre-selects the recommended option so confirming is
  one click. The prompt still outweighs everything and stays sticky; the answers
  confirm and refine, never override an explicit instruction.
- **Every deck now ends on a dark closing slide** (`section`-style dark): a short
  contextual sign-off (thank-you / takeaway / call to action / contact), filled
  from context and kept on-brand. A `quote` may precede it, but the final slide
  is dark. Updated `SKILL.md` ("Rhythm and design notes") and `slide-logic.md`
  ("Deck structure").
- Instruction-level only; engine, builders and bundled template (`v05`) unchanged.

## v1.0.0 - dials reworked: richness / afwisseling / density, prompt-led framing

- **`doel` dial dropped.** It didn't steer the build reliably and the
  intern/klant/kennisdeling split rarely changed the output. The three dials are
  now **visual richness** (anchor), **afwisseling** (new), and **text density**,
  asked in that order.
- **New `afwisseling` dial (consistent ◄► afwisselend):** how much the look
  varies *across* slides, as opposed to richness *within* a slide. A deck can be
  rich-but-consistent or sober-but-afwisselend. Maps to how widely to vary
  builders and card styles over the deck.
- **Prompt guidance now outweighs everything, throughout the build.** Explicit
  precedence: user-prompt instruction > what the source implies > skill defaults,
  and a prompt instruction stays "sticky" for every later choice, not only at
  step 0.
- **Per-dial skip logic.** A dial the prompt or source already pins is adopted
  (with a one-line stated assumption), not asked; only genuinely ambiguous dials
  are asked in a chat. If all three are clear, the framing question is skipped.
- **Semantic colour is no longer derived from anything** — it simply follows the
  content (use it at a genuine risk / win / decision, sparing by default).
- Updated `SKILL.md` (banner + workflow step 0) and `slide-logic.md`; the engine,
  builders and bundled template (`v05`) are unchanged.

## v0.9.0 - doel-driven framing, fewer contradictions

- **Opening framing redesigned: the three dials are now `doel` / visual
  richness / text density.** The abstract `semantic colour` dial is gone (users
  did not recognise the concept); the **doel** — *interne communicatie* /
  *klant communicatie* / *kennisdeling* — is the lead choice and *derives* how
  much semantic colour to use plus the starting point for richness and density.
  Semantic colour still works in every form; it just isn't a question anymore.
  Updated in `SKILL.md` (banner + workflow step 0) and `slide-logic.md`.
- **Framing is no longer hard-blocking everywhere.** In an interactive chat it
  stays a blocking ask; in a non-interactive run (scheduled task / flow) the
  skill infers a sensible doel from the content, states the assumption and
  builds, instead of stalling on a question nobody can answer.
- **Speaker notes are now recommended, not required.** `validate_deck.py` no
  longer *warns* on slides without notes (it reports the count as neutral info);
  `SKILL.md` and `components-reference.md` reworded to match.
- **Fixed stale text in `slide-logic.md`** that contradicted the code: a `note`
  stacks below existing content and is skipped when full (it does **not**
  overlap builders), and card `style="fluo"` is the default **top cap** (an
  alias of `cap`), not a "left-bar accent". Card-style list completed
  (`cap`/`fluo`, `tonal`, `accent`, `plain`).
- **Reconciled apparent brand contradiction:** `brand-reference.md` now states
  that "fluo sparingly" means *thin, not rare* — the hairline accent (e.g. the
  default card cap) may appear on most slides as long as it never becomes a
  fill. Harmonised the "fill the area" vs "you needn't fill it" and "rich =
  more dark" vs "lean to steel" wordings so they no longer read as conflicting.
- **Fixed a truncated `SKILL.md`:** the `## Environment` section ended
  mid-sentence (`pip install pytho`); completed it.

## v0.8.0 - succes = Midnight, and speaker notes on every slide

- **`succes` semantic colour is now Midnight (`014046`) on light steel
  (`F1F5F6`)**, replacing the old teal-green (`30CBB1`/`EAFAF1`). It mirrors the
  positive/tip note in the Euricom Word template, so a success note/figure reads
  as a calm brand accent instead of a second green beside the fluo. Updated in
  `build_deck.SEMANTIC`, `brand-reference.md`, `SKILL.md` and
  `components-reference.md`. (`note()` already paints the bar/icon/title from the
  foreground; no other code change needed.)
- **Speaker notes per slide.** New `Deck.set_notes(slide, text)` plus a `notes=`
  keyword on `cover`/`section`/`content`/`content_blank`/`quote`. Cloned slides
  start with an empty notes pane (template instructions never leak), so notes are
  clean. Guidance: short spoken cues, 2-4 sentences — core message, what to say,
  the figure/transition to land. `validate_deck.py` now warns when slides have no
  notes. Documented in `SKILL.md` (workflow step 4), `components-reference.md` and
  `usage-examples.md`.

## v0.7.2 - reframe the third framing question (semantic colour in general)

- Workflow step 0 / slide-logic: the third dial was worded around notes. It is
  now about semantic colour **in general** — notes AND a coloured figure, word
  or accent (e.g. a green KPI, a red risk number) — matching how the four
  semantic colours are actually used since v0.6.x.

## v0.7.1 - fix stray borders on cloned components

- `_line_hex` no longer reads `shape.line.color` (which python-pptx mutates: it
  turns a `<a:ln><a:noFill/>` into an empty `<a:ln><a:solidFill/>`, rendering as
  a stray black border). It now reads the line colour straight from the XML, so
  detecting the red content-area rectangle no longer adds borders to every other
  cloned shape. This was why the cloned **team** component showed frames around
  its photos and text — the template was fine; the engine was at fault.

## v0.7.0 - bundled template v05 + image-component cloning fix

- Bundled template updated to **v05**.
- Fixed `_duplicate_slide` for python-pptx 1.0.2: image (and other)
  relationships are now re-added via the public `relate_to` API and the
  relationship ids in the copied shape XML are remapped, so a Components Library
  slide that contains photos (e.g. the new team slide) clones correctly. Before,
  cloning an image-bearing component raised a TypeError. Table-only components
  (agenda) were unaffected.

### Template version notes
- v05: base-layout examples lengthened (more body room); the agenda's 5th row
  recoloured from black to Midnight; a **team** slide added to the Components
  Library (ronde portretten + naam/rol/omschrijving), auto-discovered via its
  notes label.

## v0.6.5 - lighter, sparing notes (bundled template v04)

Notes were ported from the Word template and read too "documenty" on slides.

- `note()` is now light and slide-native: a slim rounded semantic bar (pill
  ends) + icon + bold label + text on the slide background, no coloured fill box
  or border.
- Guidance steers to sparing use: at most one note per slide, often none; for an
  informational aside, prefer a `statement` with one semantic-coloured word.

## v0.6.4 - more subtle fluo across builders (bundled template v04)

The fluo accent was too rare: icon_list/kpi_row only drew it when no icon was
present, and the design rich guidance pushes icons, so richly-built decks had
almost no green.

- `kpi_row`: a short fluo rule now sits under every figure, also when an icon is
  used (previously only without an icon).
- `icon_list`: each row divider gets a short fluo lead segment.
- `comparison`: a short fluo rule above each column title.
- Cards already carry the fluo top cap by default (v0.6.2). Net effect: subtle
  green on most slides, never loud.

## v0.6.3 - cover never overlaps (adaptive title/tagline) (bundled template v04)

The cover is the first thing seen, so it must never break. A long title or
fluo tagline used to overflow its fixed box and overlap the intro.

- New `_layout_cover`: stacks eyebrow -> title -> subtitle -> intro from a fixed
  top, sizing each box to its real line count and pushing the date/author block
  down, so nothing overlaps regardless of length.
- Long titles and taglines step down in size (36 -> 30 -> 26/24) so they stay to
  ~2 lines instead of overflowing. A short punchy tagline is still best.

## v0.6.2 - fluo cap is the default card; notes skip when no room (bundled template v04)

- `cards()` now defaults to the Euricom standard boxed card: a subtle border
  with a rounded fluo-green top cap (matches the design system's card pages), so
  the green accent shows without passing a style. `style="plain"` keeps the
  sober no-green look; `tonal` / `accent` unchanged. In `accent`, the non-hero
  cards are standard cap cards too.
- `note()` auto-placement now SKIPS the note (returns None) when the canvas has
  no room left, instead of pushing it off-slide — notes are sparing, so "no
  room" means "no note". Explicit `y=` still forces a position.

## v0.6.1 - notes auto-stack (no more overlap) (bundled template v04)

Fixes the real issue behind "notes land on top of other content": a `note`
without an explicit `y` used to default to the canvas top, so multiple notes
piled on the same spot and a note dropped onto a slide with content overlapped
it.

- `note()` now auto-places: when `y` is omitted it stacks below the previous
  note and below any content already in the canvas (new `_next_note_y` /
  `_content_bottom`). Multiple notes, and "builder + note" slides, lay out
  correctly without manual coordinates. Pass `y=` to override.

## v0.6.0 - semantic colour outside notes & a hard framing gate (bundled template v04)

From real-use feedback: the framing questions got skipped, a note overlapped a
full slide, and semantic colour was wanted beyond notes.

- Semantic colour beyond notes: `kpi_row` items take an optional `color`
  (semantic name / brand name / hex) and `statement` takes `color=` to tint a
  single figure or word; new `_resolve` maps names to RGB. Guidance loosened to
  allow occasional semantic accents outside notes (one per slide, no large fill).
- Workflow step 0 hardened into a blocking gate (prominent "ALWAYS START HERE"
  banner in SKILL.md) so the three framing questions are not skipped.
- Note placement: a `note` must not be dropped over a canvas-filling
  `icon_list`/`cards`/`kpi_row` (it overlaps). Docstrings and slide-logic now
  say to give a note its own slide or a reserved strip (`y=`).

## v0.5.0 - images: photo grids & team rows (bundled template v04)

Adds photo support so image-led design slides (like the design system's culture
and project-team pages) can be reproduced.

- `components.py` new builders:
  - `image_grid(slide, paths, cols=2, ...)` - a grid of rounded, cover-cropped
    photos with a subtle shadow; pass x/y/w/h to place it in part of a slide
    (e.g. the right half next to a text column).
  - `team(slide, members)` - a row of people: circular cover-cropped photo, bold
    name, muted role, short body.
- Helpers `_place_cover` (no-distortion cover crop via picture cropping) and
  `_pic_geom` (reshape a picture to `roundRect` / `ellipse`).
- Photos are real, editable pictures (not flattened), cropped non-destructively.

## v0.4.0 - colour & semantics (bundled template v04)

Makes decks less sober with more colour and surfaces the semantic call-outs,
without leaving the brand. Adds a framing step so the deck matches what the
user wants.

- `components.py` `cards()` gains a `style` parameter (one treatment per slide,
  never combined):
  - `tonal` - each card a different midnight tint (deep -> muted teal) from the
    new `MIDNIGHT_RAMP`; text and icon colour adapt for contrast. Rich and
    surprising with no extra hues.
  - `fluo` - white card with a rounded fluo-green top cap that follows the
    card's corners (matches the design system; steel hairline, no full outline).
  - `accent` (`accent=i`) - one midnight 'hero' card among plain white ones.
- `note()` upgraded: auto-height to its text, a matching icon per type
  (succes/info/waarschuwing/risico) and a thick accent left bar; `title`
  defaults to the type label. Brings the Word template's semantic notes to the
  deck properly.
- SKILL.md gains **workflow step 0 - frame the deck**: ask the user three dials
  (visual richness sober<->rich, text density little<->lots, semantic colour
  sparing<->frequent) and translate them into concrete style/text/colour
  choices. slide-logic and components references document the card styles,
  notes and the three dials.
- `statement()` gains an optional `top=` to anchor it instead of centring, so
  it can share a slide with a `note` below without overlapping.
- Helpers: `_tint`, `_text_on`/`_luma`, `_left_bar`.

## v0.3.0 - handover & versioned packaging (bundled template v04)

- Added `HANDOVER.md`: development handover (architecture, decisions with
  rationale, conventions, gotchas, roadmap) so the skill can be evolved in a
  fresh session or in Cowork without re-deriving the reasoning.
- Convention: package artefacts now carry the skill version in the filename,
  e.g. `euricom-powerpoint-template-v0_3.skill`.

## v0.2.0 - richness upgrade (bundled template v04)

Closes the "too sober" gap with free-form decks, within the brand.

- New `scripts/icons.py`: a compact, recolourable monoline icon set drawn from
  native shapes (arrow, bars, bulb, check, clock, doc, flag, gear, layers, lock,
  shield, star, target, trend, users) with `suggest(keyword)` mapping.
- `components.py`: `cards` and `kpi_row` now take an optional per-item icon;
  new `icon_list` (rich full-height alternative to bullets) and `statement`
  (one large takeaway with a fluo accent). KPIs are larger and centred; cards
  fill more of the area.
- Guidance shift ("design rich, don't bullet"): SKILL.md and slide-logic now
  steer to icons, cards/icon_list, kpi, statement and varied composition, with
  plain bullets reserved for genuinely list-like detail.
- Adaptive sizing on `statement` (sub-line never overlaps a multi-line head).

Known rough edges (next iteration, ideally in Cowork with real rendering):
`timeline` proportions, `gear`/`lock` icon detail, and hand-curated rich
Components Library patterns.

## v0.1.0 - bundled template v04

First working release.

Engine (`scripts/build_deck.py`)
- One consistent model: clone a reference slide and refill it.
- Standard slides (cover / content-steal / content-white / section / quote)
  clone the matching **Base Library** example and refill placeholders in place,
  inheriting exact formatting and the automatic page number.
- **Components Library** reuse: `use_component()` clones a curated slide;
  `set_title` / `set_table_rows` refill it (rows add/remove, styling preserved).
- Reads the content area from the red rectangle on the content example
  (`d.canvas`) and removes the rectangle from output.
- Native bullet lists (levels + non-bulleted lead) so humans can edit them.
- Removes Base/Components/Sample originals and the section list from output.
- Auto-selects the newest uploaded template; falls back to `assets/`.
- Robustness fixes: full-geometry placeholder moves (no zero-collapse), reliable
  in-file slide duplication with rId-preserving relationships, collapsed-box
  recovery on refill, adaptive section-title sizing, length-tiered quote font.

Components (`scripts/components.py`)
- cards, kpi_row, process_flow, timeline, comparison, maturity, data_table,
  note. White cards take a shadow on white slides, none on steel slides.

Tooling
- `scripts/catalogue.py` lists the content area, Base Library roles and
  Components Library entries with their notes - run it first.
- `scripts/validate_deck.py` checks layouts, leftover red rectangle, leftover
  sections, theme integrity and duplicate parts.

Known rough edges (next iteration): `timeline` and `cards` spacing/proportions
to be refined.

### Template version notes
- v04: introduced native sections (Base Library / Components Library / Sample
  Presentation), one annotated example per layout, and the red content-area
  rectangle on the content example. Clean role-based layout names.
