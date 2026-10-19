"""Capture Hybrid and Raster tab showcases for delivery artifact."""
import sys
import time
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mirsad_desktop.ui import MainWindow

ARTIFACT_DIR = Path(r"C:\Users\ahmad\.gemini\antigravity\brain\4c0d6476-e784-4833-99b6-7d65834ddb58")

def main():
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.resize(1350, 880)
    window.show()
    app.processEvents()

    # 1. Capture Climate Tab with Hybrid Provider & ERA5-Land model
    window.inspector.setCurrentIndex(1)
    app.processEvents()
    time.sleep(0.5)
    app.processEvents()
    window.grab().save(str(ARTIFACT_DIR / "mirsad_climate_hybrid_tab.png"), "PNG")
    print("Saved mirsad_climate_hybrid_tab.png")

    # 2. Capture Raster Tab
    window.inspector.setCurrentIndex(2)
    app.processEvents()
    time.sleep(0.5)
    app.processEvents()
    window.grab().save(str(ARTIFACT_DIR / "mirsad_raster_tab.png"), "PNG")
    print("Saved mirsad_raster_tab.png")

    window.close()

if __name__ == "__main__":
    main()
