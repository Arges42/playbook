import os

from PyQt5.QtWidgets import (QWidget, QToolTip, 
    QPushButton, QMessageBox, QApplication, QDesktopWidget, QMainWindow, QAction, qApp, QGridLayout, QFormLayout, QColorDialog, QDialogButtonBox, QLineEdit,QGraphicsLineItem,QGraphicsTextItem,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsItem, QMenu, QGraphicsObject, QDialog)
from PyQt5.QtGui import QFont,QIcon, QBrush, QColor, QPen,QKeySequence
from PyQt5.QtCore import QCoreApplication,QRectF, QPointF, Qt, pyqtSignal, QObject,QDateTime, QLineF
from PyQt5.QtXml import QDomDocument,QDomElement

from .core import FrameViewer,Frame,Dancer, TextBox
from .util import Settings,SlotManager

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


    def frameViewerToXml(self,frameViewer):
        root = self.doc.createElement("Frame")

        root.setAttribute("activeFrameID",frameViewer.activeFrameID)

        for scene in frameViewer.sceneCollection:
            root.appendChild(self.sceneToXml(scene))

        return root

    def notesToXml(self,notes):
        root = self.doc.createElement("Notes")        
        for i,note in enumerate(notes.textCollection):
            child = self.doc.createElement("Note")
            child.setAttribute("frameID",i)
            child.setAttribute("content",note)
            root.appendChild(child)
        return root

    def projectToXml(self,mainWindow):
        root = self.doc.createElement("Project")
        root.setAttribute("projectName",mainWindow.settings.get("projectName"))
        root.setAttribute("gridSize",mainWindow.settings.get("gridSize"))
        root.setAttribute("roomWidth",mainWindow.settings.get("roomWidth"))
        root.setAttribute("roomHeight",mainWindow.settings.get("roomHeight"))
        root.setAttribute("dancerWidth",mainWindow.settings.get("dancerWidth"))

        root.appendChild(self.frameViewerToXml(mainWindow.frames))
        root.appendChild(self.notesToXml(mainWindow.notes))
        
        return root

    def xmlToProject(self,mainWindow):
        domProject = self.doc.elementsByTagName("Project").item(0).toElement()

        self.settings = Settings(mainWindow)       
        self.settings.setValue("projectName",domProject.attribute("projectName"))
        self.settings.setValue("gridSize", int(domProject.attribute("gridSize")))
        self.settings.setValue("roomWidth", int(domProject.attribute("roomWidth")))
        self.settings.setValue("roomHeight", int(domProject.attribute("roomHeight")))
        self.settings.setValue("dancerWidth", int(domProject.attribute("dancerWidth")))       
        mainWindow.settings = self.settings

        mainWindow.frames.settings = self.settings
        mainWindow.frames = self.xmlToFrameViewer(mainWindow.frames,domProject)       

        self.xmlToNotes(mainWindow.notes,domProject)
        
        SlotManager.makeMainWindowConnections(mainWindow)

    def xmlToFrameViewer(self,activeFrameViewer,domProject):
        domFrame = domProject.elementsByTagName("Frame").item(0).toElement()
       
        activeFrameID = domFrame.attribute("activeFrameID")
        
        activeFrameViewer.clear()
        try:
            activeFrameViewer.activeFrameID = int(activeFrameID)
        except:
            activeFrameViewer.activeFrameID = 0

        activeFrameViewer.sceneCollection = self.xmlToFrameCollection(activeFrameViewer,domFrame)
        activeFrameViewer.frame = activeFrameViewer.sceneCollection[activeFrameViewer.activeFrameID]
        activeFrameViewer.setScene(activeFrameViewer.sceneCollection[activeFrameViewer.activeFrameID])

        SlotManager.makeFrameViewerConnections(activeFrameViewer)
        return activeFrameViewer

    def xmlToNotes(self,notes,domProject):
        domNotes = domProject.elementsByTagName("Notes").item(0).toElement().elementsByTagName("Note")
        
        for i in range(domNotes.length()):
            domNote = domNotes.item(i).toElement()
            notes.addContent(domNote.attribute("frameID"),domNote.attribute("content"))

    def xmlToFrameCollection(self,activeFrameViewer,domFrame):
        frames = []
        domScenes = domFrame.elementsByTagName("Scene")  
        for i in range(domScenes.length()):
            domScene = domScenes.item(i)
            domScene = domScene.toElement()
            scene = Frame(activeFrameViewer)
            dancers = self.xmlToDancerCollection(domScene)
            for dancer in dancers:
                SlotManager.FrameViewerToDancerConnection(activeFrameViewer,dancer)
                scene.addItem(dancer)
            self.xmlToLineCollection(domScene,scene)
            self.xmlToTextCollection(domScene,scene)
            SlotManager.FrameViewerToFrameConnection(activeFrameViewer,scene)
            frames.append(scene)

        return frames

    def xmlToDancerCollection(self,domScene):
        dancers = []
        domDancers = domScene.elementsByTagName("Dancer")
        for j in range(domDancers.length()):
            domDancer = domDancers.item(j)
            domDancer = domDancer.toElement()
            dancer = Dancer(copy=True)
            dancer.dancerID = domDancer.attribute("dancerID")
            dancer.name = domDancer.attribute("name")
            dancer.alias = domDancer.attribute("alias")
            dancer.color = QColor(domDancer.attribute("color"))
            dancer.boundaryColor = QColor(domDancer.attribute("boundaryColor"))
            dancer.setPos(float(domDancer.attribute("posX")),float(domDancer.attribute("posY")))
            dancers.append(dancer)
        return dancers
    
    def xmlToLineCollection(self,domScene,frame):
        domLines = domScene.elementsByTagName("Line")
        for j in range(domLines.length()):
            domLine = domLines.item(j)
            domLine = domLine.toElement()
            line = QLineF(float(domLine.attribute("x1")),float(domLine.attribute("y1")),float(domLine.attribute("x2")),float(domLine.attribute("y2")))
            frame.addItem(QGraphicsLineItem(line))
    
    def xmlToTextCollection(self,domScene,frame):
        domTexts = domScene.elementsByTagName("Text")
        for j in range(domTexts.length()):
            domText = domTexts.item(j)
            domText = domText.toElement()
            text = TextBox(domText.attribute("content"))
            text.setRotation(float(domText.attribute("rotation")))
            text.setPos(float(domText.attribute("x")),float(domText.attribute("y")))
            frame.addItem(text)

    

