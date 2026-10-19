"""User-owned points and study boundaries, with explicit coordinate contracts."""
from .crs import resolve_crs
import csv
import hashlib
import math
from pathlib import Path

from pyproj import CRS, Transformer
from .validation import local_dataset,MAX_POINTS,MAX_FIELDS

def table_rows(path):
    path = local_dataset(path)
    if path.suffix.lower() == ".xlsx":
        from openpyxl import load_workbook
        book = load_workbook(path,read_only=True,data_only=True)
        try:
            rows = iter(book.active.values)
            headers = [str(x).strip() if x is not None else "" for x in next(rows)]
            if not all(headers) or len(set(headers)) != len(headers):
                raise ValueError("Column names must be unique and nonempty.")
            if len(headers)>MAX_FIELDS:raise ValueError("Too many input columns.")
            result=[]
            for row in rows:
                if any(v is not None for v in row):result.append(dict(zip(headers,row)))
                if len(result)>MAX_POINTS:raise ValueError("Import is limited to %d points; subset the table first."%MAX_POINTS)
            return headers,result
        finally: book.close()
    with path.open(encoding="utf-8-sig",newline="") as handle:
        sample=handle.read(8192); handle.seek(0)
        try: dialect=csv.Sniffer().sniff(sample,delimiters=",;\t")
        except csv.Error: dialect=csv.excel
        reader=csv.DictReader(handle,dialect=dialect)
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError("CSV needs a header with unique column names.")
        if len(reader.fieldnames)>MAX_FIELDS:raise ValueError("Too many CSV columns.")
        rows=[]
        for row in reader:
            rows.append(row)
            if len(rows)>MAX_POINTS:raise ValueError("Import is limited to %d points; subset the table first."%MAX_POINTS)
        return list(reader.fieldnames),rows

def vector_layers(path):
    import pyogrio
    path=local_dataset(path)
    return [(str(n),str(t)) for n,t in pyogrio.list_layers(str(path))]

def vector_rows(path,layer=None,source_crs=None):
    import pyogrio
    from shapely import from_wkb
    path=local_dataset(path)
    info=pyogrio.read_info(path,layer=layer)
    if len(info.get("fields",[]))>MAX_FIELDS:raise ValueError("Too many input fields; select a narrower input layer.")
    meta,_,geometry,data=pyogrio.raw.read(str(path),layer=layer,max_features=MAX_POINTS+1)
    if geometry is None:raise ValueError("This is a table, not a point feature class.")
    if len(geometry)>MAX_POINTS:raise ValueError("Point import limit is %d; subset the layer first."%MAX_POINTS)
    crs=meta.get("crs") or source_crs
    if not crs: raise ValueError("The input has no CRS. Assign its actual source CRS before import.")
    transform=Transformer.from_crs(crs,"EPSG:4326",always_xy=True)
    rows=[]
    for i,wkb in enumerate(geometry):
        point=from_wkb(wkb)
        if point is None or point.is_empty or point.geom_type != "Point":
            raise ValueError("Point geometry required; invalid/non-point feature at row %d"%(i+1))
        lon,lat=transform.transform(point.x,point.y)
        row={str(field):values[i].item() if hasattr(values[i],"item") else values[i]
             for field,values in zip(meta["fields"],data)}
        row["_Longitude"],row["_Latitude"]=lon,lat
        rows.append(row)
    return list(meta["fields"]),rows,str(crs)

def make_point(identifier,name,x,y,source_crs="EPSG:4326",source="Manual",attributes=None,elevation=None):
    transformer=Transformer.from_crs(CRS.from_user_input(source_crs),"EPSG:4326",always_xy=True)
    lon,lat=transformer.transform(float(x),float(y))
    if not all(math.isfinite(v) for v in (lon,lat)) or not(-180<=lon<=180 and -90<=lat<=90):
        raise ValueError("Invalid point coordinates after transformation; check X/Y and the source CRS.")
    token=hashlib.sha256((str(source)+"|"+str(identifier)+"|%.8f|%.8f"%(lon,lat)).encode()).hexdigest()[:20]
    return dict(station_key="USER:"+token,usaf=str(identifier),wban="",name=str(name or identifier),
                country="USER",country_name="User points",country_ar="نقاط المستخدم",source_country="",
                continent="",is_arab=0,latitude=lat,longitude=lon,elevation=elevation,
                qa_status="user_supplied",input_source=str(source),point_type="User point",
                attributes=dict(attributes or {}))

