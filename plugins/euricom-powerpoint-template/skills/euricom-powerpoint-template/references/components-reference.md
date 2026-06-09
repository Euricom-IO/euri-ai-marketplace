# Components

Two kinds of "component": curated slides in the template's **Components
Library**, and free-drawn builders in `components.py`. Prefer the library.

## 1. Components Library (preferred - clone & refill)

Curated, branded slides that live in the template's "Components Library"
section. Each has speaker notes: the first line is a short label, the rest
explains the purpose and how to adapt it.

Grow the library by adding a finished slide to that section in PowerPoint and
writing a notes line - it becomes available to the skill automatically (no code
change). Recommended notes shape:

```
agenda · inhoudsoverzicht
Tabel-gebaseerde agenda; rijen kunnen toegevoegd/verwijderd worden.
```

Use it:

```python
s = d.use_component("agenda")                 # match on label/title/notes
d.set_title(s, title="Wat we doornemen", eyebrow="Agenda")
d.set_table_rows(s, [["01","Context"], ["02","Aanpak"], ["03","Q&A"]])
```

`set_table_rows` refills the first table and adds/removes rows to match,
preserving the cloned row styling. The current library ships one entry: a
table-based **agenda / table of contents**.

## 2. Free-drawn builders (`components.py`)

For visuals not yet in the library. Start from a clean canvas and draw inside
`d.canvas` (read from the red rectangle). The slide variant drives shadows
automatically (white -> subtle shadow, steel -> none).

```python
import components as C
s = d.content_blank(eyebrow="Aanpak", title="In vier fases", variant="white")
C.process_flow(s, [{"title":"Discover","body":"Workshops"}, ...])
```

Available builders (all branded, all simple native shapes a human can edit):

| Function | What it draws |
|----------|---------------|
| `cards(slide, items, columns=None, style=, accent=)` | cards with optional **icon**; `style` = `plain` / `fluo` / `tonal` / `accent` |
| `icon_list(slide, items)` | full-height rows: icon + title + body (rich bullet alternative) |
| `kpi_row(slide, items)` | big Midnight numbers, optional icon, muted labels |
| `statement(slide, text, sub=None)` | one large takeaway with a fluo accent |
| `process_flow(slide, steps)` | numbered step cards joined by fluo connectors |
| `timeline(slide, items)` | horizontal timeline, fluo milestone dots |
| `comparison(slide, left, right, left_title=, right_title=)` | two columns |
| `maturity(slide, levels)` | ascending bars (steel -> midnight) |
| `data_table(slide, headers, rows, total_row=)` | Midnight header, zebra body |
| `note(slide, kind, title=None, body=None, icon=True)` | semantic call-out (succes/waarschuwing/risico/info): accent bar + icon, auto-height |
| `image_grid(slide, paths, cols=2, x=,y=,w=,h=)` | grid of rounded, cover-cropped photos with subtle shadow |
| `team(slide, members)` | row of people: circular photo + name + role + body |

`items` accept dicts or tuples. Cards/icon_list/kpi items take an optional
`"icon"` key. Examples:

```python
C.cards(s, [{"icon":"trend","title":"Schaalbaarheid","body":"..."},
            {"icon":"shield","title":"Security","body":"..."}])
C.icon_list(s, [{"icon":"target","title":"Discover","body":"Workshops & audit"},
                {"icon":"gear","title":"Build","body":"Iteratief bouwen"}])
C.kpi_row(s, [{"icon":"trend","value":"-40%","label":"reviewtijd"}])
C.statement(s, "AI-adoptie is geen project, maar een evolutie.")
```

### Card colour styles

`cards(...)` takes a `style` to add colour without leaving the brand. Pick ONE
per slide — the styles are deliberately not combined:

