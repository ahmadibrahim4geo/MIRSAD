# -*- coding: utf-8 -*-
"""Open offline help from ArcMap/Python 2.7 or Pro/Python 3, without Qt."""
from __future__ import unicode_literals
import os
import webbrowser

TOPICS=('start', 'workspace', 'tools', 'inputs', 'providers', 'hybrid', 'modules', 'period', 'regional', 'raster', 'outputs', 'results', 'examples', 'troubleshooting', 'shortcuts', 'install', 'arcgis', 'tool-points', 'tool-stations', 'tool-raster', 'contributing', 'parameters-points', 'parameters-stations', 'parameters-raster', 'calculation-flow', 'calculation-units', 'formula-temperature', 'formula-lst', 'formula-rain', 'formula-sea-pressure', 'formula-surface-pressure', 'formula-wind', 'formula-humidity', 'formula-dewpoint', 'formula-solar', 'formula-uv', 'formula-cloud', 'formula-heat-index', 'formula-wind-chill', 'formula-de-martonne', 'formula-pet', 'formula-unep', 'formula-water-deficit', 'formula-dry-months', 'formula-trends')

def help_path(topic='start',language='en',compiled=True):
    if topic not in TOPICS or language not in ('ar','en'):raise ValueError('Unknown help topic/language')
    root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if compiled:
        path=os.path.join(root,'Help','MIRSAD_Help_'+language.upper()+'.chm')
        if os.path.isfile(path):return path,topic+'.html'
    path=os.path.join(root,'Help','MIRSAD_Help_'+language.upper()+'.html')
    if not os.path.isfile(path):raise IOError('Help package is missing. Build or download the complete MIRSAD help package.')
    return path,topic

def open_help(topic='start',language='en',compiled=True):
    path,fragment=help_path(topic,language,compiled)
    if path.lower().endswith('.chm') and os.name=='nt':
        import subprocess
        viewer=os.path.join(os.environ.get('SystemRoot','C:\\Windows'),'hh.exe')
        legacy_viewer=os.path.join(os.environ.get('SystemRoot','C:\\Windows'),'SysWOW64','hh.exe')
        if os.path.isfile(legacy_viewer):viewer=legacy_viewer
        subprocess.Popen([viewer,path+'::/'+fragment],shell=False)
    else:
        try:from urllib.request import pathname2url
        except ImportError:from urllib import pathname2url
        webbrowser.open('file:'+pathname2url(path)+'#'+fragment)
    return path
