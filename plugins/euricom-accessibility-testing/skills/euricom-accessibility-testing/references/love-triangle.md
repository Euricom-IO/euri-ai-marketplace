# Talk notes — "Browser, API and Assistive Technology: A Love Triangle"

Tshepiso Lehutjo — software engineer and accessibility champion at IKEA,
conference committee member at Øredev, accessibility and digital-divide
advocate. JSNation 2026 (Amsterdam), 28 min.
https://gitnation.com/contents/browser-api-and-assistive-technology-a-love-triangle

Scope note: the talk deliberately covers the **desktop** accessibility
journey — assistive technology history lives on desktops — even though the
world is mobile-first. The systems are also constantly changing: some APIs
discussed were not even supported a few years ago, so re-verify support
claims periodically.

## The opening case (the mystery the talk solves)

During a team accessibility session, a colleague tested keyboard navigation
(no screen reader needed) and found a focus-management failure: with a modal
open, he could Tab onto elements *behind* the modal — a real failure, since a
keyboard-only user would have to tab through all the irrelevant background
content to get back to the modal. A second colleague re-tested on the **same
browser and same operating system — and got different results.**

The resolution is the talk's thesis: the browser + OS pair does not define
the test environment. What sits between the developer's HTML and the user —
the accessibility tree the browser built, the platform API in play, and
whether an assistive technology (with its own injected code and virtual
buffer) is running — all change observed behaviour. Sometimes it's genuinely
not your code.

## Layer 1 — the browser and its accessibility tree

- DevTools shows the HTML translated into an **accessibility tree**: an
  extraction of roles, names, states, and properties — the semantics a screen
  reader (or braille reader) must communicate to users.
- Two W3C specs govern the mapping. For, e.g., a `<button>`:
  - **HTML-AAM** (accessibility mapping) supplies the role, state, and
    properties;
  - **Accessible Name and Description Computation** fills the name and
    description slots.
- The specs define **what** goes into the tree, but say nothing about its
  **structure**. Each browser builds its own *internal* accessibility tree;
  some browsers flatten certain data points more than others. Unlike the
  DOM tree, the accessibility tree is **not standardized** — the first layer
  of discrepancy. (Per the Q&A: W3C appears to be moving toward
  standardizing this, which would help a lot.)

## Layer 2 — platform accessibility APIs

- Operating systems each have their own accessibility API providing the
  protocol for conveying accessibility-tree information to assistive
  technology. **The APIs do not coordinate across operating systems.**
- **macOS: AX API** — VoiceOver has deep integration with it.
- **Windows: UI Automation (UIA)** is the modern API; **Microsoft Active
  Accessibility (MSAA)** is legacy, superseded by UIA. Narrator, JAWS, and
  NVDA can all talk to the Windows APIs.
- **IAccessible2** is special: an accessibility API **embedded in the
  browser** (Chromium-based browsers and Firefox), not in the OS. Before UIA
  adoption it was these browsers' primary API.
- Each API has different instructions for handling the accessibility tree,
  so the tree "is not a single fixed structure — it's a semantic model that
  gets reshaped to fit each platform API." Second layer of discrepancy.

### The developer/user mismatch

Two surveys frame why this matters:

- **WebAIM Screen Reader Survey #10**: the majority of screen reader users
  run **Windows** as their primary OS.
- **State of the Frontend (Software House)**: frontend developers primarily
  work on **Mac**.

Developers therefore live on the least-representative side of the triangle
by default.

## Layer 3 — screen readers

- Screen readers convert digital text to synthesized speech; essential for
  many blind and visually-impaired users. The first true screen reader was
  the **IBM Screen Reader (1986)**.
- **JAWS** — most popular (WebAIM survey); paid, Windows. Comprehensive
  support for **both UIA and IAccessible2**.
- **NVDA** — free and open source, close second in popularity. Works
  **primarily with IAccessible2** today; UIA support steadily increasing.
- **Narrator** — built into Windows; supports **UIA only**.
- **VoiceOver** — native on Apple devices; AX API. Apple has announced
  AI-driven features (contextualized, more detailed image descriptions).
- **Virtual buffers:** JAWS and NVDA inject their own code directly into the
  browser, creating a virtual buffer so pages process quickly without
  constant OS queries. Through it they can make **educated guesses that mask
  bugs caused by incorrect HTML**. Hence: report bugs (to browsers and
  screen reader projects) — masked bugs otherwise stay invisible, and public
  bug repositories help other developers troubleshoot.

## Combinations — intended vs. real

- Vendor-intended clean pipelines (whole stack owned by one company):
  - Windows: **Edge → UIA → Narrator**
  - macOS: **Safari → AX API → VoiceOver**
- Reality: only **7%** of screen reader survey users use VoiceOver + Safari.
  **Chrome and Firefox account for the most complexity**: Firefox has been
  slow to adopt UIA and primarily exposes IAccessible2; Chromium supports
  both; screen readers are mid-migration toward UIA as the default.

## Support / compatibility resources

- **a11ysupport.io** — community test results for feature × screen reader ×
  browser combinations. Can be outdated, but a good start. ~**80% of its
  tests relate to ARIA** issues.
- **ARIA-AT (W3C)** — assistive technology interoperability testing.
- **Accessibility Compact Data** — project by **Lola Odelola**: make it easy
  for developers to know whether a feature that works in the browser also
  works in assistive technology, and integrate that information **into the
  tools and browsers developers already use** rather than yet another
  platform.

## Q&A highlights

- **Multi-OS setup from a Mac:** paid VM products exist for testing
  NVDA/JAWS from a Mac; effectiveness is uncertain (mishaps can depend on
  the virtualized system) but it's worth it — or keep a dedicated
  device/devices.
- **React Aria (and similar libraries):** they expose the same ARIA
  attributes to React components, so the issues of raw ARIA carry over.
- **ARIA in general:** a native screen reader user consulted for the talk
  called ARIA one of the biggest problems in screen reader output. The
  accessible name/description computation has its own priority algorithm,
  and each browser additionally decides where a given label lands (what
  Chrome exposes as description another browser may expose as a different
  property). Over-labeling — e.g. using both `aria-description` and
  `aria-describedby` — complicates output. Best practice remains: avoid
  ARIA where possible, use it only when necessary.
- **Why JAWS beats native options in popularity:** history, not features —
  it has long been the go-to supplier for government agencies; newly blind
  people are typically handed JAWS and trained on it, so it becomes the
  default. Paid product, good marketing.
- **Pushing accessibility in a company:** champions usually start on their
  own initiative and bring a working blueprint to the company; the lack of
  standard structure for accessibility programs is a core obstacle.
- **Empathy labs** (idea borrowed from Skyscanner): ~30-minute team
  sessions — keyboard-only challenges (~10 min), screen-blur or black-screen
  tools, accessibility simulation games. "If people actually feel it
  themselves, they remember it — instead of just going to look at the
  guide." Make it fun so it starts conversations rather than feeling like a
  burden. (Speaker's own trigger: carpal tunnel episodes that made her
  unable to use a keyboard.)
- **Single most important developer action:** get to know native screen
  reader / assistive technology users — follow the content they create.
  "Our solution doesn't hinge on technicality… it starts with a human-first
  approach."
- **Cheapest / automated testing:** two operating systems with their
  respective screen readers gets you very far (Mac with Safari, Windows
  with Chrome or Firefox). For automation, **Playwright's accessibility
  plugin** is one of the most popular and effective options.
