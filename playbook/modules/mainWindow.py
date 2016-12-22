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

from .core import Frame, Dancer
from .dataManage import XmlFormat
from .ui import ClickableLabel




IMG_PATH = os.path.join(SRCDIR,'img')

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.frames = Frame(self)
        self.initUI()
        
        
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
        previous = QPushButton(QIcon(pixmap),"")
        previous.setToolTip("Previous frame")
        previous.setIconSize(pixmap.rect().size())
        previous.setFixedSize(pixmap.rect().size())
        previous.clicked.connect(self.frames.previousFrame)
        hLayout.addWidget(previous)

        frameIDBox = QLineEdit()
        frameIDBox.setFixedWidth(30)
        frameIDBox.setText("0")
        frameIDBox.setValidator(QIntValidator(0, 999))
        frameIDBox.textChanged.connect(lambda x: self.frames.selectFrameById(x))
        self.frames.frameIDChanged.connect(lambda x:frameIDBox.setText(str(x)))
        hLayout.addWidget(frameIDBox)


        pixmap = QPixmap(os.path.join(IMG_PATH,"nextArrow.svg"))
        next = QPushButton(QIcon(pixmap),"")
        next.setIconSize(pixmap.rect().size())
        next.setFixedSize(pixmap.rect().size())
        next.setToolTip("Next frame")
        next.clicked.connect(self.frames.nextFrame)
        hLayout.addWidget(next)

        pixmap = QPixmap(os.path.join(IMG_PATH,"newFrame.svg"))
        newScene = QPushButton(QIcon(pixmap),"")
        newScene.setIconSize(pixmap.rect().size())
        newScene.setFixedSize(pixmap.rect().size())
        newScene.setToolTip("Create new frame")
        newScene.clicked.connect(self.frames.createFrame)
        hLayout.addWidget(newScene)

        pixmap = QPixmap(os.path.join(IMG_PATH,"deleteFrame.svg"))
        deleteScene = QPushButton(QIcon(pixmap),"")
        deleteScene.setIconSize(pixmap.rect().size())
        deleteScene.setFixedSize(pixmap.rect().size())
        deleteScene.setToolTip("Delete active frame")
        deleteScene.clicked.connect(self.frames.deleteFrame)
        hLayout.addWidget(deleteScene)

        frameStatus.setLayout(hLayout)
        


        
        grid.addWidget(frameStatus)
        #Main window position and icon
        self.resize(600, 600)
        self.center()
        self.setWindowTitle('Playbook')
        self.setWindowIcon(QIcon(os.path.join(IMG_PATH,'GrowlLogo.png'))) 


        #Status Bar and Menu
        exitAction = QAction(QIcon(os.path.join(IMG_PATH,'GrowlLogo.png')), '&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        saveAction = QAction('&Save',self)
        saveAction.triggered.connect(self.save)

        loadAction = QAction('&Load',self)
        loadAction.triggered.connect(self.load)

        printPdfAction = QAction('&Print',self)
        printPdfAction.triggered.connect(self.printToPdf)


        drawAction = QAction(QIcon(''),'Toogle drawing',self,checkable=True)
        drawAction.triggered.connect(self.frames.toggleDrawing)
        eraseAction = QAction(QIcon(''),'Toogle eraser',self,checkable=True)
        eraseAction.triggered.connect(self.frames.toggleErase)

        self.statusBar()

        menubar = self.menuBar()  
        menubar.setNativeMenuBar(False)   
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)  
        fileMenu.addAction(saveAction)  
        fileMenu.addAction(loadAction)
        fileMenu.addAction(printPdfAction)

        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(drawAction)
        editMenu.addAction(eraseAction)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(drawAction)
        self.toolbar.addAction(eraseAction)

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
        doc.appendChild(formatter.frameToXml(self.frames))       
        saveFile = open(name,'w')
        saveFile.write(doc.toString())
        saveFile.close()

    def load(self):
        name = QFileDialog.getOpenFileName(self, 'Load File')[0]
        doc = QDomDocument(name)
        openFile = QFile(name)
        doc.setContent(openFile)
        formatter = XmlFormat(doc)
        formatter.xmlToFrame(self.frames)
        openFile.close() 
        self.centralWidget().update()


    def printToPdf(self):
        pdf_printer = QPrinter()
        pdf_printer.setOutputFormat(QPrinter.PdfFormat)
        pdf_printer.setPaperSize(self.frames.sceneRect().size(), QPrinter.Point)
        pdf_printer.setFullPage(True)
        pdf_printer.setOutputFileName("tmp.pdf")
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
