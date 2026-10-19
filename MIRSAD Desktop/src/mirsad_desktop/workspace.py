"""Permanent application shell with independent tool drafts and read-only results."""
from pathlib import Path
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QPushButton, QMenu, QListWidget, QSplitter, QTabWidget, QLineEdit, QComboBox,
    QProgressBar, QTreeWidget, QTreeWidgetItem, QStackedWidget, QCheckBox, QFileDialog,
    QInputDialog, QSizePolicy)
from . import __version__
from .catalogue import asset_dir
from .tools import TOOLS, BY_KEY, fresh_draft
from .climate_sources import resolution_options
from .viewers import DataPreview,PdfPreview
from .crs import COMMON_CRS_LIST
from .i18n import tr


class WorkspaceMixin:
    def rebuild_add_data_menu(self):
        menu = QMenu(self)
        menu.addAction(tr("add_layer_gdb", self.arabic), lambda: self.add_data("context"))
        menu.addAction(tr("import_stations", self.arabic), lambda: self.add_data("stations"))
        menu.addAction(tr("study_boundary", self.arabic), self.load_boundary)
        menu.addAction(tr("raster_geotiff", self.arabic), self.add_raster)
        menu.addAction(tr("preview_table_layer", self.arabic), self.open_preview)
        self.add_data_button.setMenu(menu)

    def build_shell(self):
        self.active_tool = "stations"
        self.tool_drafts = {tool.key: fresh_draft(tool) for tool in TOOLS}
        self.restoring_tool = False
        self.project_layers = {}
        self.preview_layer_keys = {}
        root = QWidget()
        root.setObjectName("workspace")
        outer = QVBoxLayout(root)
        outer.setContentsMargins(10, 8, 10, 8)
        outer.setSpacing(8)
        header = QFrame()
        header.setObjectName("header")
        bar = QHBoxLayout(header)
        logo = QLabel()
        self.brand_logo=logo
        logo.setPixmap(QPixmap(str(asset_dir()/"mirsad-wordmark.png")).scaled(125, 42, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setStyleSheet("background:white;padding:4px;border-radius:7px")
        bar.addWidget(logo)
        titles = QVBoxLayout()
        self.heading, self.subtitle = QLabel(), QLabel()
        self.heading.setObjectName("heading")
        self.heading.setWordWrap(True)
        self.subtitle.setWordWrap(True)
        self.subtitle.setObjectName("muted")
        titles.addWidget(self.heading)
        titles.addWidget(self.subtitle)
        bar.addLayout(titles, 1)
        self.add_data_button = QPushButton("＋ " + tr("add_data", self.arabic))
        self.rebuild_add_data_menu()
        bar.addWidget(self.add_data_button)
        self.help_button = QPushButton(tr("help", self.arabic))
        self.help_button.clicked.connect(self.show_help)
        bar.addWidget(self.help_button)
        self.theme = QPushButton()
        self.theme.clicked.connect(self.toggle_theme)
        bar.addWidget(self.theme)
        self.language = QPushButton("English" if self.arabic else "العربية")
        self.language.clicked.connect(self.toggle_language)
        bar.addWidget(self.language)
        self.layout_button=QPushButton("☰")
        self.layout_button.setToolTip("Workspace panels / لوحات مساحة العمل")
        bar.addWidget(self.layout_button)
        outer.addWidget(header)
        body = QHBoxLayout()
        outer.addLayout(body, 1)
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setMinimumWidth(160)
        self.sidebar=sidebar
        nav = QVBoxLayout(sidebar)
        self.tools_title = QLabel(tr("tools_heading", self.arabic))
        self.tools_title.setObjectName("section")
        nav.addWidget(self.tools_title)
        self.navigation = QListWidget()
        self.navigation.setObjectName("navigation")
        self.navigation.setMinimumHeight(80)
        self.navigation.setMaximumHeight(360)
        self.navigation.setWordWrap(True)
        self.navigation.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.navigation.setSpacing(0)
        nav.addWidget(self.navigation,1)
        self.contents_title = QLabel(tr("contents_heading", self.arabic))
        self.contents_title.setObjectName("section")
        nav.addWidget(self.contents_title)
        self.layers = QTreeWidget()
        self.layers.setHeaderHidden(True)
        self.layers.setMinimumWidth(0)
        self.group_layers = QTreeWidgetItem(self.layers, [tr("group_layers", self.arabic)])
        self.group_layers.setExpanded(True)
        self.group_tables = QTreeWidgetItem(self.layers, [tr("group_tables", self.arabic)])
        self.group_tables.setExpanded(True)
        self.results_root = QTreeWidgetItem(self.layers, [tr("group_results", self.arabic)])
        self.results_root.setExpanded(True)
        self.work_layer = None
        self.boundary_layer = None
        self.layers.itemDoubleClicked.connect(self.open_layer_item)
        self.layers.itemChanged.connect(self.layer_visibility)
        self.layers.setContextMenuPolicy(Qt.CustomContextMenu)
        self.layers.customContextMenuRequested.connect(self.layer_menu)
        nav.addWidget(self.layers, 1)
        brand = QLabel("MIRSAD Desktop · " + __version__ + "\nAhmad Ibrahim")
        brand.setObjectName("muted")
        nav.addWidget(brand)

        # Reuse implemented tool controls; the map is no longer a tool-specific page.
        self.pages = QStackedWidget(self)
        self.pages.hide()
        self.setup_map()
        self.setup_climate()
        self.setup_analysis()
        self.setup_data()
        self.setup_tasks()
        self.setup_about()
        old_pages = [self.pages.widget(i) for i in range(self.pages.count())]
        self.viewer_tabs = QTabWidget()
        self.viewer_tabs.setObjectName("viewerTabs")
        self.viewer_tabs.setDocumentMode(True)
        self.viewer_tabs.setUsesScrollButtons(True)
        self.viewer_tabs.tabBar().setExpanding(False)
        self.viewer_tabs.tabBar().setElideMode(Qt.ElideNone)
        self.viewer_tabs.addTab(self.map_content, tr("tab_map", self.arabic))
        self.preview_table = DataPreview()
        self.preview_table.requested.connect(self.request_preview)
        self.preview_table.use_requested.connect(lambda path,layer:self.inspect_path(path,layer or None))
        self.viewer_tabs.addTab(self.preview_table, tr("tab_table", self.arabic))
        self.viewer_tabs.addTab(old_pages[4], tr("tab_tasks", self.arabic))
        self.viewer_tabs.addTab(old_pages[3], tr("tab_input_info", self.arabic))
        self.viewer_tabs.addTab(old_pages[5], tr("tab_about", self.arabic))
        self.pdf_view=PdfPreview()
        self.pdf_view.requested.connect(lambda options:self.start_request(dict(operation="pdf_preview",options=options)))
        self.viewer_tabs.addTab(self.pdf_view, tr("tab_pdf", self.arabic))
        from .icons import outline_icon
        from PySide6.QtCore import QSize
        self.viewer_tabs.setIconSize(QSize(16,16))
        for index,name in enumerate(("map","table","tasks","file","info","pdf")):
            self.viewer_tabs.setTabIcon(index,outline_icon(name))
        self.inspector = QTabWidget()
        self.inspector.setObjectName("inspector")
        self.inspector.setMinimumWidth(300)
        self.inspector.tabBar().setExpanding(False)
        self.inspector.setUsesScrollButtons(True)
        self.inspector.addTab(self.map_controls, tr("tab_inputs", self.arabic))
        self.map_controls.setMaximumWidth(16777215)
        self.inspector.addTab(old_pages[1], tr("tab_climate", self.arabic))
        self.inspector.addTab(old_pages[2], tr("tab_raster", self.arabic))
        self.output_panel = QWidget()
        output_form = QVBoxLayout(self.output_panel)
        output_form.addWidget(QLabel("GDB + GeoPackage + Excel"))
        self.enable_raster = QCheckBox(tr("workflow_atlas", self.arabic))
        self.enable_raster.toggled.connect(lambda value: self.workflow.setCurrentIndex(max(0, self.workflow.findData("atlas" if value else "data"))))
        self.workflow.currentIndexChanged.connect(lambda _: self.enable_raster.setChecked(self.workflow.currentData() in ("atlas", "offline")))
        output_form.addWidget(self.enable_raster)
        self.project_label = QLabel(tr("project_name", self.arabic))
        output_form.addWidget(self.project_label)
        self.project_name = QLineEdit("MIRSAD_Stations")
        output_form.addWidget(self.project_name)
        self.folder_label = QLabel(tr("output_folder", self.arabic))
        output_form.addWidget(self.folder_label)
        location = QHBoxLayout()
        self.folder = QLineEdit(str(Path.home()/"Documents"/"MIRSAD Projects"))
        self.browse = QPushButton("…")
        self.browse.clicked.connect(self.choose_folder)
        location.addWidget(self.folder, 1)
        location.addWidget(self.browse)
        output_form.addLayout(location)
        self.crs_label = QLabel(tr("output_crs", self.arabic))
        output_form.addWidget(self.crs_label)
        self.footer_crs = QComboBox()
        self.footer_crs.setEditable(True)
        for code,desc in COMMON_CRS_LIST:self.footer_crs.addItem(f"{code} — {desc}",code)
        self.footer_crs_btn = QPushButton("🌐")
        self.footer_crs_btn.setToolTip(tr("dlg_crs_title", self.arabic))
        self.footer_crs_btn.setFixedWidth(36)
        self.footer_crs_btn.clicked.connect(lambda:self.choose_crs_dialog(self.footer_crs))
        footer_crs_layout = QHBoxLayout()
        footer_crs_layout.addWidget(self.footer_crs, 1)
        footer_crs_layout.addWidget(self.footer_crs_btn)
        def _sync_crs_text(src, dst):
            def _apply(txt):
                if dst.currentText() != txt:
                    dst.blockSignals(True)
                    dst.setCurrentText(txt)
                    dst.blockSignals(False)
            return _apply
        self.footer_crs.currentTextChanged.connect(_sync_crs_text(self.footer_crs, self.crs))
        self.crs.currentTextChanged.connect(_sync_crs_text(self.crs, self.footer_crs))
        self.footer_crs.currentIndexChanged.connect(lambda idx: self.crs.setCurrentIndex(idx) if self.crs.currentIndex() != idx else None)
        self.crs.currentIndexChanged.connect(lambda idx: self.footer_crs.setCurrentIndex(idx) if self.footer_crs.currentIndex() != idx else None)
        output_form.addLayout(footer_crs_layout)
        self.output_note = QLabel(tr("output_databases_note", self.arabic))
        self.output_note.setWordWrap(True)
        self.output_note.setObjectName("muted")
        output_form.addWidget(self.output_note)
        output_form.addStretch()
        self.inspector.addTab(self.output_panel, tr("tab_outputs", self.arabic))
        self.tool_title, self.tool_note = QLabel(), QLabel()
        self.tool_title.setObjectName("section")
        self.tool_note.setWordWrap(True)
        self.tool_note.setObjectName("muted")
        panel = QWidget()
        panel_box = QVBoxLayout(panel)
        panel_box.setContentsMargins(0, 0, 0, 0)
        panel_box.addWidget(self.tool_title)
        panel_box.addWidget(self.tool_note)
        panel_box.addWidget(self.inspector, 1)
        steps = QHBoxLayout()
        self.back_step = QPushButton(tr("btn_back_step", self.arabic))
        self.next_step = QPushButton(tr("btn_next_step", self.arabic))
        self.back_step.clicked.connect(lambda: self.inspector.setCurrentIndex(max(0, self.inspector.currentIndex()-1)))
        self.next_step.clicked.connect(self.next_tool_step)
        steps.addWidget(self.back_step)
        steps.addWidget(self.next_step)
        panel_box.addLayout(steps)
        split = QSplitter(Qt.Horizontal)
        split.addWidget(sidebar)
        split.addWidget(self.viewer_tabs)
        split.addWidget(panel)
        split.setHandleWidth(6)
        split.setSizes([200, 850, 360])
        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 1)
        split.setStretchFactor(2, 0)
        split.setCollapsible(1,False)
        self.tool_panel=panel
        body.addWidget(split, 1)
        self.shell_split = split

        footer = QFrame()
        footer.setObjectName("footer")
        foot = QVBoxLayout(footer)
        actions = QHBoxLayout()
        self.status, self.elapsed = QLabel(), QLabel("00:00")
        self.status.setWordWrap(True)
        actions.addWidget(self.status, 1)
        actions.addWidget(self.elapsed)
        self.open_output = QPushButton()
        self.open_output.setEnabled(False)
        self.open_output.clicked.connect(self.open_results)
        self.cancel = QPushButton()
        self.cancel.setEnabled(False)
        self.cancel.clicked.connect(self.cancel_job)
        self.export = QPushButton()
        self.export.clicked.connect(self.export_stations)
        self.run_active = QPushButton(tr("btn_run_tool", self.arabic))
        self.run_active.setObjectName("primary")
        self.run_active.clicked.connect(self.run_tool)
        for widget in (self.open_output, self.cancel, self.export, self.run_active): actions.addWidget(widget)
        foot.addLayout(actions)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        foot.addWidget(self.progress)
        outer.addWidget(footer)
        self.setCentralWidget(root)
        self.download_button.hide()
        self.analysis_button.hide()
        self.navigation.currentRowChanged.connect(self.activate_navigation)
        self.restore_tool("stations")
        menu=QMenu(self.layout_button)
        for label,widget in (("Layers / الطبقات",sidebar),("Tool settings / إعدادات الأداة",panel)):
            action=menu.addAction(label);action.setCheckable(True);action.setChecked(True)
            action.toggled.connect(widget.setVisible)
        menu.addSeparator();menu.addAction("Reset layout / استعادة التخطيط",self.reset_workspace_layout)
        self.layout_button.setMenu(menu)
        geometry=self.settings.value("workspace/geometry")
        state=self.settings.value("workspace/splitter")
        if geometry:self.restoreGeometry(geometry)
        if state:self.shell_split.restoreState(state)

    def reset_workspace_layout(self):
        self.sidebar.show();self.tool_panel.show()
        self.shell_split.setSizes([200,max(320,self.width()-580),360])
        for action in self.layout_button.menu().actions():
            if action.isCheckable():action.setChecked(True)

    def save_workspace_layout(self):
        self.settings.setValue("workspace/geometry",self.saveGeometry())
        self.settings.setValue("workspace/splitter",self.shell_split.saveState())

    def next_tool_step(self):
        index = self.inspector.currentIndex()+1
        while index < self.inspector.count() and not self.inspector.isTabEnabled(index): index += 1
        self.inspector.setCurrentIndex(min(index, self.inspector.count()-1))

    def run_tool(self):
        if self.workflow.currentData()=="offline" or (self.active_tool=="raster" and self.input_mode.currentData()=="user"): self.analyse_existing()
        elif self.active_tool=="raster":self.download_regional()
        else: self.download_climate()

    def capture_tool(self):
        return dict(mode=self.input_mode.currentData(), selected=set(self.selected_keys),
            points=dict(self.user_points), grid=dict(self.generated_points), boundary=self.boundary,
            boundary_label=self.boundary_summary.text(), download_extent=getattr(self,"download_extent",None),download_extent_label=self.download_extent_summary.text(),region=self.region.currentData(),
            country=self.country.currentData(), search=self.search.text(), project=self.project_name.text(),
            provider=self.provider.currentText(), om_model=self.om_model.currentText(),
            era5_resolution=self.om_model.currentText() if len(resolution_options(self.provider.currentText()))>1 else getattr(self,"_last_era5_resolution",self.om_model.currentText()), start=self.start.date().toString(Qt.ISODate),
            end=self.end.date().toString(Qt.ISODate), modules=self.chosen_modules(), crs=self.get_clean_crs(self.crs),
            processing_crs=self.get_clean_crs(self.analysis_crs), units=self.units.currentText(),unit_options=self.selected_unit_options(),gap=self.gap.currentData(),
            workflow=self.workflow.currentData(), daily=self.daily.isChecked(), yearly=self.yearly.isChecked(),
            ranges=self.monthly_ranges.isChecked(), generate_monthly_rasters=self.monthly_rasters_cb.isChecked(), scopes=[n for n,c in self.scopes.items() if c.isChecked()],
            method=self.method.currentText(), cell=self.cell_size.value(), power=self.power.value(),
            neighbours=self.neighbours.value(), pdf=self.pdf.isChecked(), spacing=self.grid_spacing.value(),
            reclass_enabled=self.reclass_en.isChecked(),reclass_method=self.reclass_method.currentText(),reclass_classes=self.reclass_classes.value(),
            restrict=self.restrict_boundary.isChecked(), fields=[self.raster_fields.item(i).text()
                for i in range(self.raster_fields.count()) if self.raster_fields.item(i).checkState()==Qt.Checked])

    def restore_tool(self, key):
        self.restoring_tool = True
        self.active_tool = key
        spec, draft = BY_KEY[key], self.tool_drafts[key]
        widgets = [self.input_mode, self.region, self.country, self.search, self.provider, self.restrict_boundary]
        for widget in widgets: widget.blockSignals(True)
        self.input_mode.clear()
        labels = {
            "stations": tr("mode_stations", self.arabic),
            "combined": tr("mode_combined", self.arabic),
            "user": tr("mode_user", self.arabic),
            "grid": tr("mode_grid", self.arabic)
        }
        labels["regional"]="NASA POWER Regional Download / تنزيل الشبكات الإقليمية"
        for mode in spec.modes: self.input_mode.addItem(labels.get(mode, mode), mode)
        self.input_mode.setCurrentIndex(max(0, self.input_mode.findData(draft["mode"])))
        self.selected_keys, self.user_points, self.generated_points = set(draft["selected"]), dict(draft["points"]), dict(draft["grid"])
        self.boundary = draft["boundary"]
        self.download_extent=draft["download_extent"]
        self.download_extent_summary.setText(draft["download_extent_label"])
        self.map.canvas.boundary = self.boundary
        self.boundary_summary.setText(draft["boundary_label"])
        self.region.setCurrentIndex(max(0, self.region.findData(draft["region"])))
        self.country.clear()
        self.country.addItem(tr("choose_country", self.arabic), None)
        for code, en, ar, count in self.catalogue.countries(draft["region"] or ""):
            self.country.addItem("%s (%s) · %d" % (ar if self.arabic else en, code, count), code)
        self.country.setCurrentIndex(max(0, self.country.findData(draft["country"])))
        self.search.setText(draft["search"])
        self.project_name.setText(draft["project"])
        self.provider.clear()
        from .climate_sources import point_providers
        from .climate_products import REGIONAL
        self.provider.addItems(["NASA POWER Regional Grid"]+list(REGIONAL) if key=="raster" else point_providers(stations=key=="stations"))
        self.provider.setCurrentText(draft["provider"])
        self.sync_resolution(preferred=draft.get("era5_resolution",draft["om_model"]))
        self.start.setDate(QDate.fromString(draft["start"], Qt.ISODate))
        self.end.setDate(QDate.fromString(draft["end"], Qt.ISODate))
        self.set_combo_crs(self.crs,draft["crs"])
        self.set_combo_crs(self.analysis_crs,draft["processing_crs"])
        for widget, value in ((self.units,draft["units"]),(self.method,draft["method"])): widget.setCurrentText(value)
        for k,widget in self.unit_controls.items():widget.setCurrentIndex(max(0,widget.findData(draft["unit_options"].get(k))))
        self.unit_group.setChecked(bool(draft["unit_options"]))
        self.gap.setCurrentIndex(max(0,self.gap.findData(draft["gap"])))
        self.workflow.setCurrentIndex(max(0,self.workflow.findData(draft["workflow"])))
        self.enable_raster.setChecked(draft["workflow"] in ("atlas", "offline"))
        self.monthly_rasters_cb.setChecked(draft["generate_monthly_rasters"])
        self.reclass_en.setChecked(draft["reclass_enabled"])
        self.reclass_method.setCurrentText(draft["reclass_method"])
        self.reclass_classes.setValue(draft["reclass_classes"])
        for widget, value in ((self.daily,draft["daily"]),(self.yearly,draft["yearly"]),
                              (self.monthly_ranges,draft["ranges"]),(self.pdf,draft["pdf"]),
                              (self.restrict_boundary,draft["restrict"])): widget.setChecked(value)
        for widget, value in ((self.cell_size,draft["cell"]),(self.power,draft["power"]),
                              (self.neighbours,draft["neighbours"]),(self.grid_spacing,draft["spacing"])): widget.setValue(value)
        for name, check in self.scopes.items(): check.setChecked(name in draft["scopes"])
        self.update_modules()
        for name,item in self.module_items.items(): item.setCheckState(0,Qt.Checked if name in draft["modules"] and item.flags()&Qt.ItemIsEnabled else Qt.Unchecked)
        self.update_data_fields()
        for i in range(self.raster_fields.count()):
            item=self.raster_fields.item(i)
            item.setCheckState(Qt.Checked if item.text() in draft["fields"] else Qt.Unchecked)
        for widget in widgets: widget.blockSignals(False)
        self.station_group.setVisible(key == "stations")
        self.own_group.setVisible(key != "stations" or draft["mode"] == "combined")
        self.grid_button.setVisible(key == "points")
        self.grid_spacing.setVisible(key == "points")
        self.inspector.setTabEnabled(1, key != "raster" or draft["mode"]=="regional")
        self.inspector.setTabEnabled(2, True)
        self.raster_fields.setVisible(key == "raster")
        self.raster_fields_label.setVisible(key == "raster")
        self.enable_raster.setEnabled(key != "raster")
        self.download_extent_button.setVisible(key=="raster")
        self.download_extent_summary.setVisible(key=="raster")
        self.regional_mode_changed()
        self.back_step.setVisible(key == "raster")
        self.next_step.setVisible(key == "raster")
        self.tool_title.setText(spec.arabic if self.arabic else spec.english)
        self.tool_note.setText(spec.description_ar if self.arabic else spec.description_en)
        self.restoring_tool = False
        self.fill_stations()
        self.inspector.setCurrentIndex(0)

    def activate_navigation(self, row):
        if row < 0: return
        if row < len(TOOLS):
            key = TOOLS[row].key
            if key != self.active_tool:
                self.tool_drafts[self.active_tool] = self.capture_tool()
                self.restore_tool(key)
            self.viewer_tabs.setCurrentIndex(0)
        elif row == 3:
            self.viewer_tabs.setCurrentIndex(1)
        elif row == 4: self.viewer_tabs.setCurrentIndex(2)
        else: self.viewer_tabs.setCurrentIndex(4)

    def open_preview(self):
        path, _ = QFileDialog.getOpenFileName(self,"Preview data","","Tables & GIS (*.xlsx *.csv *.tsv *.gpkg *.shp *.geojson *.sqlite)")
        if path: self.request_preview(dict(path=path))

    def request_preview(self, options):
        self.start_request(dict(operation="preview", options=options))

    def show_preview(self, result):
        if result["kind"] == "preview_layers":
            names = result["layers"]
            name, ok = QInputDialog.getItem(self,"Preview layer","Layer",names,0,False)
            if ok: self.pending_preview = dict(path=result["path"],layer=name)
            return
        self.preview_table.display(result)
        self.viewer_tabs.setCurrentIndex(1)
        if result.get("points"):
            identity=(result["path"],result.get("layer"))
            key=self.preview_layer_keys.get(identity)
            if key in self.map.canvas.display_layers:
                self.map.canvas.display_layers[key]["payload"]=result["points"]
                if key in self.project_layers:self.project_layers[key]["crs"]=result.get("crs")
                self.map.canvas.update()
            elif len(self.map.canvas.display_layers)<24:
                layer_id=self.map.canvas.add_preview_points(result)
                self.preview_layer_keys[identity]=layer_id
                self.register_map_layer(Path(result["path"]).name+" / "+str(result.get("layer") or ""),layer_id,
                                        kind="point",path=result["path"],layer_name=result.get("layer"),crs=result.get("crs"))

    def update_working_points_layer(self):
        if not hasattr(self, "group_layers"): return
        points_count = len(self.selected_stations()) if hasattr(self, "selected_stations") else 0
        if points_count > 0:
            label = f"📍 {tr('working_points', self.arabic)} ({points_count})"
            if self.work_layer is None:
                self.work_layer = QTreeWidgetItem(self.group_layers, [label])
                self.work_layer.setCheckState(0, Qt.Checked)
            else:
                self.work_layer.setText(0, label)
        else:
            if self.work_layer is not None:
                self.group_layers.removeChild(self.work_layer)
                self.work_layer = None

    def update_boundary_layer(self):
        if not hasattr(self, "group_layers"): return
        if getattr(self, "boundary", None) is not None:
            name = self.boundary_summary.text() if hasattr(self, "boundary_summary") else ""
            label = f"🔲 {tr('study_boundary_layer', self.arabic)}" + (f" ({name})" if name and name != tr("study_boundary_layer", self.arabic) else "")
            if self.boundary_layer is None:
                self.boundary_layer = QTreeWidgetItem(self.group_layers, [label])
                self.boundary_layer.setCheckState(0, Qt.Checked)
            else:
                self.boundary_layer.setText(0, label)
        else:
            if self.boundary_layer is not None:
                self.group_layers.removeChild(self.boundary_layer)
                self.boundary_layer = None

    def update_tool_layer_selectors(self):
        if hasattr(self, "point_layer_combo"):
            prev_pt = self.point_layer_combo.currentData()
            self.point_layer_combo.blockSignals(True)
            self.point_layer_combo.clear()
            self.point_layer_combo.addItem(tr("import_point_file", self.arabic) + "…", None)
            for key, info in self.project_layers.items():
                if info.get("kind") == "point":
                    name = info.get("name") or key
                    count = info.get("count")
                    label = f"📍 {name}" + (f" ({count})" if count else "")
                    self.point_layer_combo.addItem(label, key)
            idx = self.point_layer_combo.findData(prev_pt)
            if idx >= 0:
                self.point_layer_combo.setCurrentIndex(idx)
            self.point_layer_combo.blockSignals(False)

        if hasattr(self, "boundary_combo"):
            prev_poly = self.boundary_combo.currentData()
            self.boundary_combo.blockSignals(True)
            self.boundary_combo.clear()
            self.boundary_combo.addItem(tr("study_boundary_layer", self.arabic) + "…", None)
            for key, info in self.project_layers.items():
                if info.get("kind") == "polygon":
                    name = info.get("name") or key
                    label = f"🔲 {name}"
                    self.boundary_combo.addItem(label, key)
            idx = self.boundary_combo.findData(prev_poly)
            if idx >= 0:
                self.boundary_combo.setCurrentIndex(idx)
            self.boundary_combo.blockSignals(False)

    def point_layer_selected(self, index):
        if not hasattr(self, "point_layer_combo"): return
        key = self.point_layer_combo.currentData()
        if not key: return
        info = self.project_layers.get(key)
        if info and info.get("path"):
            self.inspect_path(info["path"], layer=info.get("layer"), role="stations")

    def boundary_layer_selected(self, index):
        if not hasattr(self, "boundary_combo"): return
        key = self.boundary_combo.currentData()
        if not key: return
        info = self.project_layers.get(key)
        if info and info.get("path"):
            self.inspect_path(info["path"], layer=info.get("layer"), role="mask")

    def register_results(self, folder):
        parent = QTreeWidgetItem(self.results_root, [Path(folder).name])
        paths = sorted(Path(folder).rglob("*"))
        for path in paths[:1500]:
            if any(part.endswith(".gdb") for part in path.relative_to(folder).parts[:-1]): continue
            if path.suffix.lower() not in (".gdb", ".gpkg", ".xlsx", ".tif", ".tiff", ".pdf"): continue
            icon = "🗄️" if path.suffix.lower() == ".gdb" else ("📦" if path.suffix.lower() == ".gpkg" else ("📊" if path.suffix.lower() == ".xlsx" else ("🗺️" if path.suffix.lower() in (".tif", ".tiff") else "📄")))
            item = QTreeWidgetItem(parent, [f"{icon} {path.relative_to(folder)}"])
            item.setData(0, Qt.UserRole, str(path))
            item.setToolTip(0, str(path))
        parent.setExpanded(True)

    def register_map_layer(self, name, layer_id, kind="vector", path=None, layer_name=None, crs=None, count=None):
        if layer_id in self.project_layers:
            existing = self.project_layers[layer_id]
            if existing.get("item") and hasattr(self, "group_layers"):
                self.group_layers.removeChild(existing["item"])
        icon = "🗺️" if kind == "raster" else "📍" if kind == "point" else "🔲" if kind == "polygon" else "〰️"
        item = QTreeWidgetItem(self.group_layers, [f"{icon} {name}"])
        item.setData(0, Qt.UserRole+1, layer_id)
        if path:
            item.setData(0, Qt.UserRole, str(path))
            item.setToolTip(0, f"{name}\n{path}\nCRS: {crs or 'Unknown'}")
        item.setCheckState(0, Qt.Checked)
        self.project_layers[layer_id] = {
            "name": name,
            "kind": kind,
            "path": path,
            "layer": layer_name,
            "crs": crs,
            "count": count,
            "item": item
        }
        self.update_tool_layer_selectors()
        return item

    def register_table_layer(self, name, path, layer_name=None, count=None):
        item = QTreeWidgetItem(self.group_tables, [f"📊 {name}"])
        item.setData(0, Qt.UserRole, str(path))
        if layer_name:
            item.setData(0, Qt.UserRole+2, str(layer_name))
        item.setToolTip(0, f"{name}\n{path}")
        return item

    def layer_menu(self, position):
        item = self.layers.itemAt(position)
        if item is None or item in (self.group_layers, self.group_tables, self.results_root):
            return
        menu = QMenu(self)
        if self.work_layer is not None and item is self.work_layer:
            zoom_act = menu.addAction(tr("menu_zoom_points", self.arabic))
            clear_act = menu.addAction(tr("clear_all", self.arabic))
            chosen = menu.exec(self.layers.viewport().mapToGlobal(position))
            if chosen is zoom_act:
                self.map.canvas.fit_points()
            elif chosen is clear_act:
                self.selected_keys.clear()
                self.user_points.clear()
                self.generated_points.clear()
                self.fill_stations()
            return
        if self.boundary_layer is not None and item is self.boundary_layer:
            zoom_act = menu.addAction(tr("menu_zoom_boundary", self.arabic))
            clear_act = menu.addAction(tr("menu_clear_boundary", self.arabic))
            chosen = menu.exec(self.layers.viewport().mapToGlobal(position))
            if chosen is zoom_act and self.boundary is not None:
                west, south, east, north = self.boundary.bounds
                from .mapview import world_pixel
                for zoom in range(17, 0, -1):
                    a, b_y = world_pixel(west, north, zoom)
                    c, d = world_pixel(east, south, zoom)
                    if abs(c - a) < max(100, self.map.canvas.width() - 80) and abs(d - b_y) < max(100, self.map.canvas.height() - 80):
                        break
                self.map.canvas.zoom = zoom
                self.map.canvas.center = world_pixel((west + east) / 2, (south + north) / 2, zoom)
                self.map.canvas.changed()
            elif chosen is clear_act:
                self.boundary = None
                self.map.canvas.boundary = None
                self.boundary_summary.setText(tr("study_boundary_layer", self.arabic) + ": " + tr("no_layers_hint", self.arabic))
                self.update_boundary_layer()
                self.map.canvas.update()
            return
        key = item.data(0, Qt.UserRole+1)
        if key:
            zoom_act = menu.addAction(tr("menu_zoom_layer", self.arabic))
            open_table_act = menu.addAction(tr("menu_open_table", self.arabic))
            remove_act = menu.addAction(tr("menu_remove_layer", self.arabic))
            chosen = menu.exec(self.layers.viewport().mapToGlobal(position))
            if chosen is remove_act:
                self.map.canvas.display_layers.pop(key, None)
                parent = item.parent() or self.layers.invisibleRootItem()
                parent.removeChild(item)
                self.project_layers.pop(key, None)
                self.update_tool_layer_selectors()
                self.map.canvas.update()
            elif chosen is open_table_act:
                meta = self.project_layers.get(key, {})
                if meta.get("path"):
                    self.request_preview(dict(path=meta["path"], layer=meta.get("layer")))
            elif chosen is zoom_act:
                display_layer = self.map.canvas.display_layers.get(key)
                if display_layer and display_layer.get("kind") == "raster":
                    _, bounds = display_layer["payload"]
                    west, south, east, north = bounds
                    from .mapview import world_pixel
                    for zoom in range(17, 0, -1):
                        a, b_y = world_pixel(west, north, zoom)
                        c, d = world_pixel(east, south, zoom)
                        if abs(c - a) < max(100, self.map.canvas.width() - 80) and abs(d - b_y) < max(100, self.map.canvas.height() - 80):
                            break
                    self.map.canvas.zoom = zoom
                    self.map.canvas.center = world_pixel((west + east) / 2, (south + north) / 2, zoom)
                    self.map.canvas.changed()

    def layer_visibility(self, item, column):
        if not hasattr(self,"map"): return
        if self.work_layer is not None and item is self.work_layer:
            self.map.canvas.points_visible = (item.checkState(0) == Qt.Checked)
        elif self.boundary_layer is not None and item is self.boundary_layer:
            self.map.canvas.boundary_visible = (item.checkState(0) == Qt.Checked)
        else:
            key = item.data(0, Qt.UserRole+1)
            if key in self.map.canvas.display_layers:
                self.map.canvas.display_layers[key]["visible"] = (item.checkState(0) == Qt.Checked)
        self.map.canvas.update()

    def open_layer_item(self, item, column):
        path=item.data(0,Qt.UserRole)
        if not path or self.job_thread: return
        if Path(path).suffix.lower() in (".tif",".tiff"):
            self.preview_raster_path=str(path)
            self.inspect_path(path)
        elif Path(path).suffix.lower()==".pdf": self.open_pdf_preview(path)
        else: self.request_preview(dict(path=path))

    def open_pdf_preview(self, path):
        self.start_request(dict(operation="pdf_preview",options=dict(path=str(path),page=0)))
