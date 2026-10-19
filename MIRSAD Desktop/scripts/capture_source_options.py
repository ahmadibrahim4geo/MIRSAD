"""Inspect the real source/resolution controls in both languages and themes."""
import os
from pathlib import Path
import sys
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/".test-output/source-ui"
OUT.mkdir(exist_ok=True)
os.environ["MIRSAD_TEST_SETTINGS"]=str(OUT/"capture.ini")
os.environ["MIRSAD_OFFLINE"]="1"
sys.path.insert(0,str(ROOT/"src"))
from mirsad_desktop.ui import MainWindow
from mirsad_desktop.climate_sources import ERA5_ONLY,NOAA_ONLY
from mirsad_desktop.climate_products import CDS,IMERG,CHIRPS

app=QApplication([])
window=MainWindow();window.resize(1500,900);window.show()
def capture():
    try:
        for arabic,dark in ((True,True),(False,False),(True,False),(False,True)):
            window.arabic=arabic;window.translate();window.dark=dark;window.apply_theme()
            window.inspector.setCurrentIndex(1)
            for provider,slug in ((ERA5_ONLY,"auto"),(CDS,"cds"),(IMERG,"imerg"),(CHIRPS,"chirps")):
                window.provider.setCurrentText(provider);app.processEvents()
                scroll=window.inspector.widget(1)
                if provider in (CDS,IMERG):scroll.ensureWidgetVisible(window.source_credentials)
                else:scroll.verticalScrollBar().setValue(0)
                app.processEvents()
                stem=("ar" if arabic else "en")+("-dark" if dark else "-light")+"-"+slug
                window.grab().save(str(OUT/(stem+".png")))
    finally:window.close();app.quit()
QTimer.singleShot(500,capture)
sys.exit(app.exec())
