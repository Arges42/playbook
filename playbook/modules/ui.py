import sys
from PyQt5.QtWidgets import (QWidget, QToolTip, 
    QPushButton, QMessageBox, QApplication, QDesktopWidget, QMainWindow, QAction, qApp, QGridLayout, QFormLayout, QColorDialog, QDialogButtonBox, QLineEdit, QLabel, QSpinBox,
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsItem, QMenu, QGraphicsObject, QDialog)
from PyQt5.QtGui import QFont,QIcon, QBrush, QColor, QPen, QPixmap
from PyQt5.QtCore import QCoreApplication,QRectF, QPointF, Qt, pyqtSignal, QObject,QDateTime, QSize

from .util import Settings

class QColorButton(QPushButton):
    '''
    Custom Qt Widget to show a chosen color.

    Left-clicking the button shows the color-chooser, while
    right-clicking resets the color to None (no-color).    
    '''

    colorChanged = pyqtSignal()

    def __init__(self, *args,_color=None, **kwargs):
        super(QColorButton, self).__init__(*args, **kwargs)

        self._color = _color
        self.setColor(_color)
        self.setMaximumWidth(32)
        self.pressed.connect(self.onColorPicker)

    def setColor(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit()

        if self._color:
            self.setStyleSheet("background-color: %s;" % self._color)
        else:
            self.setStyleSheet("")

    def color(self):
        return self._color

    def onColorPicker(self):
        '''
        Show color-picker dialog to select color.

        Qt will use the native dialog by default.

        '''
        dlg = QColorDialog(self)
        if self._color:
            dlg.setCurrentColor(QColor(self._color))

        if dlg.exec_():
            self.setColor(dlg.currentColor().name())

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.setColor(None)

        return super(QColorButton, self).mousePressEvent(e)


class DancerDialog(QDialog):
    def __init__(self, parent = None,dancer=None):
        super(DancerDialog, self).__init__(parent)

        layout = QFormLayout(self)

        # nice widget for editing the date
        self.name = QLineEdit(dancer.name,self)
        self.alias = QLineEdit(dancer.alias,self)
        self.colorButton = QColorButton(self,_color = dancer.color)
        self.bColor = QColorButton(self,_color = dancer.boundaryColor)
        layout.addRow("Name",self.name)
        layout.addRow("Alias",self.alias)
        layout.addRow("Color",self.colorButton)
        layout.addRow("Boundary color",self.bColor)
        # OK and Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getModification(parent = None,dancer=None):
        dialog = DancerDialog(parent,dancer)
        result = dialog.exec_()
        name = dialog.name.text()
        alias = dialog.alias.text()
        color = dialog.colorButton.color()
        bColor = dialog.bColor.color()
        return {"name":name, "alias":alias, "color":color, "bColor": bColor, "accept": result == QDialog.Accepted}

class SettingsDialog(QDialog):
    def __init__(self, parent = None, currentSettings = None):
        super(SettingsDialog, self).__init__(parent)

        self.setWindowTitle("Settings")
        layout = QFormLayout(self)

        self.projectName = QLineEdit("",self)

        self.roomWidth = QSpinBox(self)
        self.roomWidth.setMinimum(1)
        self.roomWidth.setMaximum(2000)

        self.roomHeight = QSpinBox(self)
        self.roomHeight.setMinimum(1)
        self.roomHeight.setMaximum(2000)

        self.gridSize = QSpinBox(self)
        self.gridSize.setMinimum(1)

        self.dancerWidth = QSpinBox(self)
        self.dancerWidth.setMinimum(1)

        layout.addRow("Project name",self.projectName)
        layout.addRow("Room width",self.roomWidth)
        layout.addRow("Room height",self.roomHeight)
        layout.addRow("Grid size",self.gridSize)
        layout.addRow("Dancer size",self.dancerWidth)

        # OK and Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if currentSettings:
            self.setDefaults(currentSettings)

    def setDefaults(self,settings):
        self.projectName.setText(settings.get("projectName","unnamed"))
        self.roomHeight.setValue(settings.get("roomHeight",600))
        self.roomWidth.setValue(settings.get("roomWidth",600))
        self.gridSize.setValue(settings.get("gridSize",20))
        self.dancerWidth.setValue(settings.get("dancerWidth",30))

    @staticmethod
    def getModification(parent = None,currentSettings=None):
        dialog = SettingsDialog(parent,currentSettings)
        result = dialog.exec_()

        projectName = dialog.projectName.text()
        roomWidth = dialog.roomWidth.value()
        roomHeight = dialog.roomHeight.value()
        gridSize = dialog.gridSize.value()
        dancerWidth = dialog.dancerWidth.value()

        return {"projectName" : projectName,"roomHeight" : roomHeight, "roomWidth" : roomWidth, "gridSize" : gridSize, "dancerWidth" : dancerWidth, "accept": result == QDialog.Accepted}

class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, width, height, imgpath):
        super(ClickableLabel, self).__init__()
        pixmap = QIcon(imgpath).pixmap(QSize(width,height))
        self.setPixmap(pixmap)

    def mousePressEvent(self, event):
        self.clicked.emit()

