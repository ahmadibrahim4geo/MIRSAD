# -*- coding: utf-8 -*-
"""Backward-compatibility module redirecting to MIRSAD_Weather_Stations_Atlas_Generator.pyt"""
import os, sys
_dir = os.path.dirname(os.path.abspath(__file__))
_mirsad_pyt = os.path.join(_dir, 'MIRSAD_Weather_Stations_Atlas_Generator.pyt')
if sys.version_info[0] >= 3:
    from importlib.machinery import SourceFileLoader
    _mod = SourceFileLoader('mirsad_weather_core', _mirsad_pyt).load_module('mirsad_weather_core')
else:
    import imp
    _mod = imp.load_source('mirsad_weather_core', _mirsad_pyt)
for _k, _v in _mod.__dict__.items():
    if not _k.startswith('__') or _k in ('__file__', '__name__'):
        globals()[_k] = _v
