"""Bounded desktop controls; popup size never determines workspace width."""
from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QComboBox, QProxyStyle, QStyle, QStyleFactory, QSizePolicy


class DesktopStyle(QProxyStyle):
    def __init__(self):
        super().__init__(QStyleFactory.create("Fusion"))

    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint == QStyle.SH_ComboBox_Popup:
            return 0
        return super().styleHint(hint, option, widget, returnData)


class CompactControls(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Polish and isinstance(obj, QComboBox):
            obj.setMaxVisibleItems(10)
            obj.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
            obj.setMinimumContentsLength(12)
            obj.setMinimumWidth(0)
            obj.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Fixed)
            obj.view().setTextElideMode(Qt.ElideMiddle)
            obj.view().setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            obj.view().setMaximumWidth(640)
            obj.currentTextChanged.connect(obj.setToolTip)
            obj.setToolTip(obj.currentText())
            if obj.isEditable():obj.lineEdit().setCursorPosition(0)
        return super().eventFilter(obj, event)
