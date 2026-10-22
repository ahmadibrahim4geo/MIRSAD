import sys
import json
import tempfile
import time
import unittest
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from mirsad_desktop.ui import MainWindow


class UiTests(unittest.TestCase):
    def test_supplementary_choices_are_nested_optional_and_keep_each_tools_draft(self):
        from mirsad_desktop.climate_sources import ERA5_ONLY
        from mirsad_desktop.climate_products import CHELSA
        window=MainWindow();window.show();self.app.processEvents()
        try:
            window.navigation.setCurrentRow(0)
            window.provider.setCurrentText(ERA5_ONLY)
            self.assertEqual(window.chosen_extra_variables(),[])
            self.assertEqual(len(window.module_items),19)
            self.assertNotIn("Evapotranspiration",window.chosen_modules())
            window.extra_items["RHmax"].setCheckState(0,Qt.Checked)
            self.assertEqual(window.module_items["Relative Humidity"].checkState(0),Qt.Checked)
            self.assertEqual(window.chosen_extra_variables(),["RHmax"])
            window.navigation.setCurrentRow(1)
            self.assertEqual(window.chosen_extra_variables(),[])
            window.navigation.setCurrentRow(0)
            self.assertEqual(window.chosen_extra_variables(),["RHmax"])
            window.inspector.setCurrentIndex(1)
            window.module_items["Relative Humidity"].setExpanded(True)
            window.resize(1600,950)
            for arabic,dark,name in ((True,True,"ar-dark"),(False,False,"en-light")):
                window.arabic=arabic;window.dark=dark;window.translate();window.apply_theme();self.app.processEvents()
                window.inspector.widget(1).ensureWidgetVisible(window.module_tree)
                window.module_tree.scrollToItem(window.extra_items["RHmax"])
                self.app.processEvents()
                self.assertTrue(window.grab().save(str(ROOT/".test-output"/("supplementary-"+name+".png"))))
            window.provider.setCurrentText(CHELSA)
            self.assertFalse(window.extra_items["RHmax"].flags()&Qt.ItemIsEnabled)
            self.assertEqual(window.chosen_extra_variables(),[])
        finally:window.close()

    @classmethod
    def setUpClass(cls):
        (ROOT/".test-output").mkdir(exist_ok=True)
        cls.previous_settings=os.environ.get("MIRSAD_TEST_SETTINGS")
        os.environ["MIRSAD_TEST_SETTINGS"]=str(ROOT/".test-output/ui-test-settings.ini")
        cls.app = QApplication.instance() or QApplication([])

    @classmethod
    def tearDownClass(cls):
        import shiboken6
        from PySide6.QtCore import QCoreApplication,QEvent
        cls.app.closeAllWindows()
        cls.app.processEvents()
        for window in list(cls.app.topLevelWidgets()):
            if isinstance(window,MainWindow) and shiboken6.isValid(window):shiboken6.delete(window)
        QCoreApplication.sendPostedEvents(None,QEvent.DeferredDelete)
        cls.app.processEvents()
        cls.app.quit()
        shiboken6.delete(cls.app)
        cls.app = None
        if cls.previous_settings is None:os.environ.pop("MIRSAD_TEST_SETTINGS",None)
        else:os.environ["MIRSAD_TEST_SETTINGS"]=cls.previous_settings

    def test_global_themes_menus_crs_and_native_resizing(self):
        from PySide6.QtWidgets import QComboBox,QDialog,QVBoxLayout,QLabel
        from PySide6.QtGui import QPalette
        from mirsad_desktop.dialogs import CrsSelectionDialog
        window=MainWindow();window.show();self.app.processEvents()
        try:
            for dark in (False,True):
                window.dark=dark;window.apply_theme();self.app.processEvents()
                dialog=QDialog(window);QVBoxLayout(dialog).addWidget(QLabel("Dialog text"));dialog.show();self.app.processEvents()
                bg=dialog.palette().color(QPalette.Window).lightness()
                fg=dialog.palette().color(QPalette.WindowText).lightness()
                self.assertGreater(fg,bg) if dark else self.assertGreater(bg,fg)
                for combo in window.findChildren(QComboBox):self.assertLessEqual(combo.maxVisibleItems(),10)
                dialog.close()
            self.assertFalse(hasattr(window.map,"connect_provider"))
            window.map.change_basemap("Google Satellite")
            self.assertEqual(window.map.canvas.basemap,"Offline / بدون خلفية")
            window.resize(1100,720);self.app.processEvents()
            window.shell_split.setSizes([180,500,350]);self.app.processEvents()
            self.assertGreater(window.sidebar.width(),150)
            window.crs.setEditText("EPSG:32636")
            self.assertEqual(window.get_clean_crs(window.crs),"EPSG:32636")
            # All scientific drafts retain the model, end date and monthly options.
            window.om_model.setCurrentIndex(2);window.end.setDate(window.end.date().addYears(-1));end=window.end.date()
            window.monthly_rasters_cb.setChecked(True);window.reclass_en.setChecked(True)
            window.navigation.setCurrentRow(1);self.assertTrue(window.inspector.isTabEnabled(2))
            window.navigation.setCurrentRow(0)
            self.assertEqual(window.om_model.currentIndex(),2);self.assertEqual(window.end.date(),end)
            self.assertTrue(window.monthly_rasters_cb.isChecked());self.assertTrue(window.reclass_en.isChecked())
            picker=CrsSelectionDialog(parent=window)
            picker.custom_input.setText("INVALID_CRS");picker.accept()
            self.assertNotEqual(picker.result(),QDialog.DialogCode.Accepted)
            picker.close()
        finally:window.close()

    def test_provider_resolution_scope_and_tool_draft_memory(self):
        from mirsad_desktop.climate_sources import NOAA_ONLY,ERA5_ONLY,ERA5_MODELS,GRID_HYBRID,NOAA_RESOLUTION,POWER_RESOLUTION
        window=MainWindow()
        try:
            window.navigation.setCurrentRow(0)
            self.assertGreaterEqual(window.provider.findText(NOAA_ONLY),0)
            window.provider.setCurrentText(ERA5_ONLY)
            self.assertEqual(window.om_model.currentText(),ERA5_MODELS[0])
            window.om_model.setCurrentIndex(2)
            window.provider.setCurrentText(NOAA_ONLY)
            self.assertEqual(window.om_model.currentText(),NOAA_RESOLUTION)
            self.assertFalse(window.om_model.isEnabled())
            window.navigation.setCurrentRow(1)
            self.assertEqual(window.provider.findText(NOAA_ONLY),-1)
            self.assertEqual(window.provider.currentText(),GRID_HYBRID)
            self.assertEqual(window.om_model.currentText(),ERA5_MODELS[0])
            window.provider.setCurrentText("NASA POWER")
            self.assertEqual(window.om_model.currentText(),POWER_RESOLUTION)
            window.navigation.setCurrentRow(0)
            self.assertEqual(window.provider.currentText(),NOAA_ONLY)
            window.provider.setCurrentText(ERA5_ONLY)
            self.assertEqual(window.om_model.currentText(),ERA5_MODELS[2])
        finally:window.close()

    def test_need_sign_in_fields_and_credentials_never_enter_job_files(self):
        from mirsad_desktop.climate_products import CDS,IMERG,CHIRPS
        from mirsad_desktop.process_worker import ProcessWorker
        window=MainWindow();window.show();self.app.processEvents()
        window.inspector.setCurrentIndex(1)
        try:
            window.provider.setCurrentText(CDS);self.app.processEvents()
            self.assertTrue(window.source_credentials.isVisible())
            self.assertTrue(window.source_token.isVisible());self.assertFalse(window.source_password.isVisible())
            window.provider.setCurrentText(IMERG);self.app.processEvents()
            self.assertTrue(window.source_username.isVisible());self.assertTrue(window.source_password.isVisible())
            self.assertEqual(window.source_password.echoMode(),type(window.source_password).EchoMode.Password)
            window.provider.setCurrentText(CHIRPS);self.app.processEvents()
            self.assertFalse(window.source_credentials.isVisible());self.assertFalse(window.daily.isEnabled())
            secret="EXAMPLE_NOT_REAL_CREDENTIAL_94317"
            with tempfile.TemporaryDirectory(dir=ROOT/".test-output") as folder:
                worker=ProcessWorker(dict(operation="invalid",_credentials=dict(token=secret)),folder,window)
                self.assertNotIn(secret,worker.path.read_text(encoding="utf-8"))
                worker.start();deadline=time.monotonic()+30
                while not worker.done and time.monotonic()<deadline:self.app.processEvents();time.sleep(.02)
                self.assertTrue(worker.done)
                self.assertEqual(worker.secret_payload,b"")
                for path in worker.directory.iterdir():
                    if path.is_file():self.assertNotIn(secret.encode(),path.read_bytes(),path.name)
        finally:window.close()

    def test_selection_survives_search_and_language_changes(self):
        window = MainWindow()
        self.assertIsNone(window.country.currentData())
        self.assertEqual(window.table.rowCount(),0)
        window.country.setCurrentIndex(window.country.findData("EG"))
        self.assertEqual(window.table.rowCount(),85)
        key = window.current_rows[0]["station_key"]
        window.table.item(0,0).setCheckState(Qt.Checked)
        self.assertEqual(window.selected_keys,{key})
        window.search.setText("NO_SUCH_STATION")
        self.assertEqual(window.table.rowCount(),0)
        initial_arabic = window.arabic
        window.search.clear()
        window.toggle_language()
        self.assertEqual(window.selected_stations()[0]["station_key"], key)
        self.assertEqual(window.arabic, not initial_arabic)
        self.assertEqual(window.centralWidget().layoutDirection(), Qt.RightToLeft if window.arabic else Qt.LeftToRight)
        window.toggle_language()
        self.assertEqual(window.arabic, initial_arabic)
        self.assertEqual(window.centralWidget().layoutDirection(), Qt.RightToLeft if window.arabic else Qt.LeftToRight)
        window.close()

    def test_crs_picker_native_overview_favorites_layers_and_search_restoration(self):
        from PySide6.QtWidgets import QDialog
        from mirsad_desktop.dialogs import CrsSelectionDialog
        window=MainWindow();window.show();self.app.processEvents()
        previous=window.settings.value("crs/favorites","[]");window.settings.setValue("crs/favorites","[]")
        try:
            window.register_map_layer("Projected points","source_points",kind="point",crs="EPSG:32637")
            window.register_map_layer("Unknown CRS","unknown",kind="polygon")
            picker=CrsSelectionDialog("EPSG:32636",window);picker.show();self.app.processEvents()
            self.assertTrue(picker.screen().availableGeometry().contains(picker.frameGeometry()))
            roots=[picker.crs_tree.topLevelItem(i) for i in range(4)]
            self.assertEqual([item.text(0) for item in roots],["Favorites","Layers","Geographic Coordinate System","Projected Coordinate System"])
            self.assertFalse(roots[2].isExpanded());self.assertFalse(roots[3].isExpanded())
            self.assertEqual(roots[1].child(0).child(0).data(0,Qt.UserRole),"EPSG:32637")
            self.assertIsNone(roots[1].child(1).child(0).data(0,Qt.UserRole))
            picker.search_input.setText("Projected points")
            self.assertFalse(roots[1].isHidden());self.assertFalse(roots[1].child(0).child(0).isHidden())
            picker.search_input.clear()
            self.assertTrue(picker.select_initial_crs("EPSG:32637"))
            self.assertEqual(picker.crs_tree.currentItem().parent().text(0),"Northern Hemisphere")
            self.assertTrue(picker.select_initial_crs("EPSG:32636"))
            item=picker.crs_tree.currentItem();path=[];parent=item.parent()
            while parent:path.insert(0,parent.text(0));parent=parent.parent()
            self.assertEqual(path,["Projected Coordinate System","UTM","WGS 1984","Northern Hemisphere"])
            picker.favorite_button.click();self.assertEqual(picker.favorites,["EPSG:32636"])
            expanded={item.data(0,Qt.UserRole+1) for item in picker.items() if item.isExpanded()}
            picker.search_input.setText("Egypt")
            self.assertTrue(any(not item.isHidden() for item in picker.items() if item.data(0,Qt.UserRole)=="EPSG:22992"))
            picker.search_input.clear()
            self.assertEqual({item.data(0,Qt.UserRole+1) for item in picker.items() if item.isExpanded()},expanded)
            picker.search_input.setText("WGS 84 UTM Zone 36N")
            self.assertTrue(any(not item.isHidden() for item in picker.items() if item.data(0,Qt.UserRole)=="EPSG:32636"))
            picker.search_input.clear();picker.catalogue_toggle.setChecked(True)
            projected=picker.crs_tree.topLevelItem(3)
            self.assertEqual(projected.child(10).text(0),"UTM")
            self.assertTrue(projected.child(projected.childCount()-1).text(0).startswith("Additional Esri definitions"))
            picker.close()
            reopened=CrsSelectionDialog("EPSG:4326",window)
            self.assertEqual(reopened.favorites,["EPSG:32636"])
            reopened.select_initial_crs("EPSG:32636");reopened.favorite_button.click()
            self.assertEqual(reopened.favorites,[])
            reopened.custom_input.setText("INVALID_CRS");reopened.accept()
            self.assertNotEqual(reopened.result(),QDialog.Accepted)
            self.assertFalse(reopened.favorite_button.isEnabled());reopened.close()
        finally:
            window.settings.setValue("crs/favorites",previous);window.close()

    def test_map_gallery_navigation_keyboard_and_compact_controls(self):
        from PySide6.QtTest import QTest
        from PySide6.QtWidgets import QToolButton
        window=MainWindow();window.resize(1250,800);window.show();self.app.processEvents()
        panel=window.map
        try:
            self.assertIsInstance(panel.basemap,QToolButton)
            panel.basemap.click();self.app.processEvents()
            self.assertTrue(panel.gallery.isVisible())
            self.assertLessEqual(panel.gallery.width(),340)
            # Screenshot UI can deactivate the window without a pointer click.
            from PySide6.QtCore import QEvent
            self.app.sendEvent(window,QEvent(QEvent.WindowDeactivate));self.app.processEvents()
            self.assertTrue(panel.gallery.isVisible())
            self.app.sendEvent(panel.gallery,QEvent(QEvent.WindowDeactivate));self.app.processEvents()
            self.assertTrue(panel.gallery.isVisible())
            panel.gallery.cards["Offline / بدون خلفية"].click();self.app.processEvents()
            self.assertEqual(panel.canvas.basemap,"Offline / بدون خلفية")
            self.assertFalse(panel.gallery.isVisible())
            panel.basemap.click();self.app.processEvents()
            QTest.keyClick(panel.gallery,Qt.Key_Escape);self.app.processEvents()
            self.assertFalse(panel.gallery.isVisible())
            panel.basemap.click();self.app.processEvents()
            QTest.mouseClick(window.brand_logo,Qt.LeftButton);self.app.processEvents()
            self.assertFalse(panel.gallery.isVisible())
            # After screenshot focus loss, clicks in another application are
            # absent from Qt's event queue; exercise the native pointer boundary.
            from unittest.mock import patch
            native_state=panel.gallery.pointer_state
            panel.basemap.click();self.app.processEvents()
            panel.gallery.pointer_state=lambda key:0
            panel.gallery.pointer_down=False;panel.gallery.check_outside_pointer()
            self.assertTrue(panel.gallery.isVisible())
            panel.gallery.pointer_state=lambda key:0x8000 if key==1 else 0
            with patch("mirsad_desktop.mapcontrols.QCursor.pos",return_value=window.brand_logo.mapToGlobal(window.brand_logo.rect().center())):
                panel.gallery.check_outside_pointer()
            self.assertFalse(panel.gallery.isVisible())
            panel.gallery.pointer_state=native_state
            panel.canvas.zoom=8;panel.canvas.changed();panel.canvas.setFocus()
            QTest.keyClick(panel.canvas,Qt.Key_Plus);self.app.processEvents()
            self.assertEqual(panel.canvas.zoom,9)
            panel.world.click();self.assertEqual(panel.canvas.zoom,2)
            panel.add.click();self.assertTrue(panel.canvas.add_mode)
            QTest.keyClick(panel.canvas,Qt.Key_Escape);self.app.processEvents()
            self.assertFalse(panel.canvas.add_mode);self.assertFalse(panel.add.isChecked())
            panel.canvas.zoom=19;panel.canvas.changed();self.assertFalse(panel.plus.isEnabled())
            panel.canvas.zoom=1;panel.canvas.changed();self.assertFalse(panel.minus.isEnabled())
            for arabic in (False,True):
                window.arabic=arabic;window.translate()
                for dark in (False,True):
                    window.dark=dark;window.apply_theme();self.app.processEvents()
                    self.assertTrue(panel.basemap.accessibleName())
                    self.assertTrue(panel.gallery.cards["Esri Imagery"].text())
                    self.assertTrue(panel.canvas.rect().contains(panel.tools.geometry()))
                    self.assertTrue(panel.canvas.rect().contains(panel.navigation.geometry()))
            window.resize(1000,650);window.reset_workspace_layout();self.app.processEvents()
            self.assertFalse(panel.tools.geometry().intersects(panel.navigation.geometry()))
        finally:window.close()

    def test_bilingual_user_guide_contents_search_and_local_navigation(self):
        from mirsad_desktop.registry import MODULES
        from PySide6.QtCore import QUrl
        window=MainWindow();window.show();self.app.processEvents()
        try:
            window.show_help();self.app.processEvents();guide=window.help_dialog
            self.assertTrue(guide.isVisible());self.assertFalse(guide.isModal())
            for language in ("en","ar"):
                guide.language.setCurrentIndex(guide.language.findData(language));self.app.processEvents()
                self.assertGreaterEqual(len(guide.topics),15)
                self.assertEqual(guide.sidebar.x()>guide.page.x(),language=="ar")
                guide.open_topic('modules')
                text=guide.browser.toPlainText()
                for module in MODULES:self.assertIn(module.name,text)
                guide.open_topic('providers');text=guide.browser.toPlainText()
                for date in ("1981","1984","2001","1940","1950","1929"):self.assertIn(date,text)
                guide.search.setText("NASA");self.assertTrue(guide.find_text())
                self.assertIn("NASA",guide.browser.textCursor().selectedText())
                self.assertTrue(guide.find_text(True))
                guide.search.setText("NO_MATCH_01293847");self.assertFalse(guide.find_text())
                guide.follow_link(QUrl("#providers"));self.app.processEvents()
                self.assertEqual(guide.contents.currentItem().data(0,Qt.UserRole),"providers")
            guide.close();window.show_help();self.assertIs(window.help_dialog,guide)
        finally:window.close()

    def test_export_button_completes_worker_and_writes_all_formats(self):
        window = MainWindow()
        errors = []
        window.on_error = errors.append
        original_hook = sys.excepthook
        sys.excepthook = lambda kind,value,tb: errors.append(str(value))
        try:
            (ROOT/".test-output").mkdir(exist_ok=True)
            with tempfile.TemporaryDirectory(dir=ROOT/".test-output") as folder:
                window.folder.setText(folder)
                window.project_name.setText("UI_Export")
                window.country.setCurrentIndex(window.country.findData("CA"))
                window.table.item(0,0).setCheckState(Qt.Checked)
                window.export.click()
                deadline = time.monotonic()+20
                while window.job_thread and time.monotonic()<deadline:
                    self.app.processEvents()
                    time.sleep(0.02)
                self.assertFalse(errors, errors)
                self.assertIsNone(window.job_thread, "Export worker did not finish")
                output = Path(folder)/"UI_Export"
                manifest = json.loads((output/"manifest.json").read_text(encoding="utf-8"))
                self.assertEqual(manifest["status"],"complete")
                self.assertTrue(window.open_output.isEnabled())
        finally:
            sys.excepthook = original_hook
            window.close()

    def test_own_points_map_zoom_dark_mode_and_provider_capabilities(self):
        from mirsad_desktop.inputs import make_point
        window=MainWindow();window.navigation.setCurrentRow(1)
        point=make_point("001","نقطتي",31.2,30,attributes={"T_Annual_Mean":25})
        window.append_points([point])
        self.assertEqual(window.input_mode.currentData(),"user")
        self.assertEqual(len(window.selected_stations()),1)
        self.assertEqual(window.selected_stations()[0]["usaf"],"001")
        self.assertEqual(window.raster_fields.count(),1)
        zoom=window.map.canvas.zoom;window.map.plus.click();self.assertEqual(window.map.canvas.zoom,zoom+1)
        dark=window.dark;window.theme.click();self.assertEqual(window.dark,not dark);window.theme.click()
        self.assertEqual(len(window.module_items),19)
        window.footer_crs.setCurrentText("EPSG:32636");self.assertEqual(window.crs.currentText(),"EPSG:32636")
        window.crs.setCurrentText("EPSG:4326");self.assertEqual(window.footer_crs.currentText(),"EPSG:4326")
        window.provider.setCurrentText("Open-Meteo ERA5")
        self.assertTrue(window.module_items["UV Index"].flags() & Qt.ItemIsEnabled)
        window.provider.setCurrentText("NASA POWER");window.check_modules(True)
        self.assertEqual(len(window.chosen_modules()),19)
        window.on_progress({"stage":"download","completed":4,"total":10,"message":"4/10"})
        self.assertEqual(window.progress.value(),40)
        window.close()

    def test_worker_crash_does_not_close_ui_and_next_export_succeeds(self):
        from unittest.mock import patch
        from mirsad_desktop.process_worker import ProcessWorker
        window=MainWindow();errors=[];window.on_error=errors.append
        with tempfile.TemporaryDirectory(dir=ROOT/".test-output") as folder:
            window.folder.setText(folder);window.country.setCurrentIndex(window.country.findData("NZ"));window.table.item(0,0).setCheckState(Qt.Checked)
            request=dict(operation="export",folder=folder,name="Interrupted",points=window.selected_stations(),metadata=window.meta,options={})
            original_start=ProcessWorker.start
            def start_then_crash(worker):
                worker.process.started.connect(worker.process.kill)
                original_start(worker)
            with patch.object(ProcessWorker,"start",start_then_crash):window.start_request(request)
            deadline=time.monotonic()+15
            while window.job_thread and time.monotonic()<deadline:self.app.processEvents();time.sleep(.02)
            self.assertIsNone(window.job_thread);self.assertTrue(errors)
            self.assertTrue(window.export.isEnabled())
            window.project_name.setText("Recovery");window.export.click();deadline=time.monotonic()+20
            while window.job_thread and time.monotonic()<deadline:self.app.processEvents();time.sleep(.02)
            self.assertIsNone(window.job_thread)
            self.assertTrue((Path(folder)/"Recovery/Project.gpkg").exists())
        window.close()

    def test_tools_keep_independent_points_climate_and_raster_drafts(self):
        from mirsad_desktop.inputs import make_point
        window=MainWindow()
        try:
            self.assertEqual(window.region.currentData(),"")
            self.assertIsNone(window.country.currentData())
            self.assertEqual(window.table.rowCount(),0)
            window.region.setCurrentIndex(window.region.findData("North America"))
            window.country.setCurrentIndex(window.country.findData("CA"))
            window.table.item(0,0).setCheckState(Qt.Checked)
            station_key=window.selected_stations()[0]["station_key"]
            window.project_name.setText("Canada_draft")
            window.yearly.setChecked(True)
            window.enable_raster.setChecked(True)
            window.cell_size.setValue(7000)
            window.navigation.setCurrentRow(1)
            self.assertEqual(window.active_tool,"points")
            self.assertFalse(window.yearly.isChecked())
            self.assertFalse(window.enable_raster.isChecked())
            self.assertTrue(window.inspector.isTabEnabled(2))
            window.append_points([make_point("B01","Brazil",-46.6,-23.5)])
            window.project_name.setText("Brazil_draft")
            point_key=window.selected_stations()[0]["station_key"]
            window.navigation.setCurrentRow(2)
            self.assertEqual(window.selected_stations(),[])
            self.assertTrue(window.inspector.isTabEnabled(1))
            self.assertTrue(window.inspector.isTabEnabled(2))
            window.next_step.click()
            self.assertEqual(window.inspector.currentIndex(),1)
            window.navigation.setCurrentRow(0)
            self.assertEqual(window.selected_stations()[0]["station_key"],station_key)
            self.assertEqual(window.project_name.text(),"Canada_draft")
            self.assertTrue(window.yearly.isChecked())
            self.assertTrue(window.inspector.isTabEnabled(2))
            self.assertEqual(window.cell_size.value(),7000)
            window.navigation.setCurrentRow(1)
            self.assertEqual(window.selected_stations()[0]["station_key"],point_key)
            self.assertEqual(window.project_name.text(),"Brazil_draft")
            self.assertEqual(window.viewer_tabs.widget(0),window.map_content)
        finally:window.close()

    def test_readonly_workbook_preview_uses_worker_and_preserves_source(self):
        import hashlib
        from openpyxl import Workbook
        window=MainWindow();errors=[];window.on_error=errors.append
        try:
            with tempfile.TemporaryDirectory(dir=ROOT/".test-output") as folder:
                window.folder.setText(folder)
                path=Path(folder)/"Results.xlsx"
                book=Workbook();book.active.title="Data";book.active.append(["ID","Value"])
                for i in range(1001):book.active.append([str(i).zfill(5),i])
                book.create_sheet("Source_Data").append(["Source","Unit"]);book.save(path)
                before=hashlib.sha256(path.read_bytes()).hexdigest()
                def wait():
                    deadline=time.monotonic()+15
                    while window.job_thread and time.monotonic()<deadline:self.app.processEvents();time.sleep(.02)
                    self.assertIsNone(window.job_thread);self.assertFalse(errors,errors)
                window.request_preview(dict(path=str(path)));wait()
                self.assertEqual(window.preview_table.table.model().rowCount(),500)
                self.assertEqual(window.preview_table.sheets.count(),2)
                window.preview_table.next.click();wait()
                self.assertEqual(window.preview_table.offset,500)
                self.assertEqual(window.preview_table.table.model().rows[0][0],"00500")
                window.preview_table.sheets.setCurrentText("Source_Data");wait()
                self.assertEqual(window.preview_table.offset,0)
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),before)
                self.assertEqual(window.selected_stations(),[])
        finally:window.close()


if __name__ == "__main__": unittest.main()
