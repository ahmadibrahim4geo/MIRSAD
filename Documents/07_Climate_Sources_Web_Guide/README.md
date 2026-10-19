# 07. Climate sources web guide | دليل مصادر المناخ

[افتح الدليل التفاعلي](climate-sources.html) · [Open the interactive guide](climate-sources.html?lang=en)

انتقلت صفحة `climate-sources.html` من جذر المستودع إلى هذا المجلد في 19 أكتوبر
2026. الترجمة العربية تشمل التغطية والفترة والدقة والأدوات والعناصر ووحداتها؛
أسماء المنتجات ورموز المتغيرات تحتفظ بصيغتها الأصلية لسهولة المطابقة مع البرنامج.
الصفحة تعمل بالعربية والإنجليزية وبالوضعين الفاتح والداكن، مع البحث وفلاتر الأداة
والفاصل الزمني وتسجيل الدخول. روابط الموقع والأدلة تستخدم المسار الجديد.

The guide describes MIRSAD's implemented source adapters, not every product
offered by each provider. The source registry review remains **18 October 2026**;
the website presentation was updated on **19 October 2026**. Dates are not live
archive guarantees. Account, coverage and native-runtime limits remain explicit.

## Maintenance

- Templates: `scripts/templates/index.html`, `scripts/templates/climate-sources.html`.
- Shared local styling/interaction: `assets/site.css`, `assets/site.js`.
- Presentation translations: `scripts/website_content.py`.
- Source capabilities: `scripts/build_climate_source_catalogue.py`, backed by the
  implemented shared provider registry. Runtime JSON snapshots are unchanged.
- The home page's 19 module names/dependencies are generated from Desktop's registry.
- Regenerate both pages with `python scripts/build_website.py`; the catalogue
  generator also writes the source page here, never back into the repository root.
- Check links, anchors, translation completeness and generated drift with
  `python scripts/check_website.py` (included in repository checks).
- Download the full repository to keep local page assets available offline.
  Provider references and release downloads require a network connection.

The app image is a real acceptance screenshot of the current development build,
with an empty station selection and no user project. This website update does not
rebuild or replace the accepted installer or the CHM files.

## Verification, 19 October 2026

- Both generated pages match their templates/registries. All 56 local web
  links/assets/anchors resolve, including generated help topic fragments.
- Browser review passed in Arabic/RTL and English/LTR, light and dark themes.
  CHIRPS shows its monthly rainfall unit and the Arabic meanings of the code.
- Source filters: account-required = 2; regional/monthly = 3;
  regional/daily = 0, correctly excluding POWER's daily point-only path.
  Jump navigation clears filters before revealing the requested source.
- Module search: Wind Chill = 1; primary-only plus Wind Chill = 0; clear = 19;
  derived-only = 8. Language/theme preferences carry between the two pages.
- The reviewed 969-CSS-pixel browser viewport had no horizontal page overflow.
  Dedicated device emulation and a full accessibility audit were not performed.
- Runtime source snapshots, scientific code, help resources and binaries remain
  unchanged. Screenshots and local preview files remain in ignored QA space.

## Published verification

Website source commit: `a97ec9023ac324959a65160b4a23ea542f241a45`.
The [Pages deployment](https://github.com/ahmadibrahim4geo/MIRSAD/actions/runs/39226077314)
completed successfully. Public readback matched both HTML pages, CSS, JavaScript
and the app screenshot (text normalized to LF); all **23 distinct local resource
URLs returned HTTP 200**. Arabic source fields and monthly rainfall units were
also reviewed on the live site. The 65 existing user dataset/XML changes stayed
local and were not included. Full
[source checks](https://github.com/ahmadibrahim4geo/MIRSAD/actions/runs/39226077535)
are recorded separately from the successful website deployment.

- [Published home page](https://ahmadibrahim4geo.github.io/MIRSAD/).
- [Published source guide](https://ahmadibrahim4geo.github.io/MIRSAD/Documents/07_Climate_Sources_Web_Guide/climate-sources.html).

This verification note was added after deployment; it does not change the two
reviewed pages or any application binary.

## Atlas design revision — 19 October 2026

Reworked the visual direction with a navy/teal/gold atlas cover, local vector
graticule/contour artwork, a larger app preview and clearer section hierarchy.
Restored the full developer biography, circular portrait, GitHub/email/WhatsApp
icon buttons and a dedicated hydrology/infrastructure consulting panel. The
icons are inline local SVGs and require no external font/icon service.

Fixed the Hybrid monthly-fill double frame: only direct `.pipeline-step`
children receive the border/background. Browser readback in Arabic and English
confirmed four 1px outer borders and 0px borders on both translated inner labels.
The Arabic/light Hybrid view and English/light and Arabic/dark author views were
visually reviewed; the 969px viewport had no horizontal overflow. Language
switching retains the current anchored section. Source filters and calculated
data remain the existing implementation.

Maintenance still starts from the templates. `site-icons.html` supplies the
shared inline symbols; `atlas-lines.svg` is the local decorative background.
The generator derives an asset query version from CSS/JS/vector contents to
invalidate old cached presentation. Repository checks passed 150 documentation
links, 63 local HTML references/anchors, the CSS background path, generated-page
matching and the existing scientific/help/catalogue contracts.
