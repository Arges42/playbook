from PyQt5.QtWidgets import (QWidget, QToolTip, 
    QPushButton, QMessageBox, QApplication, QDesktopWidget, QMainWindow, QAction, qApp, QGridLayout, QFormLayout, QColorDialog, QDialogButtonBox, QLineEdit,QGraphicsLineItem,QGraphicsTextItem,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsItem, QMenu, QGraphicsObject, QDialog)
from PyQt5.QtGui import QFont,QIcon, QBrush, QColor, QPen
from PyQt5.QtCore import QCoreApplication,QRectF, QPointF, Qt, pyqtSignal, QObject,QDateTime, QLineF
from PyQt5.QtXml import QDomDocument,QDomElement

from .core import Frame,Dancer

class XmlFormat():
    def __init__(self,doc=None):
        self.doc = doc

    def dancerToXml(self,dancer):
        root = self.doc.createElement("Dancer")
        root.setAttribute("name",dancer.name)
        root.setAttribute("alias",dancer.alias)
        root.setAttribute("color",dancer.color.name())
        root.setAttribute("boundaryColor",dancer.boundaryColor.name())
        root.setAttribute("dancerID",dancer.dancerID)
        root.setAttribute("posX",dancer.x())
        root.setAttribute("posY",dancer.y())
        return root

    def lineToXml(self,line):
        root = self.doc.createElement("Line")
        root.setAttribute("x1",line.x1())
        root.setAttribute("y1",line.y1())
        root.setAttribute("x2",line.x2())
        root.setAttribute("y2",line.y2())
        return root
     
    def textToXml(self,text):
        root = self.doc.createElement("Text")
        root.setAttribute("x",text.x())
        root.setAttribute("y",text.y())
        root.setAttribute("rotation",text.rotation())
        root.setAttribute("content",text.toPlainText())
        return root
           
    def sceneToXml(self,scene):
        root = self.doc.createElement("Scene")

        for item in scene.items():
            if isinstance(item,Dancer):
                dancer = self.dancerToXml(item)
                root.appendChild(dancer)
            elif isinstance(item,QGraphicsLineItem):
                line = self.lineToXml(item.line())
                root.appendChild(line)
            elif isinstance(item,QGraphicsTextItem):
                text = self.textToXml(item)
                root.appendChild(text)

        return root

    def frameToXml(self,frame):
        root = self.doc.createElement("Frame")
        root.setAttribute("roomRectX",frame.roomRect.x())
        root.setAttribute("roomRectY",frame.roomRect.y())
        root.setAttribute("roomRectW",frame.roomRect.width())
        root.setAttribute("roomRectH",frame.roomRect.height())

        root.setAttribute("gridSize",frame.gridSize)
        root.setAttribute("activeFrameID",frame.activeFrameID)

        for scene in frame.sceneCollection:
            root.appendChild(self.sceneToXml(scene))

        return root


    def xmlToFrame(self,activeFrame):
        domFrame = self.doc.elementsByTagName("Frame").item(0).toElement()
        
        roomRect = QRectF(float(domFrame.attribute("roomRectX")),float(domFrame.attribute("roomRectY")),float(domFrame.attribute("roomRectW")),float(domFrame.attribute("roomRectH")))
        activeFrameID = domFrame.attribute("activeFrameID")
        
        activeFrame.clear()
        activeFrame.activeFrameID = int(activeFrameID)
        activeFrame.roomRect = roomRect
        

        domScenes = domFrame.elementsByTagName("Scene")
        for i in range(domScenes.length()):
            domScene = domScenes.item(i)
            domScene = domScene.toElement()
            scene = QGraphicsScene(activeFrame)
            domDancers = domScene.elementsByTagName("Dancer")
            for j in range(domDancers.length()):
                domDancer = domDancers.item(j)
                domDancer = domDancer.toElement()
                dancer = Dancer(roomRect,copy=True)
                dancer.dancerID = domDancer.attribute("dancerID")
                dancer.name = domDancer.attribute("name")
                dancer.alias = domDancer.attribute("alias")
                dancer.color = QColor(domDancer.attribute("color"))
                dancer.boundaryColor = QColor(domDancer.attribute("boundaryColor"))
                dancer.setPos(float(domDancer.attribute("posX")),float(domDancer.attribute("posY")))
                scene.addItem(dancer)

            domLines = domScene.elementsByTagName("Line")
            for j in range(domLines.length()):
                domLine = domLines.item(j)
                domLine = domLine.toElement()
                line = QLineF(float(domLine.attribute("x1")),float(domLine.attribute("y1")),float(domLine.attribute("x2")),float(domLine.attribute("y2")))
                scene.addItem(QGraphicsLineItem(line))

            domTexts = domScene.elementsByTagName("Text")
            for j in range(domTexts.length()):
                domText = domTexts.item(j)
                domText = domText.toElement()
                text = TextBox(domText.attribute("content"))
                text.setRotation(float(domText.attribute("rotation")))
                text.setPos(float(domText.attribute("x")),float(domText.attribute("y")))
                scene.addItem(text)

            activeFrame.sceneCollection.append(scene)
        activeFrame.scene = activeFrame.sceneCollection[activeFrame.activeFrameID]
        activeFrame.setScene(activeFrame.sceneCollection[activeFrame.activeFrameID])
        activeFrame.setSceneRect(activeFrame.roomRect)
