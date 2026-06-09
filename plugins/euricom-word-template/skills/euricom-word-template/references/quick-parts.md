# Quick Parts — Euricom Word template

## A property of the .dotx, not of generated documents

The template ships six user-facing Quick Parts: `Note - Tip`,
`Note - Waarschuwing`, `Note - Alarm`, `Note - Info`, and
`Color Picker` in the **Euricom** category, plus `Quote` in **General**.
All six live in the `AutoText` gallery of the template's glossary.

**Important:** these are available to a Word user only if the
`.dotx` is loaded as a template — either as the active document
template, or as a global template (File → Options → Add-ins →
Manage: Templates → Go → Add the Euricom `.dotx`). They are **not**
visible in the Building Blocks Organizer when opening a generated
`.docx`, even though the glossary XML is physically present inside
the file. This is Word's own design: Building Blocks are sourced
from loaded templates, not from the current document.

This is documented by Microsoft: Building Blocks can only be saved
in a template (document template or global template). Saving a
.dotx-with-Quick-Parts as .docx — which is essentially what the
build script does, content-type-wise — drops the user's access to
those Quick Parts even though the data survives in the zip.

**Practical guidance for users who want the Quick Parts:**

> Install the Euricom template once as a global template. In Word:
> File → Options → Add-ins → bottom-of-screen Manage dropdown →
> Templates → Go → Add → select `Euricom_Generic_Template.dotx`.
> From then on, Insert → Quick Parts → Building Blocks Organizer
> shows the six Euricom blocks in every Word session.

**What the skill does about this**: nothing special. The build
script doesn't try to preserve UI-level Quick Parts in the output
.docx, because it can't — that's not how Word resolves Building
Blocks. The skill renders notes, quotes, and tables programmatically
via the helpers in `render_components.py`. The output of those
helpers is byte-equivalent to what a human gets by inserting the
Quick Part manually, so a generated document looks identical to
one assembled by hand.

## Writing a Quick Parts installation guide

Users who want the in-template Quick Parts available in Word's UI
must install the `.dotx` as a global template — a one-time per-laptop
action (see the section above for the underlying reason).
Generated documents that explain this should include both Windows and
macOS paths. The canonical version of the instructions lives in the
v1.7 template's own styleguide content under "Quick Parts activeren
in Word". When asked to write or update this guide, follow that
structure: a one-paragraph intro, then a Windows section with two
routes (STARTUP-folder + Word-instellingen), then a macOS section
with two routes (Word-instellingen + Startup-folder), with a
`Waarschuwing`-note after each platform explaining the limitation of
the secondary route. Use `InlineCodeChar` for every file path,
filename, and shortcut throughout.
