"""Native basemap style gallery. Illustrative swatches never request tiles."""
import sys
from PySide6.QtCore import Qt, QSize, Signal, QEvent, QTimer
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap, QIcon, QCursor
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QToolButton, QGridLayout, QButtonGroup, QScrollArea, QWidget, QApplication, QSizePolicy
from .icons import outline_icon

LABELS = {
    "Esri Imagery + Labels": ("صور جوية + أسماء", "Imagery + labels"),
    "Esri Imagery": ("صور جوية", "Imagery"),
    "Esri Streets": ("الشوارع", "Streets"),
    "Esri Topographic": ("طبوغرافية", "Topographic"),
    "Esri Light Gray + Labels": ("رمادي فاتح", "Light gray"),
    "Esri Dark Gray + Labels": ("رمادي داكن", "Dark gray"),
    "OpenStreetMap": ("OpenStreetMap", "OpenStreetMap"),
    "Offline / بدون خلفية": ("بدون خلفية", "No basemap"),
}


def style_swatch(name):
    """Schematic style sample, not a geographic image or downloaded tile."""
    colors = ("#314e36", "#21506a", "#9ba57b") if "Imagery" in name else (
        ("#33383d", "#475d70", "#737b82") if "Dark" in name else
        ("#e8e4d8", "#b4d7df", "#c4c5ac") if "Topographic" in name else
        ("#eceeed", "#cedbe0", "#c4c8ca") if "Gray" in name else
        ("#ece9df", "#a9d2df", "#ffffff"))
    image = QPixmap(256, 88)
    image.fill(QColor(colors[0]))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)
    if "Offline" in name:
        painter.fillRect(image.rect(), QColor("#dfe5e7"))
        painter.setPen(QPen(QColor("#b6c3c7"), 1))
        for x in range(0,256,24): painter.drawLine(x,0,x,88)
        for y in range(0,88,24): painter.drawLine(0,y,256,y)
    else:
        river = QPainterPath()
        river.moveTo(170, -10);river.cubicTo(80,25,215,40,110,98)
        painter.setPen(QPen(QColor(colors[1]), 24));painter.drawPath(river)
        painter.setPen(QPen(QColor(colors[2]), 4 if "Imagery" in name else 6))
        for x in (-15,45,115,220): painter.drawLine(x,0,x+55,88)
        painter.drawLine(0,51,256,28)
        if "Labels" in name or name in ("Esri Streets", "OpenStreetMap"):
            painter.setPen(QPen(QColor("#a9b8ac" if "Imagery" in name else "#9b9c96"), 3))
            painter.drawLine(26,24,60,24);painter.drawLine(189,62,222,62)
    painter.end()
    image.setDevicePixelRatio(2)
    return QIcon(image)


