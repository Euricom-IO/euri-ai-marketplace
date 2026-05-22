# Styles reference — Euricom Word template

This is the catalogue of styles defined in the template, with guidance
on when to use each. **Use the exact `styleId` shown** — not the
display name — when generating XML, since paragraph references go
through `<w:pStyle w:val="...">`.

## Rule of thumb

> **Always pick a style. Never apply manual formatting (font size,
> colour, bold, spacing) to simulate one.** If the right style does
> not exist, fall back to `Normal` rather than inventing a look.

The template's spacing, fonts (Aptos / Aptos Display), and colours
(Midnight `#014046`, Chacoal `#1D252D`, Steel Gray `#CBD9DA`, etc.)
are all baked into the styles. Manual overrides break visual
consistency across documents.

## Headings & titles

| styleId | Display name | Use for |
|---|---|---|
| `Title` | Title | The main document title on the first body page (after the cover, if any). 27pt, Midnight `#014046`, Aptos Display. Used at most **once** per document. |
| `Subtitle` | Subtitle | Optional subtitle directly below `Title`. |
| `Heading1` | Heading 1 | Chapters — top-level sections. Auto-numbered, appears in TOC, page-break-before behaviour is handled by the style. |
| `Heading2` | Heading 2 | Sections within a chapter. |
| `Heading3` | Heading 3 | Sub-sections — use only when extra nuance is genuinely needed. |
| `H1Intro` | H1 Intro | Italic lead paragraph immediately under a `Heading1`, framing the chapter. Use sparingly. |

**Depth cap.** The template explicitly discourages going deeper than
`Heading3`. If you find yourself reaching for `Heading4`, restructure
the section instead — split it into two chapters, or merge the deepest
items into a bulleted list under `Heading3`.

## Body & lists

| styleId | Display name | Use for |
|---|---|---|
| `Normal` | Normal | Default body text. Aptos 11pt, line-height 15pt, 6pt space after. |
| `NoSpacing` | No Spacing | Body text without the trailing space — useful for tight blocks (addresses, signature lines). |
| `Bullet1` | Bullet 1 | First-level bullet. |
| `Bullet2` | Bullet 2 | Second-level bullet (indented). |

**Bullet depth cap.** Use at most two levels. Deeper lists become hard
to scan; prefer splitting into multiple short lists or sub-sections.

**Numbered lists.** The template does not define a dedicated numbered-
list style. Only use numbering when sequence is semantically
meaningful (steps, ranked items); otherwise bullets are preferred.

## Cover page

| styleId | Display name | Use for |
|---|---|---|
| `ECCoverTitle` | EC Cover Title | Large title on the cover page. 36pt bold Aptos Display, Chacoal `#1D252D`. |
| `ECCoverSubtitle` | EC Cover Subtitle | Subtitle/tagline directly under the cover title. 16pt Aptos Display. |
| `ECCoverMeta` | EC Cover Meta | The "voor"-line at the bottom of the cover. **Always uppercase** by convention: `VOOR EURICOM`, `VOOR KRÊFEL`, `CONFIDENTIEEL`, `VOOR INTERN`. |

The cover page already includes the Euricom logo (anchored top-left)
when built via `cover_page()` in `render_components.py`.

## Tables

| styleId | Display name | Use for |
|---|---|---|
| `TableGrid` | Table Grid | Carrier style for the quote block only — not for data. |
| `EuricomDataTable` | Euricom Data Table | **The default for all data tables.** Branded styling: header row (Midnight + white bold), zebra-striped body (alternating Light Steel Gray), optional bold total row (light blue accent), subtle borders (`#DCE5E6` 2pt), Aptos 10pt body text. |

The `table()` helper in `render_components.py` applies
`EuricomDataTable` automatically — do not set per-cell shading,
borders, or font on tables. If you need a row to stand out as a total
or summary row, pass `last_row_is_total=True`; the template's
conditional formatting handles the rest.

## Headers, footers, page numbering

These are **inherited automatically** when the build script copies
the template. You do not need to add or reference them in body XML:

- **Header (page 1, cover):** empty.
- **Header (subsequent pages):** Euricom logo (top-left), Aptos.
- **Footer (subsequent pages):** `Blarenberglaan 3A, 2800 Mechelen  •  euri.com` and a `page / total` indicator.

## Theme colours

The template's theme exposes these slots (the values come from the
Euricom brand palette):

| Theme slot | Hex | Brand name |
|---|---|---|
| Dark 1 (text1) | `#1D252D` | Chacoal |
| Light 1 (background1) | `#FFFFFF` | White |
| Dark 2 (text2) | `#014046` | Midnight |
| Light 2 (background2) | `#F1F5F6` | Light Steel Gray |
| Accent 1 | `#00FF00` | Fluorescent Green — use sparingly |
| Accent 2 | `#014046` | Midnight |
| Accent 3 | `#809FA2` | Light Midnight |
| Accent 4 | `#CBD9DA` | Steel Gray |
| Accent 5 | `#1D252D` | Chacoal |
| Accent 6 | `#F1F5F6` | Light Steel Gray |

Reference colours via `w:themeColor` when you can (e.g.
`w:themeColor="accent4"`), so a future palette change ripples through
all documents without touching XML.

## Semantic colours (for Notes)

These are used inside note callouts, not at paragraph level:

| Type | Foreground | Background |
|---|---|---|
| Alarm | `#E80F0F` | `#FEF0F0` |
| Waarschuwing | `#E9AB0C` | `#FEF9EC` |
| Neutraal / Info | `#5C7B7E` | `#F1F5F6` |
| Positief | `#30CBB1` | `#EAFAF1` |

The note renderer in `render_components.py` applies these
automatically — there is no need to set them by hand.
