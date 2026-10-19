"""Acceptance of the actual application shell and QProcess jobs, including frozen builds."""
import hashlib
import json
import time
import uuid
from pathlib import Path
from PySide6.QtCore import Qt,QTimer,QEvent
from PySide6.QtWidgets import QApplication
from .inputs import make_point


def schedule(window,app,report,errors):
    report=Path(report).resolve();report.parent.mkdir(parents=True,exist_ok=True)
    folder=report.parent/"workspace-fixtures"/uuid.uuid4().hex
    folder.mkdir(parents=True)
    started=time.monotonic();state={"stage":0,"checks":[]}
    window.on_error=errors.append
    original_start=window.start_request
    secret_fixture="EXAMPLE_NOT_A_REAL_CREDENTIAL_FROZEN_01958"
    def start_with_private_pipe(request,*args,**kwargs):
        if request.get("operation")=="analysis":request=dict(request,_credentials={"token":secret_fixture})
        return original_start(request,*args,**kwargs)
    window.start_request=start_with_private_pipe

    def check(value,message):
        if not value:raise AssertionError(message)
        state["checks"].append(message)

    def finish(passed):
        report.write_text(json.dumps(dict(passed=passed,checks=state["checks"],errors=errors,
                          output=str(window.last_output or "")),ensure_ascii=False,indent=2),encoding="utf-8")
        app.quit()

    def step():
        try:
            if time.monotonic()-started>120:raise TimeoutError("Workspace acceptance timed out")
            if errors:raise RuntimeError(str(errors))
            if window.job_thread or getattr(window,"pending_data_result",None):QTimer.singleShot(100,step);return
            stage=state["stage"]
            if stage==0:
                check(window.country.currentData() is None and not window.current_rows,"World start has no assumed country")
                window.dark=True;window.apply_theme()
                window.country.setCurrentIndex(window.country.findData("CA"))
                window.table.item(0,0).setCheckState(Qt.Checked)
                state["station"]=window.selected_stations()[0]["station_key"]
                window.yearly.setChecked(True);window.enable_raster.setChecked(True)
                window.navigation.setCurrentRow(1)
                check(not window.selected_stations() and not window.yearly.isChecked(),"Point-tool draft is independent")
                window.append_points([make_point("BR1","Sao Paulo",-46.63,-23.55)])
                window.navigation.setCurrentRow(0)
                check(window.selected_stations()[0]["station_key"]==state["station"] and window.yearly.isChecked(),"Station draft restored after tool switch")
                window.navigation.setCurrentRow(2)
                check(not window.selected_stations(),"Raster wizard owns independent inputs")
                window.append_points([make_point("BR%02d"%i,"Brazil site %d"%i,-46.63+dx,-23.55+dy,
                    attributes={"T_Annual_Mean":20+i}) for i,(dx,dy) in enumerate(((0,0),(.1,0),(0,.1),(.1,.1)))])
                window.analysis_crs.setCurrentText("EPSG:32723");window.cell_size.setValue(2000)
                window.folder.setText(str(folder));window.project_name.setText("Brazil_Atlas_QA")
                window.run_active.click();state["stage"]=1
            elif stage==1:
                output=window.last_output
                check(output is not None and (output/"Project.gdb").is_dir(),"Run-tool button generated FileGDB")
                check((output/"Project.gpkg").is_file(),"Run-tool button generated GeoPackage")
                manifest=json.loads((output/"manifest.json").read_text(encoding="utf-8"))
                check(manifest["status"]=="complete","Raster wizard worker completed without partial failures")
                check(all(secret_fixture.encode() not in p.read_bytes() for p in (folder/".mirsad-jobs").rglob("*") if p.is_file()),
                      "Credentials crossed the worker pipe without entering job files or logs")
                state["xlsx"]=next(output.rglob("*.xlsx"));state["xlsx_hash"]=hashlib.sha256(state["xlsx"].read_bytes()).hexdigest()
                window.request_preview(dict(path=str(state["xlsx"])));state["stage"]=2
            elif stage==2:
                check(window.preview_table.table.model().rowCount()>0,"Excel preview loaded inside the application")
                window.grab().save(str(report.with_name("workspace_excel.png")))
                check(hashlib.sha256(state["xlsx"].read_bytes()).hexdigest()==state["xlsx_hash"],"Excel source remains byte-identical")
                window.request_preview(dict(path=str(window.last_output/"Project.gpkg"),layer="Input_Climate"));state["stage"]=3
            elif stage==3:
                check(window.preview_table.table.model().rowCount()==4,"GeoPackage attribute preview returned four sites")
                check(bool(window.map.canvas.display_layers),"Preview layer appears without replacing tool inputs")
                window.open_pdf_preview(next(window.last_output.rglob("*.pdf")))
                state["stage"]=4
            elif stage==4:
                check(window.pdf_view.page_count>0 and not window.pdf_view.image.isNull(),"PDF atlas displayed inside the application")
                window.grab().save(str(report.with_name("workspace_pdf.png")))
                window.inspect_path(next(window.last_output.rglob("*.tif")));state["stage"]=5
            else:
                check(any(v["kind"]=="raster" for v in window.map.canvas.display_layers.values()),"Generated GeoTIFF displayed on shared map")
                window.inspector.setCurrentIndex(2);window.viewer_tabs.setCurrentIndex(0)
                window.grab().save(str(report.with_name("workspace_map.png")))
                window.map.basemap.setChecked(True);window.map.show_basemaps()
                QApplication.sendEvent(window.map.gallery,QEvent(QEvent.WindowDeactivate))
                check(window.map.gallery.isVisible(),"Basemap panel survives screenshot focus loss")
                window.map.gallery.choose(window.map.gallery.names[-1])
                check(not window.map.gallery.isVisible(),"Choosing a basemap dismisses the transient panel")
                window.show_help();guide=window.help_dialog
                for language in ("ar","en"):
                    guide.language.setCurrentIndex(guide.language.findData(language))
                    check(len(guide.topics)>=15,"Bundled guide has all core topics in "+language)
                    guide.open_topic('providers')
                    text=guide.browser.toPlainText()
                    check(all(year in text for year in ("1929","1940","1950","1981","1984","2001")),
                          "Bundled guide includes provider coverage in "+language)
                guide.open_topic('providers')
                guide.grab().save(str(report.with_name("workspace_guide.png")))
                guide.close()
                from .dialogs import CrsSelectionDialog
                picker=CrsSelectionDialog("EPSG:32723",window);picker.show();app.processEvents()
                check([picker.crs_tree.topLevelItem(i).text(0) for i in range(4)]==[
                    "Favorites","Layers","Geographic Coordinate System","Projected Coordinate System"],
                    "CRS browser opens with Favorites, Layers and native coordinate-system groups")
                check(any(layer.get("crs")=="EPSG:32723" for layer in picker.layer_sources),
                      "CRS browser reads the real projected CRS from the loaded GeoPackage layer")
                check(picker.select_initial_crs("EPSG:32723"),"Native UTM definition is selectable in packaged CRS browser")
                parent=picker.crs_tree.currentItem().parent();path=[]
                while parent:path.insert(0,parent.text(0));parent=parent.parent()
                check(path==["Projected Coordinate System","UTM","WGS 1984","Southern Hemisphere"],
                      "Packaged UTM uses the native WGS 1984 / Southern Hemisphere path")
                picker.grab().save(str(report.with_name("workspace_crs.png")))
                picker.catalogue_toggle.setChecked(True)
                check(picker.crs_tree.topLevelItem(3).child(10).text(0)=="UTM",
                      "Additional Esri definitions retain the native taxonomy")
                picker.close()
                finish(True);return
            QTimer.singleShot(250,step)
        except Exception as exc:
            errors.append(str(exc));finish(False)
    QTimer.singleShot(300,step)
