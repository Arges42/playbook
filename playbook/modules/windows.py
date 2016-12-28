import sys,os
from PyQt5.QtWidgets import (QWidget, QToolTip, 
    QPushButton, QMessageBox, QApplication, QDesktopWidget, QMainWindow, QAction, qApp, QGridLayout, QFormLayout, QHBoxLayout,QVBoxLayout, QColorDialog, QDialogButtonBox, QLineEdit, QDockWidget,QScrollArea,QLabel,QScrollBar,QMessageBox,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsItem, QMenu, QGraphicsObject, QDialog, QFileDialog)
from PyQt5.QtGui import QFont,QIcon, QBrush, QColor, QPen, QPainter, QPixmap,QIntValidator
from PyQt5.QtCore import QCoreApplication,QRectF, QPointF, Qt, pyqtSignal, QObject,QDateTime, QFile, QSize, QStandardPaths

from PyQt5.QtXml import QDomDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

if getattr(sys, 'frozen', False):
    # The application is frozen
    SRCDIR = os.path.dirname(sys.executable)
else:
    # The application is not frozen
    # Change this bit to match where you store your data files:
    SRCDIR = os.path.dirname(os.path.dirname(__file__))

from .core import FrameViewer, SingleFrameViewer, Dancer
from .dataManage import XmlFormat,SettingWriter
from .ui import ClickableLabel,SettingsDialog,OverviewLabel,ActionDialog
from .util import Settings,SlotManager



IMG_PATH = os.path.join(SRCDIR,'img')

