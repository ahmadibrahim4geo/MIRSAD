"""Capture actual native map/gallery in both themes and languages, including HiDPI."""
import json
import os
from pathlib import Path
import sys
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/".test-output/map-controls"
OUT.mkdir(exist_ok=True)
os.environ["MIRSAD_TEST_SETTINGS"]=str(OUT/"settings.ini")
sys.path.insert(0,str(ROOT/"src"))
from mirsad_desktop.ui import MainWindow

app=QApplication([]);window=MainWindow();window.resize(1500,930)
window.reset_workspace_layout();window.show()
scale=os.environ.get("QT_SCALE_FACTOR","1")
errors=[]
sys.excepthook=lambda kind,value,tb:errors.append(str(value))

def capture():
    try:
        for arabic in (False,True):
            window.arabic=arabic;window.translate()
            for dark in (True,False):
                window.dark=dark;window.apply_theme();app.processEvents()
                label=("dark" if dark else "light")+("_ar" if arabic else "_en")+"_"+scale
                window.grab().save(str(OUT/(label+".png")))
                window.map.grab().save(str(OUT/(label+"_map.png")))
                window.map.basemap.click();app.processEvents()
                window.map.gallery.grab().save(str(OUT/(label+"_gallery.png")))
                window.map.gallery.hide();app.processEvents()
        window.resize(1000,650);window.reset_workspace_layout();app.processEvents()
        window.grab().save(str(OUT/("compact_"+scale+".png")))
        (OUT/("report_"+scale+".json")).write_text(json.dumps(dict(errors=errors,tile_successes=window.map.canvas.tile_successes,
            tools=[window.map.tools.x(),window.map.tools.y(),window.map.tools.width(),window.map.tools.height()],
            navigation=[window.map.navigation.x(),window.map.navigation.y(),window.map.navigation.width(),window.map.navigation.height()])),encoding="utf-8")
    finally:window.close();app.quit()

QTimer.singleShot(6000,capture)
raise SystemExit(app.exec())
