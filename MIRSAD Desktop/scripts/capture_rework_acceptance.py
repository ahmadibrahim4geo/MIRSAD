"""Exercise and capture the real Qt window at the requested Windows scale."""
import json
import os
from pathlib import Path
import sys
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/".test-output/rework-ui"
OUT.mkdir(exist_ok=True)
os.environ["MIRSAD_TEST_SETTINGS"]=str(OUT/"capture-settings.ini")
os.environ["MIRSAD_OFFLINE"]="1"
sys.path.insert(0,str(ROOT/"src"))
from mirsad_desktop.ui import MainWindow
from mirsad_desktop.dialogs import CrsSelectionDialog

app=QApplication([]);window=MainWindow()
window.resize(1500,900);window.reset_workspace_layout();window.show()
scale=os.environ.get("QT_SCALE_FACTOR","1")
errors=[]
sys.excepthook=lambda kind,value,tb:errors.append(str(value))

def capture():
    try:
        for arabic in (False,True):
            window.arabic=arabic;window.translate()
            for dark in (True,False):
                window.dark=dark;window.apply_theme()
                window.navigation.setCurrentRow(1);window.inspector.setCurrentIndex(2)
                app.processEvents()
                label=("dark" if dark else "light")+("_ar" if arabic else "_en")+"_"+scale
                window.grab().save(str(OUT/(label+".png")))
                window.method.showPopup();app.processEvents()
                popup=window.method.view().window()
                popup.grab().save(str(OUT/(label+"_menu.png")))
                window.method.hidePopup()
        dialog=CrsSelectionDialog("EPSG:22992",window);dialog.show();app.processEvents()
        dialog.grab().save(str(OUT/("crs_"+scale+".png")));dialog.close()
        window.resize(1000,650);window.reset_workspace_layout();app.processEvents()
        window.grab().save(str(OUT/("compact_"+scale+".png")))
        (OUT/("report_"+scale+".json")).write_text(json.dumps(dict(scale=scale,errors=errors,splitter_sizes=window.shell_split.sizes())),encoding="utf-8")
    finally:window.close();app.quit()

QTimer.singleShot(500,capture)
sys.exit(app.exec())
