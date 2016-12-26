import sys
from functools import wraps
from PyQt5.QtWidgets import (QWidget, QToolTip, 
    QPushButton, QMessageBox, QApplication, QDesktopWidget, QMainWindow, QAction, qApp, QGridLayout, QFormLayout, QColorDialog, QDialogButtonBox, QLineEdit, QGraphicsLineItem, QGraphicsTextItem,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsItem, QMenu, QGraphicsObject, QDialog)
from PyQt5.QtGui import QFont,QIcon, QBrush, QColor, QPen
from PyQt5.QtCore import QCoreApplication,QRectF, QPointF, Qt, pyqtSignal, QObject,QDateTime, QLineF, QSizeF,QSize, QRect


from .ui import DancerDialog
from .util import SlotManager

def changeWrapper(fn):
    @wraps(fn)
    def emitter(*args,**kwargs):
        if(args[1] == False):
            result = fn(args[0],**kwargs)
        else:
            result = fn(*args,**kwargs)
        self = args[0]
        self.contentChanged.emit()
        return result
    return emitter


class FrameViewer(QGraphicsView):

    frameIDChanged = pyqtSignal(int)
    contentChanged = pyqtSignal()
    resized = pyqtSignal(QSize)
    frameCreated = pyqtSignal(int) 
    frameDeleted = pyqtSignal(int)   

    def __init__(self,parent,settings=None,new=True):
        super().__init__(parent)    

        self.mainWindow = parent
        self.activeFrameID = 0

        #Collection for all scenes
        self.sceneCollection = []
       
        if new:
            #Default scene
            self.frame = Frame(self)
            SlotManager.FrameViewerToFrameConnection(self,self.frame)
            #self.settings.settingsChanged.connect(lambda x:self.frame.updateSettings(x))
            self.setScene(self.frame)
            self.sceneCollection.append(self.scene())
        
        #SlotManager.makeFrameViewerConnections(self)

    ###########SLOT DEFINITIONS###########
    @changeWrapper
    def createDancer(self,pos):
        newDancer = Dancer()
        newDancer.setPos(self.mapToScene(pos))
        #newDancer.deleteRequested.connect(lambda x:self.deleteDancer(x))
        #self.settings.settingsChanged.connect(lambda x:newDancer.updateSettings(x))
        SlotManager.FrameViewerToDancerConnection(self,newDancer)
        self.scene().addItem(newDancer)

    @changeWrapper
    def deleteDancer(self,dancerID=0):
        for item in self.scene().items():
            if(item.dancerID==dancerID):
                self.scene().removeItem(item)

    @changeWrapper
    def addText(self,pos):
        text = TextBox("Text")
        text.setPos(self.mapToScene(pos))
        self.scene().addItem(text)

    @changeWrapper
    def createFrame(self):
        self.frame = self.copyScene(self.sceneCollection[self.activeFrameID])
        #self.settings.settingsChanged.connect(lambda x:self.frame.updateSettings(x))
        SlotManager.FrameViewerToFrameConnection(self,self.frame)
        self.setScene(self.frame)
        self.setSceneRect(self.mapToScene(self.viewport().rect()).boundingRect())
        self.sceneCollection.insert(self.activeFrameID,self.frame)
        self.activeFrameID+=1
        self.frameIDChanged.emit(self.activeFrameID)
        self.frameCreated.emit(self.activeFrameID)

    @changeWrapper
    def deleteFrame(self):
        if len(self.sceneCollection) == 1:
            self.scene().clear()
        else:
            if self.activeFrameID == (len(self.sceneCollection)-1):
                newID = self.activeFrameID-1
            else:
                newID = self.activeFrameID
            self.frame = self.sceneCollection[newID]
            self.setScene(self.frame)
            del self.sceneCollection[self.activeFrameID]
            self.activeFrameID -= 1
            self.frameIDChanged.emit(self.activeFrameID)
            self.frameDeleted.emit(self.activeFrameID)

  
    def nextFrame(self):
        if self.activeFrameID == (len(self.sceneCollection)-1):
            self.activeFrameID = 0
        else:
            self.activeFrameID += 1
        self.frame = self.sceneCollection[self.activeFrameID]
        self.setScene(self.frame)
        self.frameIDChanged.emit(self.activeFrameID)

    def previousFrame(self):
        if self.activeFrameID == 0:
            self.activeFrameID = len(self.sceneCollection)-1
        else:
            self.activeFrameID -= 1
        self.frame = self.sceneCollection[self.activeFrameID]
        self.setScene(self.frame)
        self.frameIDChanged.emit(self.activeFrameID)

    def selectFrameById(self,i):
        if isinstance(i,str):
            try:            
                i = int(i)
            except ValueError:
                return
        if isinstance(i,int):
            if(i<len(self.sceneCollection)):
                self.activeFrameID = i
                self.frame = self.sceneCollection[self.activeFrameID]
                self.setScene(self.frame)
            self.frameIDChanged.emit(self.activeFrameID)

    def toggleDrawing(self):
        self.frame.drawing = not self.frame.drawing
    def toggleErase(self):
        self.frame.erase = not self.frame.erase
    def toggleGrid(self):
        for frame in self.sceneCollection:
            frame.grid = not frame.grid
        self.scene().update()
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

    def resizeEvent(self, event):
        self.resized.emit(event.size()) 
        QGraphicsView.resizeEvent(self,event)

    
    #Hier müssen alle Items der scene kopiert werden
    def copyScene(self,scene):
        copiedScene = Frame(self)
        
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
        self.frame = None
        self.setScene(self.frame)


