# Paper Cut field atlas

FloodLens now uses a cartographic field-atlas composition: the terrain is the first and largest measurement surface; an inspection/legend sheet sits in its margin; the wide crossing record pairs a curve with a reading column; a survey-setup sheet sits below the records. The desk remains a single warm background. There is no marketing hero, emblem, repeated statistic-card grid or dark dashboard shell.

## Reference and exact tokens

Source: [Motion Graphic Style Library / Paper Cut](https://github.com/TheRollerBlader/motion-graphic-style-library/blob/ab7faf2be3e17350f5c6c7e78dfb53d1792ae9cc/catalog/papercut.md), revision `ab7faf2be3e17350f5c6c7e78dfb53d1792ae9cc`, style ID `papercut`, library `motionstyle_papercut`. Its exported CSS is copied verbatim to `frontend/src/motion-theme.css` and imported before the application styles. The MIT notice is preserved in `THIRD_PARTY_NOTICES.md`.

| Source token | Exact value | Application mapping |
|---|---|---|
| bg | `#E7D7C3` | Desk |
| bgRaised | `#F3E6D4` | Inspection sheet / controls |
| surface | `#FFF8F0` | Terrain and crossing paper |
| ink / text | `#2A2118` | Display and body text |
| textDim | `#7A6556` | Coordinates, axes, annotations |
| primary | `#E25B45` | Crossing marks, cursor, notes |
| primaryDark | `#B93E2C` | Route and threshold warning text |
| secondary | `#2F6F6A` | Gauges, causal forecast and water-depth endpoint |
| accent | `#F0C14A` | Small folio tab |
| info | `#3E6BA8` | Simulator-truth curve |
| sheet / sheet_pink | `#F6E4D4` / `#F6D6D0` | Under-sheets and tabs |

The original remaining palette tokens are retained in the copied CSS without substituting a second palette. Water-depth fill interpolates only between source surface and secondary colors, using the same fixed 0–90 mm scale. This interpolation changes appearance, not depths. Discrete categories also use marker shapes/dashes and text. No neon/glass effects are added.

Display is exactly the reference stack `Iowan Old Style, Palatino, Georgia, serif`, weight 700, tracking −0.010em, line height 1.0. Body is `Helvetica Neue, Helvetica, Arial, sans-serif`, weight 500, line height 1.4. Mono annotations use the reference SF Mono stack, weight 600, tracking 0.040em, uppercase, line height 1.2. Sheet radius is 18 px; sheet borders are absent; shadows are exactly `0 16px 24px rgba(80, 50, 30, 0.18)`. Scientific axes retain fine ink guides rather than adopting comic outlines. Matplotlib uses its available serif fallback for portable chart evidence.

## Motion mapping and scientific exceptions

`sheet_x`: −36→0 px (alternate +36→0 by decorative layer), 0.55 s, `cubic-bezier(0.16, 1, 0.3, 1)`. `sheet_y`: +24→0 px, same 0.55 s/easing. Underlay layers combine both shifts. Tabs use the y clip. Layers enter with exactly 0.1 s stagger (0.0, 0.1, 0.2, 0.3 s), lower sheet first. Every entrance is finite and holds its final position. There are no springs and no additional easing families.

The source's `idle_float` token (3.8 s, `cubic-bezier(0.65, 0, 0.35, 1)`, 0→−3→0 px) is retained in the imported export but deliberately not applied to this measurement application. Source guidance about keeping every scene in motion is adapted: terrain planes, numerical readouts, axes, curves and instruments remain stationary. Only decorative paper underlays and section tabs enter. No animated counters or invented intermediate readings are used. Water animation remains the existing user-controlled simulation playback, using actual samples. Rotation remains the existing user-controlled projection.

Under `prefers-reduced-motion: reduce`, CSS animations/transitions are disabled and decorative translations reset. Default playback is paused, so the reduced-motion view is still until the user explicitly plays or scrubs it.

Four primary sheets reflow to one column on narrow screens. The coordinates/curve geometry and underlying quantities are unchanged. Mobile controls wrap instead of overflowing; keyboard focus uses the source info token. Short operational annotations replace the reference's one-line explainer captions because this is an interactive scientific record, not a narrated video.

## Frozen evidence and QA

Simulation, API, arrival policy, observation handling and ML modules are unchanged. All 10 files under `models/` and `results/` retained identical SHA256 hashes throughout the redesign. No experiment was rerun and no numerical file was written. The chart generators change palette/type/layout styling only. `python scripts/restyle_saved_figures.py` reads saved NPZ/CSV/summary artifacts and renders the hero, evaluation and GIF evidence without simulation/training.

Verified locally: 12 Python tests and TypeScript/Vite production build pass. Saved-data hero/evaluation images were visually inspected. Mac headless Chrome launch is denied by the execution environment (SIGABRT / EPERM), so new atlas browser interaction and screenshot checks are prepared but have not passed locally. Existing screenshot files are explicitly treated as historical pre-atlas evidence until replaced by a successful browser run.

On a supported Linux machine, install Python 3.12, Node 24, the pinned Python and npm dependencies and Playwright Chromium; then run:

```bash
python -m pip install -r requirements.lock
cd frontend
npm ci
npm run build
npx playwright install --with-deps chromium
node browser-check.mjs
```

The script starts/stops its own loopback API and verifies desktop/mobile layout, no horizontal overflow, play/pause, rotation, crossing selection, causal arrival gating, policy reruns and reduced-motion animation suppression. Screenshots are authentic renders of the running app at 1440×1250, 390×900 and reduced-motion 1440×1250. CSS entrances are settled for capture, never applied to data values. `.github/workflows/ui-evidence.yml` performs these checks on Ubuntu 24.04 with read-only repository permissions and uploads screenshots as `floodlens-atlas-ui-evidence` after all checks succeed. It triggers on pushes to `design/**`, relevant pull requests or manual dispatch. Historical screenshot outputs are removed in the CI checkout before capture, preventing stale images from being uploaded as redesign evidence. No commit, push, workflow execution or publication has been performed in this task.
