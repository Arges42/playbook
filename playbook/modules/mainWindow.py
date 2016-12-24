import sys,os
from PyQt5.QtWidgets import (QWidget, QToolTip, 
    QPushButton, QMessageBox, QApplication, QDesktopWidget, QMainWindow, QAction, qApp, QGridLayout, QFormLayout, QHBoxLayout, QColorDialog, QDialogButtonBox, QLineEdit,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsItem, QMenu, QGraphicsObject, QDialog, QFileDialog)
from PyQt5.QtGui import QFont,QIcon, QBrush, QColor, QPen, QPainter, QPixmap,QIntValidator
from PyQt5.QtCore import QCoreApplication,QRectF, QPointF, Qt, pyqtSignal, QObject,QDateTime, QFile, QSize

from PyQt5.QtXml import QDomDocument
from PyQt5.QtPrintSupport import QPrinter

if getattr(sys, 'frozen', False):
    # The application is frozen
    SRCDIR = os.path.dirname(sys.executable)
else:
    # The application is not frozen
    # Change this bit to match where you store your data files:
    SRCDIR = os.path.dirname(os.path.dirname(__file__))

from .core import FrameViewer, Dancer
from .dataManage import XmlFormat
from .ui import ClickableLabel,SettingsDialog
from .util import Settings,SlotManager



IMG_PATH = os.path.join(SRCDIR,'img')

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.settings = Settings(self)
        self.frames = FrameViewer(self,self.settings)
        self.projectName = ""
        self.initUI()
        SlotManager.makeMainWindowConnections(self)
        
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

        #Define actions
        pixmap = QPixmap(os.path.join(IMG_PATH,"prevArrow.svg"))
        self.previous = QPushButton(QIcon(pixmap),"")
        self.previous.setToolTip("Previous frame")
        self.previous.setIconSize(pixmap.rect().size())
        self.previous.setFixedSize(pixmap.rect().size())
        #self.previous.clicked.connect(self.frames.previousFrame)
        hLayout.addWidget(self.previous)

        self.frameIDBox = QLineEdit()
        self.frameIDBox.setFixedWidth(30)
        self.frameIDBox.setText("0")
        self.frameIDBox.setValidator(QIntValidator(0, 999))
        #self.frameIDBox.textChanged.connect(lambda x: self.frames.selectFrameById(x))
        #self.frames.frameIDChanged.connect(lambda x:frameIDBox.setText(str(x)))
        hLayout.addWidget(self.frameIDBox)


        pixmap = QPixmap(os.path.join(IMG_PATH,"nextArrow.svg"))
        self.next = QPushButton(QIcon(pixmap),"")
        self.next.setIconSize(pixmap.rect().size())
        self.next.setFixedSize(pixmap.rect().size())
        self.next.setToolTip("Next frame")
        #self.next.clicked.connect(self.frames.nextFrame)
        hLayout.addWidget(self.next)

        pixmap = QPixmap(os.path.join(IMG_PATH,"newFrame.svg"))
        self.newScene = QPushButton(QIcon(pixmap),"")
        self.newScene.setIconSize(pixmap.rect().size())
        self.newScene.setFixedSize(pixmap.rect().size())
        self.newScene.setToolTip("Create new frame")
        #self.newScene.clicked.connect(self.frames.createFrame)
        hLayout.addWidget(self.newScene)

        pixmap = QPixmap(os.path.join(IMG_PATH,"deleteFrame.svg"))
        self.deleteScene = QPushButton(QIcon(pixmap),"")
        self.deleteScene.setIconSize(pixmap.rect().size())
        self.deleteScene.setFixedSize(pixmap.rect().size())
        self.deleteScene.setToolTip("Delete active frame")
        #self.deleteScene.clicked.connect(self.frames.deleteFrame)
        hLayout.addWidget(self.deleteScene)

        frameStatus.setLayout(hLayout)
        


        
        grid.addWidget(frameStatus)
        #Main window position and icon
        self.resize(600, 600)
        self.center()
        self.setWindowTitle('Playbook')
        self.setWindowIcon(QIcon(os.path.join(IMG_PATH,'GrowlLogo.png'))) 


        #Status Bar and Menu
        self.exitAction = QAction(QIcon(os.path.join(IMG_PATH,'GrowlLogo.png')), '&Exit', self)        
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        #self.exitAction.triggered.connect(qApp.quit)

        self.saveAction = QAction('&Save',self)
        #self.saveAction.triggered.connect(self.save)

        self.loadAction = QAction('&Load',self)
        #self.loadAction.triggered.connect(self.load)

        self.printPdfAction = QAction('&Print',self)
        #self.printPdfAction.triggered.connect(self.printToPdf)


        self.drawAction = QAction(QIcon(''),'Toogle drawing',self,checkable=True)
        #self.drawAction.triggered.connect(self.frames.toggleDrawing)
        self.eraseAction = QAction(QIcon(''),'Toogle eraser',self,checkable=True)
        #self.eraseAction.triggered.connect(self.frames.toggleErase)

        
        self.openSettingsAction = QAction(QIcon(''),'Open settings',self)
        #self.openSettingsAction.triggered.connect(self.changeSettings)

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

        settingsMenu = menubar.addMenu('&Settings')
        settingsMenu.addAction(self.openSettingsAction)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(self.exitAction)
        self.toolbar.addAction(self.drawAction)
        self.toolbar.addAction(self.eraseAction)

        self.show()

    def center(self):
        
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def save(self):
        name = QFileDialog.getSaveFileName(self, 'Save File')[0]
        doc = QDomDocument()
        formatter = XmlFormat(doc)
        doc.appendChild(formatter.projectToXml(self))       
        saveFile = open(name,'w')
        saveFile.write(doc.toString())
        saveFile.close()

    def load(self):
        name = QFileDialog.getOpenFileName(self, 'Load File')[0]
        doc = QDomDocument(name)
        openFile = QFile(name)
        doc.setContent(openFile)
        formatter = XmlFormat(doc)
        formatter.xmlToProject(self)
        openFile.close() 
        self.centralWidget().update()


    def printToPdf(self):
        pdf_printer = QPrinter()
        pdf_printer.setOutputFormat(QPrinter.PdfFormat)
        pdf_printer.setPaperSize(self.frames.sceneRect().size(), QPrinter.Point)
        pdf_printer.setFullPage(True)
        pdf_printer.setOutputFileName("tmp.pdf")
        pdf_printer.newPage()
        pdf_painter = QPainter()
        pdf_painter.begin(pdf_printer)
        for i,scene in enumerate(self.frames.sceneCollection):
            self.frames.setScene(scene)
            viewport = self.frames.viewport().rect()
            self.frames.render(pdf_painter, QRectF(pdf_printer.width()*0.25, pdf_printer.height()*0.1,
                   pdf_printer.width(), pdf_printer.height()/2. ),
            self.frames.mapFromScene(self.frames.roomRect).boundingRect())
            if i<len(self.frames.sceneCollection)-1:
                pdf_printer.newPage()
        pdf_painter.end()

    def changeSettings(self):

        newSettings = SettingsDialog.getModification(currentSettings = self.settings)
        if newSettings["accept"]:
            self.settings.updateSettings(newSettings)

    def updateSettings(self, settings):
        self.projectName = settings.get("projectName")
