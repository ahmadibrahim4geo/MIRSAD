"""Small scalable outline icons, drawn locally without fonts or web assets."""
from PySide6.QtCore import QByteArray, QRectF, QSize, Qt
from PySide6.QtGui import QIcon, QIconEngine, QPainter, QPixmap, QPalette
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

PATHS = {
    "folder": '<path d="M3 7V5a2 2 0 0 1 2-2h5l2 3h7a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z"/>',
    "star": '<path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-2.9-5.6 2.9 1.1-6.2L3 9.6l6.2-.9L12 3Z"/>',
    "basemap": '<path d="m12 3 9 5-9 5-9-5 9-5Zm-9 9 9 5 9-5M3 16l9 5 9-5"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "minus": '<path d="M5 12h14"/>',
    "fit": '<path d="M8 4H4v4m12-4h4v4M4 16v4h4m12-4v4h-4"/><circle cx="12" cy="12" r="3"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18M5 6.5h14M5 17.5h14"/>',
    "point": '<path d="M16.5 11.5c0 4-4.5 8.5-4.5 8.5s-7-6-7-11a7 7 0 0 1 10-6"/><circle cx="12" cy="9" r="2"/><path d="M19 2v6m-3-3h6"/>',
    "map": '<path d="m3 5 6-2 6 2 6-2v16l-6 2-6-2-6 2V5Zm6-2v16m6-14v16"/>',
    "table": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M9 9v11M3 14h18"/>',
    "tasks": '<path d="m3 6 2 2 3-4m3 2h10M3 13l2 2 3-4m3 2h10M3 20h5m3 0h10"/>',
    "file": '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9l-6-6Zm0 0v6h6M8 13h8m-8 4h6"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10v.2"/>',
    "pdf": '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9l-6-6Zm0 0v6h6M8 16l3-4 3 4 2-2"/>',
    "close": '<path d="m6 6 12 12M6 18 18 6"/>',
}


class OutlineIcon(QIconEngine):
    def __init__(self, name, checked_white=False):
        super().__init__()
        self.name = name
        self.checked_white = checked_white

    def clone(self):
        return OutlineIcon(self.name,self.checked_white)

    def paint(self, painter, rect, mode, state):
        palette = QApplication.palette()
        color = palette.color(QPalette.Disabled if mode == QIcon.Disabled else QPalette.Active, QPalette.WindowText).name()
        if state == QIcon.On and self.checked_white:
            color = "#ffffff"
        svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%s" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round">%s</svg>' % (color, PATHS[self.name])
        QSvgRenderer(QByteArray(svg.encode())).render(painter, QRectF(rect))

    def pixmap(self, size, mode, state):
        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        self.paint(painter, pixmap.rect(), mode, state)
        painter.end()
        return pixmap


def outline_icon(name, checked_white=False):
    return QIcon(OutlineIcon(name,checked_white))
