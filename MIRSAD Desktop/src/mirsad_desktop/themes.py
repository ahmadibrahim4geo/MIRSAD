# -*- coding: utf-8 -*-
"""MIRSAD Desktop theme system: Neutral charcoal and consistent light mode."""

def stylesheet(dark):
    from .catalogue import asset_dir
    check=(asset_dir()/"check.svg").as_posix()
    if dark:
        # Neutral charcoal palette
        bg = "#181818"
        panel = "#1f1f1f"
        raised = "#292929"
        text = "#ffffff"
        text_sub = "#d0d0d0"
        muted = "#aaaaaa"
        border = "#393939"
        border_strong = "#686868"
        accent = "#0b6a75"
        accent_hover = "#08525d"
        accent_active = "#14b8a6"
        gridline = "#393939"
        selection = "#363636"
        header_bg = "#242424"
    else:
        # High-Contrast Pure Light Palette (Zero invisible text bugs)
        bg = "#f7f7f7"
        panel = "#ffffff"
        raised = "#ededed"
        text = "#171717"
        text_sub = "#333333"
        muted = "#595959"
        border = "#d0d0d0"
        border_strong = "#aaaaaa"
        accent = "#0b6a75"
        accent_hover = "#08525d"
        accent_active = "#0d9488"
        gridline = "#d2d2d2"
        selection = "#dedede"
        header_bg = "#f7f7f7"

    return f"""
    QWidget {{
        font-family: 'Segoe UI', 'Cairo', -apple-system, sans-serif;
        font-size: 10pt;
        color: {text};
    }}
    QMainWindow, QWidget#workspace {{
        background-color: {bg};
    }}
    QDialog, QMessageBox, QMenu, QCalendarWidget, QTextBrowser {{
        background-color: {panel};
        color: {text};
    }}
    QFrame#header, QFrame#footer, QFrame#sidebar, QGroupBox, QTabWidget::pane {{
        background-color: {panel};
        border: 1px solid {border};
        border-radius: 5px;
    }}
    QFrame#sidebar {{
        border-radius: 5px;
    }}
    QLabel {{
        background: transparent;
        color: {text};
    }}
    QLabel#heading {{
        font-size: 15pt;
        font-weight: 700;
        color: {text};
    }}
    QLabel#section {{
        font-size: 11pt;
        font-weight: 600;
        color: {text};
    }}
    QFrame#crsCurrentPanel {{
        background: {raised}; border: 1px solid {border}; border-radius: 6px;
    }}
    QTreeWidget#crsTree::item {{ padding: 3px 0; }}
    QLabel#muted {{
        color: {muted};
        font-size: 9pt;
    }}
    QLabel#mapAttribution {{
        padding: 0;
        background: transparent;
        color: {muted};
        border: 0;
        font-size: 8pt;
    }}
    QFrame#mapStatus {{
        background: {panel};
        border-top: 1px solid {border};
    }}
    QLabel#mapReadout {{ color: {muted}; font-size: 8pt; }}
    QFrame#mapTools, QFrame#basemapGallery {{
        background: {panel}; border: 1px solid {border_strong}; border-radius: 9px;
    }}
    QToolButton#mapIcon {{
        background: transparent; border: 1px solid transparent;
        border-radius: 6px; padding: 0;
    }}
    QToolButton#mapIcon:hover {{ background: {raised}; border-color: {border}; }}
    QToolButton#mapIcon:pressed {{ background: {selection}; }}
    QToolButton#mapIcon:checked {{ background: {accent}; border-color: {accent}; }}
    QToolButton#mapIcon:focus {{ border-color: {accent_active}; }}
    QToolButton#basemapCard {{
        background: {raised}; color: {text}; border: 1px solid {border};
        border-radius: 7px; padding: 5px 2px; font-size: 9pt;
    }}
    QToolButton#basemapCard:hover {{ border-color: {border_strong}; background: {selection}; }}
    QToolButton#basemapCard:checked, QToolButton#basemapCard:focus {{
        border: 2px solid {accent_active}; background: {panel}; color: {text};
    }}
    QToolButton#basemapCard:focus:!checked {{ border: 1px dashed {border_strong}; }}
    QLabel#basemapCurrent {{ color: {text}; font-weight: 600; padding-top: 5px; }}
    QScrollArea#basemapStyles, QWidget#basemapBody {{ background: {panel}; border: 0; }}
    QListWidget#guideContents::item {{
        padding: 7px 8px; margin: 1px 0; border-radius: 4px;
        color: {text_sub}; font-size: 10pt;
    }}
    QListWidget#guideContents::item:hover {{ background: {raised}; }}
    QListWidget#guideContents::item:selected {{ background: {selection}; color: {text}; }}
    QTextBrowser#guideDocument {{
        background: {panel}; color: {text}; border: 1px solid {border}; border-radius: 6px;
    }}
    QLabel#mapHint {{
        background: {panel}; color: {text}; border: 1px solid {accent};
        border-radius: 7px; padding: 6px 9px; font-size: 9pt;
    }}
    QTabWidget#viewerTabs::pane {{ border: 0; border-top: 1px solid {border}; border-radius: 0; }}
    QTabWidget#viewerTabs QTabBar {{ background: {bg}; }}
    QTabWidget#viewerTabs QTabBar::tab {{
        background: transparent; color: {muted}; padding: 9px 12px;
        border: 0; border-bottom: 2px solid transparent; margin-right: 3px;
        min-height: 19px; font-size: 9pt;
    }}
    QTabWidget#viewerTabs QTabBar::tab:hover {{ background: {raised}; color: {text}; }}
    QTabWidget#viewerTabs QTabBar::tab:selected {{
        background: {panel}; color: {text}; border-bottom: 2px solid {accent_active};
    }}
    QTabWidget#viewerTabs QTabBar QToolButton {{
        background: {panel}; color: {text}; border: 1px solid {border}; width: 24px;
    }}
    QScrollArea {{ background: {panel}; border: 0; }}
    QScrollArea > QWidget > QWidget {{ background: {panel}; }}
    QMenuBar, QStatusBar, QToolBar {{ background: {panel}; color: {text}; }}
    QHeaderView {{ background: {raised}; }}
    QTableCornerButton::section {{ background: {raised}; border: 1px solid {border}; }}
    QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {{
        background-color: {raised};
        border: 1px solid {border};
        border-radius: 5px;
        padding: 5px 8px;
        min-height: 22px;
        color: {text};
        selection-background-color: {selection};
        selection-color: {text};
    }}
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
        border: 1px solid {accent};
    }}
    QComboBox QAbstractItemView {{
        background-color: {panel};
        color: {text};
        border: 1px solid {border_strong};
        selection-background-color: {selection};
        selection-color: {text};
    }}
    QPushButton {{
        background-color: {raised};
        color: {text};
        border: 1px solid {border};
        padding: 6px 12px;
        border-radius: 5px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: {border};
        border-color: {border_strong};
        color: {text};
    }}
    QPushButton:pressed {{
        background-color: {selection};
    }}
    QPushButton:checked, QPushButton#primary {{
        background-color: {accent};
        color: #ffffff;
        border-color: {accent_hover};
        font-weight: 600;
    }}
    QPushButton#primary:hover {{
        background-color: {accent_hover};
    }}
    QPushButton:disabled {{
        color: {muted};
        background-color: {panel};
        border-color: {border};
    }}
    QListWidget#navigation {{
        background: transparent;
        border: 0;
        outline: 0;
        font-size: 10pt;
    }}
    QListWidget#navigation::item {{
        padding: 6px 8px;
        margin: 2px 0;
        border-radius: 6px;
        color: {text_sub};
    }}
    QListWidget#navigation::item:hover {{
        background-color: {raised};
        color: {text};
    }}
    QListWidget#navigation::item:selected {{
        background-color: {selection};
        color: {text};
        font-weight: 600;
        border: 1px solid {accent};
    }}
    QListWidget, QTreeWidget, QTableWidget, QTableView, QPlainTextEdit {{
        background-color: {panel};
        alternate-background-color: {raised};
        border: 1px solid {border};
        border-radius: 6px;
        gridline-color: {gridline};
        color: {text};
        selection-background-color: {selection};
        selection-color: {text};
    }}
    QHeaderView::section {{
        background-color: {header_bg};
        color: {text};
        border: 0;
        border-bottom: 1px solid {border_strong};
        border-right: 1px solid {border};
        padding: 6px 8px;
        font-weight: 600;
        font-size: 9.5pt;
    }}
    QTableWidget::indicator, QCheckBox::indicator, QTreeWidget::indicator {{
        width: 15px;
        height: 15px;
        border: 1px solid {border_strong};
        border-radius: 3px;
        background-color: {panel};
    }}
    QTableWidget::indicator:checked, QCheckBox::indicator:checked, QTreeWidget::indicator:checked {{
        background-color: {accent};
        border-color: {accent};
        image: url("{check}");
    }}
    QCheckBox {{
        spacing: 8px;
        padding: 3px;
        color: {text};
    }}
    QGroupBox {{
        margin-top: 14px;
        padding: 14px 10px 10px 10px;
        font-weight: 600;
        color: {text};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        padding: 0 8px;
        color: {text};
    }}
    QScrollArea {{
        border: 0;
        background: transparent;
    }}
    QScrollBar::add-page, QScrollBar::sub-page {{ background: none; border: 0; }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; height: 0; }}
    QScrollBar:vertical {{
        background-color: {bg};
        width: 10px;
        border: 0;
    }}
    QScrollBar::handle:vertical {{
        background-color: {border_strong};
        min-height: 28px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {muted};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background-color: {bg};
        height: 10px;
        border: 0;
    }}
    QScrollBar::handle:horizontal {{
        background-color: {border_strong};
        min-width: 28px;
        border-radius: 5px;
    }}
    QProgressBar {{
        background-color: {raised};
        border: 1px solid {border};
        border-radius: 5px;
        min-height: 20px;
        text-align: center;
        color: {text};
        font-weight: 600;
    }}
    QProgressBar::chunk {{
        background-color: {accent};
        border-radius: 4px;
    }}
    QTabBar::tab {{
        background-color: {panel};
        padding: 7px 9px;
        border: 1px solid {border};
        border-bottom: 2px solid transparent;
        color: {muted};
        font-weight: 500;
    }}
    QTabBar::tab:hover {{
        color: {text};
        background-color: {raised};
    }}
    QTabBar::tab:selected {{
        background-color: {raised};
        color: {text};
        border-bottom: 2px solid {accent};
        font-weight: 600;
    }}
    QTabBar::tab:disabled {{
        color: {muted};
    }}
    QMenu {{
        border: 1px solid {border_strong};
        border-radius: 6px;
        padding: 4px 0;
    }}
    QMenu::item {{
        padding: 6px 20px;
        color: {text};
    }}
    QMenu::item:selected {{
        background-color: {selection};
        color: {text};
    }}
    QMenu::separator {{
        height: 1px;
        background: {border};
        margin: 4px 8px;
    }}
    QSplitter::handle {{
        background-color: {border};
    }}
    QToolTip {{
        background-color: {panel};
        color: {text};
        border: 1px solid {border_strong};
        padding: 6px;
        border-radius: 4px;
        font-size: 9pt;
    }}
    """


