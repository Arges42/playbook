#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys,os
from PyQt5.QtWidgets import QApplication
from modules.mainWindow import MainWindow


#if __name__ == '__main__':

app = QApplication(sys.argv)
ex = MainWindow()    
sys.exit(app.exec_())