def import_points(path,x_field=None,y_field=None,id_field=None,name_field=None,source_crs="EPSG:4326",layer=None):
    path=local_dataset(path)
    tabular=path.suffix.lower() in (".csv",".tsv",".xlsx")
    if tabular:
        _,rows=table_rows(path)
        if not x_field or not y_field or x_field==y_field: raise ValueError("Choose separate X and Y columns.")
    else:
        _,rows,_=vector_rows(path,layer,source_crs)
        x_field,y_field,source_crs="_Longitude","_Latitude","EPSG:4326"
    result=[]
    for i,row in enumerate(rows,1):
        try:
            result.append(make_point(row.get(id_field) if id_field and row.get(id_field) is not None else str(i),
                row.get(name_field) if name_field else "Point %d"%i,row[x_field],row[y_field],source_crs,
                str(path.resolve())+(" / "+layer if layer else ""),row))
        except Exception as exc: raise ValueError("Input row %d: %s"%(i,exc)) from exc
    if not result: raise ValueError("The input contains no points.")
    if len({p["station_key"] for p in result})!=len(result):
        raise ValueError("Duplicate point ID/location combinations in the input. Resolve them before import; rows were not silently removed.")
    return result

def read_boundary(path,layer=None,source_crs=None):
    import pyogrio
    from shapely import from_wkb
    from shapely.ops import transform,unary_union
    path=local_dataset(path)
    meta,_,geometry,_=pyogrio.raw.read(str(path),layer=layer,max_features=MAX_POINTS+1,columns=[])
    if geometry is None or len(geometry)>MAX_POINTS:raise ValueError("Boundary exceeds feature limit or has no geometry.")
    crs=meta.get("crs") or source_crs
    if not crs: raise ValueError("Boundary CRS is missing. Assign its actual source CRS.")
    polygons=[from_wkb(g) for g in geometry]
    if not polygons or any(p is None or p.is_empty or not p.is_valid or p.geom_type not in ("Polygon","MultiPolygon") for p in polygons):
        raise ValueError("A valid polygon boundary is required.")
    transformer=Transformer.from_crs(crs,"EPSG:4326",always_xy=True)
    boundary=transform(transformer.transform,unary_union(polygons))
    from shapely import count_coordinates
    if count_coordinates(boundary)>200000:raise ValueError("Boundary exceeds 200,000 vertices; simplify a copy before import.")
    if not boundary.is_valid or not(-180<=boundary.bounds[0]<=boundary.bounds[2]<=180 and -90<=boundary.bounds[1]<=boundary.bounds[3]<=90):
        raise ValueError("Boundary coordinates are invalid after transformation.")
    return boundary

def filter_boundary(points,boundary):
    from shapely import Point
    return [p for p in points if boundary.covers(Point(p["longitude"],p["latitude"]))]

def grid_points(boundary,spacing_m=25000,crs="EPSG:6933",limit=2000):
    import numpy as np
    from shapely import Point
    from shapely.ops import transform
    projection=resolve_crs(crs)
    if not projection.is_projected or projection.axis_info[0].unit_name.lower() not in ("metre","meter"):
        raise ValueError("Grid generation requires a projected CRS in metres.")
    if spacing_m<=0: raise ValueError("Grid spacing must be positive.")
    forward=Transformer.from_crs(4326,projection,always_xy=True)
    backward=Transformer.from_crs(projection,4326,always_xy=True)
    area=transform(forward.transform,boundary)
    xmin,ymin,xmax,ymax=area.bounds
    if ((xmax-xmin)/spacing_m+1)*((ymax-ymin)/spacing_m+1)>limit*5:
        raise ValueError("Grid too dense. Increase spacing; maximum %d points."%limit)
    points=[]
    for y in np.arange(ymin+spacing_m/2,ymax,spacing_m):
        for x in np.arange(xmin+spacing_m/2,xmax,spacing_m):
            if area.covers(Point(x,y)):
                lon,lat=backward.transform(x,y)
                points.append(make_point("GRID_%05d"%(len(points)+1),"Grid %d"%(len(points)+1),lon,lat,source="Generated grid"))
                if len(points)>limit: raise ValueError("Grid exceeds %d points. Increase spacing."%limit)
    if not points: raise ValueError("No grid centres fall inside the boundary. Reduce spacing.")
    return points
