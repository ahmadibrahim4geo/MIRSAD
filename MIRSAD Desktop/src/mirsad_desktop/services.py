"""Application workflows, independent of Qt and of ArcGIS."""
import datetime as dt
import hashlib
import json
from pathlib import Path

from . import climate
from .exports import element_sheets, export_project, safe_name, workbook
from .climate_sources import uses_reanalysis,resolution_options,pipeline_sources


def run_climate_project(stations,folder,name,metadata,start,end,provider,modules,save_daily=True,
                        separate_years=False,progress=None,cancelled=None,crs="EPSG:4326",gap_method="none",scopes=None,monthly_ranges=False,
                        raster_options=None,units="Metric",om_model="auto",monthly_rasters=False,unit_options=None,credentials=None):
    progress = progress or (lambda message: None)
    cancelled = cancelled or (lambda: False)
    if (Path(folder)/safe_name(name)).exists():
        raise FileExistsError("Choose a new project name; the existing project will be preserved.")
    results,errors,urls = climate.download(stations,start,end,provider,modules,Path(folder)/".mirsad-cache",progress,cancelled,om_model=om_model,**({"credentials":credentials} if credentials else {}))
    from copy import deepcopy
    results=deepcopy(results)
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
    layers,daily = climate.prepare_outputs(results,modules,start,end,provider,gap_method,scopes,monthly_ranges,units,unit_options)
    for module,records in layers.items():
        for record in records:
            properties = record["properties"]
            if properties["Status"] in ("NO_DATA","PARTIAL","INSUFFICIENT_HISTORY"):
                errors.append({"module":module,"station_key":properties["Station_Key"],"error":properties["Error_Msg"]})
    output,manifest = export_project(stations,folder,name,metadata,climate_layers=layers,
        daily=daily if save_daily else None,source=provider,progress=progress,cancelled=cancelled,crs=crs,
        source_resolutions={r["station"]["station_key"]:r.get("resolution_by_variable",{}) for r in results})
    manifest["processing"]={"gap_method":gap_method,"scopes":scopes,"monthly_ranges":monthly_ranges,"crs":crs,"units":units,
                            "om_model":climate.model_code(om_model) if uses_reanalysis(provider) else None,
                            "source_resolution":om_model if uses_reanalysis(provider) else resolution_options(provider)[0],
                            "source_policy":pipeline_sources(provider),"monthly_rasters":monthly_rasters,"unit_options":unit_options}
    manifest["source_urls"] = urls
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
                yearly,daily_year = climate.prepare_outputs(results,modules,ys,ye,provider,gap_method,scopes,monthly_ranges,units,unit_options)
                for module,records in yearly.items():
                    progress("Yearly Excel / %s / %d"%(module,year))
                    target = output/module/"Years"
                    target.mkdir(parents=True,exist_ok=True)
                    path = target/(module+"_"+str(year)+".xlsx")
                    sheets = element_sheets(records,provider,metadata,manifest["run_id"],daily_year[module] if save_daily else None,source_resolutions=manifest["resolution_by_station"])
                    workbook(path,sheets)
                    manifest["outputs"][str(path.relative_to(output))] = {"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
        if raster_options:
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
