# Euricom Word Template Skill

A Claude skill that produces professional `.docx` documents following
the Euricom brand template — Aptos fonts, brand colours, logo,
auto-numbered headings, branded tables, semantic note callouts
(Tip / Alarm / Waarschuwing / Info), and quote blocks with attribution.

## What it does

- **Convert** existing content (markdown, PDF, plain text, Word) into
  the Euricom template.
- **Generate** brand-new documents from a prompt (proposal, whitepaper,
  memo, architecture document, AI strategy, analysis, meeting notes…).

The output always preserves the template's full visual identity:
fonts, colours, theme, header (logo), footer (address + page numbers),
and every custom paragraph style.

## How to use it

There's no slash-command or `/help` in claude.ai for custom skills.
Two ways to use this one:

**1. Just ask naturally.** With the skill enabled, prompts like the
following automatically trigger it:

- *"Zet dit document om naar de Euricom template"* (+ upload a file)
- *"Maak een korte memo over X volgens onze huisstijl"*
- *"Schrijf een whitepaper over Y in de Euricom-template"*
- *"Apply our brand template to this PDF"*

**2. Ask what the skill can do.** If you want a quick overview before
diving in, just ask Claude in the chat:

- *"Wat doet de Euricom skill?"*
- *"Welke document-types kan je maken?"*
- *"Help me met de Euricom-template"*

Claude will give a concise summary covering the two modes (convert
existing content / generate new), the supported document types, and
the components available (cover, TOC, headings, notes, quotes, tables).

## How it works

Instead of building a `.docx` from scratch (which loses custom styles
and theme), the skill **copies the template `.dotx` and replaces only
its `word/document.xml` body**. The new body is assembled from Python
helper functions that emit the exact XML each component expects.

## Folder structure

```
euricom-word-template/
├── SKILL.md                                  Main entry point + workflow
├── CHANGELOG.md                              Version history of the skill
├── assets/
│   └── Euricom_Generic_Template_v1_0.dotx    Embedded default template
├── references/
│   ├── styles-reference.md                   All style IDs + when to use
│   ├── components-reference.md               Component API + examples
│   ├── document-types.md                     Blueprints per document type
│   └── tone-of-voice.md                      Belgian-Dutch writing conventions
└── scripts/
    ├── build_from_template.py                Copy template + swap body
    ├── render_components.py                  XML helpers for every component
    └── validate_output.py                    Sanity-check the output
```

## Updating the embedded template

When a new version of the Euricom template is released, replace the
file at `assets/Euricom_Generic_Template_v1_0.dotx`. If the new version
adds, renames, or removes styles, also update:

- `references/styles-reference.md` (style catalogue)
- `references/components-reference.md` (if component structure changes)
- `scripts/render_components.py` (if note colours, quote borders, or
  cell widths change — re-extract from the template's XML)

Users can also override the embedded template per-session by uploading
their own `.dotx` file — the skill prefers user uploads over the
embedded default.

## License

Proprietary to Euricom. Use within Euricom only.
