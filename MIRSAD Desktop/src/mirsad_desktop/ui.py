"""Map-centred MIRSAD workspace: stations, own points and climate atlases."""
import datetime as dt
import json
import os
import time
from pathlib import Path
from PySide6.QtCore import Qt,QDate,QTimer,QSettings
from PySide6.QtGui import QIcon,QPixmap,QShortcut,QKeySequence
from PySide6.QtWidgets import (QApplication,QCheckBox,QComboBox,QDateEdit,QDialog,QFileDialog,QFormLayout,
 QFrame,QGridLayout,QGroupBox,QHBoxLayout,QHeaderView,QLabel,QLineEdit,QListWidget,QListWidgetItem,QMainWindow,QMessageBox,
 QPlainTextEdit,QProgressBar,QPushButton,QScrollArea,QSpinBox,QDoubleSpinBox,QSplitter,QStackedWidget,
 QTableWidget,QTableWidgetItem,QTreeWidget,QTreeWidgetItem,QVBoxLayout,QWidget,QInputDialog,QSizePolicy,QTextBrowser,QMenu)
from . import __version__,runtime_channel
from .catalogue import Catalogue,asset_dir
from .exports import export_project
from .services import run_climate_project
from .registry import MODULES,BY_NAME,unavailable
from .climate_sources import point_providers,resolution_options,canonical_resolution,ERA5_MODELS,uses_reanalysis,NOAA_ONLY,ERA5_ONLY
from .mapview import MapPanel
from .themes import stylesheet,apply_application_theme
from .inputs import filter_boundary,read_boundary,vector_layers,grid_points
from .dialogs import ImportDialog,PointDialog,GisAddDataDialog,CrsSelectionDialog
from .crs import COMMON_CRS_LIST,validate_and_describe_crs
from .analysis import METHODS,numeric_fields,run_existing_project
from .process_worker import ProcessWorker
from .workspace import WorkspaceMixin
from .i18n import tr

def scroll_page(widget):
    scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(widget);return scroll

