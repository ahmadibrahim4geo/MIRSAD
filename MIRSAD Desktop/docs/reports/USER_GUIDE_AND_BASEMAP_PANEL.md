# User guide and basemap panel — 0.4.0.dev4

Reviewed 18 October 2026. This follow-up supersedes the focus-dismissal behavior of the dev3 basemap gallery. It changes Desktop help and map controls, not climate calculation or export contracts.

## User-visible behavior

The basemap icon opens an embedded transient panel, rather than a pinned sidebar. Selecting a style, clicking outside, pressing Esc or using Close dismisses it. Losing focus to the screenshot interface alone does not. A Windows mouse-button check runs only while the panel is visible, allowing a later click outside the application to dismiss it too. No global mouse hook is installed and no keyboard input is monitored. Qt handles clicks inside the application and keyboard dismissal.

The gallery identifies the selected style and provider, uses schematic local swatches without extra network requests, and scrolls when necessary. Short map canvases use compact icon/text rows. Its geometry stays inside the canvas. Light/dark palettes and Arabic/English labels share the existing application theme.

Help/F1 opens a reusable modeless manual. It has language selection, 15 contents entries, internal links, full-document search with previous/next and wraparound, Ctrl+F, and palette-aware readable text. Arabic places the contents on the right. The same generated HTML is available outside the application in `USER_GUIDE_AR.html` and `USER_GUIDE_EN.html`.

## Content and maintenance

`scripts/build_user_guide.py` generates both manuals and the bundled contents index. Module names and dependencies come from the actual registry, with an explicit check covering all 19 groups. The development build regenerates the guide before running tests. The document covers the actual three tools, input roles/CRS/selection, climate sources and date ranges, Hybrid sequencing and estimates, temporal summaries/units, regional monthly grids, interpolation, outputs, previews, tasks/cancellation, worked examples and troubleshooting.

Provider coverage is documented using the official POWER Daily/Monthly/UV, Open-Meteo Historical Weather and NOAA GSOD references linked beside the tables. Archive start dates are not station completeness guarantees. Unimplemented providers, incomplete advanced Toolbox parity, long-format daily output, raw coverage and monthly estimate limitations are stated explicitly. Downloading, climate calculation and persistence are unchanged in this update.

## Verification

Automated checks exercise focus-loss survival, selection/Esc/outside-click dismissal, the inactive-window pointer boundary, bilingual manual navigation/search and all registered modules. Frozen workspace acceptance also opens the bundled guide in both languages and checks provider coverage and chapter count.

Native Windows screenshots under `.test-output/guide-panel/` cover both languages and both themes at 100% and 200% scale. A real second Qt window receives focus while the gallery remains visible; compact canvas geometry and scrolling are checked separately. This tests native focus transfer, not the OS-specific timing of every screenshot utility.

Final candidate verification completed on 18 October 2026:

- **37 tests passed** in 84.578 seconds (`.test-output/guide-panel-final-build.log`), including bilingual search/navigation, physical contents-pane order, focus/dismissal behavior and the existing scientific/export/worker regression checks.
- Both native screenshot runs returned no errors and retained the panel across actual focus transfer. Arabic/English contents positions are asserted after layout settles; 100% and 200% captures were visually reviewed.
- The frozen EXE passed its scientific/GIS/raster self-test, GUI smoke, GUI worker export and workspace acceptance from outside the repository. Workspace acceptance opened the bundled manual in both languages and verified 15 chapters and provider date coverage. Packaged diagnostics report no ArcPy import or ArcGIS dependency paths.
- The development installer passed complete payload hash readback, installed-app workspace/manual checks and uninstall. User-created files and a separate project survived; production installation was unchanged. See `.test-output/installer_acceptance.json` and `installed_workspace.json`.
- Fixed development paths are `runtime/development/MIRSAD.exe` and `runtime/installers/development/MIRSAD-Setup.exe`. Stable still contains its reserved README only; no promotion occurred.

Candidate hashes (SHA-256):

```text
bundle     2ded2848c618e93ef1b36ac0af276dbf27cbb7575c3cc640356c90b20448c4a8
exe        f862c49c655a090b1f5ebf16da692c2fc8082a763e872c8d492292ac34f5107c
installer  5ea143847f6d580eb7083f1fc2e2bcc8bc9e0682d2752bf5b1923cdb2dbf99f4
```
