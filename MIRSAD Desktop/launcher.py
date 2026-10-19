"""The single application entry point, also used for packaged diagnostics."""
import argparse
import json
import sys
import tempfile
import traceback
from pathlib import Path

if not getattr(sys, "frozen", False):
    root = Path(__file__).resolve().parent
    sys.path.insert(0, str(root / "src"))
    venv_site = root / ".venv" / "Lib" / "site-packages"
    if venv_site.exists() and str(venv_site) not in sys.path:
        sys.path.insert(1, str(venv_site))


def diagnostics():
    import pyogrio
    from mirsad_desktop import __version__
    from mirsad_desktop.catalogue import Catalogue
    catalogue = Catalogue()
    return dict(version=__version__, frozen=bool(getattr(sys,"frozen",False)),
                catalogue=catalogue.metadata(), catalogue_file_hash=catalogue.digest(),
                gdal=pyogrio.__gdal_version_string__, drivers={key:pyogrio.list_drivers().get(key) for key in ("GPKG","OpenFileGDB")},
                executable=sys.executable, python_paths=sys.path, arcpy_imported="arcpy" in sys.modules)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--diagnostics", metavar="JSON")
    parser.add_argument("--self-test", metavar="JSON")
    parser.add_argument("--ui-smoke", metavar="PNG")
    parser.add_argument("--run-job",metavar="REQUEST_JSON")
    parser.add_argument("--ui-export-test",metavar="JSON")
    parser.add_argument("--ui-workspace-test",metavar="JSON")
    parser.add_argument("--user-guide",action="store_true",help="Open the offline help centre without the map workspace")
    parser.add_argument("--help-topic",default="start")
    parser.add_argument("--language",choices=("ar","en"),default="en")
    parser.add_argument("--help-test",metavar="JSON")
    args = parser.parse_args()
    if args.ui_export_test:
        args.ui_smoke=str(Path(args.ui_export_test).with_suffix(".png"))
    if args.ui_workspace_test:
        args.ui_smoke=str(Path(args.ui_workspace_test).with_suffix(".png"))
    def trace(stage):
        if args.ui_smoke:
            path = Path(args.ui_smoke).with_suffix(".startup.log")
            path.parent.mkdir(parents=True,exist_ok=True)
            with path.open("a",encoding="utf-8") as handle: handle.write(stage+"\n")
    try:
        if args.user_guide or args.help_test:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import QTimer
            from mirsad_desktop.userguide import UserGuideDialog
            from mirsad_desktop.themes import apply_application_theme
            app=QApplication(sys.argv[:1]);app.setApplicationName('MIRSAD Desktop');app.setOrganizationName('MIRSAD')
            apply_application_theme(app,False)
            guide=UserGuideDialog(args.language=='ar',topic=args.help_topic);guide.show()
            if args.help_test:
                def verify_help():
                    report={"passed":False}
                    try:
                        target=Path(args.help_test);target.parent.mkdir(parents=True,exist_ok=True)
                        guide.grab().save(str(target.with_suffix('.png')))
                        guide.export_pdf(target.with_suffix('.pdf'))
                        report.update(passed=True,topic=guide.current_topic,language=guide.language.currentData(),
                            topics=len(guide.topics),map_imported='mirsad_desktop.mapview' in sys.modules,
                            arcpy_imported='arcpy' in sys.modules)
                        if report['map_imported'] or report['arcpy_imported']:report['passed']=False
                    except Exception as error:report['error']=str(error)
                    Path(args.help_test).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');app.quit()
                QTimer.singleShot(700,verify_help)
            return app.exec()
        if args.run_job:
            from mirsad_desktop.jobs import run_request
            return run_request(args.run_job)
        if args.diagnostics or args.self_test:
            report = diagnostics()
            if args.self_test:
                from mirsad_desktop.catalogue import Catalogue
                from mirsad_desktop.exports import export_project
                target = Path(args.self_test).resolve()
                target.parent.mkdir(parents=True,exist_ok=True)
                with tempfile.TemporaryDirectory(prefix="mirsad_selftest_",dir=target.parent) as folder:
                    stations = Catalogue().stations("EG")[:3]
                    output,manifest = export_project(stations,folder,"Readback_QA",Catalogue().metadata())
                    if manifest["status"] != "complete":
                        raise RuntimeError(json.dumps(manifest["errors"]))
                    report["export_self_test"] = manifest
                    # Exercise the scientific/raster stack from the executable,
                    # not just the Python environment that built it.
                    from mirsad_desktop.inputs import make_point,import_points
                    from mirsad_desktop.analysis import run_existing_project
                    from mirsad_desktop.registry import MODULES
                    from mirsad_desktop.science import compute_point_fields
                    monthly={p:{(2024,m):v for m in range(1,13)} for p,v in
                        {"T2M":25,"T2M_MAX":30,"T2M_MIN":20,"PRECTOTCORR":10,"PS":100,"SLP":101,
                         "RH2M":60,"T2MDEW":16,"TS":28,"WS10M":3,"WD10M":350,"CLOUD_AMT":40,
                         "ALLSKY_SFC_SW_DWN":18,"ALLSKY_SFC_UV_INDEX":2}.items()}
                    calculated=compute_point_fields(monthly,[2024],[m.name for m in MODULES],"Daily",precip_totals=True,gap_method="none")
                    if len(calculated)<300 or calculated["PS_Annual_Mean"]!=1000:raise RuntimeError("Scientific kernel self-test failed")
                    csv=Path(folder)/"own_points.csv"
                    csv.write_text("ID,Name,X,Y,T_Annual_Mean\n001,My point,31,30,25\n",encoding="utf-8")
                    if import_points(csv,"X","Y","ID","Name")[0]["usaf"]!="001":raise RuntimeError("User point import failed")
                    points=[make_point(str(i),"QA "+str(i),31+dx,30+dy,attributes={"T_Annual_Mean":20+i})
                            for i,(dx,dy) in enumerate(((0,0),(.1,0),(0,.1),(.1,.1)))]
                    _,atlas=run_existing_project(points,folder,"Raster_QA",Catalogue().metadata(),
                                                 ["T_Annual_Mean"],cell_size=2000,crs="EPSG:32636")
                    if atlas["status"]!="complete":raise RuntimeError(json.dumps(atlas["errors"]))
                    report["workspace_self_test"]={"modules":len(MODULES),"calculated_fields":len(calculated),"user_import":"passed","raster_atlas":atlas}
            Path(args.diagnostics or args.self_test).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
            return 0
        trace("Import QtWidgets")
        from PySide6.QtWidgets import QApplication
        trace("Import QtCore")
        from PySide6.QtCore import QTimer
        trace("Import application UI")
        from mirsad_desktop.ui import MainWindow
        trace("Create QApplication")
        app = QApplication(sys.argv[:1])
        slot_errors=[]
        def qt_exception(kind,value,tb):
            slot_errors.append("".join(traceback.format_exception(kind,value,tb)))
            error_file=Path(args.ui_smoke).with_suffix(".error.txt") if args.ui_smoke else Path.home()/"MIRSAD_runtime_error.txt"
            error_file.write_text("\n".join(slot_errors),encoding="utf-8")
            if sys.stderr:traceback.print_exception(kind,value,tb)
        sys.excepthook=qt_exception
        app.setApplicationName("MIRSAD Desktop")
        app.setOrganizationName("MIRSAD")
        trace("Create main window")
        window = MainWindow()
        trace("Show main window")
        window.show()
        ui_fixture=None
        if args.ui_workspace_test:
            from mirsad_desktop.ui_acceptance import schedule
            schedule(window,app,args.ui_workspace_test,slot_errors)
        elif args.ui_export_test:
            import time
            from mirsad_desktop.inputs import make_point
            ui_fixture=tempfile.TemporaryDirectory(prefix="ui_export_",dir=Path(args.ui_export_test).parent)
            window.folder.setText(ui_fixture.name);window.project_name.setText("UI_Worker_QA");window.crs.setCurrentText("EPSG:32636")
            window.append_points([make_point("00"+str(i),"Own point "+str(i),31+dx,30+dy)
                                  for i,(dx,dy) in enumerate(((0,0),(.1,0),(0,.1),(.1,.1)))])
            ui_errors=[];window.on_error=ui_errors.append
            started=time.monotonic()
            def check_export():
                if window.job_thread and time.monotonic()-started<75:
                    QTimer.singleShot(100,check_export);return
                if window.job_thread:
                    window.job_thread.process.kill();window.job_thread.process.waitForFinished(3000)
                    ui_errors.append("UI export worker timed out")
                passed=bool(window.last_output and (window.last_output/"manifest.json").is_file() and not ui_errors)
                manifest=json.loads((window.last_output/"manifest.json").read_text(encoding="utf-8")) if passed else None
                passed=passed and manifest["status"]=="complete"
                if not passed:slot_errors.append("Frozen UI worker test failed: "+str(ui_errors))
                Path(args.ui_export_test).write_text(json.dumps({"passed":passed,"errors":ui_errors,"manifest":manifest},ensure_ascii=False,indent=2),encoding="utf-8")
                window.grab().save(args.ui_smoke);app.quit()
            def start_export():
                window.export.click();QTimer.singleShot(100,check_export)
            QTimer.singleShot(300,start_export)
        elif args.ui_smoke:
            def capture():
                trace("Capture window")
                Path(args.ui_smoke).parent.mkdir(parents=True,exist_ok=True)
                window.grab().save(args.ui_smoke)
                trace("Saved screenshot")
                app.quit()
            QTimer.singleShot(1800,capture)
        trace("Enter event loop")
        result=app.exec()
        if ui_fixture:ui_fixture.cleanup()
        return 1 if slot_errors else result
    except Exception:
        report_path = Path(args.diagnostics or args.self_test or (str(Path(args.ui_smoke).with_suffix(".error.txt")) if args.ui_smoke else Path.home()/"MIRSAD_startup_error.txt"))
        report_path.write_text(traceback.format_exc(),encoding="utf-8")
        if sys.stderr:
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
