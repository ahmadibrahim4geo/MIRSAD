"""Independent interpolation, clipped GeoTIFFs and a multi-page climate atlas.

Methods are named explicitly; no silent replacement of unavailable ArcGIS tools.
Coordinates and cell sizes are in a user-selected projected metre CRS.
"""
from .crs import resolve_crs
import json
import math
from pathlib import Path

import numpy as np
from pyproj import CRS,Transformer

METHODS=("IDW","Nearest","Linear TIN","Spline (thin plate)","Ordinary Kriging (exponential)")


def classify_surface(surface,method,classes):
    """Class 1 is highest; 0 is NoData. Jenks uses a fixed quantile sample."""
    values=np.asarray(surface)[np.isfinite(surface)]
    if not len(values):raise ValueError("No valid raster cells to classify")
    if not 2<=int(classes)<=16:raise ValueError("Choose 2 to 16 classes")
    count=min(int(classes),len(np.unique(values)))
    if count==1:internal=np.array([])
    elif method=="Equal Interval":internal=np.linspace(values.min(),values.max(),count+1)[1:-1]
    elif method=="Quantile":internal=np.unique(np.quantile(values,np.linspace(0,1,count+1)[1:-1]))
    elif method=="Natural Breaks (Jenks)":
        sample=np.sort(values)
        if len(sample)>1024:sample=sample[np.linspace(0,len(sample)-1,1024).astype(int)]
        n=len(sample);count=min(count,len(np.unique(sample)))
        sums=np.r_[0,np.cumsum(sample)];squares=np.r_[0,np.cumsum(sample*sample)]
        costs=np.full((count+1,n+1),np.inf);parents=np.zeros((count+1,n+1),dtype=int);costs[0,0]=0
        for group in range(1,count+1):
            for end in range(group,n+1):
                starts=np.arange(group-1,end)
                variance=squares[end]-squares[starts]-(sums[end]-sums[starts])**2/(end-starts)
                candidates=costs[group-1,starts]+np.maximum(variance,0)
                best=int(np.argmin(candidates));costs[group,end]=candidates[best];parents[group,end]=starts[best]
        boundaries=[];end=n
        for group in range(count,1,-1):
            split=parents[group,end];boundaries.append((sample[split-1]+sample[split])/2);end=split
        internal=np.unique(sorted(boundaries))
    else:raise ValueError("Unsupported classification method")
    count=len(internal)+1;valid=np.isfinite(surface)
    classified=np.zeros(np.asarray(surface).shape,dtype="uint8")
    classified[valid]=count-np.searchsorted(internal,np.asarray(surface)[valid],side="right")
    return classified,dict(method=method,classes=count,breaks=[float(values.min()),*map(float,internal),float(values.max())],
                           order="1 = highest; 0 = NoData",jenks_sample_limit=1024 if method=="Natural Breaks (Jenks)" else None)

class Interpolator:
    """Prepare a spatial index once and reuse it for bounded raster chunks."""
    def __init__(self,xy,values,method="IDW",power=2,neighbours=12):
        from scipy.spatial import cKDTree
        from scipy.interpolate import LinearNDInterpolator,RBFInterpolator
        xy,values=np.asarray(xy,dtype=float),np.asarray(values,dtype=float)
        if len(xy)<3:raise ValueError("Interpolation requires at least three valid points.")
        if method not in METHODS:raise ValueError("Unknown interpolation method")
        if not np.isfinite(xy).all() or not np.isfinite(values).all():raise ValueError("Interpolation values must be finite")
        unique,inverse=np.unique(xy,axis=0,return_inverse=True)
        if len(unique)!=len(xy):values=np.bincount(inverse,weights=values)/np.bincount(inverse);xy=unique
        if len(xy)<3:raise ValueError("At least three distinct coordinates are required.")
        if not math.isfinite(power) or power<=0:raise ValueError("IDW power must be positive")
        self.xy,self.values,self.method,self.power=xy,values,method,power
        self.k=1 if method=="Nearest" else min(len(xy),max(3,int(neighbours)))
        self.tree=cKDTree(xy)
        self.function=(LinearNDInterpolator(xy,values,fill_value=np.nan) if method=="Linear TIN" else
                       RBFInterpolator(xy,values,kernel="thin_plate_spline",neighbors=min(len(xy),32)) if method=="Spline (thin plate)" else None)

    def __call__(self,query):
        return _interpolate_prepared(self,query)


