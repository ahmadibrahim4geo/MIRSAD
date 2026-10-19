"""Native Windows CRS-browser acceptance captures; no alternative product entry point."""
import json
import os
import sys
from pathlib import Path
from PySide6.QtCore import QTimer,Qt
from PySide6.QtWidgets import QApplication,QAbstractItemView

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/".test-output/crs-picker"
OUT.mkdir(parents=True,exist_ok=True)
os.environ["MIRSAD_TEST_SETTINGS"]=str(OUT/"settings.ini");os.environ["MIRSAD_OFFLINE"]="1"
sys.path.insert(0,str(ROOT/"src"))
from mirsad_desktop.ui import MainWindow
from mirsad_desktop.dialogs import CrsSelectionDialog

app=QApplication([]);window=MainWindow();window.show();errors=[];checks=[]
sys.excepthook=lambda kind,value,tb:errors.append(str(value))
scale=os.environ.get("QT_SCALE_FACTOR","1")

def capture():
    try:
        # Existing records carry actual source metadata; unknown stays unknown.
        window.register_map_layer("Survey points · UTM 37N","qa_points",kind="point",crs="EPSG:32637")
        window.register_map_layer("Boundary without a CRS","qa_unknown",kind="polygon")
        window.settings.setValue("crs/favorites",'["EPSG:4326","EPSG:32637","EPSG:3857"]')
        for arabic in (False,True):
            window.arabic=arabic;window.translate()
            for dark in (True,False):
                window.dark=dark;window.apply_theme()
                dialog=CrsSelectionDialog("EPSG:32637",window);dialog.show();app.processEvents();app.processEvents()
                assert dialog.screen().availableGeometry().contains(dialog.frameGeometry()), "CRS window exceeds the available screen"
                label=("dark" if dark else "light")+("_ar" if arabic else "_en")+"_"+scale
                roots=[dialog.crs_tree.topLevelItem(i) for i in range(4)]
                assert [root.text(0) for root in roots]==["Favorites","Layers","Geographic Coordinate System","Projected Coordinate System"]
                roots[1].child(0).setExpanded(True);roots[1].child(1).setExpanded(True)
                roots[2].setExpanded(True);app.processEvents()
                dialog.grab().save(str(OUT/(label+"_geographic.png")))
                roots[2].setExpanded(False);roots[3].setExpanded(True)
                roots[1].setExpanded(False);app.processEvents()
                dialog.grab().save(str(OUT/(label+"_projected.png")))
                utm=next(roots[3].child(i) for i in range(roots[3].childCount()) if roots[3].child(i).text(0)=="UTM")
                utm.setExpanded(True);dialog.crs_tree.scrollToItem(utm,QAbstractItemView.PositionAtTop);app.processEvents()
                dialog.grab().save(str(OUT/(label+"_utm.png")))
                # Favorites can also contain this code, so explicitly open the
                # native WGS branch for this screenshot rather than that shortcut.
                wgs=next(utm.child(i) for i in range(utm.childCount()) if utm.child(i).text(0)=="WGS 1984")
                wgs.setExpanded(True);wgs.child(0).setExpanded(True)
                leaf=next(wgs.child(0).child(i) for i in range(wgs.child(0).childCount())
                          if wgs.child(0).child(i).data(0,Qt.UserRole)=="EPSG:32637")
                dialog.crs_tree.setCurrentItem(leaf);dialog.crs_tree.scrollToItem(leaf);app.processEvents()
                assert dialog.custom_input.text()=="EPSG:32637"
                dialog.grab().save(str(OUT/(label+"_wgs84.png")))
                dialog.details_toggle.setChecked(True);app.processEvents();app.processEvents()
                assert dialog.screen().availableGeometry().contains(dialog.frameGeometry()), "CRS details exceed the available screen"
                dialog.grab().save(str(OUT/(label+"_details.png")))
                checks.append(label);dialog.close()
    except Exception as exc:errors.append(str(exc))
    finally:
        (OUT/("report_"+scale+".json")).write_text(json.dumps(dict(errors=errors,checked=checks)),encoding="utf-8")
        window.close();app.quit()

QTimer.singleShot(100,capture)
result=app.exec();raise SystemExit(1 if errors else result)
