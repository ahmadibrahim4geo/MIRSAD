# -*- coding: utf-8 -*-
"""
High-Performance PySide6 Desktop GIS Map Canvas Example.
Demonstrates:
- Viewport transformation (Geographic coordinates to Screen pixels)
- Smooth Pan & Zoom navigation
- Point-in-polygon clipping
- Interactive coordinate readout
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PySide6.QtCore import Qt, QPointF, Signal

class GisMapCanvas(QWidget):
    coordinatesChanged = Signal(float, float) # (lon, lat)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setStyleSheet("background-color: #121318;")

        # Extent in Geographic Coordinates: [min_lon, min_lat, max_lon, max_lat]
        self.extent = [-180.0, -90.0, 180.0, 90.0]
        self.stations = []
        self.clip_polygon = []
        self._is_panning = False
        self._pan_start = None

    def set_extent(self, min_lon, min_lat, max_lon, max_lat):
        self.extent = [min_lon, min_lat, max_lon, max_lat]
        self.update()

    def set_stations(self, stations_list):
        """Expects list of dicts with 'longitude', 'latitude', 'name', 'insideMask'."""
        self.stations = stations_list
        self.update()

    def set_clip_mask(self, polygon_coords):
        """Expects list of [lon, lat] points."""
        self.clip_polygon = polygon_coords
        self.update()

    def geo_to_pixel(self, lon, lat):
        min_x, min_y, max_x, max_y = self.extent
        w = self.width()
        h = self.height()
        if max_x == min_x or max_y == min_y:
            return QPointF(0, 0)
        px = ((lon - min_x) / (max_x - min_x)) * w
        py = ((max_y - lat) / (max_y - min_y)) * h
        return QPointF(px, py)

    def pixel_to_geo(self, px, py):
        min_x, min_y, max_x, max_y = self.extent
        w = self.width()
        h = self.height()
        lon = min_x + (px / w) * (max_x - min_x)
        lat = max_y - (py / h) * (max_y - min_y)
        return lon, lat

    def mouseMoveEvent(self, event):
        pos = event.position()
        lon, lat = self.pixel_to_geo(pos.x(), pos.y())
        self.coordinatesChanged.emit(lon, lat)

        if self._is_panning and self._pan_start:
            delta = event.position() - self._pan_start
            self._pan_start = event.position()
            dx_geo = -(delta.x() / self.width()) * (self.extent[2] - self.extent[0])
            dy_geo = (delta.y() / self.height()) * (self.extent[3] - self.extent[1])
            self.extent = [
                self.extent[0] + dx_geo, self.extent[1] + dy_geo,
                self.extent[2] + dx_geo, self.extent[3] + dy_geo
            ]
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_panning = True
            self._pan_start = event.position()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_panning = False
            self._pan_start = None

    def wheelEvent(self, event):
        angle = event.angleDelta().y()
        factor = 0.85 if angle > 0 else 1.15
        center_x = (self.extent[0] + self.extent[2]) / 2.0
        center_y = (self.extent[1] + self.extent[3]) / 2.0
        half_w = ((self.extent[2] - self.extent[0]) / 2.0) * factor
        half_h = ((self.extent[3] - self.extent[1]) / 2.0) * factor
        self.extent = [center_x - half_w, center_y - half_h, center_x + half_w, center_y + half_h]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 1. Draw Clip Mask Polygon
        if self.clip_polygon:
            pen = QPen(QColor("#06b6d4"), 2, Qt.DashLine)
            brush = QBrush(QColor(6, 182, 212, 25))
            painter.setPen(pen)
            painter.setBrush(brush)
            points = [self.geo_to_pixel(pt[0], pt[1]) for pt in self.clip_polygon]
            from PySide6.QtGui import QPolygonF
            painter.drawPolygon(QPolygonF(points))

        # 2. Draw Station Points
        for st in self.stations:
            pt = self.geo_to_pixel(st["longitude"], st["latitude"])
            inside = st.get("insideMask", True)
            if inside:
                painter.setPen(QPen(QColor("#ffffff"), 1))
                painter.setBrush(QBrush(QColor("#06b6d4")))
                painter.drawEllipse(pt, 4, 4)
            else:
                painter.setPen(QPen(QColor("#334155"), 0.5))
                painter.setBrush(QBrush(QColor("#475569")))
                painter.drawEllipse(pt, 2.5, 2.5)
