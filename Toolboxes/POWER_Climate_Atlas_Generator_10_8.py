# -*- coding: utf-8 -*-
import os, sys
_dir = os.path.dirname(os.path.abspath(__file__))
_mirsad_pyt = os.path.join(_dir, 'MIRSAD_Climate_Atlas_Generator_10_8.pyt')
if sys.version_info[0] >= 3:
    from importlib.machinery import SourceFileLoader
    _mod = SourceFileLoader('mirsad_point_toolbox', _mirsad_pyt).load_module('mirsad_point_toolbox')
else:
    import imp
    _mod = imp.load_source('mirsad_point_toolbox', _mirsad_pyt)
for _k, _v in _mod.__dict__.items():
    if not _k.startswith('__') or _k in ('__file__', '__name__'):
        globals()[_k] = _v