class Frame (QGraphicsScene):
    
    contentChanged = pyqtSignal()
    def __init__(self,parent):
        super().__init__(parent)

        self.roomHeight = 600
        self.roomWidth = 600
        self.setSceneRect(0,0,self.roomHeight,self.roomWidth)
        self.gridSize = 30

        self.grid = True

        self.drawing = False
        self.erase = False
        self.scribbling = False
        self.lastPoint = None
        self.penWidth = 1
        self.penColor = Qt.blue
    
    ###########REIMPLEMENTATIONS###########################
    def drawBackground(self,painter,rect):
        roomRect = QRect(rect.x()+(rect.width()-self.roomWidth)*.5,rect.y()+(rect.height()-self.roomHeight)*.5,self.roomWidth,self.roomHeight)
        gridWidth = roomRect.width() - (roomRect.width()%self.gridSize)
        gridHeight = roomRect.height() - (roomRect.height()%self.gridSize)
        left = int((self.roomWidth-gridWidth+2*roomRect.left())*.5)
        top = int((self.roomHeight-gridHeight+2*roomRect.top())*.5 )   
        painter.setPen(QPen(QColor("black"), 2, Qt.SolidLine))
        if self.grid :
            for x in range(left,int(roomRect.right()),self.gridSize):
                for y in range(top,int(roomRect.bottom()),self.gridSize):
                    painter.drawPoint(x,y)
        
        painter.drawRect(roomRect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.lastPoint = event.scenePos()
            self.scribbling = True

        elif event.button() == Qt.LeftButton and self.erase:
            for item in self.items(event.scenePos()):
                if isinstance(item,QGraphicsLineItem):
                    self.removeItem(item)
        else: 
            QGraphicsScene.mousePressEvent(self,event)

    def mouseReleaseEvent(self, event):
        #Check if an item is currently grabbed, if yes propagate the release event to the item -> thus they lose focus
        if(self.mouseGrabberItem()):
            QGraphicsScene.mouseReleaseEvent(self,event)

        if (event.button() == Qt.LeftButton and self.scribbling and self.drawing):
            start = QPointF(self.lastPoint)
            end = QPointF(event.scenePos())
            self.addItem(
            QGraphicsLineItem(QLineF(start, end)))
            self.scribbling = False
    ###########REIMPLEMENTATIONS###########################

    def updateSettings(self,settings):
        self.roomWidth = settings.get("roomWidth")
        self.roomHeight = settings.get("roomHeight")
        self.setSceneRect(0,0,self.roomHeight,self.roomWidth)
        self.gridSize = settings.get("gridSize")
        self.update()

class Dancer(QGraphicsObject):

    globalID = 0
    # define signals
    deleteRequested = pyqtSignal(int)
    contentChanged = pyqtSignal()

    def __init__(self, parent=None,copy=False):
        super().__init__()

        # set flags
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # Dancer specific properties
        self.dancerWidth = 30
        self.color = QColor("black")
        self.boundaryColor = QColor("black")
        self.name = "Dummy"
        self.alias = ""

        if not copy:
            self.dancerID = Dancer.globalID
        Dancer.globalID+=1

    def boundingRect(self):
        return QRectF(-10,0,60,50)
        
    def paint(self, painter, option, widget = None):
        painter.setPen(QPen(QBrush(self.boundaryColor),int(self.dancerWidth*0.1)));
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(0,0,self.dancerWidth,self.dancerWidth)
        painter.drawText(QPointF(-10,self.dancerWidth+10),self.name)

    
    def mouseMoveEvent(self,event):
        if event.buttons() == Qt.LeftButton:
            rect = self.scene().parent().mapToScene(self.scene().parent().viewport().rect()).boundingRect()
            restrictedRect = QRectF(rect.x()+(rect.width()-self.scene().roomWidth)*.5,rect.y()+(rect.height()-self.scene().roomHeight)*.5,self.scene().roomWidth,self.scene().roomHeight)
            if restrictedRect.contains(event.scenePos()):
                self.scene().update()
                QGraphicsItem.mouseMoveEvent(self,event)

    def itemChange(self,change,value):
        
        if ((change == QGraphicsItem.ItemPositionChange) and (self.scene()!=None)):
            newPos = value

            if(QApplication.mouseButtons() == Qt.LeftButton and self.scene() != None and self.scene().grid):
                gridSize = self.scene().gridSize
                xV = round(newPos.x()/gridSize)*gridSize;
                yV = round(newPos.y()/gridSize)*gridSize;
                return QPointF(xV, yV);
            
            else:

                return newPos
    
        else:
            return QGraphicsItem.itemChange(self,change, value)

    @changeWrapper
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
        copy = Dancer(self.parent,copy=True)
        copy.color = self.color
        copy.boundaryColor = self.boundaryColor
        copy.name = self.name
        copy.alias = self.alias
        copy.dancerID = self.dancerID
        return copy

    def updateSettings(self,settings):
        self.dancerWidth = settings.get("dancerWidth")


class TextBox(QGraphicsTextItem):
    contentChanged = pyqtSignal()

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

    def mouseReleaseEvent(self, event):
        self.ungrabMouse()
        QGraphicsItem.mouseReleaseEvent(self,event)

    @changeWrapper
    def mouseMoveEvent(self,event):
        QGraphicsItem.mouseMoveEvent(self,event)
        self.scene().update()

class SingleFrameViewer(QGraphicsView):
    def __init__(self,parent,sourceFrameViewer = None):
        super().__init__(parent)    
        
        self.sourceFrameViewer = sourceFrameViewer

    #Overwrite the default drawBackground to avoid calling drawBackground of the frame
    def drawBackground(self,painter,rect):
        pass

