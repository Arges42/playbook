import sys
from PyQt5.QtWidgets import (QWidget, QToolTip, 
    QPushButton, QMessageBox, QApplication, QDesktopWidget, QMainWindow, QAction, qApp, QGridLayout, QFormLayout, QColorDialog, QDialogButtonBox, QLineEdit, QGraphicsLineItem, QGraphicsTextItem,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsItem, QMenu, QGraphicsObject, QDialog)
from PyQt5.QtGui import QFont,QIcon, QBrush, QColor, QPen
from PyQt5.QtCore import QCoreApplication,QRectF, QPointF, Qt, pyqtSignal, QObject,QDateTime, QLineF


from .ui import DancerDialog


class Frame(QGraphicsView):

    frameIDChanged = pyqtSignal(int)    

    def __init__(self,parent,roomRect=QRectF(-200,-200,400,400),new=True):
        super().__init__(parent)    

        #State variables
        self.roomRect = roomRect
        self.gridSize = 20

        self.lastPoint = None
        self.scribbling = False
        self.drawing = False
        self.erase = False
        self.penWidth = 1
        self.penColor = Qt.blue

        #Collection for all scenes
        self.sceneCollection = []
        
        if new:
            #Default scene
            self.scene = QGraphicsScene(self)
            self.setScene(self.scene)
            self.setSceneRect(self.roomRect)
            self.sceneCollection.append(self.scene)
        self.activeFrameID = 0


    ###########REIMPLEMENTATIONS###########################
    def drawBackground(self,painter,rect):
        left = int(self.roomRect.left()) - (int(self.roomRect.left()) % self.gridSize)
        top = int(self.roomRect.top()) - (int(self.roomRect.top()) % self.gridSize)
        points = []
        for x in range(left,int(self.roomRect.right()),self.gridSize):
            for y in range(top,int(self.roomRect.bottom()),self.gridSize):
                painter.drawPoint(x,y)
        
        painter.drawRect(self.roomRect)
    '''
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.lastPoint = event.pos()
            self.scribbling = True

        elif event.button() == Qt.LeftButton and self.erase:
            for item in self.items(event.pos()):
                if isinstance(item,QGraphicsLineItem):
                    self.scene. removeItem(item)
        else: 
            QGraphicsView.mousePressEvent(self,event)


    def mouseReleaseEvent(self, event):
        if (event.button() == Qt.LeftButton and self.scribbling and self.drawing):
            start = QPointF(self.mapToScene(self.lastPoint))
            end = QPointF(self.mapToScene(event.pos()))
            self.scene.addItem(
            QGraphicsLineItem(QLineF(start, end)))
            self.scribbling = False
    '''


    ###########REIMPLEMENTATIONS###########################
    ###########SLOT DEFINITIONS###########
    def createDancer(self,pos):
        newDancer = Dancer(self.roomRect)
        newDancer.setPos(self.mapToScene(pos))
        newDancer.deleteRequested.connect(lambda x:self.deleteDancer(x))
        self.scene.addItem(newDancer)

    def deleteDancer(self,dancerID=0):
        for item in self.scene.items():
            if(item.dancerID==dancerID):
                self.scene.removeItem(item)

    def addText(self,pos):
        text = TextBox("Text")
        text.setPos(self.mapToScene(pos))
        self.scene.addItem(text)

    def createFrame(self):
        self.scene = self.copyScene(self.sceneCollection[self.activeFrameID])
        self.setScene(self.scene)
        self.setSceneRect(self.roomRect)
        self.sceneCollection.append(self.scene)
        self.activeFrameID+=1
        self.frameIDChanged.emit(self.activeFrameID)

    def deleteFrame(self):
        if len(self.sceneCollection) == 1:
            self.scene.clear()
        else:
            if self.activeFrameID == (len(self.sceneCollection)-1):
                newID = self.activeFrameID-1
            else:
                newID = self.activeFrameID
            self.scene = self.sceneCollection[newID]
            self.setScene(self.scene)
            del self.sceneCollection[self.activeFrameID]
            self.activeFrameID -= 1
            self.frameIDChanged.emit(self.activeFrameID)

  
    def nextFrame(self):
        if self.activeFrameID == (len(self.sceneCollection)-1):
            self.activeFrameID = 0
        else:
            self.activeFrameID += 1
        self.scene = self.sceneCollection[self.activeFrameID]
        self.setScene(self.scene)
        self.frameIDChanged.emit(self.activeFrameID)

    def previousFrame(self):
        if self.activeFrameID == 0:
            self.activeFrameID = len(self.sceneCollection)-1
        else:
            self.activeFrameID -= 1
        self.scene = self.sceneCollection[self.activeFrameID]
        self.setScene(self.scene)
        self.frameIDChanged.emit(self.activeFrameID)

    def selectFrameById(self,i):
        if i.isdigit():            
            i = int(i)
            if(i<len(self.sceneCollection)):
                self.activeFrameID = i
                self.scene = self.sceneCollection[self.activeFrameID]
                self.setScene(self.scene)

    def toggleDrawing(self):
        self.drawing = not self.drawing
    def toggleErase(self):
        self.erase = not self.erase
    ###########SLOT DEFINITIONS###########

    def contextMenuEvent(self, event):

        QGraphicsView.contextMenuEvent(self,event)
        if(not event.isAccepted()):
            menu = QMenu()
            createDancer = QAction('&Create new dancer',self)
            createDancer.triggered.connect(lambda: self.createDancer(event.pos()))
            menu.addAction(createDancer)

            addText = QAction('&Add text',self)
            addText.triggered.connect(lambda: self.addText(event.pos()))
            menu.addAction(addText)
            menu.exec_(event.globalPos())

    #Hier müssen alle Items der scene kopiert werden
    def copyScene(self,scene):
        copiedScene = QGraphicsScene(self)
        for item in scene.items():
            if isinstance(item,Dancer):
                copy = item.copy()
                copy.setPos(item.pos())
                copiedScene.addItem(copy)
        
        return copiedScene

    def clear(self):
        for scene in self.sceneCollection:
            del scene
        self.sceneCollection = []
        self.scene = None
        self.setScene(self.scene)


