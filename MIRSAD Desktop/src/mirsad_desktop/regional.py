"""Native NASA POWER regional grid download, independent of ArcGIS and point APIs."""
import calendar
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
from .climate import number,request_json,prepare_outputs
from .registry import parameters
from .inputs import make_point
from .exports import export_project,safe_name,element_sheets,workbook

URL="https://power.larc.nasa.gov/api/temporal/monthly/regional"


def tiles(bounds):
    west,south,east,north=map(float,bounds)
    if not all(math.isfinite(v) for v in bounds) or not(-180<=west<east<=180 and -90<=south<north<=90):
        raise ValueError("Regional download requires a valid non-wrapping WGS84 extent")
    nx,ny=max(1,math.ceil((east-west)/8)),max(1,math.ceil((north-south)/8))
    if nx*ny>512:raise ValueError("Download extent exceeds 512 regional tiles; process smaller areas")
    result=[]
    for x in range(nx):
        a=west+x*(east-west)/nx;b=west+(x+1)*(east-west)/nx
        if b-a<2.2:b=min(180,a+2.2);a=max(-180,b-2.2)
        for y in range(ny):
            c=south+y*(north-south)/ny;d=south+(y+1)*(north-south)/ny
            if d-c<2.2:d=min(90,c+2.2);c=max(-90,d-2.2)
            result.append((a,c,b,d))
    return result


def parse_features(payload,parameter,start,end):
    features=payload.get("features")
    if not isinstance(features,list):raise ValueError("NASA regional response has no feature collection")
    if len(features)>20000:raise ValueError("Regional tile exceeds point limit")
    unit=str(payload.get("parameters",{}).get(parameter,{}).get("units","")).lower()
    for feature in features:
        lon,lat=map(float,feature["geometry"]["coordinates"][:2])
        if not(-180<=lon<=180 and -90<=lat<=90):raise ValueError("Invalid regional grid coordinates")
        values={}
        for key,value in feature.get("properties",{}).get("parameter",{}).get(parameter,{}).items():
            if len(key)!=6 or not key.isdigit():continue
            year,month=int(key[:4]),int(key[4:])
            if not 1<=month<=12:continue  # NASA's month 13 is an annual summary.
            begin=dt.date(year,month,1);finish=dt.date(year,month,calendar.monthrange(year,month)[1])
            if begin<start or finish>end:continue
            value=number(value)
            if value is None:continue
            if parameter=="PRECTOTCORR":value*=calendar.monthrange(year,month)[1]
            if parameter=="ALLSKY_SFC_SW_DWN" and "kw" in unit:value*=3.6
            values[(year,month)]=value
        yield lon,lat,values