class MainWindow(WorkspaceMixin,QMainWindow):
    def __init__(self):
        super().__init__()
        self.catalogue=Catalogue();self.meta=self.catalogue.metadata();self.settings=QSettings("MIRSAD","Desktop")
        if os.environ.get("MIRSAD_TEST_SETTINGS"):
            self.settings=QSettings(os.environ["MIRSAD_TEST_SETTINGS"],QSettings.IniFormat)
        from .widgets import CompactControls
        app=QApplication.instance()
        if not hasattr(app,"compact_controls"):
            app.compact_controls=CompactControls(app);app.installEventFilter(app.compact_controls)
        self.arabic=self.settings.value("arabic",False,type=bool);self.dark=self.settings.value("dark",True,type=bool)
        self.selected_keys=set();self.current_rows=[];self.user_points={};self.generated_points={}
        self.boundary=None;self.job_thread=None;self.last_output=None;self.started_at=None;self.stage_ranges={}
        self.setWindowTitle("مرصاد | MIRSAD Desktop — "+runtime_channel().title())
        self.setWindowIcon(QIcon(str(asset_dir()/"mirsad-favicon.svg")))
        self.setAttribute(Qt.WA_DeleteOnClose,True)
        screen=QApplication.primaryScreen().availableGeometry()
        self.resize(min(1500,screen.width()-50),min(960,screen.height()-65));self.setMinimumSize(800,480)
        self.build_shell()
        for label in self.inspector.findChildren(QLabel):
            label.setWordWrap(True);label.setMinimumWidth(0)
            label.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        self.clock=QTimer(self);self.clock.setInterval(1000);self.clock.timeout.connect(self.tick)
        self.region.currentIndexChanged.connect(self.fill_countries);self.country.currentIndexChanged.connect(self.fill_stations)
        self.search.textChanged.connect(self.fill_stations);self.input_mode.currentIndexChanged.connect(self.mode_changed)
        self.restrict_boundary.toggled.connect(self.fill_stations);self.table.itemChanged.connect(self.checked)
        self.map.canvas.pointClicked.connect(self.map_selection);self.map.canvas.coordinatePicked.connect(self.add_map_point)
        self.provider.currentTextChanged.connect(self.update_modules)
        self.translate();self.apply_theme();self.update_modules();self.navigation.setCurrentRow(0)
        self.help_shortcut=QShortcut(QKeySequence("F1"),self);self.help_shortcut.activated.connect(self.show_help)
        self.add_shortcut=QShortcut(QKeySequence("Ctrl+O"),self);self.add_shortcut.activated.connect(self.add_data)

    def t(self,arabic,english):return arabic if self.arabic else english
    def get_clean_crs(self,combo):
        code=combo.currentData()
        text=combo.currentText().strip()
        if code and text==combo.itemText(combo.currentIndex()):return str(code).strip()
        if " — " in text:text=text.split(" — ")[0].strip()
        return text
    def set_combo_crs(self,combo,crs_code):
        idx=combo.findData(crs_code)
        if idx>=0:combo.setCurrentIndex(idx)
        else:
            desc=validate_and_describe_crs(crs_code)
            label=f"{crs_code} — {desc.get('name',crs_code)}" if desc.get("valid") else crs_code
            combo.insertItem(0,label,crs_code);combo.setCurrentIndex(0)
    def choose_crs_dialog(self,combo):
        current=self.get_clean_crs(combo) or "EPSG:4326"
        dialog=CrsSelectionDialog(current_crs=current,parent=self)
        if dialog.exec()==QDialog.Accepted and dialog.selected_crs:
            self.set_combo_crs(combo,dialog.selected_crs)

    def setup_map(self):
        page=QWidget();box=QHBoxLayout(page);box.setContentsMargins(0,0,0,0)
        controls=QWidget();formbox=QVBoxLayout(controls);formbox.setContentsMargins(8,4,8,4)
        self.input_title=QLabel();self.input_title.setObjectName("section");formbox.addWidget(self.input_title)
        self.input_mode=QComboBox()
        for title,code in ((tr("mode_stations", self.arabic),"stations"),(tr("mode_user", self.arabic),"user"),(tr("mode_combined", self.arabic),"combined"),(tr("mode_grid", self.arabic),"grid")):self.input_mode.addItem(title,code)
        formbox.addWidget(self.input_mode)
        group=QGroupBox();self.station_group=group;form=QVBoxLayout(group);self.region=QComboBox()
        self.country=QComboBox();self.search=QLineEdit()
        for widget in (self.region,self.country,self.search):form.addWidget(widget)
        formbox.addWidget(group)
        group=QGroupBox();self.own_group=group;buttons=QVBoxLayout(group)
        self.point_layer_combo=QComboBox()
        self.point_layer_combo.currentIndexChanged.connect(self.point_layer_selected)
        self.import_button=QPushButton();self.import_button.clicked.connect(self.import_dialog)
        self.manual_button=QPushButton();self.manual_button.clicked.connect(self.manual_point)
        self.input_summary=QLabel();self.input_summary.setWordWrap(True);self.input_summary.setObjectName("muted")
        for widget in (self.point_layer_combo,self.import_button,self.manual_button,self.input_summary):buttons.addWidget(widget)
        formbox.addWidget(group)
        group=QGroupBox();self.boundary_group=group;boundarybox=QVBoxLayout(group)
        self.boundary_combo=QComboBox()
        self.boundary_combo.currentIndexChanged.connect(self.boundary_layer_selected)
        self.boundary_button=QPushButton();self.boundary_button.clicked.connect(self.load_boundary)
        self.download_extent_button=QPushButton("Download extent (AOI) / نطاق التنزيل")
        self.download_extent_button.clicked.connect(self.load_download_extent)
        self.download_extent_summary=QLabel("—");self.download_extent_summary.setWordWrap(True)
        boundarybox.addWidget(self.download_extent_button);boundarybox.addWidget(self.download_extent_summary)
        self.boundary_summary=QLabel();self.boundary_summary.setWordWrap(True)
        self.restrict_boundary=QCheckBox()
        self.grid_spacing_label=QLabel()
        self.grid_spacing=QSpinBox();self.grid_spacing.setRange(1000,500000);self.grid_spacing.setValue(50000);self.grid_spacing.setSuffix(" m")
        self.grid_button=QPushButton();self.grid_button.clicked.connect(self.generate_grid)
        for widget in (self.boundary_combo,self.boundary_button,self.boundary_summary,self.restrict_boundary,self.grid_spacing_label,self.grid_spacing,self.grid_button):boundarybox.addWidget(widget)
        formbox.addWidget(group);formbox.addStretch()
        controls.setStyleSheet("QWidget {background:transparent;}")
        for widget in controls.findChildren(QComboBox):
            widget.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon);widget.setMinimumContentsLength(10)
            widget.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Fixed);widget.setMinimumWidth(0)
        for widget in controls.findChildren(QPushButton):widget.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Fixed);widget.setMinimumWidth(0)
        controls_scroll=scroll_page(controls);controls_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);controls_scroll.setMinimumWidth(260);controls_scroll.setMaximumWidth(300);box.addWidget(controls_scroll);self.map_controls=controls_scroll
        content=QWidget();self.map_content=content;right=QVBoxLayout(content);right.setContentsMargins(0,0,0,0);self.map=MapPanel();self.preview=self.map.canvas
        self.table=QTableWidget(0,7);self.table.setAlternatingRowColors(True);self.table.setSelectionBehavior(QTableWidget.SelectRows);self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False);self.table.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
        for col in (0,2,3,4,5,6):self.table.horizontalHeader().setSectionResizeMode(col,QHeaderView.ResizeToContents)
        self.table.setMinimumHeight(60);split=QSplitter(Qt.Vertical);split.setHandleWidth(6);split.addWidget(self.map);split.addWidget(self.table);split.setSizes([540,180]);right.addWidget(split,1)
        bar=QHBoxLayout();self.count=QLabel();self.all=QPushButton();self.none=QPushButton()
        self.all.clicked.connect(lambda:self.select_visible(True));self.none.clicked.connect(lambda:self.select_visible(False))
        bar.addWidget(self.count,1);bar.addWidget(self.all);bar.addWidget(self.none);right.addLayout(bar);box.addWidget(content,1);self.pages.addWidget(page)

    def setup_climate(self):
        page=QWidget();box=QVBoxLayout(page);self.climate_title=QLabel();self.climate_title.setObjectName("heading");self.climate_title.setWordWrap(True);box.addWidget(self.climate_title)
        self.climate_note=QLabel();self.climate_note.setWordWrap(True);box.addWidget(self.climate_note)
        top=QVBoxLayout();group=QGroupBox();self.download_group=group;form=QFormLayout(group);form.setRowWrapPolicy(QFormLayout.WrapAllRows)
        self.provider=QComboBox();self.provider.addItems(point_providers(stations=True))
        self.om_model=QComboBox();self.om_model.addItems(ERA5_MODELS)
        self.om_model.setParent(page);self.om_model.hide()
        self.resolution_button=QPushButton();self.resolution_button.clicked.connect(self.choose_resolution)
        self.resolution_preview=QLabel();self.resolution_preview.setWordWrap(True);self.resolution_preview.setObjectName("muted")
        self.start=QDateEdit(QDate(2024,1,1));self.end=QDateEdit(QDate(2024,12,31))
        for field in (self.start,self.end):field.setCalendarPopup(True);field.setDisplayFormat("yyyy-MM-dd")
        self.gap=QComboBox()
        self.workflow=QComboBox()
        self.lbl_provider=QLabel();self.lbl_om_model=QLabel();self.lbl_start=QLabel();self.lbl_end=QLabel();self.lbl_gap=QLabel();self.lbl_workflow=QLabel()
        for label,widget in ((self.lbl_provider,self.provider),(self.lbl_om_model,self.resolution_button),(self.lbl_start,self.start),(self.lbl_end,self.end),(self.lbl_gap,self.gap),(self.lbl_workflow,self.workflow)):form.addRow(label,widget)
        form.insertRow(2,self.resolution_preview)
        self.source_credentials=QGroupBox("Need Sign In")
        auth_form=QFormLayout(self.source_credentials);auth_form.setRowWrapPolicy(QFormLayout.WrapAllRows)
        self.source_username=QLineEdit();self.source_password=QLineEdit();self.source_token=QLineEdit()
        self.source_password.setEchoMode(QLineEdit.Password);self.source_token.setEchoMode(QLineEdit.Password)
        self.source_username_label=QLabel();self.source_password_label=QLabel();self.source_token_label=QLabel()
        for label,field in ((self.source_username_label,self.source_username),(self.source_password_label,self.source_password),(self.source_token_label,self.source_token)):auth_form.addRow(label,field)
        self.source_auth_note=QLabel();self.source_auth_note.setWordWrap(True);auth_form.addRow(self.source_auth_note)
        form.addRow(self.source_credentials)
        self.crs=QComboBox();self.crs.setEditable(True)
        for code,desc in COMMON_CRS_LIST:self.crs.addItem(f"{code} — {desc}",code)
        self.crs_btn=QPushButton("🌐");self.crs_btn.setToolTip("Browse Coordinate Systems");self.crs_btn.setFixedWidth(36)
        self.crs_btn.clicked.connect(lambda:self.choose_crs_dialog(self.crs))
        crs_bar=QHBoxLayout();crs_bar.addWidget(self.crs,1);crs_bar.addWidget(self.crs_btn)
        self.lbl_crs=QLabel()
        form.addRow(self.lbl_crs,crs_bar)
        self.units=QComboBox();self.units.addItems(["Metric","Imperial"]);self.lbl_units=QLabel();form.addRow(self.lbl_units,self.units)
        self.unit_group=QGroupBox("Individual units / وحدات العناصر")
        self.unit_group.setCheckable(True);self.unit_group.setChecked(False)
        unit_form=QFormLayout(self.unit_group);unit_form.setRowWrapPolicy(QFormLayout.WrapAllRows)
        self.unit_controls={}
        for key,label,choices in (
            ("unit_temp","Temperature / الحرارة",["Celsius","Fahrenheit","Kelvin"]),
            ("unit_precip","Precipitation / الأمطار",["Millimeters (mm)","Inches (in)"]),
            ("unit_press","Pressure / الضغط",["hPa","kPa","inHg"]),
            ("unit_wind","Wind / الرياح",["m/s","km/h","Knots (kt)","mph"]),
            ("unit_solar","Solar radiation / الإشعاع",["kWh/m2/day","MJ/m2/day","Wh/m2/day","cal/cm2/day"])):
            combo=QComboBox();combo.addItem("System default / الافتراضي",None)
            for choice in choices:combo.addItem(choice,choice)
            self.unit_controls[key]=combo;unit_form.addRow(label,combo)
        form.addRow(self.unit_group)
        self.scopes={
            "Annual":QCheckBox("Annual"),
            "Winter":QCheckBox("Winter (DJF)"),
            "Spring":QCheckBox("Spring (MAM)"),
            "Summer":QCheckBox("Summer (JJA)"),
            "Autumn":QCheckBox("Autumn (SON)")
        }
        scopebar=QGridLayout()
        for index,checkbox in enumerate(self.scopes.values()):checkbox.setChecked(True);scopebar.addWidget(checkbox,index//2,index%2)
        self.lbl_summaries=QLabel()
        form.addRow(self.lbl_summaries,scopebar)
        self.monthly_ranges=QCheckBox();self.daily=QCheckBox();self.daily.setChecked(True);self.yearly=QCheckBox()
        self.monthly_rasters_cb=QCheckBox()
        for checkbox in (self.monthly_ranges,self.daily,self.yearly,self.monthly_rasters_cb):form.addRow(checkbox)
        top.addWidget(group,1);group=QGroupBox();self.modules_group=group;modulesbox=QVBoxLayout(group)
        self.module_tree=QTreeWidget();self.module_tree.setColumnWidth(0,245);self.module_items={}
        self.module_cat_items={}
        for category,code in (("primary","primary_elements"),("derived","derived_models")):
            parent=QTreeWidgetItem(self.module_tree,[code]);parent.setExpanded(True);self.module_cat_items[category]=parent
            for module in MODULES:
                if module.group!=category:continue
                item=QTreeWidgetItem(parent,[module.name,module.unit]);item.setFlags(item.flags()|Qt.ItemIsUserCheckable)
                item.setCheckState(0,Qt.Unchecked);self.module_items[module.name]=item
        modulesbox.addWidget(self.module_tree);modulesbar=QHBoxLayout();self.select_modules_btn=QPushButton();self.clear_modules_btn=QPushButton()
        self.select_modules_btn.clicked.connect(lambda:self.check_modules(True));self.clear_modules_btn.clicked.connect(lambda:self.check_modules(False))
        modulesbar.addWidget(self.select_modules_btn);modulesbar.addWidget(self.clear_modules_btn);modulesbox.addLayout(modulesbar)
        self.modules_note=QLabel();self.modules_note.setWordWrap(True);self.modules_note.setObjectName("muted");modulesbox.addWidget(self.modules_note);top.addWidget(group,1);box.addLayout(top,1)
        self.download_button=QPushButton();self.download_button.setObjectName("primary");self.download_button.clicked.connect(self.download_climate);box.addWidget(self.download_button)
        for combo in page.findChildren(QComboBox):
            combo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon);combo.setMinimumContentsLength(10)
            combo.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Fixed);combo.setMinimumWidth(0)
        self.pages.addWidget(scroll_page(page))
        self.start.dateChanged.connect(self.update_resolution_preview);self.end.dateChanged.connect(self.update_resolution_preview)
        self.module_tree.itemChanged.connect(self.update_resolution_preview)
        self.om_model.currentTextChanged.connect(self.update_resolution_preview)

    def setup_analysis(self):
        page=QWidget();box=QVBoxLayout(page);self.raster_title=QLabel();self.raster_title.setObjectName("section");self.raster_title.setWordWrap(True);box.addWidget(self.raster_title)
        self.raster_subtitle=QLabel();self.raster_subtitle.setWordWrap(True);box.addWidget(self.raster_subtitle)
        group=QGroupBox();self.analysis_group=group;form=QFormLayout(group);form.setRowWrapPolicy(QFormLayout.WrapAllRows);self.method=QComboBox();self.method.addItems(METHODS)
        self.analysis_crs=QComboBox();self.analysis_crs.setEditable(True)
        for code,desc in COMMON_CRS_LIST:self.analysis_crs.addItem(f"{code} — {desc}",code)
        idx=self.analysis_crs.findData("EPSG:6933")
        if idx>=0:self.analysis_crs.setCurrentIndex(idx)
        self.analysis_crs_btn=QPushButton("🌐");self.analysis_crs_btn.setToolTip("Browse Coordinate Systems");self.analysis_crs_btn.setFixedWidth(36)
        self.analysis_crs_btn.clicked.connect(lambda:self.choose_crs_dialog(self.analysis_crs))
        analysis_crs_bar=QHBoxLayout();analysis_crs_bar.addWidget(self.analysis_crs,1);analysis_crs_bar.addWidget(self.analysis_crs_btn)
        self.cell_size=QSpinBox();self.cell_size.setRange(100,500000);self.cell_size.setValue(10000);self.cell_size.setSuffix(" m")
        self.power=QDoubleSpinBox();self.power.setRange(.5,8);self.power.setValue(2);self.neighbours=QSpinBox();self.neighbours.setRange(3,64);self.neighbours.setValue(12)
        self.reclass_en=QCheckBox();self.reclass_method=QComboBox();self.reclass_method.addItems(["Natural Breaks (Jenks)","Equal Interval","Quantile"])
        self.reclass_classes=QSpinBox();self.reclass_classes.setRange(2,16);self.reclass_classes.setValue(5)
        self.pdf=QCheckBox();self.pdf.setChecked(True)
        self.lbl_method=QLabel();self.lbl_analysis_crs=QLabel();self.lbl_cell_size=QLabel();self.lbl_power=QLabel();self.lbl_neighbours=QLabel()
        self.lbl_reclass_meth=QLabel();self.lbl_reclass_cnt=QLabel()
        for label,widget in ((self.lbl_method,self.method),(self.lbl_analysis_crs,analysis_crs_bar),(self.lbl_cell_size,self.cell_size),(self.lbl_power,self.power),(self.lbl_neighbours,self.neighbours)):form.addRow(label,widget)
        form.addRow(self.reclass_en)
        form.addRow(self.lbl_reclass_meth,self.reclass_method)
        form.addRow(self.lbl_reclass_cnt,self.reclass_classes)
        form.addRow(self.pdf);box.addWidget(group);self.raster_fields=QListWidget();self.raster_fields.setMinimumHeight(150)
        self.raster_fields_label=QLabel();box.addWidget(self.raster_fields_label);box.addWidget(self.raster_fields,1)
        self.analysis_button=QPushButton();self.analysis_button.setObjectName("primary");self.analysis_button.clicked.connect(self.analyse_existing);box.addWidget(self.analysis_button)
        self.lbl_formats_note=QLabel("GeoTIFF + GDB + GeoPackage + Excel + PDF · Leave-one-out RMSE / Bias");box.addWidget(self.lbl_formats_note);self.pages.addWidget(scroll_page(page))

    def setup_data(self):
        page=QWidget();box=QVBoxLayout(page);self.data_title=QLabel();self.data_title.setObjectName("heading");box.addWidget(self.data_title)
        self.data_note=QLabel();self.data_note.setWordWrap(True);box.addWidget(self.data_note)
        self.import_pts_btn=QPushButton();self.import_pts_btn.clicked.connect(self.import_dialog);box.addWidget(self.import_pts_btn)
        self.data_details=QPlainTextEdit();self.data_details.setReadOnly(True);box.addWidget(self.data_details,1);self.pages.addWidget(page)
    def setup_tasks(self):
        page=QWidget();box=QVBoxLayout(page);self.tasks_title=QLabel();self.tasks_title.setObjectName("heading");box.addWidget(self.tasks_title)
        self.log=QPlainTextEdit();self.log.setReadOnly(True);self.log.setMaximumBlockCount(3000);box.addWidget(self.log,1);self.pages.addWidget(page)
    def setup_about(self):
        page=QWidget();box=QVBoxLayout(page);label=QLabel("مرصاد | MIRSAD Desktop");label.setObjectName("heading");box.addWidget(label)
        developer=QLabel('Ahmad Ibrahim | أحمد إبراهيم<br><a href="https://github.com/ahmadibrahim4geo/MIRSAD">github.com/ahmadibrahim4geo/MIRSAD</a><br>ahmadibrahim.geo@gmail.com · MIT License');developer.setOpenExternalLinks(True);box.addWidget(developer)
        self.about_note=QLabel();self.about_note.setWordWrap(True);box.addWidget(self.about_note)
        import pyogrio
        self.diagnostics=QPlainTextEdit();self.diagnostics.setReadOnly(True);self.diagnostics.setPlainText(json.dumps(dict(version=__version__,developer="Ahmad Ibrahim",channel=runtime_channel(),catalogue=self.meta,
            modules=len(MODULES),GDAL=pyogrio.__gdal_version_string__,ArcGIS_required=False,
            sources="NASA POWER; selected Open-Meteo model with declared NASA supplement; Hybrid prioritizes NOAA GSOD daily observations matched by USAF/WBAN/location",
            science="Reviewed legacy monthly kernel; independent raster methods need further native ArcGIS parity acceptance",
            signing="Product metadata is not a trusted digital signature"),ensure_ascii=False,indent=2));box.addWidget(self.diagnostics,1);self.pages.addWidget(page)

    def translate(self):
        self.setLayoutDirection(Qt.RightToLeft if self.arabic else Qt.LeftToRight)
        self.centralWidget().setLayoutDirection(Qt.RightToLeft if self.arabic else Qt.LeftToRight)
        self.heading.setText(tr("app_title", self.arabic))
        self.subtitle.setText(tr("app_subtitle", self.arabic) + "  |  " + __version__)
        self.language.setText("English" if self.arabic else "العربية")
        self.help_button.setText(tr("help", self.arabic))
        self.theme.setText(tr("light_mode", self.arabic) if self.dark else tr("dark_mode", self.arabic))
        if getattr(self,"help_dialog",None):self.help_dialog.apply_document_theme()
        self.add_data_button.setText("＋ " + tr("add_data", self.arabic))
        self.rebuild_add_data_menu()

        row = max(0, self.navigation.currentRow())
        self.navigation.blockSignals(True)
        self.navigation.clear()
        self.navigation.addItems([
            tr("tool_stations", self.arabic),
            tr("tool_points", self.arabic),
            tr("tool_raster", self.arabic),
            tr("nav_results", self.arabic),
            tr("nav_tasks", self.arabic),
            tr("nav_about", self.arabic)
        ])
        self.navigation.setCurrentRow(row)
        self.navigation.blockSignals(False)

        if hasattr(self, "tools_title"): self.tools_title.setText(tr("tools_heading", self.arabic))
        if hasattr(self, "contents_title"): self.contents_title.setText(tr("contents_heading", self.arabic))
        if hasattr(self, "group_layers"): self.group_layers.setText(0, tr("group_layers", self.arabic))
        if hasattr(self, "group_tables"): self.group_tables.setText(0, tr("group_tables", self.arabic))
        if hasattr(self, "results_root"): self.results_root.setText(0, tr("group_results", self.arabic))
        self.update_working_points_layer()
        self.update_boundary_layer()

        self.input_title.setText(tr("working_points_source", self.arabic))
        cur_mode = self.input_mode.currentData()
        self.input_mode.blockSignals(True)
        self.input_mode.clear()
        from .tools import BY_KEY
        spec = BY_KEY.get(getattr(self, "active_tool", "stations"))
        modes = spec.modes if spec else ["stations", "combined", "user", "grid"]
        mode_labels = {
            "stations": tr("mode_stations", self.arabic),
            "combined": tr("mode_combined", self.arabic),
            "user": tr("mode_user", self.arabic),
            "grid": tr("mode_grid", self.arabic),
            "regional": "تنزيل الشبكات الإقليمية" if self.arabic else "Regional Native Grid Download"
        }
        for m in modes:
            self.input_mode.addItem(mode_labels.get(m, m), m)
        idx = self.input_mode.findData(cur_mode)
        if idx >= 0: self.input_mode.setCurrentIndex(idx)
        self.input_mode.blockSignals(False)

        if hasattr(self, "map"):
            self.map.translate(self.arabic)

        self.station_group.setTitle(tr("station_filters", self.arabic))
        self.own_group.setTitle(tr("mode_user", self.arabic))
        self.boundary_group.setTitle(tr("study_boundary_layer", self.arabic))

        self.search.setPlaceholderText(tr("search_station_placeholder", self.arabic))
        self.import_button.setText(tr("import_point_file", self.arabic))
        self.import_button.setToolTip("SHP · FileGDB · GeoPackage · GeoJSON · Excel · CSV")
        self.manual_button.setText(tr("enter_point_coords", self.arabic))
        self.boundary_button.setText(tr("load_boundary_btn", self.arabic))
        if not getattr(self, "boundary", None):
            self.boundary_summary.setText(tr("study_boundary_layer", self.arabic) + ": " + tr("no_layers_hint", self.arabic))
        self.restrict_boundary.setText(tr("points_inside_boundary", self.arabic))
        self.grid_spacing_label.setText(tr("grid_spacing_label", self.arabic))
        self.grid_button.setText(tr("generate_grid_btn", self.arabic))
        self.all.setText(tr("select_visible", self.arabic))
        self.none.setText(tr("clear_visible", self.arabic))

        self.table.setHorizontalHeaderLabels([
            tr("col_check", self.arabic),
            tr("col_point", self.arabic),
            tr("col_usaf", self.arabic),
            tr("col_wban", self.arabic),
            tr("col_lat", self.arabic),
            tr("col_lon", self.arabic),
            tr("col_qa", self.arabic)
        ])

        # Region combo items
        region_code = self.region.currentData()
        self.region.blockSignals(True)
        self.region.clear()
        regions = [
            (tr("all_regions", self.arabic), ""),
            ("الدول العربية" if self.arabic else "Arab League", "Arab"),
            ("إفريقيا" if self.arabic else "Africa", "Africa"),
            ("آسيا" if self.arabic else "Asia", "Asia"),
            ("أوروبا" if self.arabic else "Europe", "Europe"),
            ("أمريكا الشمالية" if self.arabic else "North America", "North America"),
            ("أمريكا الجنوبية" if self.arabic else "South America", "South America"),
            ("أوقيانوسيا" if self.arabic else "Oceania", "Oceania"),
            ("القارة القطبية الجنوبية" if self.arabic else "Antarctica", "Antarctica")
        ]
        for name, code in regions:
            self.region.addItem(name, code)
        idx = self.region.findData(region_code)
        if idx >= 0: self.region.setCurrentIndex(idx)
        self.region.blockSignals(False)

        # Gap combo items
        gap_code = self.gap.currentData()
        self.gap.blockSignals(True)
        self.gap.clear()
        self.gap.addItem("متوسط الشهر المناخي (موصى به)" if self.arabic else "Climatological Month Mean (Recommended)", "climatological")
        self.gap.addItem("الاستيفاء الخطي وحدود الأطراف" if self.arabic else "Linear + Boundary Interpolation", "linear")
        self.gap.addItem("استكمال مكاني IDW من أقرب 3 محطات" if self.arabic else "Spatial IDW (up to 3 nearest stations)", "spatial")
        self.gap.addItem("بدون استكمال (إبقاء القيم المفقودة)" if self.arabic else "No Fill (Keep Missing)", "none")
        idx = self.gap.findData(gap_code)
        if idx >= 0: self.gap.setCurrentIndex(idx)
        self.gap.blockSignals(False)

        # Workflow combo items
        wf_code = self.workflow.currentData()
        self.workflow.blockSignals(True)
        self.workflow.clear()
        self.workflow.addItem("تنزيل البيانات وإنتاج الأطلس كاملاً (المسار الشامل) [الافتراضي]" if self.arabic else "Online Download & Full Processing", "atlas")
        self.workflow.addItem("استيفاء ورسم الخرائط لبيانات موجودة مسبقاً (وضع أوفلاين)" if self.arabic else "Offline: Process Existing GDB / Layers", "offline")
        self.workflow.addItem("تنزيل وحفظ بيانات النقاط فقط (تخطي الراستر)" if self.arabic else "Download Point Data Only (Skip Rasters & Atlas)", "data")
        idx = self.workflow.findData(wf_code)
        if idx >= 0: self.workflow.setCurrentIndex(idx)
        self.workflow.blockSignals(False)

        # Climate labels
        self.climate_title.setText(tr("climate_heading", self.arabic))
        self.climate_note.setText(tr("climate_note", self.arabic))
        self.download_group.setTitle(tr("tab_climate", self.arabic))
        self.lbl_provider.setText("مزود البيانات المناخية ومحرك المعالجة" if self.arabic else "Climate Data Provider & Engine")
        self.lbl_om_model.setText("الدقة المكانية للمصدر / Resolution" if self.arabic else "Resolution / Native Source Grid")
        self.lbl_start.setText(tr("date_from", self.arabic))
        self.lbl_end.setText(tr("date_to", self.arabic))
        self.lbl_gap.setText("خوارزمية سد الثغرات (Gap Fill)" if self.arabic else "Gap Fill Method")
        self.lbl_workflow.setText("نمط سير العمل والتشغيل" if self.arabic else "Workflow & Operation Mode")
        self.lbl_crs.setText(tr("output_crs", self.arabic))
        self.lbl_units.setText(tr("output_units", self.arabic))
        self.lbl_summaries.setText(tr("temporal_summaries", self.arabic))
        self.scopes["Annual"].setText("السنوي (Annual)" if self.arabic else "Annual")
        self.scopes["Winter"].setText("الشتاء (DJF)" if self.arabic else "Winter (DJF)")
        self.scopes["Spring"].setText("الربيع (MAM)" if self.arabic else "Spring (MAM)")
        self.scopes["Summer"].setText("الصيف (JJA)" if self.arabic else "Summer (JJA)")
        self.scopes["Autumn"].setText("الخريف (SON)" if self.arabic else "Autumn (SON)")
        self.monthly_rasters_cb.setText("راستر شهري (يناير–ديسمبر)" if self.arabic else "Monthly rasters (Jan–Dec)")
        self.modules_group.setTitle(tr("primary_elements", self.arabic) + " & " + tr("derived_models", self.arabic))
        self.module_tree.setHeaderLabels([tr("climate_heading", self.arabic), tr("output_units", self.arabic)])
        if "primary" in self.module_cat_items:
            self.module_cat_items["primary"].setText(0, tr("primary_elements", self.arabic))
        if "derived" in self.module_cat_items:
            self.module_cat_items["derived"].setText(0, tr("derived_models", self.arabic))
        for module in MODULES:
            if module.name in self.module_items:
                label = module.arabic if self.arabic else module.name
                self.module_items[module.name].setText(0, label)
        self.select_modules_btn.setText(tr("select_available", self.arabic))
        self.clear_modules_btn.setText(tr("clear_all", self.arabic))

        self.daily.setText(tr("include_daily", self.arabic))
        self.yearly.setText(tr("include_yearly", self.arabic))
        self.monthly_ranges.setText(tr("include_ranges", self.arabic))
        self.download_button.setText(tr("btn_run_tool", self.arabic))

        # Raster labels
        self.raster_title.setText(tr("raster_heading", self.arabic))
        self.raster_subtitle.setText(tr("raster_note", self.arabic))
        self.analysis_group.setTitle(tr("tab_raster", self.arabic))
        self.lbl_method.setText(tr("interpolation_method", self.arabic))
        self.lbl_analysis_crs.setText(tr("processing_crs", self.arabic))
        self.lbl_cell_size.setText(tr("cell_size", self.arabic))
        self.lbl_power.setText(tr("idw_power", self.arabic))
        self.lbl_neighbours.setText(tr("neighbours", self.arabic))
        self.reclass_en.setText("تفعيل إعادة تصنيف الراستر (Reclassification)" if self.arabic else "Enable Raster Reclassification")
        self.lbl_reclass_meth.setText("طريقة التصنيف" if self.arabic else "Classification Method")
        self.lbl_reclass_cnt.setText("عدد الفئات" if self.arabic else "Number of Classes")
        self.pdf.setText(tr("generate_pdf", self.arabic))
        self.raster_fields_label.setText(tr("user_fields_to_interpolate", self.arabic))
        self.analysis_button.setText(tr("run_raster_from_points", self.arabic))

        # Output panel labels
        if hasattr(self, "project_label"): self.project_label.setText(tr("project_name", self.arabic))
        if hasattr(self, "folder_label"): self.folder_label.setText(tr("output_folder", self.arabic))
        if hasattr(self, "crs_label"): self.crs_label.setText(tr("output_crs", self.arabic))
        if hasattr(self, "output_note"): self.output_note.setText(tr("output_databases_note", self.arabic))
        if hasattr(self, "enable_raster"): self.enable_raster.setText(tr("workflow_atlas", self.arabic))
        self.export.setText(tr("btn_export_points", self.arabic))
        self.cancel.setText(tr("btn_cancel", self.arabic))
        self.open_output.setText(tr("btn_open_results", self.arabic))
        self.back_step.setText(tr("btn_back_step", self.arabic))
        self.next_step.setText(tr("btn_next_step", self.arabic))
        self.run_active.setText(tr("btn_run_tool", self.arabic))

        # Data & About labels
        if hasattr(self, "data_title"): self.data_title.setText(tr("tab_input_info", self.arabic))
        if hasattr(self, "data_note"): self.data_note.setText(tr("output_databases_note", self.arabic))
        if hasattr(self, "import_pts_btn"): self.import_pts_btn.setText(tr("import_point_file", self.arabic))
        if hasattr(self, "tasks_title"): self.tasks_title.setText(tr("nav_tasks", self.arabic))
        if hasattr(self, "about_note"): self.about_note.setText(tr("about_mirsad", self.arabic, "MIRSAD Desktop GIS Platform"))

        from .tools import BY_KEY
        if hasattr(self, "active_tool") and self.active_tool in BY_KEY:
            spec = BY_KEY[self.active_tool]
            self.tool_title.setText(spec.arabic if self.arabic else spec.english)
            self.tool_note.setText(spec.description_ar if self.arabic else spec.description_en)

        tabs_inspector = [
            tr("tab_inputs", self.arabic),
            tr("tab_climate", self.arabic),
            tr("tab_raster", self.arabic),
            tr("tab_outputs", self.arabic)
        ]
        for i, text in enumerate(tabs_inspector):
            self.inspector.setTabText(i, text)

        tabs_viewer = [
            tr("tab_map", self.arabic),
            tr("tab_table", self.arabic),
            tr("tab_tasks", self.arabic),
            tr("tab_input_info", self.arabic),
            tr("tab_about", self.arabic),
            tr("tab_pdf", self.arabic)
        ]
        for i, text in enumerate(tabs_viewer):
            self.viewer_tabs.setTabText(i, text)
            self.viewer_tabs.setTabToolTip(i, text)

        self.update_count()
        self.update_tool_layer_selectors()
        if hasattr(self,"source_credentials"):self.update_modules()

    def apply_theme(self):
        apply_application_theme(QApplication.instance(),self.dark);self.map.set_theme(self.dark)
        if hasattr(self,"viewer_tabs"):
            from .icons import outline_icon
            for index,name in enumerate(("map","table","tasks","file","info","pdf")):
                self.viewer_tabs.setTabIcon(index,outline_icon(name))
        self.brand_logo.setPixmap(QPixmap(str(asset_dir()/("mirsad-icon-dark.svg" if self.dark else "mirsad-wordmark.png"))).scaled(60 if self.dark else 125,42,Qt.KeepAspectRatio,Qt.SmoothTransformation))
        self.brand_logo.setStyleSheet("background:transparent;padding:4px")
        self.theme.setText(tr("light_mode", self.arabic) if self.dark else tr("dark_mode", self.arabic))
    def toggle_theme(self):self.dark=not self.dark;self.settings.setValue("dark",self.dark);self.apply_theme()
    def toggle_language(self):self.arabic=not self.arabic;self.settings.setValue("arabic",self.arabic);self.translate();self.apply_theme();self.fill_countries()
    def fill_countries(self):
        previous=self.country.currentData();self.country.blockSignals(True);self.country.clear();self.country.addItem(tr("choose_country", self.arabic),None)
        for code,en,ar,count in self.catalogue.countries(self.region.currentData() or ""):
            label = "%s · %d" % (ar if self.arabic else en, count) if code in ("ARAB","WORLD","AFRICA","ASIA","EUROPE","NORTH AMERICA","SOUTH AMERICA","OCEANIA","ANTARCTICA") else "%s (%s) · %d" % (ar if self.arabic else en, code, count)
            self.country.addItem(label, code)
        self.country.setCurrentIndex(max(0,self.country.findData(previous)));self.country.blockSignals(False);self.fill_stations()
    def mode_changed(self):
        self.regional_mode_changed()
        mode=self.input_mode.currentData()
        if mode=="user":self.selected_keys.intersection_update(self.user_points)
        elif mode=="grid":self.selected_keys.intersection_update(self.generated_points)
        elif mode=="stations":self.selected_keys.difference_update(self.user_points.keys()|self.generated_points.keys())
        self.own_group.setVisible(mode!="stations");self.fill_stations()
    def fill_stations(self):
        mode=self.input_mode.currentData();query=self.search.text().strip();rows=[];self.region.setEnabled(mode in ("stations","combined"));self.country.setEnabled(mode in ("stations","combined"))
        if mode in ("stations","combined") and self.country.currentData():rows=self.catalogue.stations(self.country.currentData(),query)
        extra=self.generated_points if mode=="grid" else self.user_points if mode in ("user","combined") else {}
        rows += [p for p in extra.values() if not query or query.lower() in (p["name"]+" "+p["usaf"]).lower()]
        if self.boundary is not None and self.restrict_boundary.isChecked():rows=filter_boundary(rows,self.boundary)
        self.current_rows=rows;self.table.blockSignals(True);self.table.setRowCount(len(rows))
        for i,row in enumerate(rows):
            item=QTableWidgetItem();item.setFlags(Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);item.setCheckState(Qt.Checked if row["station_key"] in self.selected_keys else Qt.Unchecked);self.table.setItem(i,0,item)
            qa={"reference_match":tr("qa_reference", self.arabic),"review_required":tr("qa_review", self.arabic),"user_supplied":tr("qa_user", self.arabic)}.get(row.get("qa_status"),tr("qa_unverified", self.arabic))
            for col,value in enumerate((row["name"],row["usaf"],row["wban"],"%.5f"%row["latitude"],"%.5f"%row["longitude"],qa),1):self.table.setItem(i,col,QTableWidgetItem(str(value)))
        self.table.blockSignals(False);self.map.canvas.selected=set(self.selected_keys);self.map.canvas.set_points(rows,fit=not bool(query));self.update_count()
    def checked(self,item):
        if item.column()!=0:return
        key=self.current_rows[item.row()]["station_key"]
        if item.checkState()==Qt.Checked:self.selected_keys.add(key)
        else:self.selected_keys.discard(key)
        self.map.canvas.selected=set(self.selected_keys);self.map.canvas.update();self.update_count()
    def map_selection(self,key):
        for index,point in enumerate(self.current_rows):
            if point["station_key"]==key:
                item=self.table.item(index,0);item.setCheckState(Qt.Unchecked if item.checkState()==Qt.Checked else Qt.Checked);self.table.scrollToItem(item);break
    def select_visible(self,value):
        for row in range(self.table.rowCount()):self.table.item(row,0).setCheckState(Qt.Checked if value else Qt.Unchecked)
    def selected_stations(self):
        points=[];mode=self.input_mode.currentData()
        if mode in ("stations","combined"):
            with self.catalogue.connect() as db:
                db.row_factory=__import__("sqlite3").Row;points=[dict(row) for row in db.execute("SELECT * FROM stations") if row["station_key"] in self.selected_keys]
        if mode in ("user","combined"):points += [p for key,p in self.user_points.items() if key in self.selected_keys]
        if mode=="grid":points += [p for key,p in self.generated_points.items() if key in self.selected_keys]
        if self.boundary is not None and self.restrict_boundary.isChecked():points=filter_boundary(points,self.boundary)
        return points
    def update_count(self):
        if hasattr(self,"count"):self.count.setText(tr("visible_selected_count", self.arabic)%(len(self.current_rows),len(self.selected_keys)))
        if hasattr(self,"input_summary"):self.input_summary.setText(tr("user_grid_count", self.arabic)%(len(self.user_points),len(self.generated_points)))
        if hasattr(self,"status") and not self.job_thread:self.status.setText("GDB + GeoPackage + Excel · "+self.meta["catalogue_version"])
        self.update_working_points_layer()
        self.update_boundary_layer()
    def append_points(self,points):
        from .validation import MAX_POINTS
        if len(set(self.user_points)|{p["station_key"] for p in points})>MAX_POINTS:
            self.on_error("Maximum %d loaded user points. Subset the inputs before adding more."%MAX_POINTS);return
        for point in points:self.user_points[point["station_key"]]=point
        target="combined" if self.active_tool=="stations" else "user"
        self.input_mode.setCurrentIndex(self.input_mode.findData(target));self.selected_keys.update(p["station_key"] for p in points);self.fill_stations();self.update_data_fields()
    def import_dialog(self):
        path,_=QFileDialog.getOpenFileName(self,"Import points","","Supported (*.shp *.gpkg *.geojson *.xlsx *.csv *.tsv);;All files (*)")
        if not path and QMessageBox.question(self,"GDB","اختيار مجلد File Geodatabase؟ / Select a FileGDB directory?")==QMessageBox.Yes:path=QFileDialog.getExistingDirectory(self,"Select .gdb")
        if not path:return
        self.inspect_path(path)
    def manual_point(self):
        dialog=PointDialog(self)
        if dialog.exec()==QDialog.Accepted:self.append_points([dialog.point])
    def add_map_point(self,lon,lat):
        dialog=PointDialog(self,lon,lat)
        if dialog.exec()==QDialog.Accepted:self.append_points([dialog.point])
    def update_data_fields(self):
        self.raster_fields.clear()
        for field in numeric_fields(list(self.user_points.values())):
            if field.startswith("_"):continue
            item=QListWidgetItem(field,self.raster_fields);item.setFlags(item.flags()|Qt.ItemIsUserCheckable);item.setCheckState(Qt.Checked if "Annual_Mean" in field else Qt.Unchecked)
        self.data_details.setPlainText(json.dumps(dict(user_points=len(self.user_points),grid_points=len(self.generated_points),coordinate_storage="WGS84; input CRS transformed with always_xy=True",
            inputs=sorted({p.get("input_source","") for p in self.user_points.values()}),fields=numeric_fields(list(self.user_points.values()))),ensure_ascii=False,indent=2))
    def choose_layer(self,path,geometry):
        layers=[name for name,kind in vector_layers(path) if geometry in kind]
        if not layers:raise ValueError("No "+geometry+" layer in input")
        if len(layers)==1:return layers[0]
        name,ok=QInputDialog.getItem(self,"Layer","Select layer",layers,0,False);return name if ok else None
    def load_boundary(self):
        path,_=QFileDialog.getOpenFileName(self,"Study boundary","","Polygon (*.shp *.gpkg *.geojson);;All files (*)")
        if not path:return
        self.inspect_path(path)
    def generate_grid(self):
        if self.boundary is None:QMessageBox.information(self,"Grid","حمّل حدود الدراسة أولًا / Load a study boundary first.");return
        try:
            points=grid_points(self.boundary,self.grid_spacing.value(),self.get_clean_crs(self.analysis_crs));self.generated_points={p["station_key"]:p for p in points}
            self.input_mode.setCurrentIndex(self.input_mode.findData("grid"));self.selected_keys=set(self.generated_points);self.fill_stations();self.update_data_fields()
        except Exception as exc:QMessageBox.warning(self,"Grid",str(exc))
    def sync_resolution(self,preferred=None):
        options=resolution_options(self.provider.currentText())
        previous=self.om_model.currentText()
        if preferred is not None:self._last_era5_resolution=canonical_resolution(preferred)
        elif previous in ERA5_MODELS:self._last_era5_resolution=canonical_resolution(previous)
        current_options=[self.om_model.itemText(i) for i in range(self.om_model.count())]
        if list(options)!=current_options:
            self.om_model.clear();self.om_model.addItems(options)
        if len(options)>1:self.om_model.setCurrentText(getattr(self,"_last_era5_resolution",options[0]))
        self.om_model.setEnabled(len(options)>1);self.om_model.setVisible(False);self.lbl_om_model.setVisible(True)
        self.om_model.setToolTip(self.t("تلقائي: أدق منتج لكل متغير يغطي الفترة كاملة. الحرارة والرطوبة والندى: Land من 1950؛ بقية المتغيرات: ERA5. قبل 1950 يستخدم ERA5 للفترة كلها. الاختيارات الأخرى تثبيت يدوي؛ دقة الإخراج منفصلة.",
            "Auto: finest supported product per variable for the whole period. Temperature/humidity/dewpoint: Land from 1950; other variables: ERA5. Periods starting before 1950 use ERA5 throughout. Other choices are manual overrides; output pixels are separate."))
        if not uses_reanalysis(self.provider.currentText()):
            self.om_model.setToolTip(self.t("هذا المنتج له شبكة أصلية ثابتة لكل متغير. لا توجد دقات تنزيل إضافية؛ حجم بكسل الإخراج إعداد مستقل.","This product has a fixed native grid per variable. There are no additional download resolutions; output pixel size is a separate setting."))
        self.update_resolution_preview()

    def choose_resolution(self):
        dialog=QDialog(self);dialog.setWindowTitle(self.t("الدقة — إعدادات متقدمة","Resolution — Advanced settings"))
        box=QVBoxLayout(dialog);note=QLabel(self.om_model.toolTip());note.setWordWrap(True);box.addWidget(note)
        combo=QComboBox();combo.addItems([self.om_model.itemText(i) for i in range(self.om_model.count())]);combo.setCurrentText(self.om_model.currentText());combo.setEnabled(self.om_model.isEnabled());combo.setMaxVisibleItems(6);box.addWidget(combo)
        apply=QPushButton(self.t("تطبيق","Apply"));apply.clicked.connect(dialog.accept);box.addWidget(apply);dialog.resize(570,230)
        if dialog.exec()==QDialog.Accepted:self.om_model.setCurrentText(combo.currentText())

    def update_resolution_preview(self,*unused):
        if not hasattr(self,"resolution_preview"):return
        from .climate_sources import reanalysis_plan,variable_resolution
        from .climate_products import descriptor
        from .registry import parameters
        provider=self.provider.currentText();required=parameters(self.chosen_modules()) if hasattr(self,"module_items") else []
        self.resolution_button.setText(self.t("تلقائي / إعدادات متقدمة…","Auto / Advanced settings…") if "Auto:" in self.om_model.currentText() else self.om_model.currentText())
        if not uses_reanalysis(provider):self.resolution_button.setText(self.t("تفاصيل دقة المصدر…","Native resolution details…"))
        spec=descriptor(provider)
        if spec:lines=[spec["resolution"]+" · "+spec["temporal"],self.t("المتغيرات: ","Variables: ")+", ".join(spec["variables"])]
        elif uses_reanalysis(provider):
            lines=[code+": "+", ".join(variables)+" — "+variable_resolution("Open-Meteo",variables[0],code)["spatial"] for code,variables in reanalysis_plan(required or ["T2M","PRECTOTCORR"],self.om_model.currentText(),self.start.date().toPython())]
        else:lines=[self.om_model.currentText()]
        self.resolution_preview.setText("\n".join(lines))

    def update_modules(self):
        provider=self.provider.currentText();count=0
        if hasattr(self, "om_model") and hasattr(self, "lbl_om_model"):
            self.sync_resolution()
        for module,item in self.module_items.items():
            reason=unavailable(provider,module);flags=item.flags()
            if reason:item.setCheckState(0,Qt.Unchecked);item.setFlags(flags & ~Qt.ItemIsEnabled)
            else:item.setFlags(flags|Qt.ItemIsEnabled);count+=1
            item.setToolTip(0,reason or "Inputs: "+", ".join(BY_NAME[module].params))
        self.modules_note.setText(self.t("المتاح لهذا المصدر: %d من 19. مرّر المؤشر لعرض التبعيات.","Available for this source: %d of 19. Hover to inspect dependencies.")%count)
        from .climate_products import descriptor
        spec=descriptor(provider);auth=spec.get("auth") if spec else None
        self.daily.setEnabled(not spec or spec["temporal"]=="Daily")
        self.daily.setToolTip(self.t("المنتج الشهري/المركب لا ينتج أيامًا مصطنعة.","Monthly/composite products do not generate fabricated daily rows.") if spec and spec["temporal"]!="Daily" else "")
        self.source_credentials.setVisible(bool(auth))
        self.source_credentials.setTitle(self.t("بيانات الوصول — Need Sign In","Source account — Need Sign In"))
        for widget in (self.source_username,self.source_username_label,self.source_password,self.source_password_label):widget.setVisible(auth=="earthdata")
        for widget in (self.source_token,self.source_token_label):widget.setVisible(auth=="cds_token")
        self.source_username_label.setText(self.t("اسم مستخدم NASA Earthdata","NASA Earthdata username"));self.source_password_label.setText(self.t("كلمة المرور","Password"));self.source_token_label.setText("CDS personal API token")
        self.source_auth_note.setText(self.t("حسابك الشخصي فقط. البيانات تبقى في الذاكرة ولا تُحفظ في المشروع. CDS يحتاج قبول شروط المنتج؛ NASA قد يحتاج تصريح GES DISC داخل Earthdata.","Use your own account. Credentials remain in memory and are excluded from project files. Accept CDS product terms; authorize GES DISC in NASA Earthdata if required."))
        if spec:self.modules_note.setText(self.t("المصدر يوفر المتغيرات الموضحة أعلاه فقط. المؤشر الذي تنقصه اعتماديات يبقى NULL مع حالة جودة؛ لا استكمال من مصدر آخر.","Only the listed variables are provided. Missing dependencies yield NULL with quality status; no other-provider supplement."))
        if provider==NOAA_ONLY:
            self.modules_note.setText(self.t("رصد المحطة فقط: يلزم USAF وWBAN والموقع الصحيح. المتغيرات غير المتاحة تبقى مفقودة؛ لا استكمال من ERA5 أو NASA.",
                "Station observations only: valid USAF/WBAN/location required. Unavailable variables remain missing; no ERA5/NASA supplement."))
        elif provider==ERA5_ONLY:
            self.modules_note.setText(self.t("ERA5 مستقل بلا NASA. تلقائي يختار Land أو ERA5 لكل متغير؛ الاختيار اليدوي يثبت النموذج. تُسجل الدقة الفعلية، وغير المتاح يبقى مفقودًا.",
                "Standalone ERA5 without NASA. Auto selects Land/ERA5 per variable; manual choices fix the model. Actual resolution is recorded; unavailable values remain missing."))
        elif "Open-Meteo" in provider:
            self.modules_note.setText(self.t("جميع العناصر متاحة. تُستكمل متغيرات ERA5 غير المتاحة والقيم المفقودة من NASA POWER مع توثيق مصدر كل قيمة.","All modules available. Missing ERA5 variables/values use an explicit NASA POWER supplement, recorded per value."))

    def check_modules(self,value):
        for item in self.module_items.values():
            if item.flags()&Qt.ItemIsEnabled:item.setCheckState(0,Qt.Checked if value else Qt.Unchecked)
    def chosen_modules(self):return [name for name,item in self.module_items.items() if item.checkState(0)==Qt.Checked and item.flags()&Qt.ItemIsEnabled]
    def raster_options(self):
        from shapely.geometry import mapping
        return dict(crs=self.get_clean_crs(self.analysis_crs),cell_size=self.cell_size.value(),
                    method=self.method.currentText(),power=self.power.value(),neighbours=self.neighbours.value(),
                    boundary=mapping(self.boundary) if self.boundary is not None else None,
                    reclass_enabled=self.reclass_en.isChecked() if hasattr(self, "reclass_en") else False,
                    reclass_method=self.reclass_method.currentText() if hasattr(self, "reclass_method") else "Natural Breaks (Jenks)",
                    reclass_classes=self.reclass_classes.value() if hasattr(self, "reclass_classes") else 5,
                    pdf=self.pdf.isChecked())
    def selected_unit_options(self):
        return {k:w.currentData() for k,w in self.unit_controls.items() if w.currentData()} if self.unit_group.isChecked() else {}
    def validated_points(self):
        points=self.selected_stations()
        if not points:raise ValueError("اختر نقاط العمل أولًا / Select working points first.")
        from pyproj import CRS
        from .crs import resolve_crs
        resolve_crs(self.get_clean_crs(self.crs));return points
    def choose_folder(self):
        path=QFileDialog.getExistingDirectory(self,"Output folder",self.folder.text())
        if path:self.folder.setText(path)
    def export_stations(self):
        try:
            points=self.validated_points();folder,name,crs=self.folder.text(),self.project_name.text(),self.get_clean_crs(self.crs)
            self.start_request(dict(operation="export",points=points,folder=folder,name=name,metadata=self.meta,options={"crs":crs}),{"export":(0,100)})
        except Exception as exc:self.on_error(str(exc))
    def download_climate(self):
        try:
            points=self.validated_points();modules=self.chosen_modules();scopes=[n for n,c in self.scopes.items() if c.isChecked()]
            if not modules or not scopes:raise ValueError("اختر العناصر والملخصات / Select climate modules and temporal summaries.")
            folder,name=self.folder.text(),self.project_name.text();start,end=self.start.date().toPython(),self.end.date().toPython();provider=self.provider.currentText()
            om_model=self.om_model.currentText() if hasattr(self, "om_model") else ""
            daily,yearly=self.daily.isChecked(),self.yearly.isChecked();crs,gap=self.get_clean_crs(self.crs),self.gap.currentData();ranges=self.monthly_ranges.isChecked();units=self.units.currentText()
            monthly_rasters=self.monthly_rasters_cb.isChecked() if hasattr(self, "monthly_rasters_cb") else False
            raster=self.raster_options() if self.workflow.currentData() in ("atlas", "full") else None
            options=dict(start=start.isoformat(),end=end.isoformat(),provider=provider,om_model=om_model,modules=modules,save_daily=daily,separate_years=yearly,crs=crs,gap_method=gap,scopes=scopes,monthly_ranges=ranges,monthly_rasters=monthly_rasters,raster_options=raster,units=units,unit_options=self.selected_unit_options())
            from .climate_products import descriptor
            spec=descriptor(provider);auth=spec.get("auth") if spec else None;credentials=None
            if auth=="cds_token":credentials={"token":self.source_token.text().strip()}
            elif auth=="earthdata":credentials={"username":self.source_username.text().strip(),"password":self.source_password.text()}
            if credentials and not all(credentials.values()):raise ValueError(self.t("Need Sign In: أدخل بيانات الوصول الخاصة بك أسفل إعدادات المناخ.","Need Sign In: enter your own credentials below the climate settings."))
            request=dict(operation="climate",points=points,folder=folder,name=name,metadata=self.meta,options=options)
            if credentials:request["_credentials"]=credentials
            self.start_request(request,{"download":(0,65),"export":(65,85 if raster else 100),"raster":(85,100)})
        except Exception as exc:self.on_error(str(exc))
    def regional_mode_changed(self):
        if not hasattr(self,"inspector") or not hasattr(self,"active_tool"):return
        if self.active_tool=="raster":
            regional=self.input_mode.currentData()=="regional"
            self.inspector.setTabEnabled(1,regional)
            self.raster_fields.setVisible(not regional);self.raster_fields_label.setVisible(not regional)
            self.own_group.setVisible(not regional)

    def download_regional(self):
        try:
            from shapely.geometry import mapping
            extent=getattr(self,"download_extent",None)
            if extent is None:raise ValueError("حدد نطاق التنزيل AOI أولًا / Select the download extent (AOI).")
            options=dict(provider=self.provider.currentText(),download_extent=mapping(extent),boundary=mapping(self.boundary) if self.boundary is not None else None,
                         start=self.start.date().toString(Qt.ISODate),end=self.end.date().toString(Qt.ISODate),modules=self.chosen_modules(),
                         crs=self.get_clean_crs(self.crs),raster_options=self.raster_options() if self.workflow.currentData()=="atlas" else None,
                         separate_years=self.yearly.isChecked(),gap_method=self.gap.currentData(),scopes=[n for n,c in self.scopes.items() if c.isChecked()],
                         monthly_ranges=self.monthly_ranges.isChecked(),monthly_rasters=self.monthly_rasters_cb.isChecked(),units=self.units.currentText(),unit_options=self.selected_unit_options())
            self.start_request(dict(operation="regional",folder=self.folder.text(),name=self.project_name.text(),metadata=self.meta,options=options),{"download":(0,60),"export":(60,80),"raster":(80,100)})
        except Exception as exc:self.on_error(str(exc))
    def analyse_existing(self):
        try:
            points=[p for p in self.selected_stations() if p.get("attributes")];fields=[self.raster_fields.item(i).text() for i in range(self.raster_fields.count()) if self.raster_fields.item(i).checkState()==Qt.Checked]
            if not points or not fields:raise ValueError("اختر نقاطك المستوردة وحقول الاستيفاء / Select imported points and numeric interpolation fields.")
            folder,name=self.folder.text(),self.project_name.text();options=self.raster_options()
            options["fields"]=fields
            self.start_request(dict(operation="analysis",points=points,folder=folder,name=name,metadata=self.meta,options=options),{"export":(0,20),"raster":(20,100)})
        except Exception as exc:self.on_error(str(exc))
    def start_request(self,request,stages=None):
        if self.job_thread:return
        self.request_operation=request.get("operation")
        self.request_succeeded=False
        try:self.job_thread=ProcessWorker(request,self.folder.text(),self)
        except Exception as exc:self.on_error(str(exc));return
        self.job_thread.progress.connect(self.on_progress);self.job_thread.finished.connect(self.on_request_result);self.job_thread.failed.connect(self.on_error)
        self.job_thread.stopped.connect(self.job_finished)
        self.stage_ranges=stages or {"export":(0,100)};self.started_at=time.monotonic();self.clock.start();self.progress.setValue(0);self.progress.setFormat("%p%");self.status.setText(self.t("بدء المهمة…","Starting task…"))
        for widget in (self.export,self.download_button,self.analysis_button,self.import_button,self.manual_button,self.grid_button,self.run_active,self.navigation,self.inspector):widget.setEnabled(False)
        self.add_data_button.setEnabled(False);self.cancel.setEnabled(True);self.job_thread.start()
    def on_progress(self,update):
        if isinstance(update,dict):
            message=update.get("message","");done,total=update.get("completed",0),max(1,update.get("total",1));low,high=self.stage_ranges.get(update.get("stage"),(0,100))
            self.progress.setValue(max(self.progress.value(),int(low+(high-low)*done/total)));self.progress.setFormat("%p%  ·  "+str(done)+"/"+str(total))
        else:message=str(update)
        self.status.setText(message);self.log.appendPlainText(dt.datetime.now().strftime("%H:%M:%S")+"  "+message)
    def tick(self):
        if self.started_at is None:return
        seconds=int(time.monotonic()-self.started_at);percent=self.progress.value();eta=int(seconds*(100-percent)/percent) if 0<percent<100 else None
        self.elapsed.setText("%02d:%02d"%(seconds//60,seconds%60)+(" · ETA %02d:%02d"%(eta//60,eta%60) if eta is not None else ""))
    def on_result(self,result):
        self.last_output,manifest=result;self.open_output.setEnabled(True);status=manifest["status"]
        self.status.setText(self.t("اكتملت المهمة","Complete") if status=="complete" else self.t("نتيجة جزئية؛ راجع السجل","Partial result; inspect log"));self.log.appendPlainText(str(self.last_output)+"\n"+json.dumps(manifest,ensure_ascii=False,indent=2))
        self.register_results(self.last_output)
        if status=="complete":self.progress.setValue(100)
    def on_error(self,message):
        self.status.setText(message[:500]);self.log.appendPlainText(message)
        if not message.startswith("Cancelled"):
            dialog=QMessageBox(self);dialog.setIcon(QMessageBox.Warning);dialog.setWindowTitle("MIRSAD")
            dialog.setTextFormat(Qt.PlainText);dialog.setText(message);dialog.exec()
    def job_finished(self):
        self.job_thread.deleteLater();self.job_thread=None;self.clock.stop();self.tick()
        for widget in (self.export,self.download_button,self.analysis_button,self.import_button,self.manual_button,self.grid_button,self.run_active,self.navigation,self.inspector):widget.setEnabled(True)
        self.cancel.setEnabled(False)
        self.add_data_button.setEnabled(True)
        if self.request_succeeded and self.request_operation in ("preview","inspect","import_points","pdf_preview"):
            self.status.setText(self.t("انتهت قراءة البيانات؛ المعاينة لا تعدّل المصدر","Data read finished; previews do not modify the source"))
        pending=getattr(self,"pending_preview",None);self.pending_preview=None
        if pending:QTimer.singleShot(0,lambda:self.request_preview(pending))
    def open_results(self):
        if self.last_output:os.startfile(str(self.last_output))
    def closeEvent(self,event):
        if self.job_thread:self.job_thread.cancel();self.status.setText(self.t("جاري الإلغاء؛ انتظر الطلب الجاري","Cancelling; waiting for current request"));event.ignore()
        else:
            self.save_workspace_layout();event.accept()

    def cancel_job(self):
        if self.job_thread:self.job_thread.cancel()
    def add_data(self, default_role="stations"):
        dialog=GisAddDataDialog(parent=self)
        if default_role=="mask":dialog.role_mask.setChecked(True)
        elif default_role=="context":dialog.role_context.setChecked(True)
        else:dialog.role_stations.setChecked(True)
        if dialog.exec()==QDialog.Accepted and dialog.selected_path:
            self.inspect_path(dialog.selected_path,layer=dialog.selected_layer,role=dialog.selected_role)
    def add_database(self):
        self.add_data(default_role="context")
    def add_raster(self):
        self.add_data(default_role="context")
    def load_boundary(self):
        self.add_data(default_role="mask")
    def load_download_extent(self):
        dialog=GisAddDataDialog(parent=self);dialog.role_mask.setChecked(True)
        if dialog.exec()==QDialog.Accepted and dialog.selected_path:
            self.inspect_path(dialog.selected_path,layer=dialog.selected_layer,role="download_extent")
    def import_dialog(self):
        self.add_data(default_role="stations")
    def inspect_path(self,path,layer=None,source_crs=None,role=None):
        self.pending_role=role
        self.start_request(dict(operation="inspect",options=dict(path=str(path),layer=layer,source_crs=source_crs)))
    def on_request_result(self,result):
        self.request_succeeded=True
        if result.get("kind")!="project":self.progress.setValue(100)
        if result.get("kind")=="pdf_preview":
            self.pdf_view.display(result);self.viewer_tabs.setCurrentIndex(5);self.progress.setValue(100);return
        # Queue follow-up dialogs until the current QProcess has fully stopped.
        if result.get("kind")=="project":self.on_result((Path(result["output"]),result["manifest"]));return
        if result.get("kind", "").startswith("preview_"):
            self.show_preview(result);self.progress.setValue(100);return
        self.pending_data_result=result
        QTimer.singleShot(0,self.apply_data_result)
    def apply_data_result(self):
        if self.job_thread:QTimer.singleShot(20,self.apply_data_result);return
        result=self.pending_data_result;self.pending_data_result=None
        if not result:return
        role=getattr(self,"pending_role",None);self.pending_role=None
        kind=result["kind"];self.data_details.setPlainText(json.dumps(result if kind!="points" else {"points":len(result["points"])},ensure_ascii=False,indent=2)[:40000])
        if kind=="layers":
            layers=result["layers"]
            if not layers:self.on_error("Dataset contains no readable layers.");return
            labels=[name+"  ["+geometry+"]" for name,geometry in layers]
            if len(labels)==1:choice,ok=labels[0],True
            else:choice,ok=QInputDialog.getItem(self,"Add Data","الطبقة / Layer",labels,0,False)
            if ok:self.inspect_path(result["path"],layers[labels.index(choice)][0],role=role)
        elif kind=="needs_crs":
            dialog=CrsSelectionDialog(parent=self)
            if dialog.exec()==QDialog.Accepted and dialog.selected_crs:
                self.inspect_path(result["path"],result.get("layer"),dialog.selected_crs,role=role)
        elif kind=="point_mapping":
            dialog=ImportDialog(result["path"],self,metadata=result)
            if dialog.exec()==QDialog.Accepted:self.start_request(dict(operation="import_points",options=dialog.options))
        elif kind=="points":
            self.append_points(result["points"])
            path=result.get("path")
            layer=result.get("layer")
            if path:
                layer_id=f"pts_{path}_{layer}"
                name=Path(path).name + (f" ({layer})" if layer else "")
                self.register_map_layer(name,layer_id,kind="point",path=path,layer_name=layer,crs=result.get("crs"),count=len(result["points"]))
            self.viewer_tabs.setCurrentIndex(0)
        elif kind=="boundary":
            if role=="download_extent":
                from shapely.geometry import shape
                self.download_extent=shape(result["boundary"])
                self.download_extent_summary.setText(Path(result["path"]).name)
                return
            from shapely.geometry import shape
            self.boundary=shape(result["boundary"])
            self.map.canvas.boundary=self.boundary.simplify(.002,preserve_topology=True)
            b_name=Path(result["path"]).name+(f" / {result['layer']}" if result.get("layer") else "")
            self.boundary_summary.setText(b_name)
            layer_id=f"poly_{result.get('path')}_{result.get('layer')}"
            self.register_map_layer(b_name,layer_id,kind="polygon",path=result.get("path"),layer_name=result.get("layer"),crs=result.get("crs"))
            self.fill_stations()
            self.map.canvas.fit_points()
            self.update_boundary_layer()
            self.viewer_tabs.setCurrentIndex(0)
        elif kind=="raster":
            layer_id=self.map.canvas.add_raster(result)
            self.register_map_layer(Path(result["path"]).name,layer_id,kind="raster",path=result.get("path"),crs=result.get("crs"))
            self.viewer_tabs.setCurrentIndex(0)
        elif kind=="vector":
            layer_id=self.map.canvas.add_vectors(result)
            v_name=Path(result["path"]).name+(f" / {result['layer']}" if result.get("layer") else "")
            self.register_map_layer(v_name,layer_id,kind="vector",path=result.get("path"),layer_name=result.get("layer"),crs=result.get("crs"))
            self.viewer_tabs.setCurrentIndex(0)
        elif kind=="table":
            t_name=Path(result["path"]).name+(f" / {result['layer']}" if result.get("layer") else "")
            self.register_table_layer(t_name,result.get("path"),layer_name=result.get("layer"),count=len(result.get("rows",[])))
            self.viewer_tabs.setCurrentIndex(1)
        else:self.viewer_tabs.setCurrentIndex(3)
    def show_help(self):
        from .userguide import UserGuideDialog
        dialog=getattr(self,"help_dialog",None)
        if dialog is None:
            dialog=UserGuideDialog(self.arabic,self);self.help_dialog=dialog
        topic={"stations":"tool-stations","points":"tool-points","raster":"tool-raster"}.get(getattr(self,"active_tool",""),"workspace")
        if topic in dialog.topics:dialog.open_topic(topic)
        dialog.show();dialog.raise_();dialog.activateWindow()