- **default** (`style="cap"`, alias `"fluo"`) — the Euricom standard boxed card:
  white card, subtle border and a rounded fluo-green TOP cap following the
  corners (matches the design system's card pages). This is what you get without
  a `style`, so the green accent shows by default.
- `style="plain"` — white cards, steel border, a small fluo rule/icon, no green
  cap. The soberest look; use when you explicitly want no green.
- `style="tonal"` — each card a different tint from `MIDNIGHT_RAMP` (deep
  midnight -> muted teal); text and icon colour adapt for contrast. Rich and
  surprising with no extra hues.
- `style="accent", accent=i` — one midnight 'hero' card (index `i`); the rest
  are standard cap cards. Use to spotlight the key item in a row.

```python
C.cards(s, items)                       # default: fluo top cap
C.cards(s, items, style="tonal")
C.cards(s, items, style="plain")          # sober, no green
C.cards(s, items, style="accent", accent=1)   # 2nd card is the hero
```

### Semantic notes

`note(slide, kind, title=None, body=None)` draws a LIGHT, slide-native call-out
in the semantic colours: a slim rounded semantic bar + a matching icon + a bold
label + text on the slide background (no coloured fill box). `kind` is `succes`
/ `info` / `waarschuwing` / `risico`; `title` defaults to the type label. Notes
auto-stack (no `y` needed) and are skipped when the canvas is full. Use sparingly
— at most one per slide, often none; for an informational aside prefer a
`statement` with one semantic-coloured word instead of a note.

`succes` renders in **Midnight** (`014046`), not green — matching the Word
template's positive note. So a `succes` note/figure reads as a calm brand accent,
not a second green next to the fluo.

```python
C.note(s, "risico", "Hard deadline", "Go-live moet voor de jaarafsluiting.")
C.note(s, "succes", body="Pilot bevestigt 40% tijdwinst.")   # title defaults to "Succes", Midnight
```

### Speaker notes (`d.set_notes` / `notes=`)

Speaker notes are recommended where they help — short presenter cues in the
notes pane (never shown on the slide). They are not required, and the validator
won't warn if a slide has none. Pass `notes="..."` to any factory
(`cover`/`section`/`content`/`content_blank`/`quote`) or call
`d.set_notes(slide, "...")` for a component or hand-drawn slide. Keep it to 2-4
sentences: the core message, what to say out loud, the figure or transition to
land. Cloned slides start with an empty notes pane, so nothing leaks from the
template examples.

```python
s = d.content_blank(eyebrow="Resultaat", title="Pilot in cijfers", notes=(
    "Open met de winst: 40% minder reviewtijd in zes weken. "
    "Benadruk dat dit met het bestaande team is gehaald. "
    "Brug naar de volgende slide: hoe we dit opschalen."))
C.kpi_row(s, [{"value":"-40%","label":"reviewtijd"}])

comp = d.use_component("agenda")
d.set_notes(comp, "Loop de vier blokken kort langs; vraag of de volgorde klopt.")
```

### Photos

`image_grid` and `team` place real, editable pictures, cover-cropped without
distortion. `image_grid` fills a rect (default the whole canvas; pass x/y/w/h
to use, say, the right half beside a text column) with rounded photos. `team`
draws a row of circular portraits with a name, muted role and short body.

```python
C.image_grid(s, [p1, p2, p3, p4], cols=2, x=6.95, y=2.05, w=5.62, h=4.7)
C.team(s, [{"photo": path, "name": "An De Smet", "role": "Agile analist",
            "body": "Vertaalt de business naar heldere specificaties."}, ...])
```

## 3. Icons (`icons.py`)

A compact monoline icon set drawn from native shapes - vector, recolourable,
editable. `icons.NAMES` lists them; `icons.suggest("growth")` maps a keyword to
an icon. Default colour Midnight; pass `color="00FF00"` for a fluo accent (use
sparingly). Available: arrow, bars, bulb, check, clock, doc, flag, gear, layers,
lock, shield, star, target, trend, users.

```python
import icons
icons.draw(slide, "target", x=1.0, y=2.0, size=0.5)            # Midnight
icons.draw(slide, icons.suggest("security"), x=2.0, y=2.0, size=0.5)
```

### Known rough edges (next iteration)

`timeline` proportions and the `gear`/`lock` icon detail will be refined. When in
doubt, prefer a Components Library slide, `icon_list`, or `cards` with icons.

### Design guardrails

- Stay inside `d.canvas`; you need not fill it - empty space on the right is fine.
- Fluo green only as a thin accent. White cards: shadow on white slides, none on
  steel. Keep constructions simple (no fragile groups) so a human can edit them.