class BasemapGallery(QFrame):
    selected = Signal(str)
    dismissed = Signal()

    def __init__(self, names, parent, trigger):
        # An embedded transient panel survives focus loss to the screenshot UI.
        # Explicit pointer/keyboard dismissal is handled below, not WindowDeactivate.
        super().__init__(parent)
        self.setObjectName("basemapGallery")
        self.setAttribute(Qt.WA_NoMousePropagation)
        self.trigger=trigger;self.arabic=False;self.current=next(iter(names));self.names=list(names)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12,10,12,12);layout.setSpacing(8)
        header = QHBoxLayout()
        self.heading = QLabel();self.heading.setObjectName("section")
        self.close_button = QToolButton();self.close_button.setObjectName("mapIcon")
        self.close_button.setFixedSize(28,28);self.close_button.setIcon(outline_icon("close"))
        self.close_button.clicked.connect(self.close)
        header.addWidget(self.heading,1);header.addWidget(self.close_button);layout.addLayout(header)
        self.description=QLabel();self.description.setObjectName("muted");self.description.setWordWrap(True)
        layout.addWidget(self.description)
        self.scroll=QScrollArea();self.scroll.setObjectName("basemapStyles")
        self.scroll.setWidgetResizable(True);self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.body=QWidget();self.body.setObjectName("basemapBody")
        self.grid=QGridLayout(self.body);self.grid.setContentsMargins(0,0,0,0)
        self.grid.setSpacing(6);self.grid.setAlignment(Qt.AlignTop)
        self.scroll.setWidget(self.body);layout.addWidget(self.scroll,1)
        self.current_label=QLabel();self.current_label.setObjectName("basemapCurrent")
        self.current_label.setWordWrap(True);self.current_label.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Preferred)
        self.source_label=QLabel();self.source_label.setObjectName("muted");self.source_label.setWordWrap(True)
        self.source_label.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Preferred)
        layout.addWidget(self.current_label);layout.addWidget(self.source_label)
        self.group = QButtonGroup(self);self.group.setExclusive(True)
        self.cards = {}
        for index, name in enumerate(names):
            card = QToolButton();card.setObjectName("basemapCard")
            card.setCheckable(True);card.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            card.setIcon(style_swatch(name));card.setIconSize(QSize(128,40))
            card.setFixedHeight(74);card.setMinimumWidth(0);card.setFocusPolicy(Qt.StrongFocus)
            card.clicked.connect(lambda checked=False, selected=name:self.choose(selected))
            self.group.addButton(card);self.cards[name]=card
            self.grid.addWidget(card,index//2,index%2)
        self.translate(False)
        self.pointer_timer=QTimer(self);self.pointer_timer.setInterval(30)
        self.pointer_timer.timeout.connect(self.check_outside_pointer)
        self.pointer_state=None
        if sys.platform=="win32":
            import ctypes
            self.pointer_state=ctypes.windll.user32.GetAsyncKeyState
        self.pointer_down=False
        self.hide();self.scroll.viewport().installEventFilter(self)
        QApplication.instance().installEventFilter(self)

    def translate(self, arabic):
        self.arabic=arabic
        self.setLayoutDirection(Qt.RightToLeft if arabic else Qt.LeftToRight)
        self.heading.setText("الخريطة الأساسية" if arabic else "Basemap")
        self.setAccessibleName(self.heading.text())
        self.description.setText("اختر مظهر الخريطة. انقر خارج اللوحة لإغلاقها." if arabic else "Choose a map style. Click outside to close.")
        self.close_button.setToolTip("إغلاق لوحة الخلفيات" if arabic else "Close basemap panel")
        self.close_button.setAccessibleName(self.close_button.toolTip())
        for name,card in self.cards.items():
            card.setText(LABELS[name][0 if arabic else 1]);card.setToolTip(name)
            card.setAccessibleName(card.text())
        self.set_current(self.current)

    def set_current(self, name):
        self.current=name
        self.cards[name].setChecked(True)
        self.current_label.setText(("الحالي: " if self.arabic else "Current: ")+LABELS[name][0 if self.arabic else 1])
        if "Imagery" in name:
            source="Esri · صور جوية" if self.arabic else "Esri · imagery"
        elif "Esri" in name:source="Esri · خرائط مرجعية" if self.arabic else "Esri · reference cartography"
        elif name=="OpenStreetMap":source="OpenStreetMap · بيانات مجتمعية" if self.arabic else "OpenStreetMap · community mapping"
        else:source="عرض الطبقات المحلية بدون خلفية إنترنت" if self.arabic else "Local layers without an online basemap"
        self.source_label.setText(source)

    def choose(self, name):
        self.set_current(name);self.selected.emit(name);self.hide()

    def reflow(self):
        width=self.scroll.viewport().width()
        columns=2 if width>=272 else 1
        for index,name in enumerate(self.names):
            card=self.cards[name];self.grid.addWidget(card,index//columns,index%columns)
            card.setFixedWidth(max(80,(width-6*(columns-1))//columns))

    def resizeEvent(self,event):
        super().resizeEvent(event)
        compact=self.height()<260
        self.description.setVisible(not compact);self.source_label.setVisible(not compact)
        self.current_label.setVisible(self.height()>=180)
        short=self.height()<180
        self.layout().setContentsMargins(8,8,8,8) if short else self.layout().setContentsMargins(12,10,12,12)
        self.layout().setSpacing(4 if short else 8)
        self.close_button.setFixedSize(24 if short else 28,24 if short else 28)
        for card in self.cards.values():
            card.setToolButtonStyle(Qt.ToolButtonTextBesideIcon if short else Qt.ToolButtonTextUnderIcon)
            card.setIconSize(QSize(20,20) if short else QSize(128,40))
            card.setFixedHeight(32 if short else 74)
        self.reflow()

    def eventFilter(self,watched,event):
        if watched is self.scroll.viewport() and event.type()==QEvent.Resize:
            self.reflow()
        if self.isVisible():
            if event.type()==QEvent.MouseButtonPress and isinstance(watched,QWidget):
                inside=watched is self or self.isAncestorOf(watched)
                trigger=watched is self.trigger or self.trigger.isAncestorOf(watched)
                if not inside and not trigger:
                    self.hide();return True
            if event.type()==QEvent.KeyPress and event.key()==Qt.Key_Escape:
                self.hide();self.trigger.setFocus();return True
        return super().eventFilter(watched,event)

    def showEvent(self,event):
        super().showEvent(event)
        if self.pointer_state:
            self.pointer_down=any(self.pointer_state(key)&0x8000 for key in (1,2,4))
            self.pointer_timer.start()

    def check_outside_pointer(self):
        # Qt receives no pointer events after focus moves to another application.
        # Read only mouse buttons while this panel is visible, without a hook.
        states=[self.pointer_state(key) for key in (1,2,4)]
        down=any(state&0x8000 for state in states)
        pressed=(down and not self.pointer_down) or any(state&1 for state in states)
        self.pointer_down=down
        if pressed:
            position=QCursor.pos()
            inside=self.rect().contains(self.mapFromGlobal(position))
            trigger=self.trigger.rect().contains(self.trigger.mapFromGlobal(position))
            if not inside and not trigger:self.hide()

    def hideEvent(self, event):
        super().hideEvent(event)
        if hasattr(self,"pointer_timer"):self.pointer_timer.stop()
        self.dismissed.emit()