def apply_application_theme(app, dark):
    from PySide6.QtGui import QColor, QPalette
    from .widgets import DesktopStyle
    if not isinstance(app.style(), DesktopStyle):
        app.setStyle(DesktopStyle())
    palette = QPalette()
    c = dict(window="#181818" if dark else "#f7f7f7", base="#1f1f1f" if dark else "#ffffff",
             button="#292929" if dark else "#ededed", text="#f5f5f5" if dark else "#171717",
             muted="#aaaaaa" if dark else "#595959", selection="#363636" if dark else "#dedede")
    roles = {"Window":"window", "WindowText":"text", "Base":"base", "AlternateBase":"button",
             "ToolTipBase":"base", "ToolTipText":"text", "Text":"text", "Button":"button",
             "ButtonText":"text", "Highlight":"selection", "HighlightedText":"text", "PlaceholderText":"muted"}
    for group in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
        for role, key in roles.items():
            if group == QPalette.Disabled and role in ("Text", "WindowText", "ButtonText"):key="muted"
            palette.setColor(group, getattr(QPalette,role), QColor(c[key]))
        palette.setColor(group, QPalette.Link, QColor("#65d1dd" if dark else "#08525d"))
    app.setPalette(palette)
    app.setStyleSheet(stylesheet(dark))
