# Euricom brand reference (PowerPoint)

Mirrors the Euricom Word template so decks, documents and sheets share one
identity. The theme inside the template already encodes all of this; reference
colours by name via `EURICOM[...]` / `SEMANTIC[...]` in `build_deck.py`, never
hand-type a hex elsewhere.

## Fonts

Montserrat for everything (headings and body). The template theme sets both the
major and minor font to Montserrat. Native shapes built by `components.py`
also set Montserrat explicitly. (In the LibreOffice QA render Montserrat falls
back to a substitute because it isn't installed there; in PowerPoint on a
machine with Montserrat it renders correctly.)

## Core palette

| Name        | Hex     | Use |
|-------------|---------|-----|
| Chacoal     | 1D252D  | Primary text on light backgrounds |
| Midnight    | 014046  | Dark slide background, table headers, big numbers, card titles |
| White       | FFFFFF  | Text on dark slides, white cards |
| Light steel | F1F5F6  | Steel content-slide background, zebra rows |
| Steel       | CBD9DA  | Card borders, dividers, timeline base line, total-row fill |
| Light mid   | 809FA2  | Muted captions, KPI labels, secondary text |
| Fluo green  | 00FF00  | Accent ONLY - see below |

## Fluo-green rule

Use fluo green **very sparingly**, as a thin accent only. "Sparingly" means *thin*, not *rare*: the same hairline accent (e.g. the default card top cap) may sit on most slides as long as it never grows into a fill or a block of colour. Recurring touchpoints:
the dot left of an eyebrow, the rounded top cap on cards (default), a short rule
under each KPI figure, the lead segment on icon_list dividers, a short rule
above comparison column titles, process-step connectors, timeline dots, and the
cover's italic sub-title. NEVER a large fill or a background behind text — it is
the single thin accent that ties the brand together, present on most slides but
never loud.

## Semantic colours (call-outs)

Keep these consistent with the Word template notes. Each is (foreground/border,
background):

| Meaning      | Foreground | Background |
|--------------|------------|------------|
| succes       | 014046     | F1F5F6     |
| waarschuwing | E9AB0C     | FEF9EC     |
| risico       | E80F0F     | FEF0F0     |
| info         | 5C7B7E     | F1F5F6     |

`succes` uses **Midnight** (`014046`), not a teal-green — matching the
positive/tip note in the Euricom Word template. (The old `30CBB1` green is
retired; richness comes from composition, not a second green.)

These are primarily for `note` call-outs, but the foreground colour MAY also be
used **sparingly outside notes** to code meaning: a single KPI figure (a
positive number in `succes` (Midnight), a risk count in `risico`), one word in a statement,
or an icon. Keep it occasional — one semantic accent per slide, and never as a
large fill behind text. `components` resolves a semantic name via `_resolve`
(e.g. `kpi_row([{... ,"color":"succes"}])`, `statement(..., color="risico")`).

## Background and shadow rules

- **Dark slides** (cover, section, closing): Midnight background, white text.
  These provide the dark contrast points in a deck's rhythm.
- **Content white**: white background. White elements (cards) MAY carry a light
  shadow here.
- **Content steel**: Light steel background. White elements should have NO
  shadow here - a thin steel border is enough. The engine applies this
  automatically based on the slide variant.
- Borders on cards/dividers are Steel (CBD9DA), thin (~0.75 pt).
