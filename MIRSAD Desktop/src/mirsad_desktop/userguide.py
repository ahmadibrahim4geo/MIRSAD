"""Native offline help centre; no map, network or scientific runtime needed."""
import json
import os
import re
import unicodedata
from PySide6.QtCore import Qt,QUrl,QSettings
from PySide6.QtGui import QKeySequence,QShortcut,QTextDocument,QTextCursor,QPalette,QPdfWriter
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QLineEdit,
    QPushButton,QListWidget,QListWidgetItem,QTreeWidget,QTreeWidgetItem,QSplitter,QTextBrowser,
    QWidget,QTabWidget,QToolBar,QFileDialog,QApplication)
from .catalogue import asset_dir


def normalize_search(text):
    text=unicodedata.normalize('NFKC',text).casefold()
    text=re.sub('[\u064b-\u065f\u0670\u0640]','',text)
    return re.sub('[أإآٱ]','ا',text)


class UserGuideDialog(QDialog):
    def __init__(self,arabic=False,parent=None,topic=None):
        super().__init__(parent)
        self.setObjectName('userGuide');self.resize(1180,790);self.setMinimumSize(760,500)
        self.index=json.loads((asset_dir()/'help_index.json').read_text(encoding='utf-8'))
        self.topics={s['id']:s for s in self.index['sections']}
        self.arabic=arabic;self.current_topic='start';self.history=[];self.history_cursor=-1;self.text_size=11
        filename=os.environ.get('MIRSAD_TEST_SETTINGS')
        self.settings=QSettings(filename,QSettings.IniFormat) if filename else QSettings('MIRSAD','Desktop')
        try:self.favorites=json.loads(self.settings.value('help/favorites','[]'))
        except (ValueError,TypeError):self.favorites=[]
        if not isinstance(self.favorites,list):self.favorites=[]
        self.favorites=[key for key in self.favorites if isinstance(key,str) and key in self.topics]
        box=QVBoxLayout(self);box.setContentsMargins(12,12,12,12)
        header=QHBoxLayout();self.title=QLabel();self.title.setObjectName('heading');header.addWidget(self.title,1)
        self.language=QComboBox();self.language.addItem('العربية','ar');self.language.addItem('English','en')
        self.language.setCurrentIndex(0 if arabic else 1);header.addWidget(self.language);box.addLayout(header)
        self.toolbar=QToolBar();box.addWidget(self.toolbar)
        self.actions={}
        for key,callback in [('back',self.go_back),('forward',self.go_forward),('home',lambda:self.open_topic('start')),
            ('pane',lambda:self.sidebar.setVisible(not self.sidebar.isVisible())),('favorite',self.toggle_favorite),
            ('print',self.print_topic),('pdf',self.save_pdf),('smaller',lambda:self.zoom(-1)),('larger',lambda:self.zoom(1)),('theme',self.toggle_theme)]:
            self.actions[key]=self.toolbar.addAction(key,callback)
        self.splitter=QSplitter(Qt.Horizontal);box.addWidget(self.splitter,1)
        self.sidebar=QTabWidget();self.sidebar.setMinimumWidth(250)
        self.contents=QTreeWidget();self.contents.setHeaderHidden(True);self.contents.setWordWrap(True)
        self.contents.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sidebar.addTab(self.contents,'Contents')
        searchpage=QWidget();searchlayout=QVBoxLayout(searchpage)
        self.search=QLineEdit();self.search.setClearButtonEnabled(True);searchlayout.addWidget(self.search)
        self.results=QListWidget();self.results.setWordWrap(True);searchlayout.addWidget(self.results)
        buttons=QHBoxLayout();self.previous=QPushButton();self.next=QPushButton()
        for button in (self.previous,self.next):button.setAutoDefault(False);buttons.addWidget(button)
        searchlayout.addLayout(buttons);self.sidebar.addTab(searchpage,'Search')
        self.favorite_list=QListWidget();self.sidebar.addTab(self.favorite_list,'Favorites')
        page=QWidget();pagelayout=QVBoxLayout(page);pagelayout.setContentsMargins(0,0,0,0)
        self.breadcrumb=QLabel();self.breadcrumb.setObjectName('muted');pagelayout.addWidget(self.breadcrumb)
        self.browser=QTextBrowser();self.browser.setOpenExternalLinks(False);self.browser.setOpenLinks(False)
        self.browser.setObjectName('guideDocument');self.browser.document().setDocumentMargin(24);pagelayout.addWidget(self.browser)
        self.splitter.addWidget(self.sidebar);self.splitter.addWidget(page);self.page=page
        self.splitter.setStretchFactor(1,1);self.splitter.setSizes([290,860])
        footer=QHBoxLayout();self.status=QLabel();self.status.setObjectName('muted');footer.addWidget(self.status,1)
        self.close_button=QPushButton();self.close_button.setAutoDefault(False);self.close_button.clicked.connect(self.close)
        footer.addWidget(self.close_button);box.addLayout(footer)
        self.contents.currentItemChanged.connect(self.tree_changed)
        self.results.itemActivated.connect(lambda item:self.open_topic(item.data(Qt.UserRole)))
        self.results.itemClicked.connect(lambda item:self.open_topic(item.data(Qt.UserRole)))
        self.favorite_list.itemActivated.connect(lambda item:self.open_topic(item.data(Qt.UserRole)))
        self.favorite_list.itemClicked.connect(lambda item:self.open_topic(item.data(Qt.UserRole)))
        self.browser.anchorClicked.connect(self.follow_link);self.language.currentIndexChanged.connect(self.change_language)
        self.search.textChanged.connect(self.search_all);self.search.returnPressed.connect(lambda:self.find_text())
        self.next.clicked.connect(lambda:self.find_text());self.previous.clicked.connect(lambda:self.find_text(True))
        self.shortcuts=[]
        for key,callback in [(QKeySequence.Find,self.focus_search),(QKeySequence.Back,self.go_back),
            (QKeySequence.Forward,self.go_forward),(QKeySequence.Print,self.print_topic)]:
            shortcut=QShortcut(key,self);shortcut.activated.connect(callback);self.shortcuts.append(shortcut)
        geometry=self.settings.value('help/geometry')
        if geometry:self.restoreGeometry(geometry)
        self.change_language()
        self.open_topic(topic or self.settings.value('help/topic','start'))

    def change_language(self,*unused):
        lang=self.language.currentData();self.arabic=lang=='ar'
        self.setLayoutDirection(Qt.RightToLeft if self.arabic else Qt.LeftToRight)
        self.splitter.setLayoutDirection(Qt.LeftToRight)
        self.splitter.insertWidget(0,self.page if self.arabic else self.sidebar)
        self.splitter.setStretchFactor(self.splitter.indexOf(self.sidebar),0)
        self.splitter.setStretchFactor(self.splitter.indexOf(self.page),1)
        self.splitter.setSizes([850,290] if self.arabic else [290,850])
        self.title.setText('مركز مساعدة مرصاد' if self.arabic else 'MIRSAD Help Centre')
        self.setWindowTitle(self.title.text())
        labels={'back':('رجوع','Back'),'forward':('تقدم','Forward'),'home':('الرئيسية','Home'),
            'pane':('الفهرس','Contents pane'),'favorite':('المفضلة','Bookmark'),'print':('طباعة','Print'),
            'pdf':('حفظ PDF','Save PDF'),'smaller':('A−','A−'),'larger':('A+','A+'),'theme':('فاتح / داكن','Light / Dark')}
        for key,pair in labels.items():self.actions[key].setText(pair[0 if self.arabic else 1])
        for i,pair in enumerate([('المحتويات','Contents'),('بحث','Search'),('المفضلة','Favorites')]):self.sidebar.setTabText(i,pair[0 if self.arabic else 1])
        self.search.setPlaceholderText('ابحث في كامل الدليل…' if self.arabic else 'Search the entire manual…')
        self.search.setAccessibleName(self.search.placeholderText());self.contents.setAccessibleName(self.sidebar.tabText(0))
        self.previous.setText('التطابق السابق' if self.arabic else 'Previous match');self.next.setText('التطابق التالي' if self.arabic else 'Next match')
        self.close_button.setText('إغلاق' if self.arabic else 'Close')
        self.contents.blockSignals(True);self.contents.clear();self.tree_items={}
        for group in self.index['groups']:
            parent=QTreeWidgetItem([group[lang]]);self.contents.addTopLevelItem(parent)
            for topic in self.index['sections']:
                if topic['group']!=group['id']:continue
                item=QTreeWidgetItem([topic[lang]]);item.setData(0,Qt.UserRole,topic['id']);parent.addChild(item)
                self.tree_items[topic['id']]=item
        self.contents.blockSignals(False)
        self.refresh_favorites();self.open_topic(self.current_topic,record=False);self.search_all()

    def tree_changed(self,item,previous):
        if item and item.data(0,Qt.UserRole):self.open_topic(item.data(0,Qt.UserRole))

    def open_topic(self,key,record=True):
        if key not in self.topics:key='start'
        self.current_topic=key
        if record and (self.history_cursor<0 or self.history[self.history_cursor]!=key):
            self.history=self.history[:self.history_cursor+1]+[key];self.history_cursor=len(self.history)-1
        self.contents.blockSignals(True)
        item=self.tree_items[key];item.parent().setExpanded(True);self.contents.setCurrentItem(item);self.contents.scrollToItem(item)
        self.contents.blockSignals(False)
        self.apply_document_theme();self.actions['back'].setEnabled(self.history_cursor>0)
        self.actions['forward'].setEnabled(self.history_cursor<len(self.history)-1)
        self.actions['favorite'].setText(('★ إزالة المفضلة' if self.arabic else '★ Remove bookmark') if key in self.favorites else ('☆ المفضلة' if self.arabic else '☆ Bookmark'))
        self.update_status()

    def apply_document_theme(self):
        import html
        lang='ar' if self.arabic else 'en';topic=self.topics[self.current_topic]
        color=self.palette().color(QPalette.Text).name();dark=self.palette().color(QPalette.Window).lightness()<128
        link='#75d9d3' if dark else '#086770';border='#555' if dark else '#aaa'
        direction='rtl' if self.arabic else 'ltr'
        self.browser.document().setDefaultStyleSheet(f'body{{color:{color};font-size:{self.text_size}pt;}} a{{color:{link};}} h1{{font-size:22pt;}} table{{border-collapse:collapse;}} th,td{{border:1px solid {border};padding:8px;}}')
        self.browser.document().setBaseUrl(QUrl.fromLocalFile(str(asset_dir())+'/'))
        self.browser.setHtml(f'<html dir="{direction}"><body dir="{direction}"><h1>'+html.escape(topic[lang])+'</h1>'+topic[lang+'_body']+'</body></html>')
        option=self.browser.document().defaultTextOption();option.setTextDirection(Qt.RightToLeft if self.arabic else Qt.LeftToRight)
        self.browser.document().setDefaultTextOption(option)
        from PySide6.QtGui import QTextTable
        frames=list(self.browser.document().rootFrame().childFrames())
        while frames:
            frame=frames.pop();frames.extend(frame.childFrames())
            if isinstance(frame,QTextTable):
                fmt=frame.format();fmt.setLayoutDirection(Qt.RightToLeft if self.arabic else Qt.LeftToRight);frame.setFormat(fmt)
        group=next(g for g in self.index['groups'] if g['id']==topic['group'])
        self.breadcrumb.setText(group[lang]+' › '+topic[lang])

    def update_status(self):
        self.status.setText(('دليل محلي · الإصدار ' if self.arabic else 'Offline manual · Version ')+self.index['version']+' · '+self.index['reviewed'])

    def go_back(self):
        if self.history_cursor>0:self.history_cursor-=1;self.open_topic(self.history[self.history_cursor],False)

    def go_forward(self):
        if self.history_cursor<len(self.history)-1:self.history_cursor+=1;self.open_topic(self.history[self.history_cursor],False)

    def refresh_favorites(self):
        self.favorite_list.clear();lang='ar' if self.arabic else 'en'
        for key in self.favorites:
            item=QListWidgetItem(self.topics[key][lang]);item.setData(Qt.UserRole,key);self.favorite_list.addItem(item)

    def toggle_favorite(self):
        key=self.current_topic
        if key in self.favorites:self.favorites.remove(key)
        else:self.favorites.append(key)
        self.settings.setValue('help/favorites',json.dumps(self.favorites,ensure_ascii=False));self.settings.sync()
        self.refresh_favorites();self.open_topic(key,False)

    def focus_search(self):
        self.sidebar.show();self.sidebar.setCurrentIndex(1);self.search.setFocus();self.search.selectAll()

    def search_all(self,*unused):
        self.results.clear();query=normalize_search(self.search.text().strip());lang='ar' if self.arabic else 'en'
        if not query:return
        for topic in self.index['sections']:
            document=QTextDocument();document.setHtml(topic[lang+'_body']);text=document.toPlainText()
            normalized=normalize_search(topic[lang]+' '+text)
            position=normalized.find(query)
            if position<0:continue
            excerpt=text[max(0,position-50):position+130].replace('\n',' ')
            item=QListWidgetItem(topic[lang]+'\n'+excerpt);item.setData(Qt.UserRole,topic['id']);self.results.addItem(item)
        self.status.setText(str(self.results.count())+(' موضوع مطابق' if self.arabic else ' matching topics'))

    def find_text(self,backward=False):
        query=self.search.text().strip()
        if not query:self.focus_search();return False
        if not self.results.count():self.status.setText('لا توجد نتائج' if self.arabic else 'No matches');return False
        flags=QTextDocument.FindBackward if backward else QTextDocument.FindFlags()
        if self.browser.find(query,flags):return True
        if not self.browser.document().find(query).isNull():
            cursor=self.browser.textCursor();cursor.movePosition(QTextCursor.End if backward else QTextCursor.Start);self.browser.setTextCursor(cursor)
            return self.browser.find(query,flags)
        self.open_topic(self.results.item(0).data(Qt.UserRole))
        # Arabic normalization may match a spelling that QTextDocument.find does
        # not match literally. The topic/result still identifies that match.
        self.browser.find(query,flags);return True

    def follow_link(self,url):
        if url.scheme() in ('https','mailto'):
            from PySide6.QtGui import QDesktopServices
            QDesktopServices.openUrl(url)
        elif not url.scheme() and url.fragment():self.open_topic(url.fragment())

    def zoom(self,delta):
        self.text_size=max(8,min(22,self.text_size+delta));self.apply_document_theme()

    def toggle_theme(self):
        if self.parent() and hasattr(self.parent(),'toggle_theme'):
            self.parent().toggle_theme();return
        from .themes import apply_application_theme
        apply_application_theme(QApplication.instance(),self.palette().color(QPalette.Window).lightness()>=128)
        self.apply_document_theme()

    def paper_document(self):
        import html
        topic=self.topics[self.current_topic];lang='ar' if self.arabic else 'en';direction='rtl' if self.arabic else 'ltr'
        document=QTextDocument();document.setDefaultStyleSheet('body{color:#111;font-size:11pt;} a{color:#111;} table{border-collapse:collapse;} th,td{border:1px solid #888;padding:7px;}')
        document.setHtml(f'<body dir="{direction}"><h1>'+html.escape(topic[lang])+'</h1>'+topic[lang+'_body']+'</body>')
        option=document.defaultTextOption();option.setTextDirection(Qt.RightToLeft if self.arabic else Qt.LeftToRight);document.setDefaultTextOption(option)
        return document

    def export_pdf(self,path):
        writer=QPdfWriter(str(path));writer.setTitle(self.topics[self.current_topic]['ar' if self.arabic else 'en']);writer.setCreator('MIRSAD')
        self.paper_document().print_(writer)

    def save_pdf(self):
        path,_=QFileDialog.getSaveFileName(self,'PDF',self.current_topic+'.pdf','PDF (*.pdf)')
        if path:self.export_pdf(path)

    def print_topic(self):
        from PySide6.QtPrintSupport import QPrinter,QPrintPreviewDialog
        printer=QPrinter(QPrinter.HighResolution);preview=QPrintPreviewDialog(printer,self)
        document=self.paper_document();preview.paintRequested.connect(lambda target:document.print_(target));preview.exec()

    def closeEvent(self,event):
        self.settings.setValue('help/topic',self.current_topic);self.settings.setValue('help/geometry',self.saveGeometry());self.settings.sync()
        super().closeEvent(event)
