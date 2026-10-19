# -*- coding: utf-8 -*-
"""Cold imports from outside the checkout, not native ArcGIS verification."""
from __future__ import unicode_literals
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class RepositoryLayoutTests(unittest.TestCase):
    def test_toolboxes_and_compatibility_modules_load_without_checkout_cwd(self):
        scratch = os.path.join(ROOT, 'tests', '.output')
        if not os.path.isdir(scratch):os.makedirs(scratch)
        directory = tempfile.mkdtemp(prefix='layout-', dir=scratch)
        script = r'''
import json,os,sys,types
# Deliberate import double: never wait for a license or call native geoprocessing.
sys.modules['arcpy']=types.ModuleType('arcpy')
try:
    from importlib.machinery import SourceFileLoader
    def load(name,path):return SourceFileLoader(name,path).load_module()
except ImportError:
    import imp
    def load(name,path):return imp.load_source(name,path)
root=sys.argv[1];folder=os.path.join(root,'Toolboxes');counts=[]
for n,filename in enumerate(('MIRSAD_Climate_Atlas_Generator_10_8.pyt','MIRSAD_Weather_Stations_Atlas_Generator.pyt','MIRSAD_Grid_Raster_Climate_Atlas_Generator.pyt')):
    module=load('layout_probe_'+str(n),os.path.join(folder,filename))
    counts.append(len(module.Toolbox().tools))
    if n==1:
        assert os.path.normcase(os.path.realpath(module.HUB_DIR))==os.path.normcase(os.path.realpath(os.path.join(root,'Weather_Stations_Hub')))
        assert os.path.normcase(os.path.realpath(module.REPO_DIR))==os.path.normcase(os.path.realpath(root))
load('layout_point_wrapper',os.path.join(folder,'POWER_Climate_Atlas_Generator_10_8.py'))
load('layout_station_wrapper',os.path.join(folder,'NOAA_WMO_Weather_Stations_Atlas_Generator.py'))
import mirsad_core
assert hasattr(mirsad_core,'__path__'), 'Compatibility module shadowed the package'
from mirsad_core.help_viewer import help_path
path,topic=help_path('formula-pet','ar')
assert os.path.isfile(path) and topic=='formula-pet.html'
assert os.path.isfile(os.path.join(root,'data','stations.sqlite'))
print(json.dumps(dict(counts=counts,native_arcpy=False)))
'''
        env=dict(os.environ);env.pop('PYTHONPATH',None)
        try:
            output=subprocess.check_output([sys.executable,'-c',script,ROOT],cwd=directory,env=env)
            report=json.loads(output.decode('utf-8').splitlines()[-1])
            self.assertEqual(report['counts'],[2,2,2])
            self.assertFalse(report['native_arcpy'])
        finally:shutil.rmtree(directory)

    def test_root_has_no_duplicate_toolboxes_or_old_utils_package(self):
        self.assertFalse(os.path.exists(os.path.join(ROOT,'utils')))
        self.assertFalse(any(name.endswith('.pyt') for name in os.listdir(ROOT)))
        self.assertTrue(os.path.isfile(os.path.join(ROOT,'mirsad_core','__init__.py')))


if __name__=='__main__':unittest.main()
