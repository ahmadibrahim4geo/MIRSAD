# -*- coding: utf-8 -*-
"""
MIRSAD: Gridded & Raster Climate Atlas Generator
Enterprise Geoprocessing Toolbox for ArcMap (10.x / Python 2.7) & ArcGIS Pro (Python 3).

Downloads gridded/raster climate data from NASA POWER and numerical reanalysis across
Layer 1 (Download Extent AOI), converts cells to 32-bit Float points with full seasonal
and annual indicators in Project_Data.gdb, performs high-precision spatial interpolation,
and clips final rasters using Layer 2 (Study Area Mask). Supports full Offline Mode.

Developed by: Ahmad Ibrahim (@ahmadibrahim4geo)
إعداد وتطوير: أحمد إبراهيم
Email / البريد الإلكتروني: ahmadibrahim.geo@gmail.com
"""
import os
import sys

_TOOLBOX_DIR = os.path.dirname(os.path.abspath(__file__))
if _TOOLBOX_DIR not in sys.path:
    sys.path.insert(0, _TOOLBOX_DIR)

import raster_atlas_generator as _rag

RasterDataClimateAtlasGenerator = _rag.RasterDataClimateAtlasGenerator
RasterDataClimateAtlasGeneratorAR = _rag.RasterDataClimateAtlasGeneratorAR


class Toolbox(object):
    """MIRSAD Gridded & Raster Climate Atlas (ArcMap 10.x & ArcGIS Pro compatible)."""

    def __init__(self):
        self.label = "MIRSAD Grid Raster Climate Atlas Generator"
        self.alias = "MirsadRasterAtlas"
        self.description = (
            "Enterprise Geoprocessing Toolbox for Gridded Climate Data Processing, "
            "High-Precision Spatial Interpolation, Continuous Surface Rasterization, "
            "and Cartographic Atlas Generation under the MIRSAD platform."
        )
        self.tools = [RasterDataClimateAtlasGenerator, RasterDataClimateAtlasGeneratorAR]
