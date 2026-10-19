# -*- coding: utf-8 -*-
"""MIRSAD Desktop Internationalization (i18n) Catalog.

Provides unmixed localization:
- English (en-US) default on first launch.
- Pure English interface when in English mode (no Arabic text).
- Pure Arabic interface when in Arabic mode (no English text, except standard technical acronyms/formulas).
"""

STRINGS = {
    # App Shell & Header
    "app_title": ("مِرصاد | MIRSAD", "MIRSAD | مِرصاد"),
    "app_subtitle": (
        "قاعدة بيانات الأطلس المكاني لإعادة التحليل المتكامل للأرصاد الجوية",
        "Meteorological Integrated Reanalysis Spatial Atlas Database"
    ),
    "add_data": ("إضافة بيانات", "Add Data"),
    "add_layer_gdb": ("إضافة طبقة أو قاعدة بيانات…", "Add Layer or Database…"),
    "import_stations": ("استيراد نقاط محطات…", "Import Station Points…"),
    "study_boundary": ("حدود منطقة الدراسة (مضلع)…", "Study Area Boundary (Polygon)…"),
    "raster_geotiff": ("راستر جغرافي (GeoTIFF)…", "Geographic Raster (GeoTIFF)…"),
    "preview_table_layer": ("معاينة جدول أو طبقة…", "Preview Table or Layer…"),
    "help": ("دليل الاستخدام", "User Guide"),
    "light_mode": ("الوضع الفاتح", "Light Mode"),
    "dark_mode": ("الوضع الداكن", "Dark Mode"),

    # Sidebar Navigation & Tools
    "tools_heading": ("أدوات المعالجة الجغرافية", "Geoprocessing Tools"),
    "tool_stations": ("أطلس محطات الأرصاد الجوية السطحية", "Ground Weather Stations Atlas"),
    "tool_points": ("الأطلس المناخي المكاني النقطي", "Spatial Climate Atlas (Points)"),
    "tool_raster": ("أطلس الراستر والشبكات المناخية", "Grid Raster Climate Atlas"),
    "nav_results": ("استعراض النتائج", "Browse Results"),
    "nav_tasks": ("سجل المهام والتنزيل", "Tasks & Download Log"),
    "nav_about": ("عن مرصاد", "About MIRSAD"),

    # Table of Contents (Contents / TOC)
    "contents_heading": ("محتويات الخريطة", "Contents"),
    "group_layers": ("الطبقات", "Layers"),
    "group_tables": ("الجداول", "Tables"),
    "group_results": ("النتائج المخرجة", "Output Results"),
    "working_points": ("نقاط العمل", "Working Points"),
    "study_boundary_layer": ("حدود الدراسة", "Study Boundary"),
    "no_layers_hint": ("لا توجد طبقات مضافة", "No layers added"),

    # Context Menus
    "menu_zoom_layer": ("تكبير إلى نطاق الطبقة", "Zoom to Layer"),
    "menu_zoom_points": ("تكبير إلى نقاط العمل", "Zoom to Working Points"),
    "menu_zoom_boundary": ("تكبير إلى حدود الدراسة", "Zoom to Study Boundary"),
    "menu_clear_boundary": ("إزالة حدود الدراسة", "Clear Study Boundary"),
    "menu_open_table": ("فتح جدول البيانات", "Open Attribute Table"),
    "menu_layer_props": ("خصائص الطبقة وإسقاطها", "Layer Properties & CRS"),
    "menu_remove_layer": ("إزالة من المشروع", "Remove from Project"),

    # Map Navigation & Controls
    "map_fit_tip": ("تكبير إلى نطاق النقاط", "Zoom to points"),
    "map_add_point": ("＋ إضافة نقطة", "+ Add Point"),
    "map_instructions": ("سحب للتحريك · عجلة الماوس للتكبير", "Pan: drag · Zoom: wheel"),
    "map_click_add_hint": ("اضغط على الخريطة لإضافة نقطة", "Click map to add a point"),

    # Central Tabs
    "tab_map": ("الخريطة", "Map"),
    "tab_table": ("الجدول", "Attribute Table"),
    "tab_tasks": ("المهام", "Tasks"),
    "tab_input_info": ("بيانات المدخل", "Input Info"),
    "tab_about": ("عن مرصاد", "About"),
    "tab_pdf": ("معاينة أطلس PDF", "PDF Atlas Preview"),
    "tab_inputs": ("المدخلات", "Inputs"),
    "tab_climate": ("المناخ", "Climate"),
    "tab_raster": ("الراستر", "Raster"),
    "tab_outputs": ("المخرجات", "Outputs"),

    # Station & Point Tool Forms
    "working_points_source": ("مصدر نقاط العمل", "Working Points Source"),
    "mode_stations": ("محطات الكتالوج المعتمد", "Catalogue Weather Stations"),
    "mode_user": ("نقاط المستخدم المستوردة", "User Points"),
    "mode_combined": ("المحطات المعتمدة ونقاط إضافية", "Stations and Additional Points"),
    "mode_grid": ("شبكة نقاط منتظمة داخل الحدود", "Regular Grid Inside Boundary"),
    "station_filters": ("تصفية المحطات", "Station Filters"),
    "region": ("الإقليم الجغرافي", "Region"),
    "choose_country": ("اختر الدولة", "Choose Country"),
    "search_station_placeholder": ("اسم المحطة أو كود النقطة…", "Station name or point ID…"),
    "all_regions": ("جميع الأقاليم", "All Regions"),
    "import_point_file": ("استيراد ملف نقاط", "Import Point File"),
    "enter_point_coords": ("إدخال إحداثيات نقطة", "Enter Point Coordinates"),
    "load_boundary_btn": ("فتح حدود الدراسة", "Load Study Boundary"),
    "points_inside_boundary": ("النقاط داخل الحدود فقط", "Points inside boundary only"),
    "generate_grid_btn": ("توليد شبكة نقاط", "Generate Point Grid"),
    "grid_spacing_label": ("مسافة الشبكة (متر)", "Grid Spacing (m)"),
    "select_visible": ("تحديد المعروض", "Select Visible"),
    "clear_visible": ("إلغاء المعروض", "Clear Visible"),

    # Station Table Columns
    "col_check": ("✓", "✓"),
    "col_point": ("النقطة / المحطة", "Point / Station"),
    "col_usaf": ("ID / USAF", "ID / USAF"),
    "col_wban": ("WBAN", "WBAN"),
    "col_lat": ("دائرة العرض", "Latitude"),
    "col_lon": ("خط الطول", "Longitude"),
    "col_qa": ("حالة الفحص", "QA Status"),

    # QA Status Values
    "qa_reference": ("مطابق للمرجع المعتمد", "Reference Match"),
    "qa_review": ("يحتاج مراجعة", "Review Required"),
    "qa_user": ("نقطة مدخلة من المستخدم", "User Supplied"),
    "qa_unverified": ("غير محقق ميدانياً", "Unverified"),

    # Climate Elements & Models
    "climate_heading": ("العناصر والنماذج المناخية", "Climate Elements & Models"),
    "climate_note": (
        "اختر من مجموعات التولبوكس الـ19 المعتمدة، عند المحطات أو نقاطك أو شبكة منتظمة.",
        "Choose from all 19 verified toolbox module groups for stations, points, or grids."
    ),
    "source_provider": ("مصدر البيانات", "Data Source Provider"),
    "date_from": ("تاريخ البداية", "Start Date"),
    "date_to": ("تاريخ النهاية", "End Date"),
    "gap_filling": ("ملء الفجوات الشهرية", "Monthly Gap Filling"),
    "gap_none": ("بدون ملء", "No Gap Filling"),
    "gap_clim": ("متوسط مناخي (1991–2020)", "Climatological Mean (1991–2020)"),
    "gap_linear": ("استيفاء خطي", "Linear Interpolation"),
    "workflow": ("مسار المعالجة", "Processing Workflow"),
    "workflow_gis": ("تنزيل وقواعد بيانات وجداول Excel", "Download, GIS Databases & Excel"),
    "workflow_atlas": ("المسار الكامل: تنزيل واستيفاء وأطلس", "Full Pipeline: Download, Raster & Atlas"),
    "output_crs": ("نظام إسقاط المخرجات", "Output Coordinate System (CRS)"),
    "output_units": ("وحدات القياس", "Measurement Units"),
    "unit_metric": ("متري (°م، ملم)", "Metric (°C, mm)"),
    "unit_imperial": ("إمبراطوري (°ف، بوصة)", "Imperial (°F, in)"),
    "temporal_summaries": ("الملخصات الزمنية", "Temporal Summaries"),
    "summary_annual": ("سنوي", "Annual"),
    "summary_seasonal": ("فصلي", "Seasonal"),
    "summary_monthly": ("شهري", "Monthly"),
    "include_ranges": ("المدى الشهري بين السنوات", "Interannual Monthly Ranges"),
    "include_daily": ("تضمين البيانات اليومية الخام", "Include Raw Daily Records"),
    "include_yearly": ("ملف إضافي لكل سنة مستقلة", "Additional Workbook per Year"),
    "primary_elements": ("العناصر الأساسية", "Primary Elements"),
    "derived_models": ("النماذج والمؤشرات المشتقة", "Derived Models & Indices"),
    "select_available": ("تحديد المتاح", "Select Available"),
    "clear_all": ("إلغاء التحديد", "Clear Selection"),

    # Raster & Analysis
    "raster_heading": ("الراستر والأطلس المناخي", "Raster & Climate Atlas"),
    "raster_note": (
        "استيفاء الحقول الرقمية بالمسقط المتري المختار. دقة الخلية بالأمتار.",
        "Interpolate numeric fields using the selected projected metric CRS."
    ),
    "interpolation_method": ("طريقة الاستيفاء", "Interpolation Method"),
    "processing_crs": ("إسقاط المعالجة المكانية", "Processing Metric CRS"),
    "cell_size": ("حجم الخلية (متر)", "Cell Size (m)"),
    "idw_power": ("معامل القوة (IDW Power)", "IDW Power"),
    "neighbours": ("عدد الجيران", "Number of Neighbours"),
    "generate_pdf": ("إنتاج أطلس خرائط بصيغة PDF", "Generate Multi-Page PDF Atlas"),
    "user_fields_to_interpolate": ("الحقول الرقمية المراد استيفاؤها", "Numeric Fields to Interpolate"),
    "run_raster_from_points": ("بدء معالجة واستيفاء الحقول المحددة", "Interpolate Selected Point Fields"),

    # Outputs & Project Settings
    "project_name": ("اسم المشروع", "Project Name"),
    "output_folder": ("مجلد حفظ المخرجات", "Output Workspace Folder"),
    "browse_folder": ("تصفح المجلدات…", "Browse Folders…"),
    "output_databases_note": (
        "تنتج نفس السجلات المحسوبة في قواعد بيانات FileGDB وGeoPackage وجداول Excel.",
        "Calculated records are saved identically into FileGDB, GeoPackage, and Excel."
    ),

    # Footer Actions
    "btn_run_tool": ("تشغيل الأداة", "Run Tool"),
    "btn_export_points": ("تصدير النقاط (GDB + GPKG + Excel)", "Export Points (GDB + GPKG + Excel)"),
    "btn_cancel": ("إلغاء", "Cancel"),
    "btn_open_results": ("فتح مجلد النتائج", "Open Results Folder"),
    "btn_back_step": ("السابق", "Back"),
    "btn_next_step": ("التالي", "Next"),

    # Add Data GIS Dialog
    "dlg_add_data_title": ("إضافة بيانات جغرافية وجداول", "Add Spatial & Tabular Data"),
    "look_in": ("الموقع الحالي:", "Look In:"),
    "up_directory": ("للأعلى", "Up"),
    "browse_folder_action": ("تصفح مجلد…", "Browse Folder…"),
    "search_datasets": ("بحث في الملفات والطبقات…", "Search datasets & layers…"),
    "col_dataset_name": ("الاسم", "Name"),
    "col_dataset_type": ("النوع", "Type"),
    "col_dataset_geom": ("الهندسة", "Geometry"),
    "col_dataset_crs": ("نظام الإحداثيات", "CRS"),
    "col_dataset_count": ("عدد المعالم", "Features"),
    "filter_all_supported": ("جميع البيانات المدعومة (*.gdb, *.gpkg, *.shp, *.tif, *.xlsx, *.csv)", "All Supported Data (*.gdb, *.gpkg, *.shp, *.tif, *.xlsx, *.csv)"),
    "filter_gdb": ("قواعد بيانات File Geodatabase (*.gdb)", "File Geodatabases (*.gdb)"),
    "filter_gpkg": ("حاويات GeoPackage (*.gpkg)", "GeoPackages (*.gpkg)"),
    "filter_shp": ("ملفات Shapefile (*.shp)", "Shapefiles (*.shp)"),
    "filter_raster": ("راستر وصور فضائية (*.tif, *.tiff)", "Rasters (*.tif, *.tiff)"),
    "filter_tables": ("جداول وجداول بيانات (*.xlsx, *.csv, *.tsv)", "Tables & Spreadsheets (*.xlsx, *.csv, *.tsv)"),
    "add_selected": ("إضافة المحدد", "Add Selected"),
    "open_folder": ("فتح", "Open"),
    "dialog_cancel": ("إلغاء", "Cancel"),
    "role_stations": ("نقاط محطات للتحليل المناخي", "Working Station Points"),
    "role_mask": ("نطاق الدراسة وقناع القص (مضلع)", "Study Area Clipping Mask"),
    "role_context": ("طبقة مرجعية للعرض فقط", "Map Context Layer"),

    # CRS Picker Dialog
    "dlg_crs_title": ("اختيار نظام الإسناد الجغرافي والإسقاط", "Choose Coordinate Reference System"),
    "search_crs": ("بحث في أنظمة الإسقاط:", "Search Coordinate Systems:"),
    "search_crs_placeholder": ("ابحث بكود EPSG أو اسم المسقط أو الدولة (مثل: 32636 أو UTM أو Egypt)…", "Search by EPSG code, name, or area (e.g. 32636, UTM, Egypt)…"),
    "custom_crs_code": ("كود EPSG مخصص:", "Custom EPSG Code:"),
    "type_projected": ("مسقط متري", "Projected Metric"),
    "type_geographic": ("جغرافي بالدرجات", "Geographic Degrees"),
    "crs_valid": ("نظام إحداثيات صالح ومعتمد", "Valid Coordinate Reference System"),
    "crs_warning": ("تحذير: كود الإسقاط غير صالح", "Warning: Invalid CRS"),

    # Dialog Buttons
    "btn_ok": ("موافق", "OK"),
    "btn_close": ("إغلاق", "Close"),

    # Progress & Status
    "status_ready": ("جاهز للعمل", "Ready"),
    "status_running": ("المعالجة جارية…", "Processing…"),
    "status_complete": ("اكتملت المعالجة بنجاح", "Processing Complete"),
    "status_partial": ("اكتملت جزئياً؛ راجع السجل", "Partial Result; Inspect Log"),
    "status_cancelled": ("تم إلغاء المهمة", "Task Cancelled"),
    "task_duration": ("المدة المنقضية", "Elapsed"),
    "visible_selected_count": ("المعروض: %d · المحدد: %d", "Visible: %d · Selected: %d"),
    "user_grid_count": ("نقاطي: %d · نقاط الشبكة: %d", "My Points: %d · Grid Points: %d"),
}


def tr(key, arabic=False, default=""):
    """Look up a translated string key.

    If arabic is True, returns pure Arabic text.
    If arabic is False, returns pure English text.
    """
    entry = STRINGS.get(key)
    if not entry:
        return default or key
    return entry[0] if arabic else entry[1]
