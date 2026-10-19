# Repository reorganization — 19 October 2026

Authorized scope: gather ArcMap/Pro tools in a dedicated folder, rename `utils`
to `mirsad_core` using English folder names, retire completed/redundant execution
plans, organize Desktop documentation, validate dependencies and update GitHub.

## Layout and documentation

- `Toolboxes/`: three `.pyt` entry points, matching XML, raster implementation
  and two compatibility modules. No duplicate root-level toolboxes.
- `mirsad_core/`: shared runtime support only. Style, document, station and data
  maintenance generators are grouped under the corresponding `scripts/` folders.
- Desktop documentation: `STATUS.md`, `BACKLOG.md`, `CHANGELOG.md`, and the
  `architecture/`, `reports/`, `development/`, `user/`, `design/` categories.
- Consolidated and removed the old help/readiness execution plan and parity
  execution plan after retaining outstanding requirements in the backlog.
  The old implementation plan is a delivery history, not an active plan.
  Original product/design requirements and images remain as clearly marked
  reference material; they are not claims of completed functionality.
- Updated source imports, independent build/vendoring, catalogue/style/calendar
  paths, maintenance entry points, native parameter extraction, tool help,
  generated manual destinations, contributor guidance and relative links.
- Renamed the point compatibility module's dynamic module alias so it cannot
  shadow the real `mirsad_core` package. Removed an obsolete root-level compiled
  raster cache from import resolution into ignored migration scratch.

## Preservation and scientific contracts

The ignored local migration record contains the before-status snapshot,
before-file hashes, original moved files and old-to-new map. User Sample Data,
geodatabases, existing deletions and original station data were not reorganized.
Two locally modified container XML files and two untracked ArcGIS XML files
were moved byte-for-byte; their incidental edits are not included in the commit.

All reviewed scientific function/constant signatures and the 521 emitted field
definitions are unchanged. Shared adapters remain byte-identical to Desktop
copies. The scientific-module provenance hash changes because its reference
file moved and gained bootstrap paths; no climate formula changed.

## Verification

- Native **ArcGIS Pro 3.6** loaded the relocated tools and re-read default
  parameters: **69 point, 76 station, 36 raster**. Compared against the previous
  native snapshot: **no parameter-definition changes**. Source paths/hashes now
  identify the new files. This is metadata verification, not a processing run.
- **17 isolated legacy suites / 146 tests** verify imports, providers, scientific
  dependencies, exports, station identity/selection, tool validation and layout.
- **7 Python 2.7 suites / 68 tests** passed, including cold relocated imports.
  ArcPy doubles were explicit; native ArcMap processing remains unverified.
- New cold-import checks start a fresh interpreter outside the checkout, with
  no inherited PYTHONPATH. All three toolbox registrations and both compatibility
  wrappers load, catalogue/help paths resolve, and the package is not shadowed.
- **63 Desktop tests** passed in 160.547 seconds. Frozen self-test, GUI, worker
  exports, workspace and bilingual standalone help passed outside the checkout
  with a clean PATH; help imported neither map nor ArcPy. The development bundle
  was replaced only after its acceptance/hash checks passed.
- Layout/link checks passed. The old XML edits remain unstaged at their new
  paths; **105 existing data/reference files** and both modified XML files matched
  their pre-migration bytes. Prior limits remain in [BACKLOG](../BACKLOG.md).

This work does not promote stable, publish a binary release, change provider
credentials, correct observations or alter scientific missing-data/unit rules.

## Final delivery

- A clean export of the staged source passed catalogue/asset preparation,
  scientific vendoring, guide generation, repository contracts, **111 local
  documentation links**, and the two cold-import/layout tests. It used the
  existing independent QA interpreter, not a newly installed environment or a
  second complete PyInstaller build.
- The development installer passed payload readback, installed workspace,
  uninstall and user-file preservation checks. The development program was
  reopened; stable and the production installation were unchanged.
- Development EXE SHA-256:
  `c10d974769e54fb8dc4607254e54f3123cd5e57747e6f9e619e7764bdd691389`.
- Development bundle SHA-256:
  `e03c4179e6957bb590b08735e60bade22f273b03f423a8c2a5aa4376fb6ac196`.

After updating an existing checkout, point ArcGIS folder connections at
`Toolboxes/`. Old root-level toolbox paths and `utils` imports are intentionally
retired. Keep the whole repository layout for ArcGIS tools; Desktop distributions
remain self-contained.
