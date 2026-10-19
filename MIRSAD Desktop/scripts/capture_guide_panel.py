"""Capture actual manual/panel and verify survival of native focus transfer."""
import json
import os
from pathlib import Path
import sys
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication,QDialog,QVBoxLayout,QLabel

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/".test-output/guide-panel";OUT.mkdir(exist_ok=True)
os.environ["MIRSAD_TEST_SETTINGS"]=str(OUT/"settings.ini")
sys.path.insert(0,str(ROOT/"src"))
from mirsad_desktop.ui import MainWindow

app=QApplication([]);window=MainWindow();window.resize(1500,960)
window.reset_workspace_layout();window.show();errors=[]
sys.excepthook=lambda kind,value,tb:errors.append(str(value))
scale=os.environ.get("QT_SCALE_FACTOR","1")

def capture():
    try:
        focus_survived=False
        for arabic in (False,True):
            window.arabic=arabic;window.translate()
            for dark in (True,False):
                window.dark=dark;window.apply_theme();app.processEvents()
                label=("dark" if dark else "light")+("_ar" if arabic else "_en")+"_"+scale
                window.map.basemap.setChecked(True);window.map.show_basemaps();app.processEvents()
                focus=QDialog(window);QVBoxLayout(focus).addWidget(QLabel("Capture focus transfer"));focus.show();focus.activateWindow();app.processEvents()
                focus_survived=window.map.gallery.isVisible();assert focus_survived
                focus.close();app.processEvents()
                window.map.grab().save(str(OUT/(label+"_map.png")))
                window.map.gallery.grab().save(str(OUT/(label+"_panel.png")))
                window.map.gallery.hide();window.show_help();guide=window.help_dialog
                guide.language.setCurrentIndex(guide.language.findData("ar" if arabic else "en"))
                guide.apply_document_theme();guide.resize(1100,760);guide.open_topic('providers');app.processEvents();app.processEvents()
                assert (guide.sidebar.x()>guide.page.x())==arabic, "Guide contents direction does not match language"
                guide.grab().save(str(OUT/(label+"_providers.png")))
                guide.open_topic('modules');app.processEvents()
                guide.grab().save(str(OUT/(label+"_modules.png")))
                guide.close()
        window.resize(1000,650);window.reset_workspace_layout();app.processEvents()
        window.map.basemap.setChecked(True);window.map.show_basemaps();app.processEvents()
        window.grab().save(str(OUT/("compact_"+scale+".png")))
        gallery=window.map.gallery
        assert window.map.canvas.rect().contains(gallery.geometry())
        report=dict(errors=errors,focus_transfer_survived=focus_survived,scale=scale,
                    panel=[gallery.x(),gallery.y(),gallery.width(),gallery.height()],
                    chapters=15,tile_successes=window.map.canvas.tile_successes)
        (OUT/("report_"+scale+".json")).write_text(json.dumps(report),encoding="utf-8")
    except Exception as exc:
        errors.append(str(exc))
        (OUT/("report_"+scale+".json")).write_text(json.dumps(dict(errors=errors,scale=scale)),encoding="utf-8")
    finally:window.close();app.quit()

QTimer.singleShot(6000,capture)
result=app.exec()
raise SystemExit(1 if errors else result)