class SettingWriter():
    
    SHORTCUT = "##Shortcuts##"
    def __init__(self,parent=None):
        self.parent = parent

    def getActions(self):
        mainWindow = self.parent
        actions = []
        actions.append(mainWindow.previous)
        actions.append(mainWindow.next)
        actions.append(mainWindow.newScene)
        actions.append(mainWindow.exitAction)
        actions.append(mainWindow.saveAction)
        actions.append(mainWindow.loadAction)
        actions.append(mainWindow.printPdfAction)
        actions.append(mainWindow.drawAction)
        actions.append(mainWindow.eraseAction)
        actions.append(mainWindow.toggleGridAction)

        return actions

    def writeSettings(self,path="."):
        f = open(os.path.join(path,"settings.txt"),'w')
        actions = self.getActions()
        f.write("##Shortcuts##\n")
        for action in actions:
            f.write("{}\t{}\n".format(action.objectName(),action.shortcut().toString()))
        f.close()

    def loadSettings(self,path="."):
        try:
            f = open(os.path.join(path,"settings.txt"),'r')
        except FileNotFoundError:
            return
        for line in f:
            if line.strip() == self.SHORTCUT:
                break
        for line in f:
            if line[0:2] == "##":
                break
            
            pair = line.strip().split("\t")
            if len(pair) == 2:
                objectName,shortcut = pair
                action = self.parent.findChild(QObject,objectName)
                try:
                    action.setShortcut(QKeySequence(shortcut))
                except:
                    print("Action or shortcut misdefined!")
        f.close()
