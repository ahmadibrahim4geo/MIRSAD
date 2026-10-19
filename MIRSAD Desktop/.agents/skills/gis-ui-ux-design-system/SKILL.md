---
name: gis-ui-ux-design-system
description: >-
  Design and polish professional UI/UX for desktop GIS applications inspired by modern GIS suites
  (ArcGIS Pro, QGIS, RustGIS) and OpenAI Codex Dark Mode. Use whenever styling GIS widgets,
  ribbons, dark themes, attribute tables, cartographic print layouts, or map navigation controls.
---

# GIS UI/UX Design System & Theme Guide

This skill establishes visual identity guidelines, layout standards, and styling tokens for building modern, professional Desktop GIS user interfaces.

It synthesizes design patterns from:
- **OpenAI Codex Dark IDE Aesthetic**: Layered slate/charcoal gradients, hairline borders, crisp white headers, silvery gray secondary text, and subtle glowing cyan/amber accents.
- **RustGIS Ribbon & Viewports** (`opengeos/RustGIS`): High-density, compact GIS tools arranged logically.
- **ArcGIS Pro & QGIS Docking Layouts**: Left Table of Contents (TOC), Right Processing Toolbox, Center Document Tabs (Map, Table, Graphs, Layout), and Bottom Status Bar.

---

## 1. Color Palette & Design Tokens (Codex Dark Mode)

```css
/* Core Design Tokens */
:root {
  /* Surfaces & Backgrounds */
  --codex-bg-app:        #0d0f12; /* Deepest canvas / status bar */
  --codex-bg-titlebar:   linear-gradient(180deg, #1f2129 0%, #16171e 100%);
  --codex-bg-menubar:    #16171d;
  --codex-bg-ribbon:     linear-gradient(180deg, #1c1d25 0%, #14151a 100%);
  --codex-bg-dock:       #14151a; /* Sidebar & panels base */
  --codex-bg-panel:      linear-gradient(180deg, #1c1d25 0%, #16171e 100%);
  --codex-bg-card:       #191a22; /* Normal item background */
  --codex-bg-card-hover: #222430; /* Hover state */
  --codex-bg-active:     #262938; /* Active / selected state */
  --codex-bg-input:      #101116; /* Input & text boxes */

  /* Hairline Borders (Crisp 1px) */
  --codex-border-subtle: #252733;
  --codex-border-strong: #333646;
  --codex-border-focus:  #38bdf8;

  /* Typography Contrast Hierarchy */
  --codex-text-primary:   #ffffff; /* Pure white: Titles, active tabs, key metrics */
  --codex-text-secondary: #cbd5e1; /* Silvery gray: Body labels, table cells */
  --codex-text-muted:     #94a3b8; /* Cool gray: Units, captions, shortcuts */
  --codex-text-disabled:  #64748b; /* Disabled items */

  /* Semantic Accents */
  --codex-accent-cyan:    #06b6d4; /* Primary GIS action, active boundary, points */
  --codex-accent-teal:    #14b8a6; /* Secondary action */
  --codex-accent-amber:   #f59e0b; /* Selected station points, warnings */
  --codex-accent-emerald: #10b981; /* Validated data, online engine, success */
  --codex-accent-rose:    #f43f5e; /* Cancellation, errors, delete */
}
```

---

## 2. Qt Style Sheet (QSS) Implementation for PySide6

Use this complete QSS snippet when styling PySide6/Qt widgets:

```qss
/* Main Window & Docks */
QMainWindow {
    background-color: #0d0f12;
    color: #cbd5e1;
}

QDockWidget {
    background: #14151a;
    border: 1px solid #252733;
    titlebar-close-icon: url(assets/close.svg);
}

QDockWidget::title {
    background: #16171e;
    padding: 6px;
    font-weight: bold;
    color: #ffffff;
}

/* Ribbons & Toolbars */
QToolBar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1c1d25, stop:1 #14151a);
    border-bottom: 1px solid #252733;
    spacing: 6px;
    padding: 4px;
}

QToolButton {
    background-color: #191a22;
    border: 1px solid #252733;
    border-radius: 4px;
    color: #ffffff;
    padding: 5px 8px;
    font-size: 11px;
}

QToolButton:hover {
    background-color: #222430;
    border-color: #06b6d4;
}

QToolButton:pressed {
    background-color: #262938;
}

/* Tree & Table Views (TOC, Catalog, Attribute Table) */
QTreeView, QTableView {
    background-color: #101116;
    border: 1px solid #252733;
    color: #cbd5e1;
    gridline-color: #1f2129;
    selection-background-color: #262938;
    selection-color: #ffffff;
}

QHeaderView::section {
    background-color: #191a22;
    color: #ffffff;
    padding: 5px;
    border: 1px solid #252733;
    font-weight: 600;
}

/* Status Bar */
QStatusBar {
    background-color: #0f1014;
    border-top: 1px solid #252733;
    color: #94a3b8;
    font-family: 'JetBrains Mono', Consolas, monospace;
    font-size: 10px;
}
```

---

## 3. GIS UX Principles & Component Rules

### 1. The Map Canvas is King (Center Stage):
- The central map viewport must occupy at least 60% of horizontal space by default.
- Never cover the map with blocking popups when performing spatial analysis; use dockable panes or floating glass overlays.

### 2. Table of Contents (TOC) Symbology & Status:
- Every layer in the TOC must display:
  - Visibility Checkbox (`[x]`).
  - Geometry Swatch (Point marker, Line, Polygon outline/fill, Raster ramp).
  - Layer name (truncated gracefully if long).
  - Real-time count badge: e.g. `(136 stations | 42 clipped | 12 selected)`.

### 3. Organized Results & Outputs (Never Stack Tables Blindly):
- When tools finish and generate multiple Excel workbooks or spatial layers:
  - List them in an **Outputs & Results Tree** in the left sidebar.
  - Clicking any workbook opens **ONLY THAT SPECIFIC TABLE** in the dedicated Data Table tab.
  - Provide a live search box, column sorting, pagination (25-50 rows), and a 1-click "Export CSV" button.

### 4. ArcToolbox Geoprocessing Isolation:
- Each tool operates as an independent module.
- Running a tool shows a dedicated progress bar (0% to 100%) and timestamped logging output.
- Tools do NOT collide with each other.

### 5. Cartographic Layout Designer:
- Standard paper formats (A3 Landscape, A4 Portrait).
- Standard map elements: Map Frame, Dynamic North Arrow (SVG), Dynamic Graphic Scale Bar, Legend, Graticule/Grid, and Developer/Metadata credits.
