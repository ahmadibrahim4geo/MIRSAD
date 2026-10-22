# Desktop documentation

ابدأ بالحالة الحالية وقائمة المتبقي؛ تقارير الإصدارات السابقة أدلة تاريخية وليست
قائمة بالوظائف المكتملة الآن. خطط التنفيذ المنتهية دُمجت في الحالة والسجل.

| Read | Purpose |
|---|---|
| [22 October source/docs delivery](../../Documents/SOURCE_UPDATE_2026_10_22.md) | Final source checks, website/index update and explicit pending work; public installer remains older |
| [STATUS.md](STATUS.md) | Current implementation and accepted limits |
| [BACKLOG.md](BACKLOG.md) | Remaining acceptance work and requirements |
| [CHANGELOG.md](CHANGELOG.md) | Historical delivery log and evidence |
| [Arabic user guide](user/USER_GUIDE_AR.html) / [English user guide](user/USER_GUIDE_EN.html) | Bilingual offline help |
| [architecture/](architecture/) | Architecture decisions, pipeline and original requirements |
| [reports/](reports/) | Audits, contracts, acceptance reports and hashes |
| [Climate enrichment baseline](reports/climate-enrichment/BASELINE_AUDIT.md) | Current-source inventory, regression guards, live sample probes and accepted implementation contracts |
| [Climate enrichment source acceptance](reports/climate-enrichment/DESKTOP_SOURCE_ACCEPTANCE.md) | Optional Desktop variables/DEM/PM/XLSX, actual evidence and remaining cross-host/frozen work |
| [Legacy large-Daily Excel](reports/climate-enrichment/LEGACY_EXCEL_ACCEPTANCE.md) | Standard-library Python 2/3 XLSX, million-row boundary, native Pro readback and explicit ArcMap limit |
| [Point/Station daily additions](reports/climate-enrichment/TOOLBOX_ACCEPTANCE.md) | Earlier 11-variable snapshot, yearly XLSX/audit and native Pro fixture evidence; later PM evidence is below |
| [Point/Station HG and PM](reports/climate-enrichment/TOOLBOX_PM_ACCEPTANCE.md) | Separate daily PM and preserved HG, yearly sums/units, six native Pro method fixtures and remaining DEM/raster scope |
| [development/SECURITY.md](development/SECURITY.md) | Runtime and packaging security controls |
| [design/README.md](design/README.md) | Visual prototype and design references |

Shared help source remains in [`Documents/Help/`](../../Documents/Help/).
Generated toolbox HTML and CHM remain in [`Help/`](../../Help/). Build and
local test artifacts are ignored under `.build/` and `.test-output/`.
