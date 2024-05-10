import os
import threading
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
from view_py.MainFace import Ui_MainWindow
from PyQt5.QtGui import QPixmap

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import *
from controller.MainWindow_controller import MainWindow as main
import shutil
from model.data_visualization_helper import data_visualization_helper
import torch
import os
# 输入想要存储图像的路径
# os.chdir('./')
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
# 改变绘图风格
import seaborn as sns
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import time
from PyQt5.QtCore import QCoreApplication
import MainWindow_controller


class MainWindow(Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.center()

        self.label_3.setText('<font color=red>' + '热轧钢带缺陷检测与分析系统' + '</font>')
        self.label_3.setAlignment(QtCore.Qt.AlignHCenter)
        self.label_3.setFont(QFont('Ariai', 30))

        self.label_2.setText('<font color=red>' + '视觉图像分类系统' + '</font>')
        self.label_2.setAlignment(QtCore.Qt.AlignHCenter)
        self.label_2.setFont(QFont('Ariai', 30))

        self.pushButton.setText('进入系统')         # 进入视觉图像分类系统
        self.pushButton_2.setText('进入系统')       # 进入热轧钢带缺陷检测与分析系统

        self.pushButton.clicked.connect(self.open_1)      # 进入视觉图像分类系统
        self.pushButton_2.clicked.connect(self.open_2)     # 进入热轧钢带缺陷检测与分析系统

        self.setWindowTitle('引导')

    def open_1(self):
        import classify_start_controller
        self.new_window = classify_start_controller.MainWindow()
        self.new_window.show()
        self.close()


    def open_2(self):
        import start_controller
        self.new_window = start_controller.MainWindow()
        self.new_window.show()
        self.close()



    def center(self):       # 将窗口显示在屏幕正中间
        # 获取屏幕的尺寸信息
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口的尺寸信息
        size = self.geometry()
        # 将窗口移动到指定位置
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)


    def flash_progressBar(self, lens, completes):       # 调整进度条百分比
        flag = int(completes / lens * 100)
        self.progressBar.setValue(flag)

    def start_show(self):           # 接收自定义信号发射的槽
        self.progressBar.show()

    def mid_show(self, a, b):
        self.flash_progressBar(a, b)

    def end_show(self):
        self.progressBar.hide()
        self.new_window = MainWindow_controller.MainWindow()
        self.new_window.show()
        self.destroy()




if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())