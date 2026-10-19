# -*- coding: utf-8 -*-
"""Desktop GIS Add Data browser, Coordinate Reference System (CRS) Picker, and import dialogs."""

import os
import string
from pathlib import Path
from PySide6.QtCore import Qt, Signal, QTimer, QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox,
    QLabel, QLineEdit, QMessageBox, QDoubleSpinBox, QListWidget, QListWidgetItem,
    QSplitter, QRadioButton, QButtonGroup, QPushButton, QFrame, QTextBrowser,
    QGroupBox, QFileDialog, QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QCheckBox
)
from .inputs import table_rows, vector_layers, vector_rows, import_points, make_point
from .i18n import tr


from .crspicker import CrsSelectionDialog


class GisAddDataDialog(QDialog):
    """
    ArcGIS Pro inspired Desktop GIS 'Add Data' browser.
    Left panel: Navigation tree (Project databases/folders, This PC drives, Favorites).
    Center: Dataset/layer contents table with Name, Type, Geometry, and CRS.
    Supports deep container inspection inside File Geodatabases (.gdb),
    GeoPackages (.gpkg), and Excel workbooks (.xlsx).
    """
    def __init__(self, initial_dir=None, parent=None):
        super().__init__(parent)
        self.arabic = getattr(parent, "arabic", False)
        self.setWindowTitle(tr("dlg_add_data_title", self.arabic))
        self.resize(880, 560)

        self.current_dir = Path(initial_dir or Path.home()).resolve()
        self.history = [self.current_dir]
        self.history_index = 0

        self.selected_path = None
        self.selected_layer = None
        self.selected_layers = []  # List of (path, layer_name, kind)
        self.selected_role = "stations"

        self.setup_ui()
        self.navigate_to(self.current_dir, record_history=False)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # Top Navigation Toolbar
        nav_toolbar = QHBoxLayout()
        nav_toolbar.setSpacing(6)

        self.btn_back = QPushButton("◀")
        self.btn_back.setFixedWidth(32)
        self.btn_back.setToolTip("Back")
        self.btn_back.clicked.connect(self.go_back)
        nav_toolbar.addWidget(self.btn_back)

        self.btn_forward = QPushButton("▶")
        self.btn_forward.setFixedWidth(32)
        self.btn_forward.setToolTip("Forward")
        self.btn_forward.clicked.connect(self.go_forward)
        nav_toolbar.addWidget(self.btn_forward)

        self.btn_up = QPushButton("▲")
        self.btn_up.setFixedWidth(32)
        self.btn_up.setToolTip(tr("up_directory", self.arabic))
        self.btn_up.clicked.connect(self.go_up_directory)
        nav_toolbar.addWidget(self.btn_up)

        self.path_edit = QLineEdit(str(self.current_dir))
        self.path_edit.returnPressed.connect(self.on_path_entered)
        nav_toolbar.addWidget(self.path_edit, 1)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(tr("search_datasets", self.arabic))
        self.search_box.setFixedWidth(200)
        self.search_box.textChanged.connect(self.filter_table_items)
        nav_toolbar.addWidget(self.search_box)

        self.btn_refresh = QPushButton("🔄")
        self.btn_refresh.setFixedWidth(32)
        self.btn_refresh.setToolTip("Refresh")
        self.btn_refresh.clicked.connect(lambda: self.navigate_to(self.current_dir, record_history=False))
        nav_toolbar.addWidget(self.btn_refresh)

        main_layout.addLayout(nav_toolbar)

        # Splitter: Left Places Tree | Center Data Items Table
        splitter = QSplitter(Qt.Horizontal)

        # Left Places Tree
        self.places_tree = QTreeWidget()
        self.places_tree.setHeaderHidden(True)
        self.places_tree.setMinimumWidth(180)
        self.places_tree.setMaximumWidth(240)
        self.populate_places_tree()
        self.places_tree.itemClicked.connect(self.on_place_clicked)
        splitter.addWidget(self.places_tree)

        # Right Container: Data Table
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        self.data_table = QTableWidget(0, 5)
        headers = [
            tr("col_dataset_name", self.arabic),
            tr("col_dataset_type", self.arabic),
            tr("col_dataset_geom", self.arabic),
            tr("col_dataset_crs", self.arabic),
            tr("col_dataset_count", self.arabic)
        ]
        self.data_table.setHorizontalHeaderLabels(headers)
        self.data_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.data_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.data_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.data_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.data_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.data_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.data_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.data_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.data_table.itemSelectionChanged.connect(self.on_table_selection_changed)
        self.data_table.itemDoubleClicked.connect(self.on_table_double_clicked)
        right_layout.addWidget(self.data_table, 1)

        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        main_layout.addWidget(splitter, 1)

        # Bottom Options: Filter + Roles + Buttons
        bottom_box = QVBoxLayout()
        bottom_box.setSpacing(6)

        # Role Radios
        role_bar = QHBoxLayout()
        role_label = QLabel(tr("contents_heading", self.arabic) + ":")
        role_bar.addWidget(role_label)

        self.role_stations = QRadioButton(tr("role_stations", self.arabic))
        self.role_mask = QRadioButton(tr("role_mask", self.arabic))
        self.role_context = QRadioButton(tr("role_context", self.arabic))
        self.role_stations.setChecked(True)

        self.role_group = QButtonGroup(self)
        self.role_group.addButton(self.role_stations, 1)
        self.role_group.addButton(self.role_mask, 2)
        self.role_group.addButton(self.role_context, 3)

        role_bar.addWidget(self.role_stations)
        role_bar.addWidget(self.role_mask)
        role_bar.addWidget(self.role_context)
        role_bar.addStretch()
        bottom_box.addLayout(role_bar)

        # Filter + Action Buttons
        footer = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItem(tr("filter_all_supported", self.arabic), "all")
        self.filter_combo.addItem(tr("filter_gdb", self.arabic), "gdb")
        self.filter_combo.addItem(tr("filter_gpkg", self.arabic), "gpkg")
        self.filter_combo.addItem(tr("filter_shp", self.arabic), "shp")
        self.filter_combo.addItem(tr("filter_raster", self.arabic), "raster")
        self.filter_combo.addItem(tr("filter_tables", self.arabic), "table")
        self.filter_combo.currentIndexChanged.connect(lambda: self.navigate_to(self.current_dir, record_history=False))
        footer.addWidget(self.filter_combo, 1)

        self.btn_add = QPushButton(tr("add_selected", self.arabic))
        self.btn_add.setObjectName("primary")
        self.btn_add.setEnabled(False)
        self.btn_add.clicked.connect(self.confirm_selection)
        footer.addWidget(self.btn_add)

        self.btn_cancel = QPushButton(tr("dialog_cancel", self.arabic))
        self.btn_cancel.clicked.connect(self.reject)
        footer.addWidget(self.btn_cancel)

        bottom_box.addLayout(footer)
        main_layout.addLayout(bottom_box)

    def populate_places_tree(self):
        self.places_tree.clear()

        # 1. Project
        project_root = QTreeWidgetItem(self.places_tree, ["Project" if not self.arabic else "المشروع"])
        project_root.setExpanded(True)

        cwd = Path.cwd()
        item_cwd = QTreeWidgetItem(project_root, [f"📁 Workspace ({cwd.name})"])
        item_cwd.setData(0, Qt.UserRole, str(cwd))

        project_dir = Path.home() / "Documents" / "MIRSAD Projects"
        if project_dir.exists():
            item_proj = QTreeWidgetItem(project_root, ["🗂️ MIRSAD Projects"])
            item_proj.setData(0, Qt.UserRole, str(project_dir))

        # 2. Computer / This PC
        pc_root = QTreeWidgetItem(self.places_tree, ["This PC" if not self.arabic else "هذا الكمبيوتر"])
        pc_root.setExpanded(True)

        home = Path.home()
        item_home = QTreeWidgetItem(pc_root, [f"🏠 Home ({home.name})"])
        item_home.setData(0, Qt.UserRole, str(home))

        docs = home / "Documents"
        if docs.exists():
            item_docs = QTreeWidgetItem(pc_root, ["📄 Documents"])
            item_docs.setData(0, Qt.UserRole, str(docs))

        # Windows root drives
        for drive in string.ascii_uppercase:
            p = Path(f"{drive}:/")
            if p.exists():
                drive_item = QTreeWidgetItem(pc_root, [f"💽 Drive ({drive}:)"])
                drive_item.setData(0, Qt.UserRole, str(p))

    def on_place_clicked(self, item, column):
        target = item.data(0, Qt.UserRole)
        if target and Path(target).exists():
            self.navigate_to(Path(target))

    def on_path_entered(self):
        target = Path(self.path_edit.text().strip())
        if target.exists():
            self.navigate_to(target)
        else:
            QMessageBox.warning(self, "Add Data", f"Path not found: {target}")

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.navigate_to(self.history[self.history_index], record_history=False)

    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.navigate_to(self.history[self.history_index], record_history=False)

    def go_up_directory(self):
        # If currently inside a container (.gdb or .gpkg or .xlsx)
        if self.current_dir.suffix.lower() in (".gdb", ".gpkg", ".xlsx", ".xls"):
            self.navigate_to(self.current_dir.parent)
            return

        parent = self.current_dir.parent
        if parent and parent != self.current_dir and parent.exists():
            self.navigate_to(parent)

    def navigate_to(self, target_dir, record_history=True):
        self.current_dir = Path(target_dir).resolve()
        self.path_edit.setText(str(self.current_dir))
        self.data_table.setRowCount(0)
        self.btn_add.setEnabled(False)

        if record_history:
            if self.history_index < len(self.history) - 1:
                self.history = self.history[:self.history_index + 1]
            self.history.append(self.current_dir)
            self.history_index = len(self.history) - 1

        self.btn_back.setEnabled(self.history_index > 0)
        self.btn_forward.setEnabled(self.history_index < len(self.history) - 1)

        # 1. Inside a File Geodatabase (.gdb)
        if self.current_dir.suffix.lower() == ".gdb":
            self.inspect_gdb(self.current_dir)
            return

        # 2. Inside a GeoPackage (.gpkg)
        if self.current_dir.suffix.lower() == ".gpkg":
            self.inspect_gpkg(self.current_dir)
            return

        # 3. Inside an Excel Workbook (.xlsx, .xls)
        if self.current_dir.suffix.lower() in (".xlsx", ".xls"):
            self.inspect_excel_sheets(self.current_dir)
            return

        # 4. Standard Directory Browsing
        self.browse_directory_contents()

    def browse_directory_contents(self):
        try:
            entries = sorted(self.current_dir.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
            filter_mode = self.filter_combo.currentData()

            for p in entries:
                if p.name.startswith("."):
                    continue

                # File Geodatabase container
                if p.is_dir() and p.suffix.lower() == ".gdb":
                    if filter_mode in ("all", "gdb"):
                        self.add_table_row(f"🗄️ {p.name}", "File Geodatabase", "Container", "—", "—", str(p), "gdb")
                # Regular Directory
                elif p.is_dir():
                    self.add_table_row(f"📁 {p.name}", "File Folder", "Folder", "—", "—", str(p), "dir")
                # GeoPackage
                elif p.is_file() and p.suffix.lower() == ".gpkg":
                    if filter_mode in ("all", "gpkg"):
                        self.add_table_row(f"📦 {p.name}", "GeoPackage", "Container", "—", "—", str(p), "gpkg")
                # Shapefile
                elif p.is_file() and p.suffix.lower() == ".shp":
                    if filter_mode in ("all", "shp"):
                        geom, crs, count = self.quick_probe_vector(p)
                        icon = "📍" if "Point" in geom else ("🔲" if "Polygon" in geom else "〰️")
                        self.add_table_row(f"{icon} {p.name}", "Shapefile", geom, crs, str(count or "—"), str(p), "shp")
                # Raster
                elif p.is_file() and p.suffix.lower() in (".tif", ".tiff", ".img", ".dem"):
                    if filter_mode in ("all", "raster"):
                        self.add_table_row(f"🗺️ {p.name}", "Raster Dataset", "Raster", "GeoTIFF", "1 Band", str(p), "raster")
                # Tabular
                elif p.is_file() and p.suffix.lower() in (".xlsx", ".xls"):
                    if filter_mode in ("all", "table"):
                        self.add_table_row(f"📊 {p.name}", "Excel Workbook", "Container", "—", "Sheets…", str(p), "excel")
                elif p.is_file() and p.suffix.lower() in (".csv", ".tsv"):
                    if filter_mode in ("all", "table"):
                        self.add_table_row(f"📄 {p.name}", "Delimited Table", "Table", "—", "—", str(p), "csv")
                # GeoJSON
                elif p.is_file() and p.suffix.lower() in (".geojson", ".json"):
                    if filter_mode in ("all", "shp"):
                        self.add_table_row(f"🌐 {p.name}", "GeoJSON Layer", "Vector", "EPSG:4326", "—", str(p), "shp")

        except Exception as exc:
            pass

    def inspect_gdb(self, gdb_path):
        """Deep inspection inside a File Geodatabase container."""
        try:
            layers = vector_layers(gdb_path)
            for name, kind in layers:
                icon = "📍" if "Point" in kind else ("🔲" if "Polygon" in kind else ("〰️" if "Line" in kind else "📊"))
                self.add_table_row(f"{icon} {name}", "Feature Class" if "Point" in kind or "Polygon" in kind or "Line" in kind else "Table",
                                   kind, "OpenFileGDB", "—", str(gdb_path), "db_layer", layer_name=name)
        except Exception:
            pass

    def inspect_gpkg(self, gpkg_path):
        """Deep inspection inside a GeoPackage container."""
        try:
            layers = vector_layers(gpkg_path)
            for name, kind in layers:
                icon = "📍" if "Point" in kind else ("🔲" if "Polygon" in kind else ("〰️" if "Line" in kind else "📊"))
                self.add_table_row(f"{icon} {name}", "GeoPackage Layer", kind, "GPKG", "—", str(gpkg_path), "db_layer", layer_name=name)
        except Exception:
            pass

    def inspect_excel_sheets(self, excel_path):
        """Inspects sheets of an Excel workbook as selectable tables."""
        try:
            import openpyxl
            wb = openpyxl.load_workbook(excel_path, read_only=True)
            for sheet in wb.sheetnames:
                self.add_table_row(f"📊 {sheet}", "Worksheet Table", "Table", "—", "—", str(excel_path), "excel_sheet", layer_name=sheet)
        except Exception:
            pass

    def quick_probe_vector(self, path):
        try:
            layers = vector_layers(path)
            if layers:
                name, kind = layers[0]
                return kind, "Layer CRS", ""
        except Exception:
            pass
        return "Vector", "—", ""

    def add_table_row(self, name_text, type_text, geom_text, crs_text, count_text, path_str, kind, layer_name=None):
        row = self.data_table.rowCount()
        self.data_table.insertRow(row)

        item_name = QTableWidgetItem(name_text)
        item_name.setData(Qt.UserRole, path_str)
        item_name.setData(Qt.UserRole + 1, kind)
        if layer_name:
            item_name.setData(Qt.UserRole + 2, layer_name)
        item_name.setData(Qt.UserRole + 3, geom_text)

        self.data_table.setItem(row, 0, item_name)
        self.data_table.setItem(row, 1, QTableWidgetItem(type_text))
        self.data_table.setItem(row, 2, QTableWidgetItem(geom_text))
        self.data_table.setItem(row, 3, QTableWidgetItem(crs_text))
        self.data_table.setItem(row, 4, QTableWidgetItem(count_text))

    def filter_table_items(self, query):
        query = query.strip().lower()
        for row in range(self.data_table.rowCount()):
            name = self.data_table.item(row, 0).text().lower()
            kind = self.data_table.item(row, 1).text().lower()
            match = not query or (query in name or query in kind)
            self.data_table.setRowHidden(row, not match)

    def on_table_selection_changed(self):
        selected_rows = self.data_table.selectionModel().selectedRows()
        if not selected_rows:
            self.btn_add.setEnabled(False)
            return

        first_item = self.data_table.item(selected_rows[0].row(), 0)
        kind = first_item.data(Qt.UserRole + 1)

        # Containers require double click to enter, not directly Add
        if kind in ("dir", "gdb", "gpkg", "excel") and len(selected_rows) == 1:
            self.btn_add.setEnabled(False)
            return

        self.btn_add.setEnabled(True)

        # Auto-suggest role based on geometry
        geom = first_item.data(Qt.UserRole + 3) or ""
        if "Polygon" in geom:
            self.role_mask.setChecked(True)
        elif "Point" in geom:
            self.role_stations.setChecked(True)
        else:
            self.role_context.setChecked(True)

    def on_table_double_clicked(self, item):
        row = item.row()
        name_item = self.data_table.item(row, 0)
        path = Path(name_item.data(Qt.UserRole))
        kind = name_item.data(Qt.UserRole + 1)

        if kind in ("dir", "gdb", "gpkg", "excel"):
            self.navigate_to(path)
        else:
            self.confirm_selection()

    def confirm_selection(self):
        selected_rows = self.data_table.selectionModel().selectedRows()
        if not selected_rows:
            return

        self.selected_layers = []
        for index in selected_rows:
            row = index.row()
            name_item = self.data_table.item(row, 0)
            path = Path(name_item.data(Qt.UserRole))
            kind = name_item.data(Qt.UserRole + 1)
            layer = name_item.data(Qt.UserRole + 2)
            geom = name_item.data(Qt.UserRole + 3)
            self.selected_layers.append({
                "path": path,
                "layer": layer,
                "kind": kind,
                "geometry": geom
            })

        first = self.selected_layers[0]
        self.selected_path = first["path"]
        self.selected_layer = first["layer"]

        if self.role_stations.isChecked():
            self.selected_role = "stations"
        elif self.role_mask.isChecked():
            self.selected_role = "mask"
        else:
            self.selected_role = "context"

        self.accept()


class ImportDialog(QDialog):
    """Point field mapping and coordinate entry dialog."""
    def __init__(self, path, parent=None, metadata=None):
        super().__init__(parent)
        self.arabic = getattr(parent, "arabic", False)
        self.path = Path(path)
        self.points = []
        self.options = None
        self.metadata = metadata
        self.setWindowTitle("Import Points" if not self.arabic else "استيراد نقاط المستخدم")
        self.resize(580, 440)
        box = QVBoxLayout(self)
        note = QLabel(str(self.path))
        note.setWordWrap(True)
        box.addWidget(note)
        form = QFormLayout()
        box.addLayout(form)
        self.layer = QComboBox()
        self.x, self.y, self.identifier, self.name = [QComboBox() for _ in range(4)]
        self.crs = QLineEdit("EPSG:4326")
        self.tabular = self.path.suffix.lower() in (".csv", ".xlsx", ".tsv")
        self.sample = QLabel()
        self.sample.setWordWrap(True)
        self.sample.setTextFormat(Qt.PlainText)

        layer_lbl = "Layer" if not self.arabic else "الطبقة"
        x_lbl = "X / Longitude / Easting" if not self.arabic else "X / خط الطول / الشرق"
        y_lbl = "Y / Latitude / Northing" if not self.arabic else "Y / دائرة العرض / الشمال"
        id_lbl = "Point ID / Code" if not self.arabic else "كود النقطة"
        name_lbl = "Point Name" if not self.arabic else "اسم النقطة"
        crs_lbl = "Input Coordinate Reference System (CRS)" if not self.arabic else "نظام إسناد المدخل الفعلي (CRS)"

        form.addRow(layer_lbl, self.layer)
        form.addRow(x_lbl, self.x)
        form.addRow(y_lbl, self.y)
        form.addRow(id_lbl, self.identifier)
        form.addRow(name_lbl, self.name)
        form.addRow(crs_lbl, self.crs)
        box.addWidget(self.sample)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        box.addWidget(buttons)
        buttons.accepted.connect(self.load)
        buttons.rejected.connect(self.reject)
        if metadata:
            self.layer.addItem(metadata.get("layer") or "—")
            self.layer.setEnabled(False)
            self.crs.setText(metadata.get("crs") or "EPSG:4326")
            self.crs.setReadOnly(not self.tabular)
            self.crs.setToolTip("Actual source CRS. Output reprojection is a separate setting.")
            self.set_fields(metadata["headers"], metadata["rows"])
            rec_txt = "records" if not self.arabic else "صف"
            self.sample.setText(f"{metadata.get('features', '')} {rec_txt}\n{self.sample.text()}")
            self.x.setEnabled(self.tabular)
            self.y.setEnabled(self.tabular)
        elif self.tabular:
            self.layer.setEnabled(False)
            headers, rows = table_rows(self.path)
            self.set_fields(headers, rows)
        else:
            self.layer.addItems([name for name, kind in vector_layers(self.path) if kind.startswith("Point")])
            if not self.layer.count():
                raise ValueError("This dataset has no Point layer.")
            self.x.setEnabled(False)
            self.y.setEnabled(False)
            self.layer.currentTextChanged.connect(self.inspect_layer)
            self.inspect_layer()

    def set_fields(self, headers, rows):
        for combo in (self.x, self.y, self.identifier, self.name):
            combo.clear()
            combo.addItems(["—"] + headers)
        for combo, candidates in ((self.x, ("longitude", "lon", "point_lon", "x", "easting")),
                                 (self.y, ("latitude", "lat", "point_lat", "y", "northing")),
                                 (self.identifier, ("station_id", "usaf", "id", "point_id")),
                                 (self.name, ("station_name", "name", "station"))):
            index = next((i + 1 for i, h in enumerate(headers) if h.lower() in candidates), 0)
            combo.setCurrentIndex(index)
        rec_txt = "records" if not self.arabic else "صف"
        self.sample.setText("%d %s\n%s" % (len(rows), rec_txt, str(rows[0])[:450] if rows else "Empty"))

    def inspect_layer(self):
        try:
            headers, rows, crs = vector_rows(self.path, self.layer.currentText(), self.crs.text())
            self.crs.setText(crs)
            self.set_fields(headers, rows)
        except Exception as exc:
            self.sample.setText(str(exc))

    def load(self):
        try:
            field = lambda combo: combo.currentText() if combo.currentIndex() > 0 else None
            if self.metadata:
                self.options = dict(path=str(self.path), x_field=field(self.x), y_field=field(self.y),
                                   id_field=field(self.identifier), name_field=field(self.name),
                                   source_crs=self.crs.text(), layer=self.metadata.get("layer"))
                self.accept()
                return
            self.points = import_points(self.path, field(self.x), field(self.y), field(self.identifier),
                                       field(self.name), self.crs.text(), self.layer.currentText() or None)
            self.accept()
        except Exception as exc:
            QMessageBox.warning(self, "Import", str(exc))


class PointDialog(QDialog):
    """Manual single-point coordinate creation dialog."""
    def __init__(self, parent=None, lon=31.2357, lat=30.0444):
        super().__init__(parent)
        self.arabic = getattr(parent, "arabic", False)
        self.point = None
        self.setWindowTitle("Enter Point Coordinates" if not self.arabic else "إدخال نقطة بإحداثيات")
        box = QVBoxLayout(self)
        form = QFormLayout()
        box.addLayout(form)
        self.identifier = QLineEdit("P001")
        self.name = QLineEdit("Point_1")
        self.crs = QLineEdit("EPSG:4326")
        self.x, self.y = QDoubleSpinBox(), QDoubleSpinBox()
        for field, value in ((self.x, lon), (self.y, lat)):
            field.setRange(-1e9, 1e9)
            field.setDecimals(7)
            field.setValue(value)

        id_lbl = "ID / Code" if not self.arabic else "الكود / المعرف"
        name_lbl = "Point Name" if not self.arabic else "اسم النقطة"
        crs_lbl = "CRS"
        x_lbl = "X / Longitude / Easting" if not self.arabic else "X / خط الطول / الشرق"
        y_lbl = "Y / Latitude / Northing" if not self.arabic else "Y / دائرة العرض / الشمال"

        form.addRow(id_lbl, self.identifier)
        form.addRow(name_lbl, self.name)
        form.addRow(crs_lbl, self.crs)
        form.addRow(x_lbl, self.x)
        form.addRow(y_lbl, self.y)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        box.addWidget(buttons)
        buttons.accepted.connect(self.create)
        buttons.rejected.connect(self.reject)

    def create(self):
        try:
            self.point = make_point(self.identifier.text(), self.name.text(), self.x.value(), self.y.value(), self.crs.text())
            self.accept()
        except Exception as exc:
            QMessageBox.warning(self, "Coordinates", str(exc))
