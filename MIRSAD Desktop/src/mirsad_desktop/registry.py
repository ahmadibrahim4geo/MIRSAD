"""Toolbox parity registry: scientific dependencies, names and output contracts."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Module:
    name: str
    arabic: str
    params: tuple
    prefixes: tuple
    unit: str
    group: str = "primary"

MODULES = [
 Module("Temperature","درجة حرارة الهواء",("T2M","T2M_MAX","T2M_MIN"),("T_",),"deg_C"),
 Module("Land Surface Temperature","درجة حرارة سطح الأرض",("TS","T2M"),("LST_",),"deg_C"),
 Module("Precipitation","الأمطار",("PRECTOTCORR",),("R_",),"mm"),
 Module("Sea Level Pressure","الضغط عند سطح البحر",("SLP",),("PSL_",),"hPa"),
 Module("Surface Pressure","الضغط السطحي",("PS",),("PS_",),"hPa"),
 Module("Wind","الرياح: السرعة والاتجاه",("WS10M","WD10M"),("W_",),"m/s; degree"),
 Module("Relative Humidity","الرطوبة النسبية",("RH2M",),("RH_",),"percent"),
 Module("Dew Point","نقطة الندى",("T2MDEW",),("Td_",),"deg_C"),
 Module("Solar Radiation","الإشعاع الشمسي",("ALLSKY_SFC_SW_DWN",),("Sol_",),"kWh/m2/day"),
 Module("UV Index","الأشعة فوق البنفسجية",("ALLSKY_SFC_UV_INDEX",),("UV_",),"WHO index"),
 Module("Cloud Cover","الغطاء السحابي",("CLOUD_AMT",),("Cld_",),"percent"),
 Module("Heat Index","مؤشر الحرارة والإجهاد الحراري",("T2M","RH2M"),("HI_","WBGT_"),"deg_C","derived"),
 Module("Wind Chill","برودة الرياح والإجهاد البارد",("T2M","WS10M"),("WC_",),"deg_C","derived"),
 Module("De Martonne Aridity","الجفاف: دي مارتون",("T2M","PRECTOTCORR"),("DM_",),"index","derived"),
 Module("Evapotranspiration","البخر والنتح: هارجريفز",("T2M","T2M_MAX","T2M_MIN"),("ET_","PET_"),"mm","derived"),
 Module("UNEP Aridity","الجفاف: UNEP",("T2M","T2M_MAX","T2M_MIN","PRECTOTCORR"),("UNEP_",),"ratio","derived"),
 Module("Water Deficit","العجز المائي",("T2M","T2M_MAX","T2M_MIN","PRECTOTCORR"),("Water_Deficit_",),"mm","derived"),
 Module("Dry Months","عدد الأشهر الجافة",("T2M","PRECTOTCORR"),("Dry_Months_",),"months","derived"),
 Module("Trends & Anomalies","الاتجاهات والشذوذ عن خط الأساس",("T2M","PRECTOTCORR"),("T_","R_"),"mixed","derived"),
]
BY_NAME = {m.name:m for m in MODULES}
OM_DAILY = {"T2M":"temperature_2m_mean","T2M_MAX":"temperature_2m_max","T2M_MIN":"temperature_2m_min",
            "PRECTOTCORR":"precipitation_sum","ALLSKY_SFC_SW_DWN":"shortwave_radiation_sum"}
OM_HOURLY = {"RH2M":"relative_humidity_2m","T2MDEW":"dew_point_2m","PS":"surface_pressure",
             "SLP":"pressure_msl","WS10M":"wind_speed_10m","WD10M":"wind_direction_10m","CLOUD_AMT":"cloud_cover"}

def parameters(modules):
    return sorted({p for m in modules for p in BY_NAME[m].params})

def unavailable(provider,module):
    # Missing ERA5 variables have an explicit NASA supplement in the adapter;
    # every offered module is selectable, while genuine source gaps stay NULL.
    return ""

def module_fields(module,fields):
    if module == "Trends & Anomalies":
        return {k:v for k,v in fields.items() if "Anom" in k or "Trend" in k}
    return {k:v for k,v in fields.items() if k.startswith(BY_NAME[module].prefixes)}