def interpolate(xy,values,query,method="IDW",power=2,neighbours=12):
    return Interpolator(xy,values,method,power,neighbours)(query)


def _interpolate_prepared(prepared,query):
    from scipy.spatial import cKDTree
    from scipy.interpolate import LinearNDInterpolator,RBFInterpolator
    xy,values,method,power,k,tree=prepared.xy,prepared.values,prepared.method,prepared.power,prepared.k,prepared.tree
    query=np.asarray(query,dtype=float)
    if prepared.function is not None:return prepared.function(query)
    distance,index=tree.query(query,k=k)
    if method=="Nearest":return values[index]
    if method=="IDW":
        weights=1/np.maximum(distance,1e-12)**power
        return (weights*values[index]).sum(axis=1)/weights.sum(axis=1)
    # Local ordinary kriging with an explicitly documented exponential model.
    # Automatic practical range = one third of the source extent diagonal.
    practical_range=max(float(np.linalg.norm(np.ptp(xy,axis=0)))/3,1)
    output=[]
    for offset in range(0,len(query),256):
        dist,indices=distance[offset:offset+256],index[offset:offset+256]
        sites=xy[indices];n=len(sites)
        pairwise=np.linalg.norm(sites[:,:,None,:]-sites[:,None,:,:],axis=-1)
        covariance=np.exp(-3*pairwise/practical_range)
        covariance+=np.eye(k)[None,:,:]*1e-8
        system=np.ones((n,k+1,k+1));system[:,:k,:k]=covariance;system[:,k,k]=0
        rhs=np.ones((n,k+1));rhs[:,:k]=np.exp(-3*dist/practical_range)
        weights=np.linalg.solve(system,rhs[...,None])[...,:k,0]
        output.extend((weights*values[indices]).sum(axis=1))
    return np.array(output)

def numeric_fields(points):
    fields=set()
    for point in points:
        for key,value in point.get("attributes",{}).items():
            try:
                if value is not None and math.isfinite(float(value)):fields.add(key)
            except (TypeError,ValueError):pass
    return sorted(fields)

