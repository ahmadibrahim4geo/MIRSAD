# -*- coding: utf-8 -*-
"""Small runtime guards shared by the ArcMap / ArcGIS Pro tools (Python 2/3)."""
from functools import wraps


def filegdb_raster_workspace(function):
    """Use geodatabase temporary rasters, avoiding Esri GRID space restrictions.

    Final output paths and scientific inputs are unchanged. Restore both host
    workspaces on success or failure; the ordinary tool scratch purge owns data.
    """
    @wraps(function)
    def wrapped(self,*args,**kwargs):
        import inspect
        import os
        namespace=getattr(function,"__globals__",None)
        if namespace is None:namespace=function.func_globals
        arcpy=namespace["arcpy"]
        bound=inspect.getcallargs(function,self,*args,**kwargs)
        folder=bound.get("scratch")
        if not folder and bound.get("paths"):folder=os.path.join(os.path.dirname(bound["paths"]["vec"]),"_scratch")
        if not folder:folder=os.path.join(os.path.dirname(bound["out_tif"]),"_scratch")
        if not os.path.isdir(folder):os.makedirs(folder)
        database=os.path.join(folder,"spatial_work.gdb")
        if not arcpy.Exists(database):arcpy.CreateFileGDB_management(folder,"spatial_work.gdb")
        saved=dict((key,getattr(arcpy.env,key,None)) for key in ("workspace","scratchWorkspace"))
        try:
            arcpy.env.workspace=database;arcpy.env.scratchWorkspace=database
            return function(self,*args,**kwargs)
        finally:
            for key,value in saved.items():
                if value is None:arcpy.ClearEnvironment(key)
                else:setattr(arcpy.env,key,value)
    return wrapped


_ENVIRONMENTS = (
    "workspace", "overwriteOutput", "mask", "extent", "snapRaster", "cellSize",
    "outputCoordinateSystem", "parallelProcessingFactor", "compression",
    "tileSize", "pyramid", "rasterStatistics", "scratchWorkspace",
)


def preserve_arcpy_environment(function):
    """Isolate tool settings, including on error, without resetting the host."""
    @wraps(function)
    def wrapped(self, parameters, messages):
        namespace = getattr(function, "__globals__", None)
        if namespace is None:  # Python 2.7
            namespace = function.func_globals
        arcpy = namespace.get("arcpy")
        saved = {}
        for name in _ENVIRONMENTS:
            try:
                saved[name] = getattr(arcpy.env, name)
            except Exception:
                pass
        try:
            # Ambient map settings must not clip/restrict copied input points.
            for name in ("mask", "extent", "snapRaster"):
                try:
                    arcpy.ClearEnvironment(name)
                except Exception:
                    pass
            try:
                arcpy.env.parallelProcessingFactor = "0"
            except Exception:
                pass
            return function(self, parameters, messages)
        finally:
            for name, value in saved.items():
                try:
                    if value is None:
                        arcpy.ClearEnvironment(name)
                    else:
                        setattr(arcpy.env, name, value)
                except Exception:
                    pass
    return wrapped


class SpatialLicense(object):
    """Release only a Desktop extension acquired by this run.

    ArcGIS Pro manages extension checkout itself. Explicit check-in from a Pro
    tool can enter native license shutdown while the host still owns it.
    """
    def __init__(self, arcpy):
        self.arcpy = arcpy
        self.owned = False

    def acquire(self):
        status = self.arcpy.CheckExtension("Spatial")
        if status not in ("Available", "CheckedOut"):
            raise RuntimeError("Spatial Analyst is unavailable (%s)." % status)
        if not hasattr(self.arcpy, "mp") and status != "CheckedOut":
            result = self.arcpy.CheckOutExtension("Spatial")
            if result != "CheckedOut":
                raise RuntimeError("Spatial Analyst checkout failed (%s)." % result)
            self.owned = True

    def release(self):
        if self.owned:
            self.owned = False
            try:
                self.arcpy.CheckInExtension("Spatial")
            except Exception:
                pass


def provider_error(provider, raster=False):
    """Validate provider selection; prevents unsupported source labels from failing silently."""
    if isinstance(provider, bytes):
        provider = provider.decode("utf-8", "replace")
    name = (provider or "").strip()
    if raster:
        from mirsad_core.climate_products import REGIONAL
        if name in REGIONAL:return None
    if not raster:
        from mirsad_core.climate_sources import pipeline_sources
        if pipeline_sources(name):return None
        from mirsad_core.climate_products import ENABLED
        if name in ENABLED:return None
    if not raster and any(tag in name for tag in ("Hybrid", u"هجين")):
        return None
    unsupported = any(tag in name for tag in ("NOAA Direct", "Copernicus", "CDS"))
    if not unsupported and "NASA POWER" in name:
        return None
    if not unsupported and not raster and "Open-Meteo" in name:
        return None
    supported = "NASA POWER Regional Grid" if raster else "Hybrid, Open-Meteo, or NASA POWER"
    return ("The selected provider '%s' has no direct download implementation in "
            "this tool. Select %s, or use precalculated data in Offline mode. "
            "No substitute source will be downloaded." % (name, supported))


def is_offline_mode(text):
    if isinstance(text, bytes):
        text = text.decode("utf-8", "replace")
    return bool(text and any(word in text for word in (
        "Offline", "Existing", u"أوفلاين", u"موجودة مسبقاً")))
