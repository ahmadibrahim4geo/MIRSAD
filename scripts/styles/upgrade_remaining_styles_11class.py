# -*- coding: utf-8 -*-
"""Upgrade remaining 8 mains + 29 subs to 11-class Colors/Fills (same palettes, full sequence).
Run with ArcGIS Python 2.7."""
from __future__ import unicode_literals
import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, "scripts", "styles"))
import rebuild_enriched_climate_styles as R
import generate_climate_styles as gcs
import shutil

STYLE_DIR = R.STYLE_DIR; OUT_STYLE_DIR = R.OUT_STYLE_DIR
CONSOLIDATED = R.CONSOLIDATED; MAIN_ONLY_DIR = R.MAIN_ONLY_DIR

all_els = [{"folder":"01_Temperature","name_en":"Temperature","styles":list(gcs.TEMPERATURE_STYLES)+R.NEW_TEMP}] + \
          [dict(folder=e["folder"],name_en=e["name_en"],styles=list(e["styles"])) for e in gcs.OTHER_ELEMENTS]
by_id = {}
for el in all_els:
    for s in el["styles"]:
        by_id[s["id"]] = s
elmap = dict([(e["folder"], e) for e in all_els])
def pick(ids):
    return [by_id[i] for i in ids if i in by_id]

subs = [
 ("02_Precipitation","02_Precip_Annual_Total.style","Annual Total Precipitation","Annual Precipitation Ramps","Annual Rainfall Colors","Annual Precipitation Zones",["Precip_Seq_YlGnBu","Precip_Seq_Blues","Precip_Seq_CHIRPS_Rain","Precip_Multi_ERA5_Total"]),
 ("02_Precipitation","02_Precip_Winter_Rain.style","Winter Precipitation and Flash Floods","Winter Rain & Snow Ramps","Winter Rain & Flood Colors","Winter Flood Zones",["Precip_Seq_Blues","Precip_Multi_FlashFlood","Precip_Multi_SnowIce","Precip_Seq_SWE_Snowpack"]),
 ("02_Precipitation","02_Precip_Summer_Monsoon.style","Summer Rain and Tropical Monsoon","Summer Monsoon Ramps","Monsoon Rainfall Colors","Monsoon Precipitation Zones",["Precip_Seq_BuPu","Precip_Div_MonsoonAnomaly","Precip_Multi_NASA_GPM"]),
 ("02_Precipitation","02_Precip_Spring_Autumn_Storms.style","Transitional Storms and Radar Reflectivity","Transitional Storm Ramps","Radar Reflectivity Colors","Convective Storm Zones",["Precip_Multi_DopplerRadar","Precip_Multi_ConvectiveStorm","Precip_Seq_Intensity_WMO"]),
 ("02_Precipitation","02_Precip_Drought_Anomaly_SPI.style","Precipitation Anomaly and Drought SPI","Precipitation Anomaly Ramps","Drought & Surplus Colors","SPI Drought Zones",["Precip_Div_BrBG","Precip_Div_SPI","Precip_Div_SPEI_Multi"]),
 ("03_Sea_Level_Pressure","03_Pres_Annual_MSL_Standard.style","Standard Mean Sea Level Pressure","Standard MSL Pressure Ramps","Standard Pressure Colors","Isobaric Pressure Zones",["Pres_Div_WMO_MSLP","Pres_Synoptic_HighLow","Pres_Multi_MicrobarIsobars"]),
 ("03_Sea_Level_Pressure","03_Pres_Winter_Siberian_High.style","Winter Siberian Anticyclone and Mediterranean Lows","Winter Anticyclone Ramps","Winter Anticyclone Colors","Winter Pressure Zones",["Pres_Div_SiberianAnticyclone","Pres_Div_SevereCyclone"]),
 ("03_Sea_Level_Pressure","03_Pres_Summer_Subtropical_Low.style","Summer Subtropical High and Thermal Lows","Summer Subtropical Low Ramps","Summer Low Pressure Colors","Summer Pressure Zones",["Pres_Synoptic_Subtropical","Pres_Multi_Cyclones","Pres_Seq_Density"]),
 ("06_Relative_Humidity","06_Humidity_Annual_Mean.style","Annual Relative and Specific Humidity","Annual Relative Humidity Ramps","Relative Humidity Colors","Relative Humidity Zones",["RH_Seq_YlGnBu","RH_Seq_SpecificHumidity","RH_Multi_PWAT_AtmRiver"]),
 ("06_Relative_Humidity","06_Humidity_Summer_Stress_WBGT.style","Summer Humidity Heat Stress and Vapor Deficit","Summer Humidity Stress Ramps","Heat Stress Humidity Colors","Heat Stress Humidity Zones",["RH_Multi_WBGT_Stress","RH_Seq_VPD_Agricultural","RH_Multi_SatWaterVapor"]),
 ("06_Relative_Humidity","06_Humidity_Winter_Fog_Saturation.style","Winter Dense Fog and Dew Point Saturation","Winter Fog & Saturation Ramps","Winter Fog Colors","Winter Fog Zones",["RH_Seq_FogSaturation","RH_Multi_DewPointTemp"]),
 ("06_Relative_Humidity","06_Humidity_Transitional_Depression.style","Transitional Dew Point Depression and Flux","Dew Point Depression Ramps","Dew Point Depression Colors","Dew Point Depression Zones",["RH_Div_DewPointDepression","RH_Div_MoistureFlux"]),
 ("07_Solar_Radiation","07_Solar_Annual_GHI_ESMAP.style","Annual Global Horizontal Irradiation (GHI / PVOUT)","Annual Solar Radiation (GHI) Ramps","Solar Radiation Colors","Solar Radiation Zones",["Solar_Seq_YlOrRd","Solar_Seq_ESMAP_GHI","Solar_Seq_PVOUT"]),
 ("07_Solar_Radiation","07_Solar_Summer_DNI_Thermal.style","Summer Peak Direct Normal Irradiation DNI","Summer Peak Solar DNI Ramps","Direct Solar Colors","Direct Solar Zones",["Solar_Seq_DNI_Thermal","Solar_Seq_GTI_Tilted","Solar_Seq_ClearnessIndex"]),
 ("07_Solar_Radiation","07_Solar_Winter_Diffuse_Sunshine.style","Winter Sunshine Duration and Diffuse Radiation","Winter Diffuse & Sunshine Ramps","Diffuse Solar Colors","Diffuse Solar Zones",["Solar_Seq_SunshineDuration","Solar_Seq_DHI_Diffuse","Solar_Multi_SolarAlbedo"]),
 ("07_Solar_Radiation","07_Solar_Spring_Autumn_Agronomy.style","Agronomy Photosynthetically Active Radiation PAR","Agronomy PAR Radiation Ramps","Agronomy PAR Colors","Agronomy PAR Zones",["Solar_Seq_PAR_Agronomy","Solar_Seq_YlOrRd"]),
 ("08_UV_Index","08_UV_Annual_WHO_Standard.style","Mandatory WHO Standard UV Protection","WHO Standard UV Index Ramps","WHO UV Index Colors","WHO UV Health Zones",["UV_Standard_WHO","UV_EPA_HealthRisk"]),
 ("08_UV_Index","08_UV_Summer_Peak_Extreme.style","Summer Noon Extreme UV Index Peak","Summer Extreme UV Peak Ramps","Summer UV Risk Colors","Extreme UV Risk Zones",["UV_SummerPeak","UV_ErythemalDose","UV_Multi_Fitzpatrick"]),
 ("08_UV_Index","08_UV_Winter_Safe_Synthesis.style","Winter Safe UV and Vitamin D Synthesis","Winter Safe UV Ramps","Safe Vitamin D Colors","Safe UV Synthesis Zones",["UV_Seq_VitaminDSynthesis","UV_Multi_HighAltitude","UV_Div_OzoneDepletion"]),
 ("09_Cloud_Cover","09_Cloud_Annual_Okta_Fraction.style","Annual Cloud Amount Okta Scale and Fraction","Okta Scale Cloud Cover Ramps","Cloud Okta Colors","Cloud Fraction Zones",["Cloud_Seq_Okta","Cloud_Seq_Fraction"]),
 ("09_Cloud_Cover","09_Cloud_Winter_Low_Fog.style","Winter Low Cloud Ceiling Fog and Optical Depth","Winter Low Cloud & Fog Ramps","Low Ceiling Cloud Colors","Aviation Fog Zones",["Cloud_Seq_LowCloudFog","Cloud_Seq_OpticalDepth","Cloud_Seq_CirrusIce"]),
 ("09_Cloud_Cover","09_Cloud_Summer_Convective_Aerosol.style","Summer Convective Cloud Tops and Aerosol Dust","Summer Convective Cloud Ramps","Convective Cloud Colors","Convective Storm Zones",["Cloud_Multi_ConvectiveTops","Cloud_Multi_AOD_Aerosol","Cloud_Multi_IR_CloudTop"]),
 ("10_Drought_And_Aridity","10_Aridity_Annual_UNEP_DeMartonne.style","Annual Aridity UNEP and De Martonne","UNEP & De Martonne Aridity Ramps","Aridity Index Colors","Aridity Climate Zones",["Aridity_UNEP_World","Aridity_SoilMoistureDeficit"]),
 ("10_Drought_And_Aridity","10_Drought_Summer_PET_Hargreaves.style","Summer Evapotranspiration PET Hargreaves","Summer Evapotranspiration PET Ramps","Evapotranspiration Colors","Evaporative Demand Zones",["Drought_ETo_Hargreaves","Drought_EDDI_Evaporative","Drought_ETa_ActualDeficit"]),
 ("10_Drought_And_Aridity","10_Drought_Water_Balance_SPEI.style","Climatic Water Balance SPEI and Crop Moisture","Water Balance & Deficit (SPEI) Ramps","Climatic Water Deficit Colors","Water Balance Zones",["Drought_SPEI_Index","Drought_PDSI_Palmer","Drought_CMI_CropMoisture","Drought_NDWI_WaterIndex"]),
 ("10_Drought_And_Aridity","10_Drought_Desert_Encroachment.style","Desert Encroachment and Oasis Degradation","Desert Encroachment Ramps","Desertification Colors","Desertification Zones",["Drought_Multi_DesertBoundaries","Aridity_UNEP_World"]),
 ("11_Climate_Models","11_Model_Temp_Warming_Stripes.style","Warming Stripes and Temperature Anomalies","Warming Stripes & Anomaly Ramps","Warming Stripes Colors","Warming Anomaly Zones",["Model_Div_WarmingStripes","Model_Div_TempAnomaly","Model_Seq_TropicalNightsTR20"]),
 ("11_Climate_Models","11_Model_Precip_Change_Extremes.style","Precipitation Change and Extreme Indices","Precipitation Change & Extremes Ramps","Precipitation Change Colors","Extreme Climate Zones",["Model_Div_PrecipChange","Model_Div_ExtremePrecipR95p","Model_Seq_ConsecutiveDryDays","Model_Multi_ExtremesIndex"]),
 ("11_Climate_Models","11_Model_SSP_Scenarios_Multi.style","IPCC Shared Socioeconomic SSPs and Sea Level Rise","Shared Socioeconomic SSP Ramps","SSP Scenario Colors","Socioeconomic Scenario Zones",["Model_Multi_SSPSenarios","Model_Multi_SeaLevelRise","Model_Seq_DegreeDays"]),
 ("05_Wind","05_Wind_Annual_Beaufort.style","Annual Wind Speed Beaufort Scale","Beaufort Wind Speed Ramps","Beaufort Scale Colors","Beaufort Wind Zones",["Wind_Seq_Beaufort","Wind_Seq_PowerDensity"]),
 ("05_Wind","05_Wind_Winter_Gales_Chill.style","Winter Marine Gales and Wind Chill","Winter Marine Gale Ramps","Winter Gale Colors","Winter Gale Zones",["Wind_Seq_MarineGale","Wind_Multi_WindChill","Wind_Multi_SeaState"]),
 ("05_Wind","05_Wind_Spring_Khamsin_Dust.style","Spring Khamsin Dust Storms and Severe Gales","Spring Khamsin Dust Ramps","Khamsin Dust Colors","Khamsin Dust Zones",["Wind_Multi_KhamsinDust","Wind_Multi_EF_Tornado"]),
 ("01_Temperature","01_Temp_Heat_Index.style","Perceived Temperature and Heat Index","Heat Index Ramps","Perceived Temperature Colors","Heat Stress Zones",["Temp_Multi_SteadmanApparent","Temp_Multi_HeatwaveRisk"]),
]
mains = [
 ("02_Precipitation","02_Precipitation.style","Precipitation"),
 ("03_Sea_Level_Pressure","03_Sea_Level_Pressure.style","Sea Level Pressure"),
 ("06_Relative_Humidity","06_Relative_Humidity.style","Relative Humidity"),
 ("07_Solar_Radiation","07_Solar_Radiation.style","Solar Radiation"),
 ("08_UV_Index","08_UV_Index.style","UV Index"),
 ("09_Cloud_Cover","09_Cloud_Cover.style","Cloud Cover"),
 ("10_Drought_And_Aridity","10_Drought_And_Aridity.style","Drought and Aridity"),
 ("11_Climate_Models","11_Climate_Models.style","Climate Models"),
]
print("=== Upgrading remaining subs + mains to 11-class ===")
for folder,fname,label,rc,cc,fc,ids in subs:
    sel = pick(ids)
    local = os.path.join(STYLE_DIR, folder, fname)
    R.build_sub(local, sel, label, rc, cc, fc)
    R.sync_copy(local, [os.path.join(OUT_STYLE_DIR,fname), os.path.join(CONSOLIDATED,fname)])
for folder,fname,label in mains:
    sel = elmap[folder]["styles"]
    local = os.path.join(STYLE_DIR, folder, fname)
    R.build_main(local, sel, label)
    R.sync_copy(local, [os.path.join(STYLE_DIR,folder,"STYLE",fname), os.path.join(OUT_STYLE_DIR,fname), os.path.join(CONSOLIDATED,fname), os.path.join(MAIN_ONLY_DIR,fname)])
# refresh 00 main for 01/04/05 too (already rebuilt but ensure)
for folder,fname in [("01_Temperature","01_Temperature.style"),("04_Surface_Pressure","04_Surface_Pressure.style"),("05_Wind","05_Wind.style")]:
    R.sync_copy(os.path.join(STYLE_DIR,folder,fname), [os.path.join(MAIN_ONLY_DIR,fname)])
print("=== UPGRADE DONE ===")
