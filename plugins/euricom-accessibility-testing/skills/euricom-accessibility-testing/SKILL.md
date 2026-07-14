---
name: euricom-accessibility-testing
description: >-
  Diagnose, test, and review web accessibility with awareness of the full
  pipeline: browser accessibility tree → platform accessibility API → screen
  reader. Trigger when the user (1) reports a screen reader or keyboard
  navigation bug ("works in NVDA but not JAWS", "VoiceOver reads this wrong",
  "focus escapes the modal", "two testers get different results"); (2) asks to
  test, audit, or review a page or component for accessibility / a11y / WCAG;
  (3) asks which screen reader + browser combinations to test with, or how to
  test from a Mac when users are on Windows; (4) writes or reviews ARIA
  attributes, roles, accessible names, or React Aria components; or (5) wants
  automated accessibility checks in Playwright or CI. Core insight: "browser +
  OS" never fully identifies an accessibility bug — the screen reader and the
  platform API it uses are part of the repro.
---

# Accessibility testing: the love triangle

Web accessibility behaviour is produced by **three cooperating layers** —
browser, platform accessibility API, and assistive technology — and a bug (or
a false pass) can originate in any of them. Detailed background on each layer
and the full source-talk notes live in
[references/love-triangle.md](references/love-triangle.md); read it when you
need to explain *why* a discrepancy happens or which API a given screen
reader consumes.

## The mental model (memorize this)

1. **Browser → internal accessibility tree.** The browser extracts roles,
   names, states, and properties from the DOM following W3C specs (HTML-AAM
   fills role/state/properties; the Accessible Name and Description
   Computation fills name/description). The specs define *what* goes in the
   tree, **not its structure** — each browser builds its own internal tree,
   some flatten more nodes than others. Unlike the DOM, the accessibility
   tree is not standardized. *First layer of discrepancy.*
2. **Platform API → reshaped tree.** The OS-level accessibility API conveys
   the tree to assistive technology, and each API has different instructions
   for handling it. The accessibility tree is therefore not a fixed
   structure but "a semantic model that gets reshaped to fit each platform
   API." The APIs do not coordinate across operating systems. *Second layer.*
3. **Screen reader → interpretation.** Each screen reader supports different
   APIs and applies its own heuristics. JAWS and NVDA inject code into the
   browser to build a **virtual buffer** (fast page processing without
   constant OS queries) and can make **educated guesses that mask bugs caused
   by incorrect HTML** — a page can "pass" in JAWS/NVDA while genuinely
   broken elsewhere. *Third layer.*

**Consequence:** "keyboard focus breaks in Chrome on Windows" is
under-specified. Two testers on identical browser + OS can get different
results — e.g. one tabs behind an open modal and the other doesn't —
depending on which assistive technology (if any) is running. Always record
**browser + OS + screen reader + versions** in any accessibility bug report,
and reproduce with that exact triple.

## Who runs what — don't test only your own setup

