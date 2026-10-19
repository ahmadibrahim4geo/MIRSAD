# Development handoff and GitHub distribution

Updated: 19 October 2026. The user explicitly authorized uploading **source,
documentation and the current development installer**. This authorizes the
identified preview below; it does not authorize stable promotion or future
untested releases.

## Maintainer handoff

- [Shared AGENTS.md](../AGENTS.md): chronology, layout, common contracts,
  sources, scientific/data preservation, verification and publication scope.
- [Toolbox AGENTS.md](../Toolboxes/AGENTS.md): the three ArcGIS entry points,
  shared support, Python 2.7/3 compatibility, metadata and native-test limits.
- [Desktop AGENTS.md](../MIRSAD%20Desktop/AGENTS.md): implementation milestones,
  architecture/UI/source/help decisions, build/packaging paths and acceptance.
- [Current status](../MIRSAD%20Desktop/docs/STATUS.md),
  [backlog](../MIRSAD%20Desktop/docs/BACKLOG.md),
  [delivery history](../MIRSAD%20Desktop/docs/CHANGELOG.md) and
  [reorganization evidence](../MIRSAD%20Desktop/docs/reports/REPOSITORY_REORGANIZATION.md).

Historical local milestones on 17–18 October were consolidated in source commit
`b8a97c4` on 19 October. Later changes are `fd8dae1` (field explanations),
`5856e98` (subtitle localization) and `e356ff7` (repository layout).
The handoff documents record these distinctions rather than inventing commits
or treating historical plans as current acceptance.

## Approved development preview

| Item | Value |
|---|---|
| Product/version | MIRSAD Desktop 0.4.0.dev8 |
| Platform/channel | Windows x64; development prerelease |
| GitHub tag | `desktop-v0.4.0-dev.8` |
| Installer asset | `MIRSAD-Desktop-0.4.0.dev8-Windows-x64-Setup.exe` |
| Installer bytes | 148745729 |
| Installer SHA-256 | `8740a1d41a5dbe34aba0771fd5a551840208f1e92dbf8a5bcd9b11e1d2d44b5f` |
| EXE SHA-256 | `c10d974769e54fb8dc4607254e54f3123cd5e57747e6f9e619e7764bdd691389` |
| Bundle SHA-256 | `e03c4179e6957bb590b08735e60bade22f273b03f423a8c2a5aa4376fb6ac196` |
| Runtime source baseline | `e356ff7bbf637dcdd5a4952307366cb62aa7a95e` |
| Signing/stable | Unsigned development installer; no stable promotion |

The release tag identifies the source/handoff revision used for publication.
The exact revision and asset sizes/checksums are recorded in the uploaded
`release-manifest.json`; `SHA256SUMS.txt` covers the installer, both CHMs and
that manifest. The runtime binary remains the already tested candidate above;
documentation-only handoff updates do not require an unrelated rebuild.
`installer_manifest.json` keeps `approved: false` because that flag denotes
stable-channel approval, not the user's separate development-upload permission.

Acceptance for this candidate: 63 Desktop tests, 17 isolated legacy suites / 146
tests, 7 Python 2.7 suites / 68 tests; native Pro 3.6 parameter extraction;
frozen self-test, GUI, processing exports, workspace and bilingual help; static
source equivalence; installer payload readback, installed workspace, uninstall
and preservation of user files. Exact scopes are in the reports above.

Remaining acceptance includes native ArcMap processing, full advanced
Toolbox/Desktop schema/raster parity, authenticated CDS/IMERG access, complete
DPI/accessibility coverage, ArcGIS-native help rendering and the documented
legacy LST temperature-difference conversion issue. A prerelease does not close
these items or become an approved stable version.

## Distribution targets

- [Development release](https://github.com/ahmadibrahim4geo/MIRSAD/releases/tag/desktop-v0.4.0-dev.8).
- Source code and documentation are tracked in the repository and available
  through the release's source archives. ArcGIS tools require the full checkout
  layout described in `Toolboxes/README.md`.
- The installer contains the independent app and bundled resources/catalogue;
  the installed app needs neither ArcGIS nor a separate Python installation.
  Its `_internal` directory belongs with the EXE.
- Both language CHMs are downloadable release assets as well as repository
  resources. Development binaries are not committed into source history.
- User Sample Data/geodatabase modifications and deletions, local ArcGIS XML
  edits, accounts, projects, virtual environments, compiler tools and test/build
  scratch remain outside this publication change.

Prepare a release draft, upload only the allowlisted installer/help/checksum
assets, verify remote sizes and SHA-256 digests, then publish as a prerelease
with `make_latest=false`. Do not replace an existing mismatched asset silently.
Record actual publication verification after completion.
