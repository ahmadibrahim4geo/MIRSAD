"""Native coordinate-system browser with the versioned Esri folder taxonomy."""
import html
import json
import os
import re
from PySide6.QtCore import Qt, QSettings, QTimer, QPoint
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,
    QPushButton,QTreeWidget,QTreeWidgetItem,QHeaderView,QTextBrowser,QDialogButtonBox,
    QCheckBox,QFrame,QSplitter,QAbstractItemView)
from .crs import (build_crs_hierarchy,validate_and_describe_crs,crs_display_name,
                  native_by_code,catalogue_by_code,additional_crs_catalogue)
from .icons import outline_icon


def searchable(text):
    return re.sub(r"[\W_]+","",str(text).casefold()).replace("wgs1984","wgs84")


class CrsSelectionDialog(QDialog):
    def __init__(self,current_crs="EPSG:4326",parent=None,layers=None):
        super().__init__(parent)
        self.arabic=getattr(parent,"arabic",False)
        self.setWindowTitle(self.t("خصائص الإسناد المكاني","Spatial Reference Properties"))
        available=self.screen().availableGeometry()
        self.setMinimumSize(620,420)
        self.resize(min(900,available.width()-40),min(820,available.height()-60))
        self.initial_screen_fit=False
        self.selected_crs=current_crs;self.latest_catalogue=False;self.search_expansion=None
        self.settings=getattr(parent,"settings",None)
        if self.settings is None:
            test_settings=os.environ.get("MIRSAD_TEST_SETTINGS")
            self.settings=QSettings(test_settings,QSettings.IniFormat) if test_settings else QSettings("MIRSAD","Desktop")
        try:
            favorites=json.loads(self.settings.value("crs/favorites","[]"))
            self.favorites=list(dict.fromkeys(value for value in favorites
                                if isinstance(value,str) and 0<len(value)<=16384))[:100] if isinstance(favorites,list) else []
        except (TypeError,ValueError):self.favorites=[]
        self.layer_sources=list(layers if layers is not None else getattr(parent,"project_layers",{}).values())
        box=QVBoxLayout(self);box.setSpacing(8)
        summary=QFrame();summary.setObjectName("crsCurrentPanel");summary_box=QVBoxLayout(summary)
        caption=QLabel(self.t("نظام الإحداثيات المختار","Selected coordinate system"));caption.setObjectName("muted")
        caption_row=QHBoxLayout();caption_row.addWidget(caption,1)
        self.details_toggle=QPushButton(self.t("التفاصيل","Details"));self.details_toggle.setAutoDefault(False)
        self.details_toggle.setCheckable(True);caption_row.addWidget(self.details_toggle)
        self.current_name=QLabel();self.current_name.setObjectName("section");self.current_name.setWordWrap(True)
        self.current_name.setTextFormat(Qt.PlainText)
        summary_box.addLayout(caption_row);summary_box.addWidget(self.current_name);box.addWidget(summary)
        search_row=QHBoxLayout();self.search_input=QLineEdit();self.search_input.setClearButtonEnabled(True)
        self.search_input.setPlaceholderText(self.t("بحث بالاسم أو الكود أو المجلد…","Search by name, code or folder…"))
        self.search_input.setAccessibleName(self.search_input.placeholderText())
        self.show_current_button=QPushButton(self.t("إظهار المختار","Show selected"))
        self.show_current_button.setIcon(outline_icon("fit"));self.show_current_button.setAutoDefault(False)
        self.show_current_button.clicked.connect(self.reveal_current)
        self.favorite_button=QPushButton();self.favorite_button.setIcon(outline_icon("star"))
        self.favorite_button.setAutoDefault(False);self.favorite_button.clicked.connect(self.toggle_favorite)
        search_row.addWidget(self.search_input,1);search_row.addWidget(self.show_current_button);search_row.addWidget(self.favorite_button)
        box.addLayout(search_row)
        self.crs_tree=QTreeWidget();self.crs_tree.setObjectName("crsTree")
        self.crs_tree.setHeaderLabels(["Coordinate System",self.t("الكود","Authority")])
        # Preserve Esri's left-to-right scientific paths even in an Arabic shell.
        self.crs_tree.setLayoutDirection(Qt.LeftToRight);self.crs_tree.setIndentation(18)
        self.crs_tree.setUniformRowHeights(True);self.crs_tree.setSortingEnabled(False)
        self.crs_tree.header().setSectionResizeMode(0,QHeaderView.Stretch)
        self.crs_tree.header().setSectionResizeMode(1,QHeaderView.ResizeToContents)
        self.crs_tree.setMinimumHeight(60)
        self.details_box=QTextBrowser();self.details_box.setMinimumHeight(75)
        self.details_box.setOpenExternalLinks(False)
        self.details_box.hide();self.details_toggle.toggled.connect(self.details_box.setVisible)
        splitter=QSplitter(Qt.Vertical);splitter.addWidget(self.crs_tree);splitter.addWidget(self.details_box)
        splitter.setSizes([400,130]);splitter.setStretchFactor(0,1);box.addWidget(splitter,1)
        self.catalogue_toggle=QCheckBox(self.t("إظهار تعريفات Esri الإضافية", "Include additional Esri definitions")+f" (+{len(additional_crs_catalogue()):,})")
        self.catalogue_toggle.setToolTip(self.t(
            "تظل شجرة Pro 3.6 كما هي. التعريفات الإضافية لها قسم مستقل؛ المصدر العام لا يحدد مجلدات Pro لها.",
            "Keeps the Pro 3.6 tree intact. Additional definitions use a separate branch; the public catalogue does not declare their Pro folder paths."))
        box.addWidget(self.catalogue_toggle)
        self.taxonomy_note=QLabel(self.t("تصنيف وأسماء ArcGIS Pro 3.6 · توسّع في المجلد المطلوب فقط",
                                       "ArcGIS Pro 3.6 folders and names · Expand only the branch you need"))
        self.taxonomy_note.setObjectName("muted");self.taxonomy_note.setWordWrap(True);box.addWidget(self.taxonomy_note)
        custom_row=QHBoxLayout();custom_row.addWidget(QLabel(self.t("كود / تعريف مخصص:","Custom code / definition:")))
        self.custom_input=QLineEdit(current_crs);self.custom_input.setLayoutDirection(Qt.LeftToRight)
        self.custom_input.setMaxLength(16384);custom_row.addWidget(self.custom_input,1)
        validate=QPushButton(self.t("فحص","Validate"));validate.setAutoDefault(False)
        validate.clicked.connect(lambda:self.update_details(self.custom_input.text().strip()));custom_row.addWidget(validate)
        box.addLayout(custom_row)
        self.buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept);self.buttons.rejected.connect(self.reject);box.addWidget(self.buttons)
        self.validation_timer=QTimer(self);self.validation_timer.setSingleShot(True);self.validation_timer.setInterval(180)
        self.validation_timer.timeout.connect(lambda:self.update_details(self.custom_input.text().strip()))
        self.populate_tree()
        self.search_input.textChanged.connect(self.filter_tree)
        self.crs_tree.currentItemChanged.connect(self.on_item_selected)
        self.crs_tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.custom_input.textChanged.connect(self.on_custom_typed)
        self.catalogue_toggle.toggled.connect(self.switch_catalogue)
        self.update_details(current_crs)

    def t(self,arabic,english):return arabic if self.arabic else english

    def showEvent(self,event):
        super().showEvent(event)
        if not self.initial_screen_fit:
            self.initial_screen_fit=True;QTimer.singleShot(0,self.fit_initial_screen)

    def fit_initial_screen(self):
        available=self.screen().availableGeometry();frame=self.frameGeometry()
        extra_width=frame.width()-self.width();extra_height=frame.height()-self.height()
        self.resize(min(self.width(),available.width()-extra_width-16),
                    min(self.height(),available.height()-extra_height-16))
        if self.height()<650:
            self.favorites_root.setExpanded(False);self.layers_root.setExpanded(False)
            self.taxonomy_note.hide()
        frame=self.frameGeometry()
        x=max(available.left()+8,min(frame.left(),available.right()-frame.width()-7))
        y=max(available.top()+8,min(frame.top(),available.bottom()-frame.height()-7))
        self.move(self.pos()+QPoint(x-frame.left(),y-frame.top()))

    def folder(self,parent,title,path,icon="folder"):
        item=QTreeWidgetItem(parent,[title]);item.setIcon(0,outline_icon(icon))
        item.setData(0,Qt.UserRole+1,path);return item

    def leaf(self,parent,code,name=None,description=""):
        name=name or crs_display_name(code)
        item=QTreeWidgetItem(parent,[name,code]);item.setData(0,Qt.UserRole,code)
        path=parent.data(0,Qt.UserRole+1)+" / "+name
        item.setData(0,Qt.UserRole+1,path)
        row=native_by_code().get(str(code).upper()) or catalogue_by_code().get(str(code).upper()) or {}
        text=" ".join((path,code,description,row.get("esri_name",""),catalogue_by_code().get(str(code).upper(),{}).get("name","")))
        item.setData(0,Qt.UserRole+2,searchable(text))
        item.setToolTip(0,path+"\n"+code+("\n"+description if description else ""))
        geographic=path.startswith("Geographic") or validate_type_hint(code)
        item.setIcon(0,outline_icon("globe" if geographic else "map"));return item

    def placeholder(self,parent,text):
        item=QTreeWidgetItem(parent,[text]);item.setFlags(Qt.NoItemFlags)

    def populate_tree(self):
        self.crs_tree.blockSignals(True);self.crs_tree.clear()
        self.favorites_root=self.folder(self.crs_tree,"Favorites","Favorites","star")
        self.layers_root=self.folder(self.crs_tree,"Layers","Layers","basemap")
        self.populate_favorites()
        layer_groups={}
        for layer in self.layer_sources:
            name=str(layer.get("name") or layer.get("layer") or self.t("طبقة","Layer"))
            value=layer.get("crs")
            info=validate_and_describe_crs(value)
            if info["valid"]:
                key=info["code"].upper()
                if key not in layer_groups:layer_groups[key]=self.leaf(self.layers_root,str(value))
                self.leaf(layer_groups[key],str(value),name)
            else:
                if "unknown" not in layer_groups:
                    unknown=self.folder(self.layers_root,"<Unknown>","Layers/unknown","globe")
                    unknown.setFlags(Qt.ItemIsEnabled);layer_groups["unknown"]=unknown
                    unknown.setToolTip(0,self.t("لم يُفترض مسقط للطبقات غير المعروفة","No CRS is assumed for layers with an undefined or unsupported source CRS"))
                self.placeholder(layer_groups["unknown"],name)
        if not self.layer_sources:self.placeholder(self.layers_root,self.t("لم تُحمّل طبقات مكانية بعد","No spatial layers loaded"))
        def add(parent,folder,path):
            title={"Geographic Coordinate Systems":"Geographic Coordinate System",
                   "Projected Coordinate Systems":"Projected Coordinate System"}.get(folder["title"],folder["title"])
            fullpath=path+"/"+folder["title"] if path else folder["title"]
            node=self.folder(parent,title,fullpath)
            for child in folder.get("subfolders",[]):add(node,child,fullpath)
            for code,name,description in folder.get("items",[]):self.leaf(node,code,name,description)
        for root in build_crs_hierarchy(latest=self.latest_catalogue)["folders"]:add(self.crs_tree,root,"")
        self.favorites_root.setExpanded(True);self.layers_root.setExpanded(True)
        self.crs_tree.blockSignals(False)

    def populate_favorites(self):
        self.favorites_root.takeChildren()
        for value in self.favorites:self.leaf(self.favorites_root,value)
        if not self.favorites:self.placeholder(self.favorites_root,self.t("اختر مسقطًا ثم أضفه للمفضلة","Select a CRS, then add it to Favorites"))

    def switch_catalogue(self,checked):
        self.latest_catalogue=checked;self.populate_tree();self.filter_tree(self.search_input.text())

    def items(self):
        pending=[self.crs_tree.topLevelItem(i) for i in reversed(range(self.crs_tree.topLevelItemCount()))]
        while pending:
            item=pending.pop();yield item
            pending.extend(item.child(i) for i in reversed(range(item.childCount())))

    def select_initial_crs(self,target_code):
        target=str(target_code).strip().upper()
        if target.isdigit():target="EPSG:"+target
        matches=[item for item in self.items() if str(item.data(0,Qt.UserRole) or "").upper()==target]
        # Prefer the complete taxonomy path over an already-visible favorite or
        # Layers shortcut. Custom layer-only definitions remain discoverable.
        native=next((item for item in matches if str(item.data(0,Qt.UserRole+1)).startswith(
                    ("Geographic Coordinate Systems/","Projected Coordinate Systems/"))),None)
        item=native if native is not None else matches[0] if matches else None
        if item is not None:
            parent=item.parent()
            while parent:parent.setExpanded(True);parent=parent.parent()
            self.crs_tree.setCurrentItem(item);self.crs_tree.scrollToItem(item,QAbstractItemView.PositionAtCenter)
            return True
        return False

    def reveal_current(self):
        self.search_input.clear()
        if not self.select_initial_crs(self.custom_input.text()) and not self.latest_catalogue:
            self.catalogue_toggle.setChecked(True);self.select_initial_crs(self.custom_input.text())

    def filter_tree(self,query):
        query=searchable(query)
        if query and self.search_expansion is None:
            self.search_expansion={item.data(0,Qt.UserRole+1) for item in self.items() if item.isExpanded()}
        def visit(item):
            code=item.data(0,Qt.UserRole)
            matches=[visit(item.child(i)) for i in range(item.childCount())]
            match=not query or any(matches) or bool(code and query in (item.data(0,Qt.UserRole+2) or ""))
            item.setHidden(not match)
            if item.childCount():
                if query:item.setExpanded(match)
                elif self.search_expansion is not None:item.setExpanded(item.data(0,Qt.UserRole+1) in self.search_expansion)
            return match
        for i in range(self.crs_tree.topLevelItemCount()):visit(self.crs_tree.topLevelItem(i))
        if not query:self.search_expansion=None

    def on_item_selected(self,current,previous):
        if current is None:return
        code=current.data(0,Qt.UserRole)
        if not code:return
        self.validation_timer.stop();self.custom_input.blockSignals(True);self.custom_input.setText(code)
        self.custom_input.blockSignals(False);self.selected_crs=code;self.update_details(code)

    def on_item_double_clicked(self,item,column):
        if item.data(0,Qt.UserRole):self.on_item_selected(item,None);self.accept()

    def on_custom_typed(self,text):
        self.favorite_button.setEnabled(False);self.buttons.button(QDialogButtonBox.Ok).setEnabled(False)
        self.validation_timer.start()

    def toggle_favorite(self):
        code=self.custom_input.text().strip()
        info=validate_and_describe_crs(code)
        if not info["valid"]:return
        value=info["code"]
        existing=next((entry for entry in self.favorites if entry.upper()==value.upper()),None)
        if existing is not None:self.favorites.remove(existing)
        elif len(self.favorites)<100:self.favorites.append(value)
        self.settings.setValue("crs/favorites",json.dumps(self.favorites,ensure_ascii=False));self.settings.sync()
        self.populate_favorites();self.favorites_root.setExpanded(True);self.filter_tree(self.search_input.text())
        self.update_details(code)

    def accept(self):
        code=self.custom_input.text().strip();self.validation_timer.stop()
        info=self.update_details(code)
        if info["valid"]:self.selected_crs=code;super().accept()

    def update_details(self,code):
        info=validate_and_describe_crs(code);valid=info["valid"]
        self.buttons.button(QDialogButtonBox.Ok).setEnabled(valid)
        is_favorite=valid and any(value.upper()==info["code"].upper() for value in self.favorites)
        self.favorite_button.setEnabled(valid and (is_favorite or len(self.favorites)<100))
        self.favorite_button.setText(self.t("إزالة من المفضلة","Remove Favorite") if is_favorite else self.t("إضافة للمفضلة","Add Favorite"))
        if valid:
            name=crs_display_name(info["code"])
            authority=info["code"] if len(info["code"])<=80 else self.t("تعريف مخصص","Custom definition")
            self.current_name.setText(name+"  ·  "+authority)
            values=[(self.t("الاسم","Name"),name),(self.t("الكود","Authority"),authority),
                    (self.t("النوع","Type"),"Projected" if info["is_projected"] else "Geographic" if info["is_geographic"] else "Other"),
                    (self.t("وحدة القياس","Unit"),info["unit"]),(self.t("الداتوم","Datum"),info["datum"]),
                    (self.t("الإهليلج","Ellipsoid"),info["ellipsoid"]),(self.t("نطاق الاستخدام","Area of use"),info["area_of_use"])]
            if info["projection_method"]:values.append((self.t("طريقة الإسقاط","Projection"),info["projection_method"]))
            values.extend((p["name"],p["value"]) for p in info["parameters"])
            content="<br>".join("<b>"+html.escape(str(label))+":</b> "+html.escape(str(value)) for label,value in values)
            self.details_box.setHtml(content)
        else:
            self.current_name.setText(self.t("تعريف إحداثيات غير صالح","Invalid coordinate system"))
            self.details_box.setPlainText(str(info.get("error") or "")[:1000])
        return info


def validate_type_hint(code):
    row=native_by_code().get(str(code).upper()) or catalogue_by_code().get(str(code).upper())
    return bool(row and row["folder"][0].startswith("Geographic"))