def build_atlas(layers,output,manifest,progress,cancelled,crs="EPSG:32636",cell_size=10000,
                method="IDW",power=2,neighbours=12,boundary=None,fields=None,pdf=True,maximum_cells=1000000,
                reclass_enabled=False,reclass_method="Natural Breaks (Jenks)",reclass_classes=5,monthly_rasters=False,scopes=None,**extra):
    import rasterio
    from rasterio.transform import from_origin
    from rasterio.features import geometry_mask
    from shapely.geometry import mapping
    from shapely.ops import transform
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_pdf import PdfPages
    projection=resolve_crs(crs)
    if not projection.is_projected or projection.axis_info[0].unit_name.lower() not in ("metre","meter"):
        raise ValueError("Raster processing CRS must be projected in metres (for example a suitable UTM zone).")
    if cell_size<=0:raise ValueError("Raster cell size must be positive.")
    if method not in METHODS:raise ValueError("Unsupported interpolation method.")
    transformer=Transformer.from_crs(4326,projection,always_xy=True)
    area=transform(transformer.transform,boundary) if boundary is not None else None
    tasks=[]
    excluded={"Point_Lat","Point_Lon","Elevation_m","Valid_Days","Expected_Days","Coverage_Fraction"}
    for module,records in layers.items():
        keys=list(records[0]["properties"]) if records else []
        for key in keys:
            if key in excluded or (fields is not None and key not in fields):continue
            if fields is None:
                from .climate import MONTHS,SEASONS
                monthly=any("_"+m+"_" in key for m in MONTHS)
                # Monthly difference fields remain tabular, as in the toolbox.
                if monthly and (not monthly_rasters or "_minus_" in key):continue
                if not monthly and not any(s in key for s in ("Annual",*SEASONS)):continue
                if scopes is not None and not monthly:
                    scope=next((s for s in ("Annual",*SEASONS) if s in key),None)
                    if scope and scope not in scopes and not (scope in SEASONS and "Seasonal" in scopes):continue
            samples=[]
            for r in records:
                value=r["properties"].get(key)
                if isinstance(value,(int,float)) and math.isfinite(value):
                    x,y=transformer.transform(r["longitude"],r["latitude"])
                    samples.append((x,y,float(value)))
            if samples:tasks.append((module,key,samples))
    if not tasks:raise ValueError("No numeric climate fields were selected for interpolation.")
    target=Path(output)/"Atlas";target.mkdir(exist_ok=True)
    from contextlib import nullcontext
    with PdfPages(target/"MIRSAD_Climate_Atlas.pdf") if pdf else nullcontext() as book:
        for task_index,(module,key,samples) in enumerate(tasks):
            if cancelled():raise InterruptedError("Cancelled")
            progress({"stage":"raster","completed":task_index,"total":len(tasks),"message":"Raster %d/%d · %s"%(task_index+1,len(tasks),key)})
            try:
                samples=np.array(samples);xy=samples[:,:2];values=samples[:,2]
                if len(samples)<3:raise ValueError("Fewer than three valid source points")
                xmin,ymin,xmax,ymax=area.bounds if area is not None else (*xy.min(axis=0),*xy.max(axis=0))
                if area is None:
                    xmin-=cell_size;ymin-=cell_size;xmax+=cell_size;ymax+=cell_size
                width,height=max(1,math.ceil((xmax-xmin)/cell_size)),max(1,math.ceil((ymax-ymin)/cell_size))
                if width*height>maximum_cells:raise ValueError("Raster exceeds %d cells. Increase the cell size."%maximum_cells)
                if method.startswith("Ordinary Kriging") and width*height>250000:raise ValueError("Local kriging is limited to 250,000 cells; increase cell size.")
                affine=from_origin(xmin,ymax,cell_size,cell_size)
                xs=xmin+(np.arange(width)+0.5)*cell_size;ys=ymax-(np.arange(height)+0.5)*cell_size
                predict=Interpolator(xy,values,method,power,neighbours)
                circular="W_Dir_" in key
                if circular:
                    sine_predict=Interpolator(xy,np.sin(np.radians(values)),method,power,neighbours)
                    cosine_predict=Interpolator(xy,np.cos(np.radians(values)),method,power,neighbours)
                surface=np.empty((height,width),dtype="float64")
                for offset in range(0,width*height,8192):
                    if cancelled():raise InterruptedError("Cancelled")
                    rows,cols=np.divmod(np.arange(offset,min(offset+8192,width*height)),width)
                    query_chunk=np.column_stack((xs[cols],ys[rows]))
                    estimate=(np.degrees(np.arctan2(sine_predict(query_chunk),cosine_predict(query_chunk)))%360
                              if circular else predict(query_chunk))
                    surface.ravel()[offset:offset+len(estimate)]=estimate
                if area is not None:
                    mask=geometry_mask([mapping(area)],surface.shape,affine,invert=True)
                    surface[~mask]=np.nan
                from .exports import safe_name
                filename=safe_name(module)+"__"+safe_name(key)+".tif"
                path=target/filename
                stored=np.where(np.isfinite(surface),surface,-9999).astype("float32")
                with rasterio.open(path,"w",driver="GTiff",width=width,height=height,count=1,dtype="float32",
                                   crs=projection,transform=affine,nodata=-9999,compress="deflate") as dataset:
                    dataset.write(stored,1);dataset.update_tags(MIRSAD_Field=key,Module=module,Method=method,
                        Cell_Size_m=cell_size,Source_Points=len(samples),Run_ID=manifest["run_id"])
                with rasterio.open(path) as dataset:
                    if dataset.crs is None or dataset.shape!=surface.shape or not np.allclose(dataset.read(1),stored,equal_nan=True):
                        raise RuntimeError("GeoTIFF readback mismatch")
                # Independent leave-one-out error at source locations; record
                # unsupported/degenerate validation rather than inventing a score.
                validation={"n":min(len(samples),100),"sampling":"first 100 input sites"}
                residuals=[]
                if len(samples)>=4:
                    for i in range(min(len(samples),100)):
                        if cancelled():raise InterruptedError("Cancelled")
                        try:
                            estimate=interpolate(np.delete(xy,i,axis=0),np.delete(values,i),xy[i:i+1],method,power,neighbours)[0]
                            if math.isfinite(estimate):residuals.append(float(estimate-values[i]))
                        except (ValueError,np.linalg.LinAlgError):pass
                validation.update(valid_predictions=len(residuals),RMSE=float(np.sqrt(np.mean(np.square(residuals)))) if residuals else None,
                                  bias=float(np.mean(residuals)) if residuals else None)
                manifest["outputs"][str(path.relative_to(output))]={"crs":projection.to_string(),"shape":[height,width],
                    "method":method,"readback":"passed","validation":validation,
                    "kriging_model":"exponential; range=extent diagonal/3; relative nugget=1e-8" if method.startswith("Ordinary") else None}
                if reclass_enabled:
                    classified,classification=classify_surface(surface,reclass_method,reclass_classes)
                    classified_path=path.with_name(path.stem+"__Classified.tif")
                    with rasterio.open(classified_path,"w",driver="GTiff",width=width,height=height,count=1,dtype="uint8",
                                       crs=projection,transform=affine,nodata=0,compress="deflate") as dataset:
                        dataset.write(classified,1);dataset.update_tags(MIRSAD_Classification=json.dumps(classification),Source_Raster=path.name)
                    with rasterio.open(classified_path) as dataset:
                        if not np.array_equal(dataset.read(1),classified):raise RuntimeError("Classified GeoTIFF readback mismatch")
                    manifest["outputs"][str(classified_path.relative_to(output))]=dict(classification,readback="passed")
                if book:
                    fig=Figure(figsize=(11.69,8.27));ax=fig.subplots()
                    image=ax.imshow(np.ma.masked_invalid(surface),extent=(xmin,xmin+width*cell_size,ymax-height*cell_size,ymax),origin="upper",cmap="YlGnBu")
                    ax.scatter(xy[:,0],xy[:,1],s=7,c="white",edgecolors="#183b4b",linewidths=.4)
                    ax.set_title("MIRSAD | "+module+"\n"+key,loc="left",fontsize=16,color="#08273d")
                    ax.set_xlabel(projection.to_string()+" · Easting (m)");ax.set_ylabel("Northing (m)")
                    fig.colorbar(image,ax=ax,shrink=.8,label=layers[module][0]["properties"].get("Measurement_Unit",""))
                    fig.text(.1,.025,"Ahmad Ibrahim · MIRSAD | "+method+" | "+str(len(samples))+" points | RMSE: "+str(validation["RMSE"]),fontsize=8)
                    fig.tight_layout(rect=(0,.04,1,1));book.savefig(fig)
            except InterruptedError:raise
            except Exception as exc:manifest["errors"].append({"stage":"raster","field":key,"error":str(exc)})
    if pdf and (target/"MIRSAD_Climate_Atlas.pdf").exists():
        manifest["outputs"]["Atlas/MIRSAD_Climate_Atlas.pdf"]={"type":"PDF climate atlas"}
    progress({"stage":"raster","completed":len(tasks),"total":len(tasks),"message":"Raster processing finished"})

def run_existing_project(points,folder,name,metadata,fields,crs="EPSG:32636",progress=None,cancelled=None,**options):
    from .exports import export_project,station_properties
    progress=progress or (lambda message:None);cancelled=cancelled or (lambda:False)
    records=[]
    for point in points:
        props=station_properties(point)
        for key in fields:
            try:value=float(point.get("attributes",{}).get(key))
            except (ValueError,TypeError):value=None
            props[key]=value if value is not None and math.isfinite(value) else None
        props["Measurement_Unit"]="As supplied by input; verify units"
        records.append(dict(latitude=point["latitude"],longitude=point["longitude"],properties=props))
    output,manifest=export_project(points,folder,name,metadata,climate_layers={"Input_Climate":records},source="User data (no download)",crs=crs,progress=progress,cancelled=cancelled)
    try:
        build_atlas({"Input_Climate":records},output,manifest,progress,cancelled,crs=crs,fields=fields,**options)
        manifest["status"]="partial" if manifest["errors"] else "complete"
    except Exception as exc:
        manifest["status"]="cancelled" if isinstance(exc,InterruptedError) else "partial"
        manifest["errors"].append({"stage":"analysis","error":str(exc)})
    finally:(output/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    return output,manifest