Per the WebAIM Screen Reader Survey (#10) and the State of the Frontend
report: **most screen reader users are on Windows; most frontend developers
work on macOS.** A Mac-only developer is structurally testing the least-used
path. Key support facts:

| Screen reader | Platform | APIs consumed | Notes |
|---|---|---|---|
| JAWS | Windows | UIA **and** IAccessible2 (comprehensive) | Most popular (paid). Dominant for historical/government-funding reasons, not features. Virtual buffer can mask HTML bugs. |
| NVDA | Windows | Primarily IAccessible2; UIA support steadily increasing | Free and open source, second in popularity. Also uses a virtual buffer. |
| Narrator | Windows | UIA **only** | Built into Windows. Surfaces bugs that JAWS/NVDA paper over. |
| VoiceOver | macOS | AX API (deep integration) | Only ~7% of screen reader users run the "intended" VoiceOver + Safari pairing. |

Platform API landscape: **macOS** = AX API. **Windows** = UI Automation
(modern) + MSAA (legacy, superseded by UIA). **IAccessible2** is embedded in
Chromium-based browsers and Firefox (not in the OS); it was their primary API
before UIA adoption, and Firefox still primarily exposes IAccessible2. The
vendor-"intended" clean pipelines (Edge + Narrator + UIA; Safari + AX API +
VoiceOver) are the minority in the real world — Chrome/Firefox with
JAWS/NVDA account for most real usage **and** most complexity. Test those
first.

## How to test — minimum viable matrix

Two operating systems with their respective screen readers "will actually get
very far" when resources are limited:

1. **Windows + Chrome (or Firefox) + NVDA** — free, and the closest match to
   real-world screen reader usage. Add **JAWS** if the project can afford a
   licence; add **Narrator** as a cheap UIA-only cross-check.
2. **macOS + Safari + VoiceOver** — covers the AX API path.

Mac-based developers: paid VM products let you run NVDA/JAWS from a Mac.
It's workable but tricky — mishaps can depend on the virtualized system — so
if accessibility matters to the project, prefer a dedicated Windows device
(or several).

### Automated checks (a subset, never the whole story)

- **Playwright's accessibility tooling** is one of the most popular and
  effective automated options: axe scans via `@axe-core/playwright` for CI,
  plus ARIA-snapshot / accessibility-tree assertions for regression-testing
  roles and accessible names of components.
- Automation validates the tree; it cannot judge how a screen reader
  *announces* the experience. Manual keyboard-only passes (Tab/Shift+Tab,
  arrow keys, visible focus, no focus escaping dialogs, no traps) remain
  mandatory before sign-off.

### Compatibility lookups before you rely on a pattern

- **a11ysupport.io** — per-feature test results across screen reader ×
  browser pairs. Results can be outdated, but it's a good start. Telling:
  ~80% of its tests concern ARIA — that's where the fragility lives.
- **ARIA-AT (W3C)** — assistive-technology interoperability test data.
- **Accessibility Compact Data** (project by Lola Odelola) — aims to surface
  "does this browser feature work in assistive tech?" directly inside the
  developer tools and browsers you already use.
- When you hit a genuine browser or screen reader defect, **report it
  upstream** (browser trackers, NVDA GitHub, JAWS support). Virtual buffers
  masking bugs means unreported bugs stay invisible; public bug lists also
  help the next developer troubleshoot.

## ARIA: necessary sometimes, complicating always

A native screen reader user consulted for the source talk called ARIA one of
the biggest problems in screen reader output. Rules when writing or
reviewing code:

- **No ARIA is better than bad ARIA.** Native semantic HTML (`<button>`,
  `<nav>`, `<dialog>`, `<label>`) maps correctly to all three platform APIs
  for free; ARIA re-implementations must get role, states, keyboard handling,
  and focus management right by hand.
- The Accessible Name and Description Computation has its own **priority
  algorithm** for choosing among competing labels — and each browser also
  makes its own call (what Chrome exposes as the description another browser
  may expose as a different property). So **don't over-label**: stacking
  `aria-label`, `aria-description`, and `aria-describedby` on one element
  produces browser-dependent output, and redundant ARIA makes screen reader
  output verbose even when technically valid.
- **Component libraries don't exempt you.** React Aria and similar libraries
  ultimately emit ARIA attributes, so the same computation quirks and
  support gaps carry over — verify the rendered output, not the library's
  promise.
- When ARIA is genuinely needed (no native element expresses the semantics),
  implement the complete APG pattern: role **and** required states **and**
  keyboard behaviour. A role without its keyboard contract is worse than
  nothing.

## Debugging workflow: "the screen reader reads X wrong" / "testers disagree"

1. Pin down the full triple from the report: browser + OS + assistive
   technology (+ versions), and whether a screen reader was running at all —
   JAWS/NVDA virtual buffers change page behaviour, so "same browser, same
   OS" with and without a screen reader are *different environments*.
2. Inspect the accessibility tree in DevTools (Chrome: Accessibility pane;
   Firefox: Accessibility Inspector). Wrong role/name/state **in the tree**
   ⇒ fix the HTML/ARIA; this is your bug.
3. Tree correct but announcement wrong ⇒ test a second screen reader on the
   same browser. Output differs ⇒ API-layer or interpretation difference:
   check a11ysupport.io for known gaps and prefer a pattern with wider
   support over fighting the assistive technology.
4. Only one browser has a wrong tree for identical HTML ⇒ browser mapping
   difference: prefer markup that maps identically everywhere (usually more
   native HTML, less ARIA), and report the mapping bug upstream.

## Making it stick with the team

- Run **accessibility empathy labs** (format borrowed from Skyscanner):
  ~30-minute team sessions — 10 minutes keyboard-only on your own product,
  screen-blur/black-screen tools, or accessibility simulation games. People
  remember what they *felt*; nobody remembers the checklist. Keep it fun so
  it starts conversations instead of feeling like a burden.
- The single highest-leverage developer action is not technical: **get to
  know how real assistive-technology users experience the web** — follow
  screen reader users who create content, watch their videos. Accessibility
  starts with a human-first approach, then the technical model above makes
  the debugging tractable.

---

*Source: "Browser, API and Assistive Technology: A Love Triangle" — Tshepiso
Lehutjo (software engineer & accessibility champion at IKEA), JSNation 2026.
Full talk notes: [references/love-triangle.md](references/love-triangle.md).
https://gitnation.com/contents/browser-api-and-assistive-technology-a-love-triangle*
