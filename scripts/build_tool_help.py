"""Update only owned help fields in per-tool Esri XML; preserve other metadata."""
import json,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CONFIGS=(('MIRSAD_Climate_Atlas_Generator_10_8','PowerClimateAtlasGenerator','SpatialClimateAtlasGeneratorAR','points'),
 ('MIRSAD_Weather_Stations_Atlas_Generator','WeatherStationsAtlasGenerator','WeatherStationsAtlasGeneratorAR','stations'),
 ('MIRSAD_Grid_Raster_Climate_Atlas_Generator','RasterDataClimateAtlasGenerator','RasterDataClimateAtlasGeneratorAR','raster'))

def child(parent,path):
    for part in path.split('/'):
        found=parent.find(part)
        if found is None:found=ET.SubElement(parent,part)
        parent=found
    return parent

def main():
    snapshot=json.loads((ROOT/'Documents/Help/tool_parameters.json').read_text(encoding='utf-8'))
    for stem,en,ar,key in CONFIGS:
        tool=next(t for t in snapshot['tools'] if t['id']==key)
        for language,classname in (('en',en),('ar',ar)):
            path=ROOT/(stem+'.'+classname+'.pyt.xml')
            metadata=ET.parse(path).getroot() if path.exists() else ET.Element('metadata')
            metadata.set('{http://www.w3.org/XML/1998/namespace}lang',language)
            title=tool[language]
            url='https://ahmadibrahim4geo.github.io/MIRSAD/Help/MIRSAD_Help_'+language.upper()+'.html#tool-'+key
            intro=('المدخلات والخطوات والمصادر والمخرجات والمعادلات موضحة في دليل مرصاد المشترك. ' if language=='ar' else 'Inputs, workflow, sources, outputs and equations are documented in the shared MIRSAD manual. ')
            local='Help/MIRSAD_Help_'+language.upper()+'.chm'
            summary='<p>'+intro+'</p><p><a href="'+url+'">'+('الدليل الكامل' if language=='ar' else 'Full user guide')+'</a></p><p>'+('المساعدة المحلية دون إنترنت: ' if language=='ar' else 'Local offline help: ')+local+'</p><p>Python: from utils.help_viewer import open_help; open_help("tool-'+key+'", "'+language+'")</p>'
            child(metadata,'dataIdInfo/idCitation/resTitle').text=title
            child(metadata,'dataIdInfo/idAbs').text=summary
            node=child(metadata,'tool');node.set('name',classname);node.set('displayname',title)
            child(node,'summary').text=summary
            ET.ElementTree(metadata).write(path,encoding='utf-8',xml_declaration=True)
    print('Updated bilingual summaries in 6 per-tool XML files; other metadata retained.')
if __name__=='__main__':main()
