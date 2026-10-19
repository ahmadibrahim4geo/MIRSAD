# Coordinate-system browser — 0.4.0.dev5

Reviewed 18 October 2026. User references: the supplied ArcGIS Pro Geographic/Projected screenshots and the requested nested UTM folders.

## Findings and changes

The default embedded Pro taxonomy already held the native folder paths. The alternate “Latest Esri catalogue” option replaced them with the public Projection Engine catalogue's **area-of-use descriptions**. Those descriptions are not Pro folder paths; they produced the long country/area list reported by the user. Neither Favorites nor Layers existed in that browser.

The browser now always starts with Favorites, Layers, Geographic Coordinate System and Projected Coordinate System. The native scientific folder/definition names remain English in both UI languages, matching the supplied reference. Geographic contains 3D, Africa, Antarctica, Asia, Australia and New Zealand, Central America, Europe, North America, Oceans, Solar System, South America and World. Projected contains ARC (equal arc-second), Continental, County Systems, Gauss Kruger, National Grids, Polar, Solar System, State Plane, State Systems, Tribal, UTM, World and World (Sphere-based).

UTM retains Africa, Asia, BLM (US Feet), Europe, Indonesia, Italy, Malaysia, New Zealand, North America, Oceans, South America, WGS 1972 BE, WGS 1972 and WGS 1984. WGS groups retain their Northern Hemisphere/Southern Hemisphere children. Names and version follow the captured native source, rather than guessing names from the spoken examples.

The 7,519 native folder entries, including 94 aliases, cover 7,425 distinct authority codes. The optional public definitions add 1,760 distinct codes, giving 9,279 folder entries and all 9,185 public authority definitions. The additions appear inside explicit “Additional Esri definitions (outside Pro 3.6 tree)” branches. No unverified Pro folder path is invented for them. The native branches and their order stay unchanged in either mode.

## Workflow

- Favorites is an explicit user list, persisted through QSettings, with Add/Remove Favorite. No country-specific defaults are assumed. It survives cancelling the selection dialog, as a normal preference.
- Layers groups loaded layers by their actual source CRS, with the layer names underneath. Unknown/unsupported source definitions remain Unknown and cannot be selected. Opening the browser performs no GIS file parsing; worker-provided metadata is used.
- The original CRS metadata of point imports, polygon imports and spatial previews now reaches the layer registry. A normalized WGS84 display geometry does not replace the original dataset's CRS in this list. No original dataset is rewritten.
- Geographic/Projected branches start collapsed so users see the main groups immediately. Show selected opens the selected path. Search includes names, authority codes, layer names and paths; clearing it restores previous expansion. Details is optional and shows units, datum and projection parameters. Invalid definitions cannot be accepted/bookmarked.

The taxonomy is bundled and independent of ArcGIS at runtime. The development source snapshot and its hashes remain `assets/crs_pro_tree_manifest.json` and `assets/crs_catalogue_manifest.json`; this update does not refresh or alter their definitions.

When a user has development open, `build_development.ps1 -PrepareOnly` verifies build scratch without replacing that application. Installer build/QA accept `--candidate` for the same verified development scratch. This allows all candidate checks to finish before requesting closure of a user's current session. These options cannot create/promote a stable release. Normal build commands keep their previous behavior.

## Verification

Independent expected-path checks cover both full modes, the top-level folder order, every UTM subgroup and EPSG:32636/32736 in the appropriate hemisphere. Native GIS readback verifies imported EPSG:32636 metadata, normalized coordinates, identifier preservation and unchanged source bytes, including an incorrect supplied fallback overridden by the file's actual CRS. UI checks exercise bookmark persistence/removal, unknown layers, searching layer names, search expansion restoration and invalid definitions.

Native captures in `.test-output/crs-picker/` cover Arabic/English and light/dark at 100%/200%, including the details pane. They assert that the complete window frame remains inside the available desktop area. Initial sizing accounts for screen scale and native frame margins; compact windows collapse Favorites/Layers initially so the four main groups remain accessible. Packaged workspace acceptance opens the actual browser, reads EPSG:32723 from its generated/loaded GeoPackage, checks the native Southern Hemisphere path, and verifies that the additional definitions retain UTM's position.

Final candidate verification completed on 18 October 2026:

- The full 40-test regression suite passed in 87.978 seconds (`.test-output/crs-browser-final-build.log`). After the final screen-sizing adjustment, the focused CRS UI regression passed again in 2.271 seconds and both native capture runs passed their frame-containment assertions, with Details both hidden and visible.
- The final frozen candidate passed scientific/GIS/raster self-tests, GUI smoke, GUI export and workspace acceptance from outside the repository (`.test-output/crs-browser-screen-build.log`). It reads the actual EPSG:32723 source metadata and selects the native UTM/Southern Hemisphere path, including when that code also exists in Layers.
- Installer acceptance passed complete payload hash readback, installed workspace/CRS checks and uninstall, with user files preserved and production installation unchanged. See `.test-output/installer_acceptance.json` and `installed_workspace.json`.
- After the user's explicit permission to close and replace development, the verified bundle replaced `runtime/development/MIRSAD.exe` with 0.4.0.dev5. Finalization revalidated the candidate before the swap, and a separate GUI startup from the fixed development path passed afterward (`.test-output/crs-browser-development-replacement.log`, `crs-post-replacement.png`).
- The installer at `runtime/installers/development/MIRSAD-Setup.exe` was rebuilt from that final development directory and passed payload readback, installed workspace/CRS acceptance and uninstall again. Stable remains unchanged, with its reserved README only.

Candidate SHA-256 hashes:

```text
bundle     7ce8bc5fa86eb2d31cfabcf80719a30703f2dda5a7a803caea44c83f06de202e
exe        f3390d733ab3f1a63fc345c6fdca599fc5919913e6143898df3b77cdc3e541bd
installer  4712afbffafc9f019f8e9a4230523e083efe3000fd1f49ff819c44d8d11fd6ce
```
