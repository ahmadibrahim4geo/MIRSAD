"""Read-only, virtualized previews. Parsing is performed by the isolated job process."""
from pathlib import Path
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                              QComboBox, QTableView, QAbstractItemView, QScrollArea, QSpinBox)


class PreviewModel(QAbstractTableModel):
    def __init__(self, headers, rows, parent=None):
        super().__init__(parent)
        self.headers, self.rows = headers, rows

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role in (Qt.DisplayRole, Qt.ToolTipRole):
            value = self.rows[index.row()][index.column()]
            return "" if value is None else str(value)[:4000]
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self.headers[section] if orientation == Qt.Horizontal else str(section + 1)
        return None


class DataPreview(QWidget):
    requested = Signal(dict)
    use_requested = Signal(str,str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.path = None
        self.offset = 0
        self.layer = None
        box = QVBoxLayout(self)
        bar = QHBoxLayout()
        self.title = QLabel("معاينة للقراءة فقط · Read-only preview")
        self.title.setWordWrap(True)
        bar.addWidget(self.title, 1)
        self.sheets = QComboBox()
        self.sheets.setMinimumWidth(150)
        self.sheets.currentTextChanged.connect(lambda _: self.request(0))
        bar.addWidget(self.sheets)
        self.use_input=QPushButton("استخدام في الأداة / Use as input")
        self.use_input.setEnabled(False)
        self.use_input.clicked.connect(lambda:self.use_requested.emit(self.path,self.layer or ""))
        bar.addWidget(self.use_input)
        box.addLayout(bar)
        self.table = QTableView()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)
        box.addWidget(self.table, 1)
        bottom = QHBoxLayout()
        self.note = QLabel("اختر ملفًا من النتائج أو إضافة بيانات / Choose a result or Add Data")
        self.note.setWordWrap(True)
        bottom.addWidget(self.note, 1)
        self.previous = QPushButton("السابق / Previous")
        self.next = QPushButton("التالي / Next")
        self.previous.clicked.connect(lambda: self.request(max(0, self.offset - 500)))
        self.next.clicked.connect(lambda: self.request(self.offset + 500))
        for button in (self.previous, self.next):
            button.setEnabled(False)
            bottom.addWidget(button)
        box.addLayout(bottom)

    def request(self, offset):
        if self.path:
            self.requested.emit(dict(path=self.path, sheet=self.sheets.currentText() or None,
                                     layer=self.layer, offset=offset))

    def display(self, result):
        self.path, self.offset, self.layer = result["path"], result["offset"], result.get("layer")
        self.use_input.setEnabled(True)
        self.sheets.blockSignals(True)
        self.sheets.clear()
        self.sheets.addItems(result.get("sheets", []))
        self.sheets.setCurrentText(result.get("sheet") or "")
        self.sheets.setVisible(bool(result.get("sheets")))
        self.sheets.blockSignals(False)
        old = self.table.model()
        self.table.setModel(PreviewModel(result["headers"], result["rows"], self.table))
        if old: old.deleteLater()
        self.title.setText(Path(self.path).name + (" · " + self.layer if self.layer else ""))
        self.note.setText("Read-only · %d–%d · %d columns · %s" %
                          (self.offset + bool(result["rows"]), self.offset + len(result["rows"]),
                           len(result["headers"]), result.get("crs") or "Table"))
        self.previous.setEnabled(self.offset > 0)
        self.next.setEnabled(result.get("more", False))


class PdfPreview(QWidget):
    """Only bounded page images enter the UI; the PDF parser lives in a child process."""
    requested=Signal(dict)

    def __init__(self,parent=None):
        super().__init__(parent)
        self.path=None;self.page_count=0;self.image=None
        box=QVBoxLayout(self);bar=QHBoxLayout()
        self.title=QLabel();bar.addWidget(self.title,1)
        self.page=QSpinBox();self.page.setMinimum(1)
        self.page.valueChanged.connect(self.request_page)
        bar.addWidget(QLabel("الصفحة / Page"));bar.addWidget(self.page);box.addLayout(bar)
        self.scroll=QScrollArea();self.scroll.setWidgetResizable(True)
        self.picture=QLabel();self.picture.setAlignment(Qt.AlignTop|Qt.AlignHCenter)
        self.scroll.setWidget(self.picture);box.addWidget(self.scroll,1)

    def request_page(self,page):
        if self.path:self.requested.emit(dict(path=self.path,page=page-1))

    def display(self,result):
        self.path=result["path"];self.page_count=result["pages"]
        self.title.setText(Path(self.path).name+" · %d pages"%self.page_count)
        self.page.blockSignals(True);self.page.setMaximum(self.page_count)
        self.page.setValue(result["page"]+1);self.page.blockSignals(False)
        self.image=QPixmap(result["preview"])
        self.scale_page()

    def scale_page(self):
        if self.image is not None:
            self.picture.setPixmap(self.image.scaledToWidth(max(200,self.scroll.viewport().width()-30),Qt.SmoothTransformation))

    def resizeEvent(self,event):
        super().resizeEvent(event);self.scale_page()