class MainWindow(QMainWindow):
    ''' Main window of the playbook.
        The central widget displays the frame viewer and the buttons to switch between the frames.
        Additional the UI like menus,  toolbars and dock widget are initialized here.

    '''
    
    def __init__(self):
        super().__init__()
        
        self.settings = Settings(self)
        self.frames = FrameViewer(self,self.settings)
        self.projectName = "unnamed"
        self.unsavedChanges = False
        self.initUI()
        SlotManager.makeMainWindowConnections(self)

        self.setWindowTitle("Playbook - {}".format(self.projectName))
        SettingWriter(self).loadSettings(SRCDIR)
        
    def initUI(self):
        
        mainWidget = QWidget(self)
        self.setCentralWidget(mainWidget)


        #Define child widgets
        grid = QGridLayout()
        mainWidget.setLayout(grid)

        
        grid.addWidget(self.frames)

        frameStatus = QWidget(self)
        hLayout = QHBoxLayout()
        hLayout.addStretch(0)

        #Define frame viewer actions
        pixmap = QPixmap(os.path.join(IMG_PATH,"prevArrow.svg"))
        self.previous = QPushButton(QIcon(pixmap),"")
        self.previous.setToolTip("Previous frame")
        self.previous.setIconSize(pixmap.rect().size())
        self.previous.setFixedSize(pixmap.rect().size())
        self.previous.setObjectName("previousFrame")
        hLayout.addWidget(self.previous)

        self.frameIDBox = QLineEdit()
        self.frameIDBox.setFixedWidth(30)
        self.frameIDBox.setText("0")
        self.frameIDBox.setValidator(QIntValidator(0, 999))
        hLayout.addWidget(self.frameIDBox)


        pixmap = QPixmap(os.path.join(IMG_PATH,"nextArrow.svg"))
        self.next = QPushButton(QIcon(pixmap),"")
        self.next.setIconSize(pixmap.rect().size())
        self.next.setFixedSize(pixmap.rect().size())
        self.next.setToolTip("Next frame")
        self.next.setObjectName("nextFrame")
        hLayout.addWidget(self.next)

        pixmap = QPixmap(os.path.join(IMG_PATH,"newFrame.svg"))
        self.newScene = QPushButton(QIcon(pixmap),"")
        self.newScene.setIconSize(pixmap.rect().size())
        self.newScene.setFixedSize(pixmap.rect().size())
        self.newScene.setToolTip("Create new frame")
        self.newScene.setObjectName("newFrame")
        hLayout.addWidget(self.newScene)

        pixmap = QPixmap(os.path.join(IMG_PATH,"deleteFrame.svg"))
        self.deleteScene = QPushButton(QIcon(pixmap),"")
        self.deleteScene.setIconSize(pixmap.rect().size())
        self.deleteScene.setFixedSize(pixmap.rect().size())
        self.deleteScene.setToolTip("Delete active frame")
        hLayout.addWidget(self.deleteScene)

        frameStatus.setLayout(hLayout)
        


        
        grid.addWidget(frameStatus)
        #Main window position and icon
        self.resize(600, 600)
        self.center()
        self.setWindowIcon(QIcon(os.path.join(IMG_PATH,'GrowlLogo.png'))) 

        
        #Dock widgets
        dock = QDockWidget("Overview", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.overview = Overview(dock)
        dock.setWidget(self.overview)
        dock.setMinimumSize(150,0)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.frames.frameCreated.connect(lambda x: self.overview.addWidget(x))
        self.frames.frameIDChanged.connect(lambda x: self.overview.activeFrameChanged(x))

        #Define the Actions
        self.exitAction = QAction(QIcon(os.path.join(IMG_PATH,'exit.svg')), '&Exit', self)        
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.setObjectName("exit")
        self.saveAction = QAction('&Save',self)
        self.saveAction.setObjectName("save")
        self.loadAction = QAction('&Load',self)
        self.loadAction.setObjectName("load")
        self.printPdfAction = QAction('&Print',self)
        self.printPdfAction.setObjectName("print")

        self.drawAction = QAction(QIcon(os.path.join(IMG_PATH,'pen.svg')),'Toogle drawing',self,checkable=True)
        self.drawAction.setObjectName("draw")
        self.eraseAction = QAction(QIcon(os.path.join(IMG_PATH,'eraser.svg')),'Toogle eraser',self,checkable=True)
        self.eraseAction.setObjectName("erase")
        self.toogleGridAction = QAction(QIcon(os.path.join(IMG_PATH,'grid.svg')),'Toggle grid',self,checkable=True)
        self.toogleGridAction.setChecked(True)
        self.toogleGridAction.setObjectName("toggleGrid")
        
        self.openSettingsAction = QAction(QIcon(''),'Open settings',self)
        self.openShortcutAction = QAction(QIcon(''),'Modify shortcuts',self)

        #Status Bar and Menu
        self.statusBar()

        menubar = self.menuBar()  
        menubar.setNativeMenuBar(False)   
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.exitAction)  
        fileMenu.addAction(self.saveAction)  
        fileMenu.addAction(self.loadAction)
        fileMenu.addAction(self.printPdfAction)

        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(self.drawAction)
        editMenu.addAction(self.eraseAction)
        editMenu.addAction(self.toogleGridAction)

        settingsMenu = menubar.addMenu('&Settings')
        settingsMenu.addAction(self.openSettingsAction)
        settingsMenu.addAction(self.openShortcutAction)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(self.exitAction)
        self.toolbar.addAction(self.drawAction)
        self.toolbar.addAction(self.eraseAction)
        self.toolbar.addAction(self.toogleGridAction)

        self.show()

    def center(self):
        
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self,event):
        SettingWriter(self).writeSettings(SRCDIR)
        if self.unsavedChanges == True:
            msg = "You have unsaved changes!\nAre you sure you want to exit?"
            reply = QMessageBox.question(self, 'Message', 
                     msg, QMessageBox.Yes, QMessageBox.No)

            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        
    def save(self):
        name = QFileDialog.getSaveFileName(self, 'Save File')[0]
        if name:
            doc = QDomDocument()
            formatter = XmlFormat(doc)
            doc.appendChild(formatter.projectToXml(self))       
            saveFile = open(name,'w')
            saveFile.write(doc.toString())
            saveFile.close()
            self.unsavedChanges = False
            self.setWindowTitle("playbook - {}".format(self.projectName))


    def load(self):
        name = QFileDialog.getOpenFileName(self, 'Load File')[0]
        if name:
            doc = QDomDocument(name)
            openFile = QFile(name)
            doc.setContent(openFile)
            formatter = XmlFormat(doc)
            formatter.xmlToProject(self)
            openFile.close() 
            self.centralWidget().update()
            self.setWindowTitle("playbook - {}".format(self.projectName))
            self.overview.addWidget()

    def printToPdf(self):
        pdf_printer = QPrinter()
        pdf_printer.setOutputFormat(QPrinter.PdfFormat)
        pdf_printer.setPaperSize(self.frames.sceneRect().size(), QPrinter.Point)
        pdf_printer.setFullPage(True)
        
        pdf_printer.setOutputFileName(os.path.join(QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation),self.projectName+".pdf"))
        pdf_printer.setResolution(144)
        pdf_printer.newPage()
        printDialog = QPrintDialog(pdf_printer, self)
        if(printDialog.exec_() == QDialog.Accepted):
            pdf_painter = QPainter()
            pdf_painter.begin(pdf_printer)
            for i,scene in enumerate(self.frames.sceneCollection):
                #self.frames.setScene(scene)
                #viewport = self.frames.viewport().rect()
                #self.frames.render(pdf_painter, QRectF(pdf_printer.width()*0.25, pdf_printer.height()*0.1,
                #       pdf_printer.width(), pdf_printer.height()/2. ),
                #(self.frames.mapFromScene(QRectF(viewport)).boundingRect()))
                scene.render(pdf_painter)
                if i<len(self.frames.sceneCollection)-1:
                    pdf_printer.newPage()
            pdf_painter.end()

    def changeShortcuts(self):
        dialog = ActionDialog(self)
        dialog.exec_()


    def contentChanged(self):
        self.unsavedChanges = True
        self.setWindowTitle("Playbook - {}{}".format("*",self.projectName))

    def changeSettings(self):

        newSettings = SettingsDialog.getModification(currentSettings = self.settings)
        if newSettings["accept"]:
            self.settings.updateSettings(newSettings)

    def updateSettings(self, settings):
        self.projectName = settings.get("projectName")
        self.contentChanged()



