"""Optional point elevation enrichment; source attributes and geometries stay intact."""
import hashlib
import json
import math
from pathlib import Path

OPEN_METEO = "Copernicus DEM GLO-90 via Open-Meteo"


def _value(value):
    if value is None or isinstance(value,bool):return None
    try:
        value=float(value)
        return value if math.isfinite(value) and -1000<=value<=10000 else None
    except (ValueError,TypeError):return None


def enrich_points(points,options,cache_folder=None,progress=None,cancelled=None,session=None):
    """Return copied points and a per-point audit. A failed lookup is NULL, never zero."""
    progress=progress or (lambda event:None);cancelled=cancelled or (lambda:False)
    if not isinstance(options,dict) or set(options)-{"source","path","model_name","surface_type","vertical_datum","sampling"}:
        raise ValueError("Invalid elevation settings")
    source=options.get("source")
    if source not in ("open-meteo","local"):raise ValueError("Choose an implemented elevation source")
    keys=[p["station_key"] for p in points]
    if len(set(keys))!=len(keys):raise ValueError("Duplicate point identities in elevation lookup")
    for p in points:
        names={str(k).lower() for k in p.get("attributes",{})}|{str(k).lower() for k in p}
        if names&{"z_elev_m","z_source"}:raise ValueError("Elevation field collision: Z_Elev_m / Z_Source; original input columns must be preserved")
    copied=[dict(p,dem_elevation=None,dem_source=None) for p in points]
    audit=[]
    cache=Path(cache_folder) if cache_folder else None
    if cache:cache.mkdir(parents=True,exist_ok=True)
    if source=="local":
        from .validation import local_dataset
        import rasterio
        from rasterio.windows import Window
        from pyproj import Transformer
        path=local_dataset(options.get("path",""))
        if path.suffix.lower() not in (".tif",".tiff"):raise ValueError("Local elevation requires a GeoTIFF")
        sampling=options.get("sampling","nearest")
        if sampling not in ("nearest","bilinear"):raise ValueError("Unknown DEM sampling method")
        with rasterio.open(path) as raster:
            if raster.driver!="GTiff" or not raster.crs or raster.count<1:
                raise ValueError("DEM must be a genuine GeoTIFF with a known CRS")
            if raster.units[0] and raster.units[0].lower() not in ("m","metre","metres","meter","meters"):
                raise ValueError("Local DEM vertical units must be metres; convert a copy explicitly")
            model=options.get("model_name") or path.stem
            if not isinstance(model,str) or not 1<=len(model)<=160:raise ValueError("Invalid DEM model name")
            model="Local DEM: "+model
            surface=options.get("surface_type","unspecified")
            if surface not in ("DTM","DSM","unspecified"):raise ValueError("Specify DSM, DTM or unspecified for the local DEM")
            datum=options.get("vertical_datum") or "unspecified; user must verify"
            transform=Transformer.from_crs(4326,raster.crs,always_xy=True)
            # Stat identity is recorded for reproducibility, without reading the
            # complete raster or assuming that all products share a vertical datum.
            file_info=dict(path=str(path),size=path.stat().st_size,mtime_ns=path.stat().st_mtime_ns,
                           crs=str(raster.crs),resolution=list(raster.res),vertical_unit="m",
                           unit_basis="file metadata" if raster.units[0] else "user-declared metre input")
            for index,p in enumerate(copied):
                if cancelled():raise InterruptedError("Cancelled")
                progress(dict(stage="elevation",completed=index,total=len(copied),message="DEM %d/%d"%(index+1,len(copied))))
                x,y=transform.transform(p["longitude"],p["latitude"])
                value=None;reason="outside raster footprint"
                if math.isfinite(x) and math.isfinite(y):
                    col,row=(~raster.transform)@(x,y)
                    if 0<=row<raster.height and 0<=col<raster.width:
                        if sampling=="nearest":
                            r,c=math.floor(row),math.floor(col)
                            block=raster.read(1,window=Window(c,r,1,1),masked=True)
                            if not block.mask.any():value=_value(float(block[0,0])*raster.scales[0]+raster.offsets[0])
                        else:
                            left,top=math.floor(col-.5),math.floor(row-.5)
                            if 0<=left<raster.width-1 and 0<=top<raster.height-1:
                                block=raster.read(1,window=Window(left,top,2,2),masked=True)
                                if not block.mask.any():
                                    dx,dy=col-.5-left,row-.5-top
                                    sample=(block[0,0]*(1-dx)*(1-dy)+block[0,1]*dx*(1-dy)+
                                            block[1,0]*(1-dx)*dy+block[1,1]*dx*dy)
                                    value=_value(float(sample)*raster.scales[0]+raster.offsets[0])
                        reason="NoData/invalid sample or incomplete bilinear neighbourhood"
                p["dem_elevation"],p["dem_source"]=value,model if value is not None else None
                audit.append(dict(station_key=p["station_key"],value_m=value,source=p["dem_source"],requested_source=model,
                                  status="OK" if value is not None else "NO_DATA",reason="" if value is not None else reason,
                                  surface_type=surface,vertical_datum=datum,sampling=sampling,product=file_info))
    else:
        import requests
        owned=session is None
        session=session or requests.Session()
        try:
            for offset in range(0,len(copied),100):
                if cancelled():raise InterruptedError("Cancelled")
                batch=copied[offset:offset+100]
                identity=dict(product="COP-DEM-GLO90-2021-openmeteo",coordinates=[[p["latitude"],p["longitude"]] for p in batch])
                token=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
                path=cache/(token+".json") if cache else None
                values=None;error=""
                try:
                    if path and path.is_file():
                        try:
                            saved=json.loads(path.read_text(encoding="utf-8"))
                            if saved.get("identity")==identity:values=saved.get("elevation")
                        except (ValueError,OSError):values=None
                    if not isinstance(values,list) or len(values)!=len(batch) or any(_value(v) is None for v in values):
                        from .climate import request_json
                        payload,url=request_json(session,"https://api.open-meteo.com/v1/elevation",
                            dict(latitude=",".join(str(p["latitude"]) for p in batch),longitude=",".join(str(p["longitude"]) for p in batch)),cancelled)
                        values=payload.get("elevation")
                        if not isinstance(values,list) or len(values)!=len(batch):raise ValueError("DEM response count mismatch")
                        if path and all(_value(v) is not None for v in values):
                            from .hybrid_pipeline import atomic_json
                            atomic_json(str(path),dict(identity=identity,elevation=values,url=url))
                except InterruptedError:raise
                except Exception as exc:values=[None]*len(batch);error=str(exc)
                for p,raw in zip(batch,values):
                    value=_value(raw)
                    p["dem_elevation"],p["dem_source"]=value,OPEN_METEO if value is not None else None
                    audit.append(dict(station_key=p["station_key"],value_m=value,source=p["dem_source"],requested_source=OPEN_METEO,
                        status="OK" if value is not None else "NO_DATA",reason="" if value is not None else error or "No valid elevation returned",
                        surface_type="DSM",vertical_datum="EGM2008 (Copernicus GLO-90 product)",sampling="provider point lookup",
                        product=dict(id="Copernicus DEM GLO-90 2021 via Open-Meteo",nominal_cell_m=90,vertical_unit="m",
                                     attribution="Copernicus programme / Open-Meteo",url="https://open-meteo.com/en/docs/elevation-api")))
                progress(dict(stage="elevation",completed=offset+len(batch),total=len(copied),message="Elevation points %d/%d"%(offset+len(batch),len(copied))))
        finally:
            if owned:session.close()
    return copied,dict(source=source,points=audit,failed=sum(p["status"]!="OK" for p in audit),
                       notes="Optional attribute enrichment. Original station elevation and geometry unchanged. DSM/DTM and vertical datums are not silently harmonized.")
