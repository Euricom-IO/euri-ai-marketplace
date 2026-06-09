# Usage examples

Copy-paste compose scripts. Run from `scripts/` (so `import build_deck` works)
or add the scripts dir to `sys.path`.

## Minimal deck

```python
import sys; sys.path.insert(0, "scripts")
from build_deck import Deck

d = Deck()
d.cover(eyebrow="Solution proposal — voor Reynaers",
        title="Een schaalbaar orderplatform.",
        subtitle="Samen gebouwd.",
        intro="Onze aanpak, keuzes en waarborgen die uw migratie veilig maken.",
        date="5 juni 2026", author="Wim Van Hoye",
        notes=("Stel jezelf en het team kort voor. Kader: dit is een voorstel, "
               "geen offerte — we lopen samen de aanpak door. Zet de toon: "
               "veilige migratie, samen gebouwd."))
d.content(eyebrow="Agenda", title="Wat we vandaag doorlopen",
          body=["Context & doel", "Onze aanpak", "Tijdlijn", "Q&A"],
          notes=("Loop de vier blokken in één zin elk langs. Vraag of er "
                 "onderwerpen ontbreken voor we starten."))
d.save("/mnt/user-data/outputs/Reynaers-voorstel-v01.pptx")
```

Pass `notes="..."` to every factory (or `d.set_notes(slide, "...")` for a
component/free-drawn slide): short spoken cues, 2-4 sentences, in the notes pane.

## Reuse a Components Library slide

```python
d = Deck()
s = d.use_component("agenda")        # always check catalogue.py for labels
d.set_title(s, title="Wat we doornemen", eyebrow="Agenda")
d.set_table_rows(s, [["01","Context"], ["02","Aanpak"],
                     ["03","Tijdlijn"], ["04","Q&A"]])
```

## Content with native bullets + a non-bulleted lead

```python
d.content(eyebrow="Business update", title="Overzicht van nieuwe klanten",
          lead="Drie thema's kwamen telkens terug.",
          body=["Schaalbaarheid onder piekbelasting",
                "Security centraal",
                (2, "met segmentatie als basis"),   # nested bullet
                "Snellere releases"],
          variant="steel")
```

## A free-drawn component (cards, KPIs, ...)

```python
import components as C
s = d.content_blank(eyebrow="Impact", title="Wat het oplevert", variant="steel")
C.kpi_row(s, [{"value":"-40%","label":"reviewtijd"},
              {"value":"3x","label":"sneller deployen"},
              {"value":"99,9%","label":"beschikbaarheid"}])
```

## QA before presenting

```bash
python scripts/validate_deck.py /mnt/user-data/outputs/<Name>.pptx   # must PASS
# then render with the pptx skill's LibreOffice tooling and inspect every slide:
python /mnt/skills/public/pptx/scripts/office/soffice.py --headless \
    --convert-to pdf --outdir /tmp /mnt/user-data/outputs/<Name>.pptx
pdftoppm -jpeg -r 100 /tmp/<Name>.pdf /tmp/qa
```
