from PyQt5.QtWidgets import qApp
from PyQt5.QtCore import pyqtSignal,QObject

class Settings(QObject):

    settingsChanged = pyqtSignal(dict)
    def __init__(self,parent=None,default=True):
        super().__init__(parent)
        self.settings = {}
        if default:
            self.defaultSettings()
    
    def defaultSettings(self):
        self.settings["projectName"] = "unnamed"
        self.settings["gridSize"] = 20
        self.settings["dancerWidth"] = 30
        self.settings["roomHeight"] = 600
        self.settings["roomWidth"] = 600

    def setValue(self,key,value):
        self.settings[key] = value

    def getSettings(self):
        return self.settings

    def get(self,key,default=None):
        return self.settings.get(key,default)

    def compareSettings(self,x,y):
        equal = True
        for key,item in x.items():
            if item!=y.get(key,None):
                equal = False
                break
        return equal
            
    def updateSettings(self,newSettings):
        if not self.compareSettings(self.settings,newSettings):
            self.settings = {**self.settings, **newSettings}
            self.settingsChanged.emit(self.settings)

class SlotManager():
    def __init__(self):
        pass

    @staticmethod
    def makeMainWindowConnections(mainWindow):
        mainWindow.settings.settingsChanged.connect(lambda x: mainWindow.updateSettings(x))
        SlotManager.reconnect(mainWindow.previous.clicked,mainWindow.frames.previousFrame)
        SlotManager.reconnect(mainWindow.frameIDBox.textChanged,lambda x: mainWindow.frames.selectFrameById(x))
        mainWindow.frames.frameIDChanged.connect(lambda x:mainWindow.frameIDBox.setText(str(x)))
        SlotManager.reconnect(mainWindow.next.clicked,mainWindow.frames.nextFrame)
        SlotManager.reconnect(mainWindow.newScene.clicked,mainWindow.frames.createFrame)
        SlotManager.reconnect(mainWindow.deleteScene.clicked,mainWindow.frames.deleteFrame)
        SlotManager.reconnect(mainWindow.exitAction.triggered,qApp.quit)
        SlotManager.reconnect(mainWindow.saveAction.triggered,mainWindow.save)
        SlotManager.reconnect(mainWindow.loadAction.triggered,mainWindow.load)
        SlotManager.reconnect(mainWindow.printPdfAction.triggered,mainWindow.printToPdf)
        SlotManager.reconnect(mainWindow.drawAction.triggered,mainWindow.frames.toggleDrawing)
        SlotManager.reconnect(mainWindow.eraseAction.triggered,mainWindow.frames.toggleErase)
        SlotManager.reconnect(mainWindow.toogleGridAction.triggered,mainWindow.frames.toggleGrid)
        SlotManager.reconnect(mainWindow.openSettingsAction.triggered,mainWindow.changeSettings)
        SlotManager.reconnect(mainWindow.openShortcutAction.triggered,mainWindow.changeShortcuts)
        mainWindow.frames.contentChanged.connect(mainWindow.contentChanged)


    @staticmethod
    def makeFrameViewerConnections(frameViewer):
        pass

    @staticmethod
    def FrameViewerToDancerConnection(frameViewer,dancer):
        SlotManager.reconnect(dancer.deleteRequested,lambda x:frameViewer.deleteDancer(x))
        frameViewer.mainWindow.settings.settingsChanged.connect(lambda x:dancer.updateSettings(x))
        dancer.contentChanged.connect(frameViewer.mainWindow.contentChanged)

    @staticmethod
    def FrameViewerToFrameConnection(frameViewer,frame):
        frameViewer.mainWindow.settings.settingsChanged.connect(lambda x:frame.updateSettings(x))
        frame.contentChanged.connect(frameViewer.mainWindow.contentChanged)

    @staticmethod
    def reconnect(signal, newhandler=None, oldhandler=None):
        while True:
            try:
                if oldhandler is not None:
                    signal.disconnect(oldhandler)
                else:
                    signal.disconnect()
            except TypeError:
                break
        if newhandler is not None:
            signal.connect(newhandler)
