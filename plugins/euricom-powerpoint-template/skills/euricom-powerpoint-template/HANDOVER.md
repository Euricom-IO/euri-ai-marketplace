# Handover — euricom-powerpoint-template

A development handover so a fresh Claude or developer (e.g. continuing in
Cowork) can extend this skill without re-deriving the reasoning. For *using*
the skill, read `SKILL.md` and `references/`; this file is about *why* it is
built the way it is and how to evolve it safely.

## Current state

- Skill **v1.1.0**, bundled template **v05** (`assets/Euricom_PowerPoint_Template.pptx`).
- Two generation modes, one model: **clone a reference slide and refill it.**
  Standard slides clone a Base Library example; richer slides clone a Components
  Library entry; free-drawn visuals are built on a blank content slide.
- Scripts: `build_deck.py` (engine), `components.py` (visual builders),
  `icons.py` (monoline icon set), `catalogue.py` (lists the template's offer),
  `validate_deck.py` (QA).
- Works in Claude.ai, Code, API and Cowork. The skill always prefers the newest
  template the user uploads; `assets/` is the fallback.

## Architecture & key decisions (with rationale)

- **Never rebuild the theme.** We open the branded template and clone/instantiate
  from it, so the theme (Montserrat + Euricom palette), masters and layouts are
  always intact. Rebuilding (python-pptx from scratch) would drop branding.
- **Template is the single source of truth and self-documenting.** Native
  PowerPoint sections drive everything: `Base Library` (one annotated example
  per layout), `Components Library` (curated rich slides), `Sample Presentation`
  (scratch, ignored). Each library slide's speaker notes are its instructions.
  Rationale: adding/curating slides needs no code change; the catalogue is read
  from sections + notes.
- **Clone-and-refill over layout-instantiation.** Cloning a filled example
  inherits exact formatting and the automatic page number, and the notes
  document how to fill it. Layout-instantiation remains a fallback when a Base
  Library example is missing.
- **Content area via the red rectangle.** The content example carries a red
  (`FF0000`) rectangle marking the area for free-drawn components. The engine
  reads its geometry into `d.canvas` and removes the rectangle from output.
- **Brand restraint is intentional, richness comes from composition.** Fluo
  green only as a thin accent; whitespace is fine. v0.2.0 closed the "too sober"
  gap not with more colour but with icons, icon_list, cards-with-icons, kpi and
  statement, plus guidance to design rather than bullet.
- **On save**, the Base/Components/Sample originals and the section list are
  stripped, so the deliverable has only generated slides.

## Conventions to preserve

- **Section names** (case-insensitive): `Base Library`, `Components Library`,
  `Sample Presentation`. The engine keys off these.
- **Layout roles** are matched by name (`10_Cover_Dark`, `20_Content_Steal`,
  `30_Content_White`, `30_Section_Dark`, `40_Quote`) with an index fallback, so
  reordering layouts is safe. Placeholder idx maps are in `PH` in `build_deck.py`.
- **Notes format**: first line = a short label (e.g. `agenda · inhoudsoverzicht`),
  rest = purpose + how to adapt. Keeps the catalogue selectable and human-readable.
- **Template versioning**: the user bumps the template version per upload; the
  skill auto-selects the newest. Keep the `CHANGELOG.md` "template version notes"
  current.
- **Package filename carries the skill version**, e.g.
  `euricom-powerpoint-template-v0_3.skill` (see "Releasing" below).

## Gotchas / hard-won lessons (do not regress)

- **Removing slides**: only deleting the `<p:sldId>` leaves orphaned slide parts
  → duplicate zip entries on save. Always also `prs.part.drop_rel(rId)`
  (see `_cleanup`, `_duplicate_slide`).
- **Collapsed placeholders**: an empty field in an example can shrink to ~0
  width (the cover eyebrow had `cx=65` EMU); refilled text then is invisible.
  `_refill` calls `_uncollapse` to drop a tiny xfrm so it inherits layout geometry.
- **Header/footer placeholders** (incl. slide number) are NOT cloned by
  python-pptx when instantiating a bare layout. Cloning a filled example brings
  the page number for free; the layout-fallback path clones it explicitly.
- **Partial geometry moves**: setting only `.top`/`.height` on an inheriting
  placeholder zeroes the others. Use `_place(...)` with all four values from
  `_layout_geom`.
- **Never read `shape.line.color` to inspect a shape.** python-pptx mutates a
  `noFill` line into an empty `solidFill` on access, which renders as a stray
  black border on cloned shapes. Read line/fill colour from the XML instead
  (see `_line_hex`). This caused borders on the cloned team component.
- **Sections use the `p14` namespace** which python-pptx' `qn()` does not know;
  use the literal `_P14_*` constants in `build_deck.py`.
- **Refill preserves formatting** by editing the first run in place (not
  `ph.text =`), so inherited run styles (fluo subtitle, steel intro) survive.
- **Overflow**: section titles size to their line count and push the description
  down; quotes step font down by length; `statement` positions its sub-line
  adaptively. Don't reintroduce fixed positions for variable-length text.
- **LibreOffice QA is flaky** in sandboxes: kill stale `soffice`, use a fresh
  `-env:UserInstallation` profile and `--nodefault`. Montserrat falls back to a
  substitute in the render — judge fonts in real PowerPoint (a reason to iterate
  in Cowork).

## How to extend

- **Add a component (preferred):** add a finished slide to the `Components
  Library` section in PowerPoint, write a notes label line. It is auto-discovered;
  no code change. Refill it via `use_component` + `set_title`/`set_table_rows`,
  or by editing the returned slide.
- **Add a free-drawn builder:** add a function to `components.py` that draws
  inside `CANVAS` using the brand colours and (optionally) `icons.draw`. Respect
  the shadow rule (`_shadow_for`: white = subtle shadow, steel = none).
- **Add an icon:** add a `_name(s, x, y, sz, c, w)` drawer to `icons.py`,
  register it in `_ICONS`, optionally add synonyms in `_SYNONYMS`.
- **New template version:** the user uploads it; verify roles/placeholders still
  map (run `catalogue.py`), update layout names in `_LAYOUT_NAMES` only if they
  changed, and note it in the CHANGELOG.

## Dev / QA loop

```bash
python scripts/catalogue.py                          # what the template offers
python <compose>.py                                  # build via Deck + components
python scripts/validate_deck.py <out.pptx>           # must PASS
# render + eyeball every slide (LibreOffice tooling under /mnt/skills/public/pptx)
```

## Roadmap

1. **Highest leverage:** hand-curate rich slide patterns into the Components
   Library (the "21 patterns" idea), ideally in Cowork with real PowerPoint
   rendering and the Claude-for-PowerPoint add-in.
2. Polish `timeline` proportions and the `gear`/`lock` icon detail.
3. More builders as needed (two-column text+visual, big-stat hero, accent band).

Done in v0.4.0: card colour styles (tonal / fluo / accent), an upgraded semantic
`note` (icon + accent bar + auto-height), and a framing step (three dials) in
the workflow. Still open: hand-curated rich Components Library patterns, and
`timeline` / `gear` / `lock` / `shield` icon polish.

Done in v0.8.0: `succes` semantic recoloured from teal-green to Midnight
(`014046`, on `F1F5F6`) to match the Word template's positive note — `note()`
reads its bar/icon/title from the foreground, so only the `SEMANTIC` value and
docs changed. Speaker notes added: `Deck.set_notes()` + a `notes=` kwarg on
every factory write to `slide.notes_slide.notes_text_frame`; cloned slides have
no notes (the duplicator skips the notesSlide rel), so the pane is clean.
`validate_deck.py` warns on slides without notes.

Done in v0.9.0: framing redesigned — the three dials are now **doel**
(intern / klant / kennisdeling) / visual richness / text density; the abstract
`semantic colour` dial was dropped (users didn't recognise it) and colour now
*derives* from the doel. Framing is blocking in chat but inferred (non-blocking)
in scheduled tasks / flows. Speaker notes downgraded from required to
recommended (`validate_deck.py` reports missing notes as neutral info, not a
warning). Doc-vs-code contradictions in `slide-logic.md` fixed (notes don't
overlap builders; `style="fluo"` is the default top cap, not a left-bar) and a
truncated `## Environment` line in `SKILL.md` completed. These are
instruction-level changes; the engine and builders are unchanged apart from the
validator's notes check.

Done in v1.0.0: the framing dials reworked again. `doel` is dropped (it didn't
steer the build and the intern/klant/kennisdeling split rarely changed output);
the three dials are now **visual richness** (anchor) / **afwisseling** (new) /
**text density**. `afwisseling` (consistent ◄► afwisselend) captures variation
*across* slides as distinct from richness *within* one, so a deck can be
rich-but-consistent or sober-but-afwisselend. Framing is now explicitly
prompt-led: precedence is user-prompt instruction > source material > skill
defaults, and a prompt instruction stays sticky through the whole build, not
just step 0. Skip logic is per-dial — a dial the prompt or source already pins is
adopted with a one-line stated assumption, not asked; if all three are clear the
framing question is skipped. Semantic colour no longer derives from anything; it
just follows the content. Instruction-level only (`SKILL.md` banner + step 0,
`slide-logic.md`); engine, builders and template unchanged.

Done in v1.1.0: framing made an always-ask flow after a test showed it skipping
or collapsing the dials into one combined question. In a chat it now opens with a
one-line "I understood your material — a few questions to be sure", then asks the
three dials as **three separate multiple-choice questions** (never combined),
plus a fourth open question *"Wil je nog iets toevoegen?"* (Nee / free text). The
v1.0.0 per-dial *skip* became per-dial *pre-selection*: what the prompt/content
implies pre-fills the recommended option (one-click confirm) rather than skipping
the question; the prompt still outweighs and stays sticky, answers never override
an explicit instruction. Also: **every deck now ends on a dark closing slide**
(`section`-style dark, contextual sign-off, on-brand) — added to `SKILL.md`
("Rhythm and design notes") and `slide-logic.md` ("Deck structure"). Non-blocking
inference for scheduled tasks / flows is unchanged. Instruction-level only;
engine, builders and template unchanged.

## Releasing

Bump the version in `CHANGELOG.md`, then package with the skill-creator
packager and give the output a versioned filename:

```bash
python -m scripts.package_skill <skill-folder> <out-dir>     # validates + builds .skill
# then name the artefact with the skill version, e.g.:
#   euricom-powerpoint-template-v0_3.skill   (a .skill is a zip; rename to .zip if your upload needs it)
```
