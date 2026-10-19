"""Capture UI parity showcase screenshots for artifacts."""
import sys
import time
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mirsad_desktop.ui import MainWindow
from mirsad_desktop.dialogs import CrsSelectionDialog

ARTIFACT_DIR = Path(r"C:\Users\ahmad\.gemini\antigravity\brain\4c0d6476-e784-4833-99b6-7d65834ddb58")


def main():
    app = QApplication.instance() or QApplication(sys.argv)

    # 1. Capture Main Window with Arab League Aggregate Scope
    window = MainWindow()
    window.resize(1300, 850)
    window.show()
    app.processEvents()

    # Select Arab League aggregate
    window.region.setCurrentIndex(window.region.findData("Arab"))
    app.processEvents()
    arab_idx = window.country.findData("ARAB")
    if arab_idx >= 0:
        window.country.setCurrentIndex(arab_idx)
    app.processEvents()
    time.sleep(0.5)
    app.processEvents()

    # Save screenshot of main window
    main_pix = window.grab()
    main_pix.save(str(ARTIFACT_DIR / "mirsad_arab_league_showcase.png"), "PNG")
    print("Saved mirsad_arab_league_showcase.png")

    # 2. Capture ArcMap-style Hierarchical CRS Dialog
    dlg = CrsSelectionDialog(current_crs="EPSG:22992", parent=window)
    dlg.resize(760, 580)
    dlg.show()
    app.processEvents()

    # Expand Projected Coordinate Systems -> National Grids -> Egypt
    dlg.select_initial_crs("EPSG:22992")
    app.processEvents()
    time.sleep(0.5)
    app.processEvents()

    dlg_pix = dlg.grab()
    dlg_pix.save(str(ARTIFACT_DIR / "mirsad_hierarchical_crs_dialog.png"), "PNG")
    print("Saved mirsad_hierarchical_crs_dialog.png")

    dlg.close()
    window.close()


if __name__ == "__main__":
    main()
