# Layouts & the clone-and-refill model

## The five master layouts

| Role    | Layout name        | Background | Page number | Key placeholders (idx) |
|---------|--------------------|------------|-------------|------------------------|
| cover   | 10_Cover_Dark      | Midnight   | no          | eyebrow 11, title 12, subtitle 13, intro 14, date 15, author 16 |
| steel   | 20_Content_Steal   | Light steel| yes (10)    | title 0, eyebrow 11, body 12 |
| white   | 30_Content_White   | White      | yes (10)    | title 0, eyebrow 11, body 12 |
| section | 30_Section_Dark    | Midnight   | yes (15)    | eyebrow 11, title 12, description 14 |
| quote   | 40_Quote           | Light steel| yes (10)    | quote 12, author 16, role 17 |

Placeholder idx values are stable across template versions; the engine also
matches layouts by **name** with an index fallback, so reordering layouts does
not break it.

## How the engine builds standard slides

It does NOT instantiate bare layouts by default. It **clones the matching Base
Library example** (a filled, annotated slide that lives in the template's "Base
Library" section) and refills the placeholders in place. Benefits:

- exact placeholder formatting is preserved (e.g. the cover's fluo italic
  sub-title and steel intro, inherited from the layout style);
- the automatic page number comes along for free;
- the example's notes document how to fill it.

If a Base Library example is missing for a role, the engine falls back to
instantiating the bare layout and cloning the page-number placeholder.

### Refill mechanics (handled by `build_deck.py`)

- Text is overwritten by editing the first run in place (preserving formatting),
  not by replacing the text frame.
- A collapsed placeholder box (an empty field in the example can shrink to ~0
  width) is detected and its geometry falls back to the layout, so refilled text
  is visible. (This is why the cover eyebrow renders even though it was empty in
  the example.)
- The red content-area rectangle is read for `canvas` and then removed.
- Long section titles: the title box is sized to its real line count and the
  description is pushed below it (no overlap). A 3-line title shrinks to fit.
- Long quotes: the font steps down by length (32 -> 26 -> 22 -> 18 pt) plus
  native shrink-to-fit, so the quote never spills onto the author line.

## Public API (`from build_deck import Deck`)

```python
d = Deck()                      # opens newest template; reads sections + canvas
d.base_examples()               # {role: notes}  - filling instructions
d.library()                     # [{index, label, title, notes, layout}]
d.canvas                        # {x, y, w, h} content area in inches

d.cover(title, eyebrow=, subtitle=, intro=, date=, author=)
d.section(title, eyebrow=, description=)
d.content(title, body=[...], eyebrow=, lead=, variant="white"|"steel")
d.content_blank(title, eyebrow=, variant=)      # clean canvas for components
d.quote(quote, author=, role=)

s = d.use_component("agenda")   # clone a Components Library slide
d.set_title(s, title=, eyebrow=)
d.set_table_rows(s, [["01","..."], ["02","..."]])   # add/remove rows
d.table(slide, headers, rows, total_row=False)

d.save("/mnt/user-data/outputs/<Name>-v01.pptx")
```

`body` items: a string (level-1 bullet) or `(level, text)` for nesting; `lead=`
adds a non-bulleted intro line. All bullets use the layout's native list.