class Overview(QWidget):
    ''' Dock Widget
        This widget shows an overview of all created frames.
        Supports:   Change to a frame with a click.
                    The active frame is heighlighted.
    '''
    def __init__(self,parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget(self.scrollArea)
        self.vLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.vLayout.setSpacing(20)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.scrollArea.setMinimumSize(150,self.parent().parent().frames.size().height())
        self.addWidget()

        self.parent().parent().frames.resized.connect(lambda x:self.adaptFrameViewerSize(x))

        

    def addWidget(self,frameID = 0):
        for i in reversed(range(self.vLayout.count())): 
            widget = self.vLayout.takeAt(i).widget()
            if widget is not None:
                widget = widget.setParent(None)

        for i,frame in enumerate(self.parent().parent().frames.sceneCollection):
            label = OverviewLabel(self)
            view = SingleFrameViewer(label,self.parent().parent().frames)
            view.setScene(frame)
            view.scale(0.2,0.2)
            view.resize(130,130)
            label.clicked.connect(lambda x: self.labelClicked(x))
            self.vLayout.insertWidget(i,label)
        self.activeFrameChanged(self.parent().parent().frames.activeFrameID)
    
    def activeFrameChanged(self,activeFrameID):
        for i in reversed(range(self.vLayout.count())):
            widget = self.vLayout.itemAt(i).widget()
            if widget is not None:
                if widget.active:
                    widget.toggleActive() 
        activeFrame = self.vLayout.itemAt(activeFrameID)
        if activeFrame is not None:
            activeFrame.widget().toggleActive()    

    def labelClicked(self,widget):
        self.parent().parent().frames.selectFrameById(self.vLayout.indexOf(widget))

    def adaptFrameViewerSize(self,size):
        self.scrollArea.setMinimumSize(self.scrollArea.minimumSize().width(),size.height()-7)
        
