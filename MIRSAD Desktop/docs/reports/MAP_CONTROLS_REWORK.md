# Native map controls — 18 October 2026

Development 0.4.0.dev3 replaces the expanding map toolbar with compact controls
inside the existing native Qt canvas. Map, table and processing panel positions
are retained. No climate calculations, output contracts or basemap providers change.

- A 34 px layers icon opens a 320 px native popup gallery with the eight existing
  basemap styles. Selection has a visible accent border and the current style is
  available in the trigger tooltip. Swatches are schematic style illustrations,
  generated locally, not geographic tiles or extra network requests.
- A neighboring point-placement icon has a checked state, crosshair and localized
  instruction. Esc cancels placement when the map has keyboard focus.
- Zoom in/out, fit data and world extent sit in a compact floating vertical group.
  Zoom boundaries disable the corresponding button. Shortcuts (+, =, −, F) apply
  only when the canvas has focus and do not intercept text entry in tool inputs.
- At short viewport heights the extra fit/world buttons collapse; wheel/keyboard
  zoom and fit-to-data shortcut remain available. Controls stay within the canvas.
- Outline icons render from local vector paths at the requested size. Active,
  selected, hover, disabled and keyboard focus states follow the light/dark theme.
- Viewer tabs have consistent outline icons, spacing and an accent underline;
  compact windows retain native tab scrolling. Existing tab order is preserved.
- Attribution remains visible below the map, with compact coordinates and network
  status. The scale bar follows light/dark mode. Point-name tooltips now escape
  text through the explicitly imported HTML helper.

## Acceptance

- Eight UI interaction tests passed, including selecting a basemap, dismissing the
  gallery, zoom/world controls, Esc cancellation, zoom limits, geometry containment
  and Arabic/English plus light/dark variants. Existing exports, worker-crash
  recovery, readonly previews, selection and independent tool drafts also passed.
- `scripts/capture_map_controls.py` captured the actual Qt window and popup in all
  four theme/language combinations. The real network capture loaded 24 visible
  basemap tiles. Images and geometry/error reports are in
  `.test-output/map-controls/`; no screenshot/mockup is used as the application UI.
- A second capture uses `QT_SCALE_FACTOR=2` to check sharp icons and popup sizing
  at 200%, including a compact window. Captures use isolated settings.
- Development EXE/installer packaging checks are recorded alongside this candidate
  in `.test-output/map-controls-build.log` and installer acceptance reports.
- The complete Desktop suite passed **36 tests**. The rebuilt 0.4.0.dev3 EXE
  passed GIS self-test, actual GUI screenshot, UI worker export and workspace/
  preview gates outside the repository working directory, without ArcPy paths.
- The candidate installer passed payload readback, installed workspace, uninstall
  and user-file preservation checks with the separate QA AppId; production was
  unchanged. Bundle SHA256:
  `d8975246a5c900869869d5d1b0ed97d4bd9d109a6e0d120ce94ec53b25dcdb8e`.
  Installer SHA256:
  `7aea2cdbcaa8239c1fbad76f616061e0016a394745e5529f30ee1632e5d24012`.

The eight basemap entries retain their current services/attribution. This work
does not add API-key services, a tile downloader, new projection behavior or new
web/UI runtime dependencies. Stable requires the existing explicit approval flow.
