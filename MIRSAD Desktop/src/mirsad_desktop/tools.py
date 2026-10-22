"""Tool identities and independent drafts; shared services never own a tool's state."""
from dataclasses import dataclass
from .climate_sources import GRID_HYBRID,STATION_HYBRID,ERA5_MODELS


@dataclass(frozen=True)
class ToolSpec:
    key: str
    arabic: str
    english: str
    description_ar: str
    description_en: str
    modes: tuple
    operation: str


TOOLS = (
    ToolSpec("stations", "مِرصاد: أطلس محطات الأرصاد الجوية السطحية المناخي", "MIRSAD: Ground Weather Stations Climate Atlas Generator",
             "استخلاص محطات الأرصاد الجوية السطحية المعتمدة عالمياً (NOAA ISD & WMO)، وتنزيل السلاسل الزمنية، وحساب المؤشرات، وإنتاج أسطح الراستر والأطلس.",
             "Extract certified ground weather stations (NOAA ISD & WMO), query climate time series, compute indicators, and build continuous raster surfaces and atlas.",
             ("stations", "combined"), "climate"),
    ToolSpec("points", "مِرصاد: الأطلس المناخي المكاني", "MIRSAD: Spatial Climate Atlas Generator",
             "تنزيل البيانات المناخية لطبقات نقاط الإدخال من ناسا أو المركز الأوروبي، وحساب المؤشرات الموسمية والسنوية، وبناء أطلس مكاني متكامل.",
             "Fetch multi-source climate data for custom input points, compute seasonal and annual indicators, and generate an integrated spatial atlas package.",
             ("user", "grid"), "climate"),
    ToolSpec("raster", "مِرصاد: أطلس الراستر والشبكات المناخية", "MIRSAD: Gridded & Raster Climate Atlas Generator",
             "تنزيل ومعالجة البيانات الشبكية والراستر من مزودي المناخ، والتحويل إلى نقاط بدقة Float، والاستيفاء المكاني والقص بمضلع الدراسة.",
             "Download and process gridded/raster climate data, extract Float points, perform high-precision spatial interpolation, and clip to study area mask.",
             ("regional","user"), "regional"),
)
BY_KEY = {tool.key: tool for tool in TOOLS}


def fresh_draft(tool):
    return dict(mode=tool.modes[0], selected=set(), points={}, grid={}, boundary=None,download_extent=None,download_extent_label="—",
                boundary_label="—", region="", country=None, search="",
                project="MIRSAD_" + tool.key.title(),
                provider="NASA POWER Regional Grid" if tool.key=="raster" else STATION_HYBRID if tool.key=="stations" else GRID_HYBRID,
                om_model=ERA5_MODELS[0],era5_resolution=ERA5_MODELS[0],
                start="2024-01-01", end="2024-12-31", modules=[],extra_variables=[],elevation_options=None,et_methods=["HG"],et_raster_methods=["HG","PM"],
                crs="EPSG:4326", processing_crs="EPSG:6933", units="Metric",unit_options={},
                gap="Climatological Month Mean (Recommended)",
                operation="Online Download & Full Processing",
                workflow="atlas" if tool.key=="raster" else "data", daily=True, yearly=False, ranges=False,
                scopes=["Annual", "Winter", "Spring", "Summer", "Autumn"],
                generate_monthly_rasters=False,
                raster_enabled=True, method="IDW", cell=10000,
                power=2, neighbours=12,
                reclass_enabled=False, reclass_method="Natural Breaks (Jenks)", reclass_classes=5,
                pdf=True, spacing=50000, restrict=False, fields=[])
