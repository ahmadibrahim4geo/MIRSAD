"""Application workflows, independent of Qt and of ArcGIS."""
import datetime as dt
import hashlib
import json
from pathlib import Path

from . import climate
from .exports import element_sheets, export_project, safe_name, workbook,export_workbook
from .climate_sources import uses_reanalysis,resolution_options,pipeline_sources


def run_climate_project(stations,folder,name,metadata,start,end,provider,modules,save_daily=True,
                        separate_years=False,progress=None,cancelled=None,crs="EPSG:4326",gap_method="none",scopes=None,monthly_ranges=False,
                        raster_options=None,units="Metric",om_model="auto",monthly_rasters=False,unit_options=None,credentials=None,
                        extra_variables=None,elevation_options=None,et_methods=None):
    progress = progress or (lambda message: None)
    cancelled = cancelled or (lambda: False)
    if (Path(folder)/safe_name(name)).exists():
        raise FileExistsError("Choose a new project name; the existing project will be preserved.")
    extras=dict(extra_variables=extra_variables) if extra_variables else {}
    from .daily_climate import validate_et_methods,PM_PRODUCT
    methods=validate_et_methods(et_methods,modules)
    if et_methods is not None:extras["et_methods"]=et_methods
    results,errors,urls = climate.download(stations,start,end,provider,modules,Path(folder)/".mirsad-cache",progress,cancelled,om_model=om_model,**extras,**({"credentials":credentials} if credentials else {}))
    from copy import deepcopy
    results=deepcopy(results)
    elevation_report=None
    if elevation_options:
        from .elevation import enrich_points
        stations,elevation_report=enrich_points(stations,elevation_options,Path(folder)/".mirsad-cache/elevation",progress,cancelled)
        enriched={p["station_key"]:p for p in stations}
        for result in results:result["station"]=enriched[result["station"]["station_key"]]
        errors.extend(dict(stage="elevation",station_key=p["station_key"],error=p["reason"])
                      for p in elevation_report["points"] if p["status"]!="OK")
    from .climate_sources import variable_resolution
    for result in results:
        resolutions=result.setdefault("resolution_by_variable",{})
        for variable,values in result["series"].items():
            if not any(climate.number(v) is not None for v in values.values()) or variable in resolutions:continue
            sources=set(result.get("provenance",{}).get(variable,{}).values()) or {provider}
            for actual in sources:
                if "NASA POWER" in actual:resolutions.setdefault(variable,{})[actual]=variable_resolution("NASA POWER",variable)
                elif "Open-Meteo" in actual:resolutions.setdefault(variable,{})[actual]=variable_resolution("Open-Meteo",variable,actual.split(" ")[-1])
    from .climate_products import descriptor
    spec=descriptor(provider)
    if spec and spec["temporal"]!="Daily":save_daily=False
    legacy_modules=[m for m in modules if m!="Evapotranspiration" or "HG" in methods]
    layers,daily = climate.prepare_outputs(results,legacy_modules,start,end,provider,gap_method,scopes,monthly_ranges,units,unit_options)
    enrichment_metadata=None
    if extra_variables:
        from .enrichment import apply
        enrichment_metadata=apply(layers,daily,results,modules,extra_variables,start,end,scopes,monthly_ranges,progress,cancelled)
    if "PM" in methods:
        from .enrichment import build_pm
        records,pm_daily,pm_metadata=build_pm(results,start,end,provider,scopes,monthly_ranges,progress,cancelled,units,unit_options)
        layers[PM_PRODUCT]=records;daily[PM_PRODUCT]=pm_daily
        if enrichment_metadata:
            for key in ("methods","dictionary"):enrichment_metadata[key].extend(pm_metadata[key])
            for row in pm_metadata["hourly_processing"]:enrichment_metadata["hourly_processing"].append(row)
        else:enrichment_metadata=pm_metadata
    if enrichment_metadata:
        for row in enrichment_metadata["methods"]:
            if row[7]<row[8]:
                errors.append(dict(stage="supplementary_variable",station_key=row[0],variable=row[1],
                                   error="%d of %d daily values available; inspect source dependencies and coverage"%(row[7],row[8])))
    for module,records in layers.items():
        for record in records:
            properties = record["properties"]
            if properties["Status"] in ("NO_DATA","PARTIAL","INSUFFICIENT_HISTORY"):
                errors.append({"module":module,"station_key":properties["Station_Key"],"error":properties["Error_Msg"]})
    output,manifest = export_project(stations,folder,name,metadata,climate_layers=layers,
        daily=daily if save_daily else None,source=provider,progress=progress,cancelled=cancelled,crs=crs,
        source_resolutions={r["station"]["station_key"]:r.get("resolution_by_variable",{}) for r in results},
        **(dict(elevation_metadata=elevation_report) if elevation_report else {}),
        **(dict(enrichment_metadata=enrichment_metadata) if enrichment_metadata else {}))
    manifest["processing"]={"gap_method":gap_method,"scopes":scopes,"monthly_ranges":monthly_ranges,"crs":crs,"units":units,
                            "om_model":climate.model_code(om_model) if uses_reanalysis(provider) else None,
                            "source_resolution":om_model if uses_reanalysis(provider) else resolution_options(provider)[0],
                            "source_policy":pipeline_sources(provider),"monthly_rasters":monthly_rasters,"unit_options":unit_options}
    manifest["source_urls"] = urls
    if elevation_report:manifest["elevation"]=elevation_report
    if extra_variables or "PM" in methods:
        manifest["processing"]["supplementary_variables"]=list(extra_variables or [])
        manifest["processing"]["supplementary_units"]="Supplementary components use canonical SI; PM follows precipitation output units. See Field_Dictionary."
        manifest["supplementary_methods"]=enrichment_metadata["methods"]
        manifest["hourly_processing_by_station"]={r["station"]["station_key"]:r.get("processing_by_variable",{}) for r in results}
        manifest["supplementary_provenance"]={r["station"]["station_key"]:r.get("supplementary_provenance",{}) for r in results}
    if et_methods is not None:manifest["processing"]["evapotranspiration_methods"]=methods
    manifest["resolution_by_station"]={r["station"]["station_key"]:r.get("resolution_by_variable",{}) for r in results}
    # Preserve raw observations and per-value provenance with the project.
    import shutil
    raw_folder=output/"Raw_Data"
    manifest["source_warnings"]=[]
    for result in results:
        manifest["source_warnings"].extend(dict(station_key=result["station"]["station_key"],message=w) for w in result.get("warnings",[]))
        for raw_path in ([result["raw_path"]] if result.get("raw_path") else [])+result.get("raw_paths",[]):
            raw_folder.mkdir(exist_ok=True)
            try:
                src=Path(raw_path);target=raw_folder/src.name
                shutil.copy2(src,target)
                manifest["outputs"][str(target.relative_to(output))]={"sha256":hashlib.sha256(target.read_bytes()).hexdigest(),"type":"raw source responses and provenance"}
            except Exception as exc:
                manifest["errors"].append({"stage":"raw_source_copy","error":str(exc)})
        if "monthly_gap_provenance" in result:
            raw_folder.mkdir(exist_ok=True)
            target=raw_folder/(hashlib.sha256(result["station"]["station_key"].encode()).hexdigest()+"-monthly-estimates.json")
            target.write_text(json.dumps(dict(station_key=result["station"]["station_key"],
                estimates=result["monthly_gap_provenance"],source_missing_counts=result.get("missing_counts",{}),
                source_events=result.get("source_events",[])),ensure_ascii=False,indent=2),encoding="utf-8")
            manifest["outputs"][str(target.relative_to(output))]={"sha256":hashlib.sha256(target.read_bytes()).hexdigest(),"type":"monthly estimation audit; daily observations preserved"}

    manifest["errors"].extend(errors)
    stage="yearly_export"
    try:
        if separate_years and start.year != end.year:
            for year in range(start.year,end.year+1):
                if cancelled(): raise InterruptedError("Cancelled")
                ys,ye = max(start,dt.date(year,1,1)),min(end,dt.date(year,12,31))
                yearly,daily_year = climate.prepare_outputs(results,legacy_modules,ys,ye,provider,gap_method,scopes,monthly_ranges,units,unit_options)
                yearly_enrichment=None
                if extra_variables:
                    yearly_enrichment=apply(yearly,daily_year,results,modules,extra_variables,ys,ye,scopes,monthly_ranges,progress,cancelled)
                if "PM" in methods:
                    records,pm_daily,pm_metadata=build_pm(results,ys,ye,provider,scopes,monthly_ranges,progress,cancelled,units,unit_options)
                    yearly[PM_PRODUCT]=records;daily_year[PM_PRODUCT]=pm_daily
                    if yearly_enrichment:
                        for key in ("methods","dictionary"):yearly_enrichment[key].extend(pm_metadata[key])
                        for row in pm_metadata["hourly_processing"]:yearly_enrichment["hourly_processing"].append(row)
                    else:yearly_enrichment=pm_metadata
                for module,records in yearly.items():
                    progress("Yearly Excel / %s / %d"%(module,year))
                    if PM_PRODUCT in yearly and module in ("Evapotranspiration",PM_PRODUCT):
                        target=output/"15_Evapotranspiration"/("Hargreaves" if module=="Evapotranspiration" else "Penman_Monteith")/"Years"
                    else:target = output/module/"Years"
                    target.mkdir(parents=True,exist_ok=True)
                    path = target/(module+"_"+str(year)+".xlsx")
                    sheets = element_sheets(records,provider,metadata,manifest["run_id"],daily_year[module] if save_daily else None,source_resolutions=manifest["resolution_by_station"],
                                            **(dict(elevation_metadata=elevation_report) if elevation_report else {}),
                                            **(dict(enrichment_metadata=yearly_enrichment,layer_name=module) if yearly_enrichment else {}))
                    export_workbook(path,sheets,output,manifest)
        if raster_options and not (raster_options.get("et_raster_methods")==[] and all(k in ("Evapotranspiration",PM_PRODUCT) for k in layers)):
            stage="raster"
            from .analysis import build_atlas
            build_atlas(layers,output,manifest,progress,cancelled,monthly_rasters=monthly_rasters,scopes=scopes,**raster_options)
        manifest["status"] = "partial" if manifest["errors"] else "complete"
    except Exception as exc:
        manifest["status"] = "cancelled" if isinstance(exc,InterruptedError) else "partial"
        manifest["errors"].append({"stage":stage,"error":str(exc)})
    finally:
        (output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    return output,manifest
