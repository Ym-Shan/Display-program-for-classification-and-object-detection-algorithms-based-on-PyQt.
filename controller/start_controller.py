import os
import threading
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
from view_py.start import Ui_MainWindow
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
from PyQt5.QtCore import pyqtSignal

class MainWindow(Ui_MainWindow):
    start = pyqtSignal()
    mid = pyqtSignal(float, float)              # 传递变量的自定义信号
    end = pyqtSignal()

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)


        self.center()
        self.label_2.setText('<font color=red>' + '热轧钢带缺陷检测与分析系统' + '</font>')
        self.label_2.setAlignment(QtCore.Qt.AlignHCenter)

        self.label_2.setFont(QFont('Ariai', 30))
        self.progressBar.setValue(0)
        self.progressBar.hide()  # 隐藏进度条

        self.start.connect(self.start_show)         # 自定义信号
        self.mid.connect(self.mid_show)
        self.end.connect(self.end_show)

        mv = QMovie("../res/spike.gif")
        self.label.setMovie(mv)
        mv.start()

        self.new_face_and_bar()

        self.setWindowTitle('系统初始化中...')

    def new_face_and_bar(self):
        pro = threading.Thread(target=self.bat_show_controll)  # 进度条
        pro.start()  # 调用开始检测的子线程




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


    def bat_show_controll(self):
        self.start.emit()           # 发射自定义信号,显示进度条
        # t1 = time.time()
        # t2 = time.time()
        # while t2 - t1 < 10:
        #     t2 = time.time()
        #     self.flash_progressBar(10, t2 - t1)

        for i in range(1, 11):
            time.sleep(1)
            self.mid.emit(10, i)            # 发射自定义信号,更新进度条进度

        self.end.emit()         # 发射自定义信号,隐藏进度条并进入主界面



        # import MainWindow_controller
        # self.new_window = MainWindow_controller.MainWindow()
        # self.new_window.show()
        # # 关闭窗口进程需要执行的代码
        # QCoreApplication.instance().quit()

# if __name__ == '__main__':
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     MainWindow = MainWindow()
#     MainWindow.show()
#     sys.exit(app.exec_())