class Dancer(QGraphicsObject):

    globalID = 0
    # define signals
    deleteRequested = pyqtSignal(int)

    def __init__(self, restrictRect=None, parent=None,copy=False):
        super().__init__()

        # set flags
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # Dancer specific properties
        self.color = QColor("black")
        self.boundaryColor = QColor("black")
        self.name = "Dummy"
        self.alias = ""

        # set move restriction rect for the item
        if restrictRect != None:
            self.restrictRect = restrictRect

        if not copy:
            self.dancerID = Dancer.globalID
        Dancer.globalID+=1

    def boundingRect(self):
        return QRectF(-10,0,60,50)
        
    def paint(self, painter, option, widget = None):
        painter.setPen(QPen(QBrush(self.boundaryColor),3));
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(0,0,30,30)
        painter.drawText(QPointF(-10,40),self.name)

    def mouseMoveEvent(self, event):
        # check of mouse moved within the restricted area for the item 
        if self.restrictRect.contains(event.scenePos()):
            QGraphicsEllipseItem.mouseMoveEvent(self, event)

    def itemChange(self,change,value):
        
        if ((change == QGraphicsItem.ItemPositionChange) and (self.scene()!=None)):
            newPos = value

            if(QApplication.mouseButtons() == Qt.LeftButton and self.scene() != None):
                gridSize = self.scene().parent().gridSize
                xV = round(newPos.x()/gridSize)*gridSize;
                yV = round(newPos.y()/gridSize)*gridSize;
                return QPointF(xV, yV);
            
            else:

                return newPos
    
        else:
            return QGraphicsItem.itemChange(self,change, value)

    def modifyDancer(self):
        changes = DancerDialog.getModification(dancer=self)
        if changes["accept"]:
            self.name = changes["name"]
            self.alias = changes["alias"]
            self.color = QColor(changes["color"])
            self.boundaryColor = QColor(changes["bColor"])
            self.scene().update()

    def contextMenuEvent(self, event):
        menu = QMenu()
        removeDancer = QAction('&Remove Dancer',self)
        removeDancer.triggered.connect(lambda: self.deleteRequested.emit(self.dancerID))
        menu.addAction(removeDancer)

        modifyDancer = QAction('&Modify Dancer',self)
        modifyDancer.triggered.connect(self.modifyDancer)
        menu.addAction(modifyDancer)
        menu.exec_(event.screenPos())
        event.setAccepted(True)


    def copy(self):
        copy = Dancer(self.restrictRect,self.parent,copy=True)
        copy.color = self.color
        copy.boundaryColor = self.boundaryColor
        copy.name = self.name
        copy.alias = self.alias
        copy.dancerID = self.dancerID
        return copy


class TextBox(QGraphicsTextItem):
    def __init__(self,content,parent=None):
        super().__init__(content,parent)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.content = content

    def mouseDoubleClickEvent(self,event):
        if event.button() == Qt.LeftButton and self.textInteractionFlags() == Qt.NoTextInteraction:
            self.setTextInteractionFlags(Qt.TextEditorInteraction)

    def focusOutEvent(self,event):
        self.setTextInteractionFlags(Qt.NoTextInteraction)

    
