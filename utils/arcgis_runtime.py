# -*- coding: utf-8 -*-
"""Small runtime guards shared by the ArcMap / ArcGIS Pro tools (Python 2/3)."""
from functools import wraps


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
    """Prevent unsupported source labels from silently downloading NASA data."""
    if isinstance(provider, bytes):
        provider = provider.decode("utf-8", "replace")
    name = (provider or "").strip()
    unsupported = any(tag in name for tag in ("Hybrid", "NOAA", "Copernicus", "CDS"))
    if not unsupported and "NASA POWER" in name:
        return None
    if not unsupported and not raster and "Open-Meteo" in name:
        return None
    supported = "NASA POWER Regional Grid" if raster else "NASA POWER or Open-Meteo"
    return ("The selected provider '%s' has no direct download implementation in "
            "this tool. Select %s, or use precalculated data in Offline mode. "
            "No substitute source will be downloaded." % (name, supported))


def is_offline_mode(text):
    if isinstance(text, bytes):
        text = text.decode("utf-8", "replace")
    return bool(text and any(word in text for word in (
        "Offline", "Existing", u"أوفلاين", u"موجودة مسبقاً")))
