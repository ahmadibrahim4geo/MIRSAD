"""Native slippy map: Web Mercator tiles, pan/zoom, layers and point picking.

Only visible tiles are requested. Qt's HTTP disk cache honours provider cache
headers; this is not an offline tile downloader. No browser/ArcGIS dependency.
"""
import html
import math
import os
from collections import OrderedDict

from PySide6.QtCore import Qt,QPointF,QRectF,QTimer,QUrl,QStandardPaths,Signal,QEvent,QPoint,QSize
from PySide6.QtGui import QColor,QPainter,QPainterPath,QPen,QPixmap,QShortcut,QKeySequence
from PySide6.QtNetwork import QNetworkAccessManager,QNetworkRequest,QNetworkDiskCache,QNetworkReply
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QToolTip,QFrame,QToolButton,QSizePolicy
from .icons import outline_icon
from .mapcontrols import BasemapGallery,LABELS

ESRI="https://services.arcgisonline.com/ArcGIS/rest/services/"
BASEMAPS={
 "Esri Imagery + Labels":([ESRI+"World_Imagery/MapServer/tile/{z}/{y}/{x}",ESRI+"Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"],"Esri, Maxar, Earthstar Geographics, GIS User Community"),
 "Esri Imagery":([ESRI+"World_Imagery/MapServer/tile/{z}/{y}/{x}"],"Esri, Maxar, Earthstar Geographics, GIS User Community"),
 "Esri Streets":([ESRI+"World_Street_Map/MapServer/tile/{z}/{y}/{x}"],"Esri, HERE, Garmin, USGS, OpenStreetMap contributors, GIS User Community"),
 "Esri Topographic":([ESRI+"World_Topo_Map/MapServer/tile/{z}/{y}/{x}"],"Esri, HERE, Garmin, FAO, NOAA, USGS, OpenStreetMap contributors"),
 "Esri Light Gray + Labels":([ESRI+"Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}",ESRI+"Canvas/World_Light_Gray_Reference/MapServer/tile/{z}/{y}/{x}"],"Esri, HERE, Garmin, OpenStreetMap contributors"),
 "Esri Dark Gray + Labels":([ESRI+"Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}",ESRI+"Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}"],"Esri, HERE, Garmin, OpenStreetMap contributors"),
 "OpenStreetMap":(["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],"© OpenStreetMap contributors · openstreetmap.org/copyright"),
 "Offline / بدون خلفية":([],"WGS84 points · EPSG:3857 map display"),
}

def world_pixel(lon,lat,zoom):
    lat=max(-85.05112878,min(85.05112878,float(lat)))
    scale=256*2**zoom
    return ((lon+180)/360*scale,(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*scale)

def geographic(x,y,zoom):
    scale=256*2**zoom
    return ((x/scale*360-180+180)%360-180,math.degrees(math.atan(math.sinh(math.pi*(1-2*y/scale)))))

class SlippyMap(QWidget):
    pointClicked=Signal(str)
    coordinatePicked=Signal(float,float)
    coordinateMoved=Signal(float,float,int)
    tileStatus=Signal(str)
    viewChanged=Signal()

    def __init__(self,parent=None):
        super().__init__(parent)
        self.setMinimumSize(220,120)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.zoom=2; self.center=world_pixel(0,15,self.zoom)
        self.points=[]; self.selected=set(); self.boundary=None
        self.basemap="Esri Imagery + Labels"; self.dark=False; self.add_mode=False
        self.drag_start=None; self.drag_center=None; self.dragged=False
        self.cache=OrderedDict(); self.pending={}; self.queue=[]; self.failed=set(); self.tile_successes=0
        self.rasters=[];self.vector_overlays=[]
        self.display_layers={};self.layer_serial=0
        self.points_visible=True;self.boundary_visible=True
        self.manager=QNetworkAccessManager(self)
        cache=QNetworkDiskCache(self.manager)
        cache.setCacheDirectory(QStandardPaths.writableLocation(QStandardPaths.CacheLocation)+"/tiles")
        cache.setMaximumCacheSize(128*1024*1024); self.manager.setCache(cache)
        self.refresh=QTimer(self); self.refresh.setSingleShot(True); self.refresh.setInterval(120)
        self.refresh.timeout.connect(self.request_visible)

    def set_points(self,points,fit=True):
        self.points=list(points)
        if fit:self.fit_points()
        self.update()

    def add_raster(self,result):
        pixmap=QPixmap(result["preview"])
        if pixmap.isNull():raise ValueError("Raster preview could not be decoded.")
        key=self.store_layer("raster",(pixmap,result["bounds"]))
        west,south,east,north=result["bounds"]
        for zoom in range(17,0,-1):
            a,b=world_pixel(west,north,zoom);c,d=world_pixel(east,south,zoom)
            if abs(c-a)<max(100,self.width()-100) and abs(d-b)<max(100,self.height()-100):break
        self.zoom=zoom;self.center=world_pixel((west+east)/2,(south+north)/2,zoom);self.changed()
        return key

    def add_vectors(self,result):
        key=self.store_layer("vector",result["geometries"]);self.update();return key

    def store_layer(self,kind,payload):
        if len(self.display_layers)>=24:raise ValueError("Close a preview layer before adding another (maximum 24).")
        self.layer_serial+=1;key="preview_%d"%self.layer_serial
        self.display_layers[key]=dict(kind=kind,payload=payload,visible=True)
        return key

    def add_preview_points(self,result):
        key=self.store_layer("points",result["points"])
        if result["points"]:
            point=result["points"][0];self.center=world_pixel(point[0],point[1],self.zoom)
        self.changed();return key

    def set_basemap(self,name):
        if name not in BASEMAPS:name="Offline / بدون خلفية"
        self.queue=[]
        for reply in list(self.pending.values()):reply.abort()
        self.basemap=name; self.failed.clear(); self.queue=[]
        self.tileStatus.emit("Loading basemap…" if BASEMAPS[name][0] else "Offline map")
        self.update(); self.refresh.start()

    def fit_points(self):
        coords=[(p["longitude"],p["latitude"]) for p in self.points]
        if not coords and self.boundary is not None:
            a,b,c,d=self.boundary.bounds; coords=[(a,b),(c,d)]
        if not coords:return
        for z in range(17,0,-1):
            pixels=[world_pixel(x,y,z) for x,y in coords]
            xs,ys=zip(*pixels)
            if max(xs)-min(xs)<max(120,self.width()-100) and max(ys)-min(ys)<max(120,self.height()-90):break
        self.zoom=z; self.center=((min(xs)+max(xs))/2,(min(ys)+max(ys))/2)
        self.changed()

    def changed(self):
        scale=256*2**self.zoom
        self.center=(self.center[0]%scale,max(0,min(scale,self.center[1])))
        self.update();self.refresh.start();self.viewChanged.emit()

    def zoom_by(self,delta,anchor=None):
        new=max(1,min(19,self.zoom+delta))
        if new==self.zoom:return
        anchor=anchor or QPointF(self.width()/2,self.height()/2)
        dx,dy=anchor.x()-self.width()/2,anchor.y()-self.height()/2
        factor=2**(new-self.zoom)
        self.center=((self.center[0]+dx)*factor-dx,(self.center[1]+dy)*factor-dy)
        self.zoom=new;self.changed()

    def position(self,lon,lat):
        x,y=world_pixel(lon,lat,self.zoom)
        scale=256*2**self.zoom
        dx=(x-self.center[0]+scale/2)%scale-scale/2
        return QPointF(dx+self.width()/2,y-self.center[1]+self.height()/2)

    def tile_locations(self):
        left,top=self.center[0]-self.width()/2,self.center[1]-self.height()/2
        n=2**self.zoom
        for y in range(math.floor(top/256),math.floor((top+self.height())/256)+1):
            if not 0<=y<n:continue
            for x in range(math.floor(left/256),math.floor((left+self.width())/256)+1):
                yield x%n,y,x*256-left,y*256-top

    def request_visible(self):
        if os.environ.get("MIRSAD_OFFLINE")=="1":return
        self.queue=[]
        for template in BASEMAPS[self.basemap][0]:
            for x,y,_,_ in self.tile_locations():
                url=template.format(z=self.zoom,x=x,y=y)
                if url not in self.cache and url not in self.pending and url not in self.failed:
                    self.queue.append(url)
        self.pump()

    def pump(self):
        while self.queue and len(self.pending)<4:
            url=self.queue.pop(0)
            req=QNetworkRequest(QUrl(url))
            req.setRawHeader(b"User-Agent",b"MIRSAD-Desktop/0.2 (https://github.com/ahmadibrahim4geo/MIRSAD; ahmadibrahim.geo@gmail.com)")
            req.setAttribute(QNetworkRequest.CacheLoadControlAttribute,QNetworkRequest.PreferCache)
            req.setTransferTimeout(15000)
            reply=self.manager.get(req); self.pending[url]=reply
            reply.finished.connect(lambda u=url,r=reply:self.loaded(u,r))

    def loaded(self,url,reply):
        pixmap=QPixmap()
        if reply.error()==QNetworkReply.NetworkError.NoError and pixmap.loadFromData(reply.readAll()):
            self.cache[url]=pixmap; self.tile_successes+=1
            while len(self.cache)>400:self.cache.popitem(last=False)
            self.tileStatus.emit("Basemap ready" if not self.queue else "Loading map tiles…")
        else:
            self.failed.add(url)
            self.tileStatus.emit("Basemap unavailable · check connection / الخريطة غير متاحة؛ تحقق من الاتصال")
        self.pending.pop(url,None);reply.deleteLater();self.update();self.pump()

    def paintEvent(self,event):
        painter=QPainter(self); painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(),QColor("#212121" if self.dark else "#e7eaed"))
        locations=list(self.tile_locations())
        for template in BASEMAPS[self.basemap][0]:
            for x,y,px,py in locations:
                url=template.format(z=self.zoom,x=x,y=y)
                if url in self.cache:painter.drawPixmap(round(px),round(py),self.cache[url])
        if not self.cache or not BASEMAPS[self.basemap][0]:
            painter.setPen(QPen(QColor("#333333" if self.dark else "#c8cdd1"),1))
            for _,_,x,y in locations:painter.drawRect(QRectF(x,y,256,256))
        visible=[layer for layer in self.display_layers.values() if layer["visible"]]
        for pixmap,(west,south,east,north) in [layer["payload"] for layer in visible if layer["kind"]=="raster"]:
            top_left=self.position(west,north);bottom_right=self.position(east,south)
            painter.drawPixmap(QRectF(top_left,bottom_right),pixmap,QRectF(pixmap.rect()))
        painter.setPen(QPen(QColor("#edb956"),2));painter.setBrush(Qt.NoBrush)
        for layer in [item["payload"] for item in visible if item["kind"]=="vector"]:
            for geometry in layer:
                lines=[geometry["coordinates"]] if geometry["type"]=="LineString" else geometry["coordinates"]
                for line in lines:
                    path=QPainterPath()
                    for i,coord in enumerate(line):
                        point=self.position(*coord[:2])
                        if i==0:path.moveTo(point)
                        else:path.lineTo(point)
                    painter.drawPath(path)
        if self.boundary is not None and self.boundary_visible:
            polygons=[self.boundary] if self.boundary.geom_type=="Polygon" else self.boundary.geoms
            path=QPainterPath(); path.setFillRule(Qt.OddEvenFill)
            for polygon in polygons:
                for ring in [polygon.exterior,*polygon.interiors]:
                    coords=list(ring.coords)
                    if not coords:continue
                    path.moveTo(self.position(*coords[0][:2]))
                    for coord in coords[1:]:path.lineTo(self.position(*coord[:2]))
                    path.closeSubpath()
            painter.setPen(QPen(QColor("#f8c454"),2));painter.setBrush(QColor(248,196,84,30));painter.drawPath(path)
        painter.setPen(QPen(QColor("#ececec"),1));painter.setBrush(QColor("#69b7a4"))
        for layer in visible:
            if layer["kind"]=="points":
                for lon,lat in layer["payload"]:painter.drawEllipse(self.position(lon,lat),4,4)
        for point in self.points if self.points_visible else []:
            pos=self.position(point["longitude"],point["latitude"])
            if not self.rect().adjusted(-10,-10,10,10).contains(pos.toPoint()):continue
            selected=point["station_key"] in self.selected
            color="#ffca67" if selected else ("#ef8f56" if point.get("qa_status")=="review_required" else "#12c5d4")
            radius=6.5 if selected else 4.5
            painter.setPen(QPen(QColor("#ffffff"),1.5));painter.setBrush(QColor(color));painter.drawEllipse(pos,radius,radius)
        # Ground-distance scale at map centre, independent of output CRS.
        _,lat=geographic(*self.center,self.zoom)
        metres_per_px=156543.033928*math.cos(math.radians(lat))/2**self.zoom
        distance=metres_per_px*100
        rounded=10**math.floor(math.log10(max(1,distance)))
        rounded*=max(1,math.floor(distance/rounded))
        pixels=rounded/metres_per_px
        painter.fillRect(QRectF(12,self.height()-46,max(130,pixels+20),34),QColor("#242424" if self.dark else "#ffffff"))
        painter.setPen(QPen(QColor("#eeeeee" if self.dark else "#242424"),2)); y=self.height()-22
        painter.drawLine(QPointF(22,y),QPointF(22+pixels,y))
        painter.drawText(22,self.height()-29,("%.0f km"%(rounded/1000)) if rounded>=1000 else "%.0f m"%rounded)

    def resizeEvent(self,event):
        super().resizeEvent(event);self.changed()
    def showEvent(self,event):
        super().showEvent(event);self.refresh.start()
    def wheelEvent(self,event):
        self.zoom_by(1 if event.angleDelta().y()>0 else -1,event.position());event.accept()
    def mouseDoubleClickEvent(self,event):self.zoom_by(1,event.position())
    def mousePressEvent(self,event):
        if event.button()==Qt.LeftButton:
            self.setFocus(Qt.MouseFocusReason)
            self.drag_start=event.position();self.drag_center=self.center;self.dragged=False;self.setCursor(Qt.ClosedHandCursor)
    def mouseMoveEvent(self,event):
        pos=event.position()
        if self.drag_start is not None:
            delta=pos-self.drag_start
            if delta.manhattanLength()>4:self.dragged=True
            self.center=(self.drag_center[0]-delta.x(),self.drag_center[1]-delta.y())
            self.changed()
        lon,lat=geographic(self.center[0]+pos.x()-self.width()/2,self.center[1]+pos.y()-self.height()/2,self.zoom)
        self.coordinateMoved.emit(lon,lat,self.zoom)
        if not self.dragged:
            for point in self.points:
                if (self.position(point["longitude"],point["latitude"])-pos).manhattanLength()<12:
                    QToolTip.showText(event.globalPosition().toPoint(),"<qt>%s<br/>%.5f, %.5f</qt>"%(html.escape(point["name"]),point["latitude"],point["longitude"]),self);break
    def mouseReleaseEvent(self,event):
        if self.drag_start is None:return
        if not self.dragged:
            pos=event.position()
            if self.add_mode:
                lon,lat=geographic(self.center[0]+pos.x()-self.width()/2,self.center[1]+pos.y()-self.height()/2,self.zoom)
                self.coordinatePicked.emit(lon,lat)
            else:
                for point in self.points:
                    if (self.position(point["longitude"],point["latitude"])-pos).manhattanLength()<12:
                        self.pointClicked.emit(point["station_key"]);break
        self.drag_start=None;self.setCursor(Qt.CrossCursor if self.add_mode else Qt.OpenHandCursor)

class MapPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.arabic=False
        layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0);layout.setSpacing(0)
        self.canvas=SlippyMap();layout.addWidget(self.canvas,1)
        self.canvas.installEventFilter(self)
        self.tools=QFrame(self.canvas);self.tools.setObjectName("mapTools")
        tools=QHBoxLayout(self.tools);tools.setContentsMargins(4,4,4,4);tools.setSpacing(2)
        self.navigation=QFrame(self.canvas);self.navigation.setObjectName("mapTools")
        navigation=QVBoxLayout(self.navigation);navigation.setContentsMargins(4,4,4,4);navigation.setSpacing(2)
        self.basemap=self.make_button("basemap",self.tools);self.basemap.setCheckable(True)
        self.add=self.make_button("point",self.tools);self.add.setCheckable(True)
        tools.addWidget(self.basemap);tools.addWidget(self.add)
        self.plus=self.make_button("plus",self.navigation);self.minus=self.make_button("minus",self.navigation)
        self.fit=self.make_button("fit",self.navigation);self.world=self.make_button("globe",self.navigation)
        for button in (self.plus,self.minus,self.fit,self.world):navigation.addWidget(button)
        self.gallery=BasemapGallery(BASEMAPS,self.canvas,self.basemap)
        self.gallery.selected.connect(self.change_basemap)
        self.gallery.dismissed.connect(lambda:self.basemap.setChecked(False))
        self.basemap.clicked.connect(self.show_basemaps)
        self.hint=QLabel(self.canvas);self.hint.setObjectName("mapHint");self.hint.setWordWrap(True);self.hint.hide()
        status=QFrame();status.setObjectName("mapStatus");info=QVBoxLayout(status)
        info.setContentsMargins(8,4,8,4);info.setSpacing(1)
        self.attribution=QLabel();self.attribution.setWordWrap(True);self.attribution.setObjectName("mapAttribution")
        self.attribution.setTextFormat(Qt.PlainText);info.addWidget(self.attribution)
        self.attribution.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Preferred)
        row=QHBoxLayout();row.setContentsMargins(0,0,0,0)
        self.coordinates=QLabel();self.coordinates.setObjectName("mapReadout")
        self.coordinates.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Preferred)
        self.network_status=QLabel();self.network_status.setObjectName("mapReadout")
        self.network_status.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Preferred)
        row.addWidget(self.coordinates,2);row.addWidget(self.network_status,1);info.addLayout(row);layout.addWidget(status)
        self.fit.clicked.connect(self.canvas.fit_points)
        self.plus.clicked.connect(lambda:self.canvas.zoom_by(1));self.minus.clicked.connect(lambda:self.canvas.zoom_by(-1))
        self.world.clicked.connect(self.world_extent)
        self.add.toggled.connect(self.set_add_mode)
        self.canvas.coordinateMoved.connect(self.show_coordinates)
        self.canvas.tileStatus.connect(self.update_network_status)
        self.canvas.viewChanged.connect(self.update_zoom)
        self.shortcuts=[]
        for key,action in (("+",self.plus.click),("=",self.plus.click),("-",self.minus.click),("F",self.fit.click),("Escape",lambda:self.add.setChecked(False))):
            shortcut=QShortcut(QKeySequence(key),self.canvas);shortcut.setContext(Qt.WidgetShortcut)
            shortcut.activated.connect(action);self.shortcuts.append(shortcut)
        self.translate(False);self.change_basemap(self.canvas.basemap)

    def make_button(self,name,parent):
        button=QToolButton(parent);button.setObjectName("mapIcon");button.setIcon(outline_icon(name,True))
        button.setFixedSize(34,34);button.setIconSize(QSize(21,21));button.setFocusPolicy(Qt.StrongFocus)
        return button

    def translate(self,arabic):
        self.arabic=arabic;self.gallery.translate(arabic)
        labels=((self.basemap,"الخريطة الأساسية","Basemap"),(self.add,"إضافة نقطة على الخريطة · Esc للإلغاء","Place a point · Esc to cancel"),
                (self.plus,"تكبير (+)","Zoom in (+)"),(self.minus,"تصغير (−)","Zoom out (−)"),
                (self.fit,"عرض نطاق البيانات (F)","Zoom to data (F)"),(self.world,"عرض العالم","World extent"))
        for button,ar,en in labels:
            button.setToolTip(ar if arabic else en);button.setAccessibleName(button.toolTip())
        self.basemap.setToolTip(self.basemap.toolTip()+"\n"+LABELS[self.canvas.basemap][0 if arabic else 1])
        self.coordinates.setText("اسحب للتحريك · عجلة للتكبير" if arabic else "Drag to pan · Scroll to zoom")
        self.hint.setText("اضغط على الخريطة لإضافة نقطة. Esc للإلغاء." if arabic else "Click the map to place a point. Esc to cancel.")
        self.update_network_status(getattr(self,"last_network_status","Loading basemap…"))
        self.position_controls()

    def set_theme(self,dark):
        self.canvas.dark=dark;self.canvas.update()
        for button,name in ((self.basemap,"basemap"),(self.add,"point"),(self.plus,"plus"),(self.minus,"minus"),(self.fit,"fit"),(self.world,"globe")):
            button.setIcon(outline_icon(name,True))
        self.gallery.close_button.setIcon(outline_icon("close"))

    def show_basemaps(self):
        if not self.basemap.isChecked():self.gallery.hide();return
        self.position_gallery();self.gallery.show();self.gallery.raise_()
        self.gallery.cards[self.canvas.basemap].setFocus()

    def position_gallery(self):
        width=min(336,max(160,self.canvas.width()-24))
        height=min(500,max(80,self.canvas.height()-24))
        self.gallery.setGeometry(self.canvas.width()-width-12,12,width,height)

    def change_basemap(self,name):
        if name not in BASEMAPS:name="Offline / بدون خلفية"
        self.canvas.set_basemap(name);self.attribution.setText(BASEMAPS[name][1])
        self.gallery.set_current(name)
        self.basemap.setToolTip(("الخريطة الأساسية" if self.arabic else "Basemap")+"\n"+LABELS[name][0 if self.arabic else 1])

    def set_add_mode(self,value):
        self.canvas.add_mode=value;self.canvas.setCursor(Qt.CrossCursor if value else Qt.OpenHandCursor)
        self.hint.setVisible(value);self.position_controls();self.canvas.update()
        if value:self.canvas.setFocus()

    def world_extent(self):
        self.canvas.zoom=2;self.canvas.center=world_pixel(0,15,2);self.canvas.changed()

    def update_zoom(self):
        self.plus.setEnabled(self.canvas.zoom<19);self.minus.setEnabled(self.canvas.zoom>1)
        self.show_coordinates(*geographic(*self.canvas.center,self.canvas.zoom),self.canvas.zoom)

    def show_coordinates(self,lon,lat,zoom):
        text="WGS84 · %.5f, %.5f · Z%d"%(lon,lat,zoom)
        self.coordinates.setText(text);self.coordinates.setToolTip(text+" · Map EPSG:3857")

    def update_network_status(self,text):
        self.last_network_status=text
        translations={"Loading basemap…":"جارٍ تحميل الخلفية…","Offline map":"عرض بلا خلفية",
                      "Basemap ready":"الخلفية جاهزة","Loading map tiles…":"جارٍ تحميل الخريطة…"}
        if self.arabic:text=translations.get(text,"الخلفية غير متاحة؛ تحقق من الاتصال" if "unavailable" in text else text)
        self.network_status.setText(text);self.network_status.setToolTip(text)

    def position_controls(self):
        if not hasattr(self,"navigation"):return
        compact=self.canvas.height()<215
        self.fit.setVisible(not compact);self.world.setVisible(not compact)
        self.tools.adjustSize();self.navigation.adjustSize()
        self.tools.move(12,12);self.navigation.move(self.canvas.width()-self.navigation.width()-12,12)
        self.hint.setGeometry(12,60,max(96,min(260,self.canvas.width()-80)),48)
        if hasattr(self,"gallery"):self.position_gallery()

    def eventFilter(self,watched,event):
        if watched is self.canvas and event.type()==QEvent.Resize:self.position_controls()
        return super().eventFilter(watched,event)
