import json,os,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
(ROOT/".test-output").mkdir(exist_ok=True)
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt,QUrl
from PySide6.QtPdf import QPdfDocument
from mirsad_desktop.userguide import UserGuideDialog
from mirsad_desktop.themes import apply_application_theme


class HelpCentreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'.test-output');self.previous=os.environ.get('MIRSAD_TEST_SETTINGS')
        os.environ['MIRSAD_TEST_SETTINGS']=str(Path(self.tmp.name)/'settings.ini')
        apply_application_theme(self.app,False)
        self.guide=UserGuideDialog(topic='formula-pet');self.guide.show();self.app.processEvents()

    def tearDown(self):
        self.guide.close();self.guide.deleteLater();self.app.processEvents()
        if self.previous is None:os.environ.pop('MIRSAD_TEST_SETTINGS',None)
        else:os.environ['MIRSAD_TEST_SETTINGS']=self.previous
        self.tmp.cleanup()

    def test_topic_links_history_and_language_preserve_equation(self):
        guide=self.guide;self.assertEqual(len(guide.topics),45)
        guide.follow_link(QUrl('#calculation-flow'));self.assertEqual(guide.current_topic,'calculation-flow')
        guide.go_back();self.assertEqual(guide.current_topic,'formula-pet')
        guide.go_forward();self.assertEqual(guide.current_topic,'calculation-flow')
        guide.open_topic('formula-rain');guide.language.setCurrentIndex(guide.language.findData('ar'));self.app.processEvents()
        self.assertEqual(guide.current_topic,'formula-rain')
        self.assertIn('R_Annual_Mean',guide.browser.toPlainText())
        self.assertIn('المطر المفقود',guide.browser.toPlainText())
        self.assertGreater(guide.sidebar.x(),guide.page.x())

    def test_full_document_arabic_normalization_and_exact_field_search(self):
        guide=self.guide
        guide.search.setText('Water_Deficit_Annual')
        self.assertIn('formula-water-deficit',[guide.results.item(i).data(Qt.UserRole) for i in range(guide.results.count())])
        guide.language.setCurrentIndex(guide.language.findData('ar'));guide.search.setText('الامطار')
        self.assertIn('formula-rain',[guide.results.item(i).data(Qt.UserRole) for i in range(guide.results.count())])
        guide.search.setText('MIRSAD_NO_SUCH_TOPIC_09876');self.assertEqual(guide.results.count(),0)

    def test_bookmark_and_topic_survive_reopening(self):
        self.guide.open_topic('formula-pet');self.guide.toggle_favorite();self.guide.close()
        reopened=UserGuideDialog(arabic=True)
        try:
            self.assertEqual(reopened.current_topic,'formula-pet');self.assertIn('formula-pet',reopened.favorites)
            self.assertEqual(reopened.favorite_list.count(),1)
            reopened.toggle_favorite();self.assertNotIn('formula-pet',reopened.favorites)
        finally:reopened.close();reopened.deleteLater()

    def test_light_dark_equations_and_real_pdf_output(self):
        for lang in ('ar','en'):
            self.guide.language.setCurrentIndex(self.guide.language.findData(lang))
            for dark in (False,True):
                apply_application_theme(self.app,dark);self.guide.apply_document_theme()
                self.assertIn('PET_m =',self.guide.browser.toPlainText())
            path=Path(self.tmp.name)/(lang+'.pdf');self.guide.export_pdf(path)
            self.assertTrue(path.read_bytes().startswith(b'%PDF'))
            document=QPdfDocument();self.assertEqual(document.load(str(path)),QPdfDocument.Error.None_)
            self.assertGreater(document.pageCount(),0)
            text=''.join(document.getAllText(i).text() for i in range(document.pageCount()))
            self.assertIn('ET_Annual_Mean',text);document.close()


if __name__=='__main__':unittest.main()
