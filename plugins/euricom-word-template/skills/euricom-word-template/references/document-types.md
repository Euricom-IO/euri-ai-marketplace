# Document types — structural blueprints

Pick the closest match to what the user is asking for, then adapt.
None of these are rigid; they're starting points. The real signal is
the user's intent — a "memo" with 30 pages of analysis is really a
report, and a "report" with 1 page of findings is really a memo.

## Length-based decisions

These two are the most important and orthogonal calls:

| Document length | Cover page? | Table of contents? |
|---|---|---|
| ≤ 3 pages (memo, short note) | No | No |
| 4–7 pages (short analysis) | Optional | No |
| ≥ 8 pages (report, whitepaper, proposal) | **Yes** | **Yes** |
| External-facing deliverable, any length | **Yes** | Yes if ≥ 4 pages |

When in doubt, ask: would the reader benefit from a cover when forwarding
this externally? Would they want a TOC to navigate? If neither, skip both.

## Type-specific blueprints

### Voorstel / Proposal (commercial)

Audience: prospect or client. Goal: convince them to engage.

```
[Cover: title, subtitle = "Voorstel voor <project>", meta = "VOOR <CLIENT>"]
[TOC, levels=2]

H1  Executive summary
    Normal x 2–3 short paragraphs — the why, the what, the proposed value
H1  Context & uitdaging
    What the client is facing in their own words
H1  Voorgestelde aanpak
    H2  Fase 1, Fase 2, ...
    Bullets, optional table for phasing
H1  Team
    Brief profiles (Normal + bold names)
H1  Investering & timing
    Table with pricing/phases
H1  Volgende stappen
    Bullet list, 3–5 items max
[Optional Quote on the final page — vision statement from leadership]
```

### Whitepaper

Audience: technical leaders, decision-makers researching a domain.
Goal: position Euricom as a thought leader on the topic.

```
[Cover: title, subtitle = thematic tagline, meta = "VOOR EURICOM"]
[TOC, levels=2 or 3]

H1  Samenvatting (1 page max)
H1  Inleiding / Context
    H1Intro for the opening line
H1  Analyse — main argument
    H2 sub-sections, tables for comparison data
    Notes (Info) for context, Tips for actionable advice
H1  Aanbevelingen
    Bullet list or numbered if order matters
H1  Conclusie
[Optional Quote — sign-off from a Euricom expert]
```

### Architectuurdocument

Audience: engineers and architects implementing or reviewing.
Goal: communicate design decisions precisely.

```
[Cover if ≥ 8 pages, otherwise just Title]
[TOC, levels=3 — technical docs benefit from deeper TOC]

H1  Doel & scope
    What this doc covers, what it does NOT cover
H1  Context
    System landscape, stakeholders, constraints
H1  Architectuur
    H2 per major component, optional H3 per concern
    Tables for interfaces / API contracts
    Notes (Waarschuwing) for risks, (Info) for trade-offs
H1  Beslissingen (ADR-style)
    For each decision: Context, Beslissing, Gevolgen
H1  Open vragen
    Bullet list
H1  Referenties
```

### AI-strategie / Governance document

```
[Cover: meta = "VOOR EURICOM" or client name]
[TOC, levels=2]

H1  Executive summary
H1  Principes
    Bullet list, optionally with brief expansion paragraphs
H1  Scope & toepassingsgebied
H1  Verantwoordelijkheden
    Table: rol → verantwoordelijkheid
H1  Operationele richtlijnen
    H2 per domein (data, prompts, modellen, security, ...)
    Notes (Alarm) for hard rules, (Tip) for best practices
H1  Naleving & opvolging
[Optional Quote — leadership statement on the strategy]
```

### Meeting notes

Audience: attendees and absentees. Goal: capture what was decided
and what happens next. Short by default.

```
[NO cover, NO TOC — these are short]

Title: "Meeting notes — <onderwerp>" (use Title style)
H1Intro: "<datum> — <aanwezigen>"

H1  Agenda
    Bullet list
H1  Bespreking
    Per agenda-punt: paragraph(s) of discussion
H1  Beslissingen
    Bullet list, bold key decision verbs
H1  Actiepunten
    Table: Actie | Verantwoordelijke | Deadline
```

### Analyse / Rapport (analytical report)

```
[Cover if ≥ 8 pages]
[TOC if ≥ 8 pages]

H1  Samenvatting
    Two or three Normal paragraphs — what we did, what we found, what to do
H1  Methode
    Brief: data, scope, limitations
H1  Bevindingen
    H2 per theme or finding category
    Tables for quantitative results
    Charts (referenced as captions; Word can embed separately)
H1  Aanbevelingen
    Numbered if priority matters, bulleted otherwise
H1  Conclusie
H1  Bijlagen (if any)
```

### Memo / Korte nota

```
[NO cover, NO TOC]

Title: short, direct
H1Intro: one-sentence framing

H1  Aanleiding (1 paragraph)
H1  Voorstel / Standpunt (1-2 paragraphs)
H1  Implicaties (bullet list, 3-5 items)
H1  Volgende stappen (bullet list)
```

## How to infer the type

Signals from the user's request that point to a type:

| Phrase / context | Likely type |
|---|---|
| "voorstel", "offerte", "pitch", "voor de klant" | Voorstel |
| "whitepaper", "thought leadership", "vision" | Whitepaper |
| "architectuur", "design doc", "technical design" | Architectuurdocument |
| "AI governance", "AI strategie", "AI policy" | AI-strategie |
| "meeting notes", "notulen", "verslag van gesprek" | Meeting notes |
| "analyse", "rapport", "bevindingen" | Analyse / Rapport |
| "memo", "korte nota", "snelle samenvatting" | Memo |
| No clue / generic "document" | Ask, OR default to Analyse/Rapport if there's substantive content, Memo if it's brief |

## Restructuring inherited content

When converting existing content (markdown, PDF, plain text), do not
assume the source structure is already optimal. Look for these
opportunities:

- **Missing executive summary** — if the document is long but launches
  straight into details, add a "Samenvatting" H1 at the top with 2–3
  paragraphs synthesising the key points.
- **Buried recommendations** — if conclusions or recommendations are
  scattered through the body, consolidate them into a closing H1.
- **Inconsistent depth** — if the source uses H1 through H5 randomly,
  re-bucket into the template's H1–H3.
- **Overlong bullet lists** — if a list runs to 10+ items, consider
  splitting into sub-sections or grouping under H2 headings.
- **Implicit tables** — repeated parallel structures in prose ("X is
  used for A; Y is used for B; Z is used for C") become much clearer
  as a 2-column table.
- **Inline warnings** — phrases like "let op:" or "belangrijk:" in
  prose should become Note callouts.