def run_regional_project(folder,name,metadata,download_extent,boundary,start,end,modules,
                         crs="EPSG:4326",raster_options=None,progress=None,cancelled=None,
                         separate_years=False,gap_method="none",scopes=None,monthly_ranges=False,
                         monthly_rasters=False,units="Metric",unit_options=None,provider="NASA POWER Regional Grid"):
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    from shapely.geometry import shape,mapping
    progress=progress or (lambda update:None);cancelled=cancelled or (lambda:False)
    if isinstance(start,str):start=dt.date.fromisoformat(start)
    if isinstance(end,str):end=dt.date.fromisoformat(end)
    if end<start or end>=dt.date.today():raise ValueError("Choose a valid past monthly period")
    if start.day!=1 or end.day!=calendar.monthrange(end.year,end.month)[1]:
        raise ValueError("NASA regional monthly data requires complete calendar months")
    if not modules:raise ValueError("Select climate modules")
    output=Path(folder)/safe_name(name)
    if output.exists():raise FileExistsError("Existing project will be preserved; choose a new name")
    aoi=shape(download_extent);mask=shape(boundary) if boundary else aoi
    from .climate_products import REGIONAL,native_grid_cells
    if provider in REGIONAL:
        from shapely.geometry import Point
        from .services import run_climate_project
        cache=Path(folder)/".mirsad-cache";cache.mkdir(parents=True,exist_ok=True)
        progress(dict(stage="download",completed=0,total=1,message="Inspecting native source grid"))
        cells=native_grid_cells(provider,aoi.bounds,start,end,parameters(modules),str(cache),cancelled,
            contains=lambda x,y:aoi.covers(Point(x,y)))
        points=[]
        for cell in cells:
            point=make_point(cell["station_key"],cell["name"],cell["longitude"],cell["latitude"],source=provider)
            point["point_type"]="Regional native grid cell";points.append(point)
        options=dict(raster_options) if raster_options else None
        if options:options["boundary"]=mask
        output,manifest=run_climate_project(points,folder,name,metadata,start,end,provider,modules,save_daily=False,
            separate_years=separate_years,progress=progress,cancelled=cancelled,crs=crs,gap_method=gap_method,
            scopes=scopes,monthly_ranges=monthly_ranges,raster_options=options,units=units,monthly_rasters=monthly_rasters,unit_options=unit_options)
        manifest["processing"].update(download_extent=mapping(aoi),study_mask=mapping(mask),
            sampling="Original native source cell centres inside download polygon",native_grid_cells=len(points))
        (output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
        return output,manifest
    if provider!="NASA POWER Regional Grid":raise ValueError("Regional provider is not implemented: "+provider)
    grid_tiles=tiles(aoi.bounds);required=parameters(modules)
    cache=Path(folder)/".mirsad-cache";cache.mkdir(parents=True,exist_ok=True)
    cells={};raw_files=[];errors=[];total=len(grid_tiles)*len(required);done=0
    with requests.Session() as session:
        session.mount("https://",HTTPAdapter(max_retries=Retry(total=2,backoff_factor=1,status_forcelist=[429,500,502,503,504])))
        for parameter in required:
            for west,south,east,north in grid_tiles:
                if cancelled():raise InterruptedError("Cancelled")
                query={"parameters":parameter,"community":"AG","longitude-min":west,"longitude-max":east,
                       "latitude-min":south,"latitude-max":north,"start":start.year,"end":end.year,"format":"JSON"}
                token=hashlib.sha256(("regional-v1"+json.dumps(query,sort_keys=True)).encode()).hexdigest()
                path=cache/(token+".json")
                try:
                    if path.exists():record=json.loads(path.read_text(encoding="utf-8"))
                    else:
                        payload,url=request_json(session,URL,query,cancelled)
                        record=dict(raw_response=payload,url=url,retrieved_utc=dt.datetime.now(dt.timezone.utc).isoformat())
                        path.write_text(json.dumps(record),encoding="utf-8")
                    raw_files.append(path)
                    for lon,lat,values in parse_features(record["raw_response"],parameter,start,end):
                        key=(round(lon,8),round(lat,8));monthly=cells.setdefault(key,{}).setdefault(parameter,{})
                        for period,value in values.items():
                            if period in monthly and monthly[period]!=value:raise ValueError("Overlapping NASA tiles disagree")
                            monthly[period]=value
                except InterruptedError:raise
                except Exception as exc:errors.append(dict(parameter=parameter,tile=[west,south,east,north],error=str(exc)))
                if len(cells)>20000:raise ValueError("Regional job exceeds 20,000 grid points; process smaller areas")
                done+=1;progress(dict(stage="download",completed=done,total=total,message=f"NASA regional grid {done}/{total}: {parameter}"))
    if not cells:raise ValueError("No regional grid data downloaded: "+str(errors[:3]))
    results=[]
    for (lon,lat),monthly in sorted(cells.items()):
        point=make_point(f"NASA_{lon:.8f}_{lat:.8f}","NASA POWER grid cell",lon,lat,source=URL)
        point["point_type"]="Regional grid cell"
        results.append(dict(station=point,series={},monthly=monthly,status="OK",error=""))
    points=[r["station"] for r in results]
    layers,_=prepare_outputs(results,modules,start,end,"NASA POWER Regional Grid",gap_method,scopes,monthly_ranges,units,unit_options)
    for module,records in layers.items():
        for record in records:
            props=record["properties"]
            if props["Status"] in ("NO_DATA","PARTIAL","INSUFFICIENT_HISTORY"):
                errors.append(dict(module=module,station_key=props["Station_Key"],error=props["Error_Msg"]))
    output,manifest=export_project(points,folder,name,metadata,climate_layers=layers,source="NASA POWER Regional Grid (monthly native cells)",crs=crs,progress=progress,cancelled=cancelled)
    manifest["errors"].extend(errors)
    manifest["processing"]=dict(provider="NASA POWER Regional Grid",temporal="Monthly",download_extent=mapping(aoi),
                                study_mask=mapping(mask),start=str(start),end=str(end),raw_daily_records=False,
                                missing_precipitation="NULL; monthly rate multiplied by actual calendar days")
    try:
        import shutil
        raw_folder=output/"Raw_Data";raw_folder.mkdir()
        for path in dict.fromkeys(raw_files):
            target=raw_folder/path.name;shutil.copy2(path,target)
            manifest["outputs"][str(target.relative_to(output))]={"sha256":hashlib.sha256(target.read_bytes()).hexdigest()}
        if separate_years and start.year!=end.year:
            for year in range(start.year,end.year+1):
                if cancelled():raise InterruptedError("Cancelled")
                yearly,_=prepare_outputs(results,modules,max(start,dt.date(year,1,1)),min(end,dt.date(year,12,31)),"NASA POWER Regional Grid",gap_method,scopes,monthly_ranges,units,unit_options)
                for module,records in yearly.items():
                    target=output/module/"Years";target.mkdir(parents=True,exist_ok=True)
                    path=target/(module+"_"+str(year)+".xlsx")
                    workbook(path,element_sheets(records,"NASA POWER Regional Grid",metadata,manifest["run_id"]))
                    manifest["outputs"][str(path.relative_to(output))]={"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
        if raster_options:
            from .analysis import build_atlas
            options=dict(raster_options);options["boundary"]=mask
            build_atlas(layers,output,manifest,progress,cancelled,monthly_rasters=monthly_rasters,scopes=scopes,**options)
        manifest["status"]="partial" if manifest["errors"] else "complete"
    except Exception as exc:
        manifest["status"]="cancelled" if isinstance(exc,InterruptedError) else "partial"
        manifest["errors"].append(dict(stage="regional_outputs",error=str(exc)))
    finally:(output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    return output,manifest
