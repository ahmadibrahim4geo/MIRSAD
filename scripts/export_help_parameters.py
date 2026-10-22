"""Export default EN/AR ArcPy parameter metadata; never execute a tool.

Run with a licensed ArcGIS Pro Python. The ordinary help build consumes this
reviewed snapshot without importing ArcPy. No project/profile is read.
"""
import hashlib,json,sys,datetime
from pathlib import Path
import importlib.machinery
import importlib.util
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))

def load(name,path):
    loader=importlib.machinery.SourceFileLoader(name,str(path));spec=importlib.util.spec_from_loader(name,loader)
    module=importlib.util.module_from_spec(spec);loader.exec_module(module);return module

def main():
    import arcpy
    configs=[('points','Toolboxes/MIRSAD_Climate_Atlas_Generator_10_8.pyt','PowerClimateAtlasGenerator','SpatialClimateAtlasGeneratorAR'),
        ('stations','Toolboxes/MIRSAD_Weather_Stations_Atlas_Generator.pyt','WeatherStationsAtlasGenerator','WeatherStationsAtlasGeneratorAR'),
        ('raster','Toolboxes/MIRSAD_Grid_Raster_Climate_Atlas_Generator.pyt','RasterDataClimateAtlasGenerator','RasterDataClimateAtlasGeneratorAR')]
    tools=[]
    for key,filename,english,arabic in configs:
        module=load('help_metadata_'+key,ROOT/filename)
        en=getattr(module,english)();ar=getattr(module,arabic)()
        ar_params={p.name:p for p in ar.getParameterInfo()};parameters=[]
        for p in en.getParameterInfo():
            hidden='Hidden' in str(p.datatype) or any(part in p.name.lower() for part in ('password','api_key','token'))
            parameters.append(dict(name=p.name,en=p.displayName,ar=ar_params[p.name].displayName,
                datatype=str(p.datatype),required=p.parameterType,direction=p.direction,
                category=p.category or '',default=None if hidden else p.valueAsText,
                enabled=bool(p.enabled),choices=[] if hidden else list(getattr(p.filter,'list',[]) or []),
                description=getattr(p,'description','') or '',sensitive=hidden))
        tools.append(dict(id=key,file=filename,en=en.label,ar=ar.label,parameters=parameters))
    names=[item[1] for item in configs]+['Toolboxes/raster_atlas_generator.py',
        'mirsad_core/toolbox_enrichment.py','mirsad_core/toolbox_pm.py']
    result=dict(reviewed=datetime.date.today().isoformat(),runtime='ArcGIS Pro '+arcpy.GetInstallInfo()['Version'],
        source_hash_policy='normalized-utf8-lf-v1',
        source_raw_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in names},
        source_sha256={name:hashlib.sha256((ROOT/name).read_text(encoding='utf-8-sig').encode('utf-8')).hexdigest() for name in names},tools=tools)
    target=ROOT/'Documents/Help/tool_parameters.json';target.write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
    print('Exported default parameter metadata:',[(t['id'],len(t['parameters'])) for t in tools],flush=True)

if __name__=='__main__':main()
