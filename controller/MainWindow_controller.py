import threading
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
from view_py.MainWindow import Ui_MainWindow
from PyQt5.QtGui import QPixmap
import cv2
import torch
from ultralytics import YOLO
from model.MainWindow_helper import MainWindow_helper
import os
import shutil
from queue import Queue
import time
from PIL import Image
import pymysql
from PyQt5.QtWidgets import QInputDialog, QFileDialog
import os
from PIL import Image
from PIL.ExifTags import TAGS
from PyQt5.QtWidgets import *

from pynvml import *
from psutil import *
class MainWindow(Ui_MainWindow):
    ROAD = '../data_in/'       # 存储待识别照片的位置
    MODEL = '../best.pt'        # 用来识别的模型及其参数
    OUT = '../data_out/'
    NAME = ''
    DETECT = 'False'
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.init()

        self.model = YOLO(self.MODEL)  # 加载预训练模型
        self.helper = MainWindow_helper()
        self.pushButton.clicked.connect(self.select_data)     # 选择检测图像按钮被选中
        self.pushButton_2.clicked.connect(self.start_detect)  # 开始检测
        self.comboBox.currentIndexChanged.connect(self.show_detect_result)  # 下拉框的监听
        self.listWidget_2.itemClicked.connect(self.show_pic)
        self.pushButton_3.clicked.connect(self.save_result)         # 保存检测结果
        self.action.triggered.connect(self.getname)             # 点击新建项目时获取项目名字
        self.action_5.triggered.connect(self.close_project)           # 关闭项目
        self.action_bug.triggered.connect(self.debug)           # bug修复
        self.action_2.triggered.connect(self.open_project)          # 打开项目
        self.action_3.triggered.connect(self.open_project_management_face)          # 项目管理
        self.center()               # 将窗口移动到屏幕正中央
        self.pushButton_4.clicked.connect(self.data_visualization)          # 进行数据可视化
        self.action_6.triggered.connect(self.model_data)     # 查看模型数据


    def model_data(self):
        import model_data_controller
        self.new_window = model_data_controller.MainWindow()
        self.init_project()
        self.new_window.show()




    def data_visualization(self):
        import data_visualization_controller
        self.new_window = data_visualization_controller.MainWindow(self.NAME)
        self.init_project()
        self.new_window.show()

    def open_project_management_face(self):
        self.init_project()
        import project_management_controller
        self.new_window = project_management_controller.MainWindow()
        self.new_window.FATHER = self
        self.new_window.show()
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        # self.close()

    def open_project(self):
        dir = QFileDialog.getExistingDirectory(None, '清选择要打开的项目', directory='../data_out')
        name = (dir.split('/'))[-1]
        if dir:
            self.setWindowTitle('热轧钢带缺陷检测系统-' + name)  # 设置窗口名字为项目名字
            self.NAME = name
            self.textEdit_4.append('--------------------')
            self.textEdit_4.append(time.ctime())
            self.textEdit_4.append(
                '<font color=black>' + '已打开项目:   ' + '</font>' + '<font color=red>' + self.NAME + '</font>')
            # 将一些组件恢复到初始状态
            self.pushButton.setEnabled(True)
            self.pushButton_3.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.comboBox.setEnabled(True)
            self.listWidget.clear()
            self.listWidget_2.clear()
            self.label.setPixmap(QPixmap('../res/label_background.png'))
            self.textEdit_3.clear()


    def debug(self):            # 修复bug
        if os.path.exists('./runs/detect'):
            shutil.rmtree('./runs/detect')  # 删除默认的结果文件夹
        self.textEdit_4.append('--------------------')
        self.textEdit_4.append(time.ctime())
        self.textEdit_4.append('<font color=blue>' + 'bug已修复 ' + '</font>' + '可继续使用系统')

    def flash(self):                # 检测结束后刷新界面
        self.comboBox.setCurrentIndex(2)    # 刷新检测结果界面
        self.comboBox.setCurrentIndex(0)  # 将下拉框设置为显示全部结果

    def close_project(self):                # 关闭项目
        if self.NAME != '':
            self.textEdit_4.append('--------------------')
            self.textEdit_4.append(time.ctime())
            self.textEdit_4.append('<font color=blue>' + '项目 ' + self.NAME + ' 已关闭' + '</font>')
            self.init_project()
            self.pushButton.setEnabled(False)
            self.pushButton_2.setEnabled(False)
            self.pushButton_3.setEnabled(False)
            self.comboBox.setEnabled(False)
        else:
            self.textEdit_4.append('--------------------')
            self.textEdit_4.append(time.ctime())
            self.textEdit_4.append('<font color=blue>' + '当前没有项目正在运行' + '</font>')

    def init_project(self):         # 初始化项目
        self.pushButton.setEnabled(False)
        self.pushButton_4.setEnabled(False)
        self.comboBox.setEnabled(False)
        self.listWidget.clear()
        self.listWidget_2.clear()
        self.label.setPixmap(QPixmap('../res/label_background.png'))
        self.textEdit_3.clear()
        torch.save([], '../cache/detect_list.pt')  # 清空待识别图片名字列表文件
        self.progressBar.setValue(0)
        self.progressBar.hide()  # 隐藏进度条
        self.setWindowTitle('热轧钢带缺陷检测系统-请新建一个项目')
        self.NAME = ''

    def select_data(self):      # 选择需要缺陷检测的图片
        if self.NAME == '':
            self.getname()  # 提示用户输入项目名称
        from PyQt5.QtWidgets import QFileDialog
        self.listWidget.clear()         # 清空文本框
        torch.save([], '../cache/detect_list.pt')  # 清空待识别图片名字列表文件
        dir = QFileDialog()         # 创建文件对话框
        dir.setFileMode(QFileDialog.ExistingFiles)      # 设置多选
        dir.setDirectory('../data_in')
        # 设置只显示图片文件
        dir.setNameFilter('图片文件(*.jpg *.png *.bmp *.ico *.gif)')
        if dir.exec_():             # 判断是否选择了文件
            self.pushButton_2.setEnabled(True)          # 设置按钮为可点击
            file = dir.selectedFiles()
            # file = file.split()
            final_file = []
            for i in file:
                # i = i.strip()
                _ = str(i).split('/')
                # print(_[-1:])
                final_file.append(_[-1:])
            final_file = sum(final_file, [])        # 神操作拉平列表
            self.listWidget.addItems(final_file)       # 将选择的文件展示在列表中
            torch.save(final_file, '../cache/detect_list.pt')       # 将要识别的图片名字列表存储
            self.textEdit_4.append('--------------------')
            self.textEdit_4.append(time.ctime())
            self.textEdit_4.append('<font color=blue>' + '共选择了 ' + '</font>' + '<font color=red>' + str(len(final_file)) + '</font>' + '<font color=blue>' + ' 张图片' + '</font>')
        else:
            self.pushButton_2.setEnabled(False)  # 设置按钮为不可点击

    # def return_journal(self, name, defect):
    #     now_time = time.ctime()
    #     self.textEdit_4.append('-----------------')
    #     self.textEdit_4.append(now_time)
    #     self.textEdit_4.append('<font color=blue>' + name + '</font>' + '检测完成,检测到 ' + '<font color=red>' + defect + '</font>')


    def arrange_data(self, table_name, types, road, result):
        if len(types) == 0:
            self.data_insert_db(table_name, road, len(result.boxes.cls))
        elif len(types) == 1:
            self.data_insert_db(table_name, road, len(result.boxes.cls), types[0].tolist(),
                                result.boxes.xyxyn[0].tolist(), result.boxes.conf[0].tolist())
        elif len(types) == 2:
            self.data_insert_db(table_name, road, len(result.boxes.cls), types[0].tolist(),
                                result.boxes.xyxyn[0].tolist(), result.boxes.conf[0].tolist(),
                                types[1].tolist(), result.boxes.xyxyn[1].tolist(), result.boxes.conf[1].tolist())
        elif len(types) == 3:
            self.data_insert_db(table_name, road, len(result.boxes.cls), types[0].tolist(),
                                result.boxes.xyxyn[0].tolist(), result.boxes.conf[0].tolist(),
                                types[1].tolist(), result.boxes.xyxyn[1].tolist(), result.boxes.conf[1].tolist(),
                                types[2].tolist(), result.boxes.xyxyn[2].tolist(), result.boxes.conf[2].tolist())
        elif len(types) == 4:
            self.data_insert_db(table_name, road, len(result.boxes.cls), types[0].tolist(),
                                result.boxes.xyxyn[0].tolist(), result.boxes.conf[0].tolist(),
                                types[1].tolist(), result.boxes.xyxyn[1].tolist(), result.boxes.conf[1].tolist(),
                                types[2].tolist(), result.boxes.xyxyn[2].tolist(), result.boxes.conf[2].tolist(),
                                types[3].tolist(), result.boxes.xyxyn[3].tolist(), result.boxes.conf[3].tolist())
        elif len(types) == 5:
            self.data_insert_db(table_name, road, len(result.boxes.cls), types[0].tolist(),
                                result.boxes.xyxyn[0].tolist(), result.boxes.conf[0].tolist(),
                                types[1].tolist(), result.boxes.xyxyn[1].tolist(), result.boxes.conf[1].tolist(),
                                types[2].tolist(), result.boxes.xyxyn[2].tolist(), result.boxes.conf[2].tolist(),
                                types[3].tolist(), result.boxes.xyxyn[3].tolist(), result.boxes.conf[3].tolist(),
                                types[4].tolist(), result.boxes.xyxyn[4].tolist(), result.boxes.conf[4].tolist())
        elif len(types) == 6:
            self.data_insert_db(table_name, road, len(result.boxes.cls), types[0].tolist(),
                                result.boxes.xyxyn[0].tolist(), result.boxes.conf[0].tolist(),
                                types[1].tolist(), result.boxes.xyxyn[1].tolist(), result.boxes.conf[1].tolist(),
                                types[2].tolist(), result.boxes.xyxyn[2].tolist(), result.boxes.conf[2].tolist(),
                                types[3].tolist(), result.boxes.xyxyn[3].tolist(), result.boxes.conf[3].tolist(),
                                types[4].tolist(), result.boxes.xyxyn[4].tolist(), result.boxes.conf[4].tolist(),
                                types[5].tolist(), result.boxes.xyxyn[5].tolist(), result.boxes.conf[5].tolist())
        elif len(types) == 7:
            self.data_insert_db(table_name, road, len(result.boxes.cls), types[0].tolist(),
                                result.boxes.xyxyn[0].tolist(), result.boxes.conf[0].tolist(),
                                types[1].tolist(), result.boxes.xyxyn[1].tolist(), result.boxes.conf[1].tolist(),
                                types[2].tolist(), result.boxes.xyxyn[2].tolist(), result.boxes.conf[2].tolist(),
                                types[3].tolist(), result.boxes.xyxyn[3].tolist(), result.boxes.conf[3].tolist(),
                                types[4].tolist(), result.boxes.xyxyn[4].tolist(), result.boxes.conf[4].tolist(),
                                types[5].tolist(), result.boxes.xyxyn[5].tolist(), result.boxes.conf[5].tolist(),
                                types[6].tolist(), result.boxes.xyxyn[6].tolist(), result.boxes.conf[6].tolist())
        elif len(types) == 8:
            self.data_insert_db(table_name, road, len(result.boxes.cls), types[0].tolist(),
                                result.boxes.xyxyn[0].tolist(), result.boxes.conf[0].tolist(),
                                types[1].tolist(), result.boxes.xyxyn[1].tolist(), result.boxes.conf[1].tolist(),
                                types[2].tolist(), result.boxes.xyxyn[2].tolist(), result.boxes.conf[2].tolist(),
                                types[3].tolist(), result.boxes.xyxyn[3].tolist(), result.boxes.conf[3].tolist(),
                                types[4].tolist(), result.boxes.xyxyn[4].tolist(), result.boxes.conf[4].tolist(),
                                types[5].tolist(), result.boxes.xyxyn[5].tolist(), result.boxes.conf[5].tolist(),
                                types[6].tolist(), result.boxes.xyxyn[6].tolist(), result.boxes.conf[6].tolist(),
                                types[7].tolist(), result.boxes.xyxyn[7].tolist(), result.boxes.conf[7].tolist())
        elif len(types) == 9:
            self.data_insert_db(table_name, road, len(result.boxes.cls), types[0].tolist(),
                                result.boxes.xyxyn[0].tolist(), result.boxes.conf[0].tolist(),
                                types[1].tolist(), result.boxes.xyxyn[1].tolist(), result.boxes.conf[1].tolist(),
                                types[2].tolist(), result.boxes.xyxyn[2].tolist(), result.boxes.conf[2].tolist(),
                                types[3].tolist(), result.boxes.xyxyn[3].tolist(), result.boxes.conf[3].tolist(),
                                types[4].tolist(), result.boxes.xyxyn[4].tolist(), result.boxes.conf[4].tolist(),
                                types[5].tolist(), result.boxes.xyxyn[5].tolist(), result.boxes.conf[5].tolist(),
                                types[6].tolist(), result.boxes.xyxyn[6].tolist(), result.boxes.conf[6].tolist(),
                                types[7].tolist(), result.boxes.xyxyn[7].tolist(), result.boxes.conf[7].tolist(),
                                types[8].tolist(), result.boxes.xyxyn[8].tolist(), result.boxes.conf[8].tolist())
        elif len(types) == 10:
            self.data_insert_db(table_name, road, len(result.boxes.cls), types[0].tolist(),
                                result.boxes.xyxyn[0].tolist(), result.boxes.conf[0].tolist(),
                                types[1].tolist(), result.boxes.xyxyn[1].tolist(), result.boxes.conf[1].tolist(),
                                types[2].tolist(), result.boxes.xyxyn[2].tolist(), result.boxes.conf[2].tolist(),
                                types[3].tolist(), result.boxes.xyxyn[3].tolist(), result.boxes.conf[3].tolist(),
                                types[4].tolist(), result.boxes.xyxyn[4].tolist(), result.boxes.conf[4].tolist(),
                                types[5].tolist(), result.boxes.xyxyn[5].tolist(), result.boxes.conf[5].tolist(),
                                types[6].tolist(), result.boxes.xyxyn[6].tolist(), result.boxes.conf[6].tolist(),
                                types[7].tolist(), result.boxes.xyxyn[7].tolist(), result.boxes.conf[7].tolist(),
                                types[8].tolist(), result.boxes.xyxyn[8].tolist(), result.boxes.conf[8].tolist(),
                                types[9].tolist(), result.boxes.xyxyn[9].tolist(), result.boxes.conf[9].tolist())
        elif len(types) == 11:
            self.data_insert_db(table_name, road, len(result.boxes.cls), types[0].tolist(),
                                result.boxes.xyxyn[0].tolist(), result.boxes.conf[0].tolist(),
                                types[1].tolist(), result.boxes.xyxyn[1].tolist(), result.boxes.conf[1].tolist(),
                                types[2].tolist(), result.boxes.xyxyn[2].tolist(), result.boxes.conf[2].tolist(),
                                types[3].tolist(), result.boxes.xyxyn[3].tolist(), result.boxes.conf[3].tolist(),
                                types[4].tolist(), result.boxes.xyxyn[4].tolist(), result.boxes.conf[4].tolist(),
                                types[5].tolist(), result.boxes.xyxyn[5].tolist(), result.boxes.conf[5].tolist(),
                                types[6].tolist(), result.boxes.xyxyn[6].tolist(), result.boxes.conf[6].tolist(),
                                types[7].tolist(), result.boxes.xyxyn[7].tolist(), result.boxes.conf[7].tolist(),
                                types[8].tolist(), result.boxes.xyxyn[8].tolist(), result.boxes.conf[8].tolist(),
                                types[9].tolist(), result.boxes.xyxyn[9].tolist(), result.boxes.conf[9].tolist(),
                                types[10].tolist(), result.boxes.xyxyn[10].tolist(), result.boxes.conf[10].tolist())
        elif len(types) == 12:
            self.data_insert_db(table_name, road, len(result.boxes.cls), types[0].tolist(),
                                result.boxes.xyxyn[0].tolist(), result.boxes.conf[0].tolist(),
                                types[1].tolist(), result.boxes.xyxyn[1].tolist(), result.boxes.conf[1].tolist(),
                                types[2].tolist(), result.boxes.xyxyn[2].tolist(), result.boxes.conf[2].tolist(),
                                types[3].tolist(), result.boxes.xyxyn[3].tolist(), result.boxes.conf[3].tolist(),
                                types[4].tolist(), result.boxes.xyxyn[4].tolist(), result.boxes.conf[4].tolist(),
                                types[5].tolist(), result.boxes.xyxyn[5].tolist(), result.boxes.conf[5].tolist(),
                                types[6].tolist(), result.boxes.xyxyn[6].tolist(), result.boxes.conf[6].tolist(),
                                types[7].tolist(), result.boxes.xyxyn[7].tolist(), result.boxes.conf[7].tolist(),
                                types[8].tolist(), result.boxes.xyxyn[8].tolist(), result.boxes.conf[8].tolist(),
                                types[9].tolist(), result.boxes.xyxyn[9].tolist(), result.boxes.conf[9].tolist(),
                                types[10].tolist(), result.boxes.xyxyn[10].tolist(), result.boxes.conf[10].tolist(),
                                types[11].tolist(), result.boxes.xyxyn[11].tolist(), result.boxes.conf[11].tolist())
        elif len(types) == 13:
            self.data_insert_db(table_name, road, len(result.boxes.cls), types[0].tolist(),
                                result.boxes.xyxyn[0].tolist(), result.boxes.conf[0].tolist(),
                                types[1].tolist(), result.boxes.xyxyn[1].tolist(), result.boxes.conf[1].tolist(),
                                types[2].tolist(), result.boxes.xyxyn[2].tolist(), result.boxes.conf[2].tolist(),
                                types[3].tolist(), result.boxes.xyxyn[3].tolist(), result.boxes.conf[3].tolist(),
                                types[4].tolist(), result.boxes.xyxyn[4].tolist(), result.boxes.conf[4].tolist(),
                                types[5].tolist(), result.boxes.xyxyn[5].tolist(), result.boxes.conf[5].tolist(),
                                types[6].tolist(), result.boxes.xyxyn[6].tolist(), result.boxes.conf[6].tolist(),
                                types[7].tolist(), result.boxes.xyxyn[7].tolist(), result.boxes.conf[7].tolist(),
                                types[8].tolist(), result.boxes.xyxyn[8].tolist(), result.boxes.conf[8].tolist(),
                                types[9].tolist(), result.boxes.xyxyn[9].tolist(), result.boxes.conf[9].tolist(),
                                types[10].tolist(), result.boxes.xyxyn[10].tolist(), result.boxes.conf[10].tolist(),
                                types[11].tolist(), result.boxes.xyxyn[11].tolist(), result.boxes.conf[11].tolist(),
                                types[12].tolist(), result.boxes.xyxyn[12].tolist(), result.boxes.conf[12].tolist())
        elif len(types) == 14:
            self.data_insert_db(table_name, road, len(result.boxes.cls), types[0].tolist(),
                                result.boxes.xyxyn[0].tolist(), result.boxes.conf[0].tolist(),
                                types[1].tolist(), result.boxes.xyxyn[1].tolist(), result.boxes.conf[1].tolist(),
                                types[2].tolist(), result.boxes.xyxyn[2].tolist(), result.boxes.conf[2].tolist(),
                                types[3].tolist(), result.boxes.xyxyn[3].tolist(), result.boxes.conf[3].tolist(),
                                types[4].tolist(), result.boxes.xyxyn[4].tolist(), result.boxes.conf[4].tolist(),
                                types[5].tolist(), result.boxes.xyxyn[5].tolist(), result.boxes.conf[5].tolist(),
                                types[6].tolist(), result.boxes.xyxyn[6].tolist(), result.boxes.conf[6].tolist(),
                                types[7].tolist(), result.boxes.xyxyn[7].tolist(), result.boxes.conf[7].tolist(),
                                types[8].tolist(), result.boxes.xyxyn[8].tolist(), result.boxes.conf[8].tolist(),
                                types[9].tolist(), result.boxes.xyxyn[9].tolist(), result.boxes.conf[9].tolist(),
                                types[10].tolist(), result.boxes.xyxyn[10].tolist(), result.boxes.conf[10].tolist(),
                                types[11].tolist(), result.boxes.xyxyn[11].tolist(), result.boxes.conf[11].tolist(),
                                types[12].tolist(), result.boxes.xyxyn[12].tolist(), result.boxes.conf[12].tolist(),
                                types[13].tolist(), result.boxes.xyxyn[13].tolist(), result.boxes.conf[13].tolist())
        elif len(types) == 15:
            self.data_insert_db(table_name, road, len(result.boxes.cls), types[0].tolist(),
                                result.boxes.xyxyn[0].tolist(), result.boxes.conf[0].tolist(),
                                types[1].tolist(), result.boxes.xyxyn[1].tolist(), result.boxes.conf[1].tolist(),
                                types[2].tolist(), result.boxes.xyxyn[2].tolist(), result.boxes.conf[2].tolist(),
                                types[3].tolist(), result.boxes.xyxyn[3].tolist(), result.boxes.conf[3].tolist(),
                                types[4].tolist(), result.boxes.xyxyn[4].tolist(), result.boxes.conf[4].tolist(),
                                types[5].tolist(), result.boxes.xyxyn[5].tolist(), result.boxes.conf[5].tolist(),
                                types[6].tolist(), result.boxes.xyxyn[6].tolist(), result.boxes.conf[6].tolist(),
                                types[7].tolist(), result.boxes.xyxyn[7].tolist(), result.boxes.conf[7].tolist(),
                                types[8].tolist(), result.boxes.xyxyn[8].tolist(), result.boxes.conf[8].tolist(),
                                types[9].tolist(), result.boxes.xyxyn[9].tolist(), result.boxes.conf[9].tolist(),
                                types[10].tolist(), result.boxes.xyxyn[10].tolist(), result.boxes.conf[10].tolist(),
                                types[11].tolist(), result.boxes.xyxyn[11].tolist(), result.boxes.conf[11].tolist(),
                                types[12].tolist(), result.boxes.xyxyn[12].tolist(), result.boxes.conf[12].tolist(),
                                types[13].tolist(), result.boxes.xyxyn[13].tolist(), result.boxes.conf[13].tolist(),
                                types[14].tolist(), result.boxes.xyxyn[14].tolist(), result.boxes.conf[14].tolist())
        elif len(types) == 16:
            self.data_insert_db(table_name, road, len(result.boxes.cls), types[0].tolist(),
                                result.boxes.xyxyn[0].tolist(), result.boxes.conf[0].tolist(),
                                types[1].tolist(), result.boxes.xyxyn[1].tolist(), result.boxes.conf[1].tolist(),
                                types[2].tolist(), result.boxes.xyxyn[2].tolist(), result.boxes.conf[2].tolist(),
                                types[3].tolist(), result.boxes.xyxyn[3].tolist(), result.boxes.conf[3].tolist(),
                                types[4].tolist(), result.boxes.xyxyn[4].tolist(), result.boxes.conf[4].tolist(),
                                types[5].tolist(), result.boxes.xyxyn[5].tolist(), result.boxes.conf[5].tolist(),
                                types[6].tolist(), result.boxes.xyxyn[6].tolist(), result.boxes.conf[6].tolist(),
                                types[7].tolist(), result.boxes.xyxyn[7].tolist(), result.boxes.conf[7].tolist(),
                                types[8].tolist(), result.boxes.xyxyn[8].tolist(), result.boxes.conf[8].tolist(),
                                types[9].tolist(), result.boxes.xyxyn[9].tolist(), result.boxes.conf[9].tolist(),
                                types[10].tolist(), result.boxes.xyxyn[10].tolist(), result.boxes.conf[10].tolist(),
                                types[11].tolist(), result.boxes.xyxyn[11].tolist(), result.boxes.conf[11].tolist(),
                                types[12].tolist(), result.boxes.xyxyn[12].tolist(), result.boxes.conf[12].tolist(),
                                types[13].tolist(), result.boxes.xyxyn[13].tolist(), result.boxes.conf[13].tolist(),
                                types[14].tolist(), result.boxes.xyxyn[14].tolist(), result.boxes.conf[14].tolist(),
                                types[15].tolist(), result.boxes.xyxyn[15].tolist(), result.boxes.conf[15].tolist())
        elif len(types) == 17:
            self.data_insert_db(table_name, road, len(result.boxes.cls), types[0].tolist(),
                                result.boxes.xyxyn[0].tolist(), result.boxes.conf[0].tolist(),
                                types[1].tolist(), result.boxes.xyxyn[1].tolist(), result.boxes.conf[1].tolist(),
                                types[2].tolist(), result.boxes.xyxyn[2].tolist(), result.boxes.conf[2].tolist(),
                                types[3].tolist(), result.boxes.xyxyn[3].tolist(), result.boxes.conf[3].tolist(),
                                types[4].tolist(), result.boxes.xyxyn[4].tolist(), result.boxes.conf[4].tolist(),
                                types[5].tolist(), result.boxes.xyxyn[5].tolist(), result.boxes.conf[5].tolist(),
                                types[6].tolist(), result.boxes.xyxyn[6].tolist(), result.boxes.conf[6].tolist(),
                                types[7].tolist(), result.boxes.xyxyn[7].tolist(), result.boxes.conf[7].tolist(),
                                types[8].tolist(), result.boxes.xyxyn[8].tolist(), result.boxes.conf[8].tolist(),
                                types[9].tolist(), result.boxes.xyxyn[9].tolist(), result.boxes.conf[9].tolist(),
                                types[10].tolist(), result.boxes.xyxyn[10].tolist(), result.boxes.conf[10].tolist(),
                                types[11].tolist(), result.boxes.xyxyn[11].tolist(), result.boxes.conf[11].tolist(),
                                types[12].tolist(), result.boxes.xyxyn[12].tolist(), result.boxes.conf[12].tolist(),
                                types[13].tolist(), result.boxes.xyxyn[13].tolist(), result.boxes.conf[13].tolist(),
                                types[14].tolist(), result.boxes.xyxyn[14].tolist(), result.boxes.conf[14].tolist(),
                                types[15].tolist(), result.boxes.xyxyn[15].tolist(), result.boxes.conf[15].tolist(),
                                types[16].tolist(), result.boxes.xyxyn[16].tolist(), result.boxes.conf[16].tolist())
        elif len(types) == 18:
            self.data_insert_db(table_name, road, len(result.boxes.cls), types[0].tolist(),
                                result.boxes.xyxyn[0].tolist(), result.boxes.conf[0].tolist(),
                                types[1].tolist(), result.boxes.xyxyn[1].tolist(), result.boxes.conf[1].tolist(),
                                types[2].tolist(), result.boxes.xyxyn[2].tolist(), result.boxes.conf[2].tolist(),
                                types[3].tolist(), result.boxes.xyxyn[3].tolist(), result.boxes.conf[3].tolist(),
                                types[4].tolist(), result.boxes.xyxyn[4].tolist(), result.boxes.conf[4].tolist(),
                                types[5].tolist(), result.boxes.xyxyn[5].tolist(), result.boxes.conf[5].tolist(),
                                types[6].tolist(), result.boxes.xyxyn[6].tolist(), result.boxes.conf[6].tolist(),
                                types[7].tolist(), result.boxes.xyxyn[7].tolist(), result.boxes.conf[7].tolist(),
                                types[8].tolist(), result.boxes.xyxyn[8].tolist(), result.boxes.conf[8].tolist(),
                                types[9].tolist(), result.boxes.xyxyn[9].tolist(), result.boxes.conf[9].tolist(),
                                types[10].tolist(), result.boxes.xyxyn[10].tolist(), result.boxes.conf[10].tolist(),
                                types[11].tolist(), result.boxes.xyxyn[11].tolist(), result.boxes.conf[11].tolist(),
                                types[12].tolist(), result.boxes.xyxyn[12].tolist(), result.boxes.conf[12].tolist(),
                                types[13].tolist(), result.boxes.xyxyn[13].tolist(), result.boxes.conf[13].tolist(),
                                types[14].tolist(), result.boxes.xyxyn[14].tolist(), result.boxes.conf[14].tolist(),
                                types[15].tolist(), result.boxes.xyxyn[15].tolist(), result.boxes.conf[15].tolist(),
                                types[16].tolist(), result.boxes.xyxyn[16].tolist(), result.boxes.conf[16].tolist(),
                                types[17].tolist(), result.boxes.xyxyn[17].tolist(), result.boxes.conf[17].tolist())
        elif len(types) == 19:
            self.data_insert_db(table_name, road, len(result.boxes.cls), types[0].tolist(),
                                result.boxes.xyxyn[0].tolist(), result.boxes.conf[0].tolist(),
                                types[1].tolist(), result.boxes.xyxyn[1].tolist(), result.boxes.conf[1].tolist(),
                                types[2].tolist(), result.boxes.xyxyn[2].tolist(), result.boxes.conf[2].tolist(),
                                types[3].tolist(), result.boxes.xyxyn[3].tolist(), result.boxes.conf[3].tolist(),
                                types[4].tolist(), result.boxes.xyxyn[4].tolist(), result.boxes.conf[4].tolist(),
                                types[5].tolist(), result.boxes.xyxyn[5].tolist(), result.boxes.conf[5].tolist(),
                                types[6].tolist(), result.boxes.xyxyn[6].tolist(), result.boxes.conf[6].tolist(),
                                types[7].tolist(), result.boxes.xyxyn[7].tolist(), result.boxes.conf[7].tolist(),
                                types[8].tolist(), result.boxes.xyxyn[8].tolist(), result.boxes.conf[8].tolist(),
                                types[9].tolist(), result.boxes.xyxyn[9].tolist(), result.boxes.conf[9].tolist(),
                                types[10].tolist(), result.boxes.xyxyn[10].tolist(), result.boxes.conf[10].tolist(),
                                types[11].tolist(), result.boxes.xyxyn[11].tolist(), result.boxes.conf[11].tolist(),
                                types[12].tolist(), result.boxes.xyxyn[12].tolist(), result.boxes.conf[12].tolist(),
                                types[13].tolist(), result.boxes.xyxyn[13].tolist(), result.boxes.conf[13].tolist(),
                                types[14].tolist(), result.boxes.xyxyn[14].tolist(), result.boxes.conf[14].tolist(),
                                types[15].tolist(), result.boxes.xyxyn[15].tolist(), result.boxes.conf[15].tolist(),
                                types[16].tolist(), result.boxes.xyxyn[16].tolist(), result.boxes.conf[16].tolist(),
                                types[17].tolist(), result.boxes.xyxyn[17].tolist(), result.boxes.conf[17].tolist(),
                                types[18].tolist(), result.boxes.xyxyn[18].tolist(), result.boxes.conf[18].tolist())
        elif len(types) == 20:
            self.data_insert_db(table_name, road, len(result.boxes.cls), types[0].tolist(),
                                result.boxes.xyxyn[0].tolist(), result.boxes.conf[0].tolist(),
                                types[1].tolist(), result.boxes.xyxyn[1].tolist(), result.boxes.conf[1].tolist(),
                                types[2].tolist(), result.boxes.xyxyn[2].tolist(), result.boxes.conf[2].tolist(),
                                types[3].tolist(), result.boxes.xyxyn[3].tolist(), result.boxes.conf[3].tolist(),
                                types[4].tolist(), result.boxes.xyxyn[4].tolist(), result.boxes.conf[4].tolist(),
                                types[5].tolist(), result.boxes.xyxyn[5].tolist(), result.boxes.conf[5].tolist(),
                                types[6].tolist(), result.boxes.xyxyn[6].tolist(), result.boxes.conf[6].tolist(),
                                types[7].tolist(), result.boxes.xyxyn[7].tolist(), result.boxes.conf[7].tolist(),
                                types[8].tolist(), result.boxes.xyxyn[8].tolist(), result.boxes.conf[8].tolist(),
                                types[9].tolist(), result.boxes.xyxyn[9].tolist(), result.boxes.conf[9].tolist(),
                                types[10].tolist(), result.boxes.xyxyn[10].tolist(), result.boxes.conf[10].tolist(),
                                types[11].tolist(), result.boxes.xyxyn[11].tolist(), result.boxes.conf[11].tolist(),
                                types[12].tolist(), result.boxes.xyxyn[12].tolist(), result.boxes.conf[12].tolist(),
                                types[13].tolist(), result.boxes.xyxyn[13].tolist(), result.boxes.conf[13].tolist(),
                                types[14].tolist(), result.boxes.xyxyn[14].tolist(), result.boxes.conf[14].tolist(),
                                types[15].tolist(), result.boxes.xyxyn[15].tolist(), result.boxes.conf[15].tolist(),
                                types[16].tolist(), result.boxes.xyxyn[16].tolist(), result.boxes.conf[16].tolist(),
                                types[17].tolist(), result.boxes.xyxyn[17].tolist(), result.boxes.conf[17].tolist(),
                                types[18].tolist(), result.boxes.xyxyn[18].tolist(), result.boxes.conf[18].tolist(),
                                types[19].tolist(), result.boxes.xyxyn[19].tolist(), result.boxes.conf[19].tolist())


    def data_insert_db(self, table_name, pic_name, detect_number, detect_type_1='NULL', detect_located_1='NULL', conf_1='NULL',
                       detect_type_2='NULL', detect_located_2='NULL', conf_2='NULL',
                       detect_type_3='NULL', detect_located_3='NULL', conf_3='NULL',
                       detect_type_4='NULL', detect_located_4='NULL', conf_4='NULL',
                       detect_type_5='NULL', detect_located_5='NULL', conf_5='NULL',
                       detect_type_6='NULL', detect_located_6='NULL', conf_6='NULL',
                       detect_type_7='NULL', detect_located_7='NULL', conf_7='NULL',
                       detect_type_8='NULL', detect_located_8='NULL', conf_8='NULL',
                       detect_type_9='NULL', detect_located_9='NULL', conf_9='NULL',
                       detect_type_10='NULL', detect_located_10='NULL', conf_10='NULL',
                       detect_type_11='NULL', detect_located_11='NULL', conf_11='NULL',
                       detect_type_12='NULL', detect_located_12='NULL', conf_12='NULL',
                       detect_type_13='NULL', detect_located_13='NULL', conf_13='NULL',
                       detect_type_14='NULL', detect_located_14='NULL', conf_14='NULL',
                       detect_type_15='NULL', detect_located_15='NULL', conf_15='NULL',
                       detect_type_16='NULL', detect_located_16='NULL', conf_16='NULL',
                       detect_type_17='NULL', detect_located_17='NULL', conf_17='NULL',
                       detect_type_18='NULL', detect_located_18='NULL', conf_18='NULL',
                       detect_type_19='NULL', detect_located_19='NULL', conf_19='NULL',
                       detect_type_20='NULL', detect_located_20='NULL', conf_20='NULL'):
        detect_type = [detect_type_1, detect_type_2, detect_type_3, detect_type_4, detect_type_5,
                       detect_type_6, detect_type_7, detect_type_8, detect_type_9, detect_type_10,
                       detect_type_11, detect_type_12, detect_type_13, detect_type_14, detect_type_15,
                       detect_type_16, detect_type_17, detect_type_18, detect_type_19, detect_type_20]
        detect_located = [detect_located_1, detect_located_2, detect_located_3, detect_located_4, detect_located_5,
                       detect_located_6, detect_located_7, detect_located_8, detect_located_9, detect_located_10,
                       detect_located_11, detect_located_12, detect_located_13, detect_located_14, detect_located_15,
                       detect_located_16, detect_located_17, detect_located_18, detect_located_19, detect_located_20]
        conf = [conf_1, conf_2, conf_3, conf_4, conf_5,
                conf_6, conf_7, conf_8, conf_9, conf_10,
                conf_11, conf_12, conf_13, conf_14, conf_15,
                conf_16, conf_17, conf_18, conf_19, conf_20]
        for i in range(20):
            if detect_type[i] == 0.0:
                detect_type[i] = '裂纹'
            elif detect_type[i] == 1.0:
                detect_type[i] = '夹杂'
            elif detect_type[i] == 2.0:
                detect_type[i] = '斑块'
            elif detect_type[i] == 3.0:
                detect_type[i] = '麻点'
            elif detect_type[i] == 4.0:
                detect_type[i] = '磨花'
            elif detect_type[i] == 5.0:
                detect_type[i] = '划痕'
        for i in range(detect_number):
            m = detect_located[i]
            m[0] = round(m[0], 3)           # 保留三位小数
            m[1] = round(m[1], 3)
            m[2] = round(m[2], 3)
            m[3] = round(m[3], 3)
            detect_located[i] = '(' + str(m[0]) + ' ,' + str(m[1]) + '), (' + str(m[2]) + ', ' + str(m[3]) + ')'
        for i in range(detect_number):
            conf[i] = round(conf[i], 3)
            conf[i] = str(conf[i])


        self.helper.add_detect_data(table_name, pic_name, detect_number, str(detect_type[0]), str(detect_located[0]), str(conf[0]),
                               str(detect_type[1]), str(detect_located[1]), str(conf[1]),
                               str(detect_type[2]), str(detect_located[2]), str(conf[2]),
                               str(detect_type[3]), str(detect_located[3]), str(conf[3]),
                               str(detect_type[4]), str(detect_located[4]), str(conf[4]),
                               str(detect_type[5]), str(detect_located[5]), str(conf[5]),
                               str(detect_type[6]), str(detect_located[6]), str(conf[6]),
                               str(detect_type[7]), str(detect_located[7]), str(conf[7]),
                               str(detect_type[8]), str(detect_located[8]), str(conf[8]),
                               str(detect_type[9]), str(detect_located[9]), str(conf[9]),
                               str(detect_type[10]), str(detect_located[10]), str(conf[10]),
                               str(detect_type[11]), str(detect_located[11]), str(conf[11]),
                               str(detect_type[12]), str(detect_located[12]), str(conf[12]),
                               str(detect_type[13]), str(detect_located[13]), str(conf[13]),
                               str(detect_type[14]), str(detect_located[14]), str(conf[14]),
                               str(detect_type[15]), str(detect_located[15]), str(conf[15]),
                               str(detect_type[16]), str(detect_located[16]), str(conf[16]),
                               str(detect_type[17]), str(detect_located[17]), str(conf[17]),
                               str(detect_type[18]), str(detect_located[18]), str(conf[18]),
                               str(detect_type[19]), str(detect_located[19]), str(conf[19]),
                               )

    def center(self):       # 将窗口显示在屏幕正中间
        # 获取屏幕的尺寸信息
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口的尺寸信息
        size = self.geometry()
        # 将窗口移动到指定位置
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)


    def getname(self):          # 通过对话框获取项目名字
        name, ok = QInputDialog.getText(self, "请输入项目名", "设定一个项目名以更方便的观测预测结果.", QtWidgets.QLineEdit.Normal, '')
        if ok and name:
            if self.NAME != '':
                self.textEdit_4.append('--------------------')
                self.textEdit_4.append(time.ctime())
                self.textEdit_4.append('<font color=blue>' + '项目 ' + self.NAME + ' 已关闭' + '</font>')
            with open('../cache/detect_name.py', 'w+') as f:
                f.write(name)
            self.setWindowTitle('热轧钢带缺陷检测系统-' + name)        # 设置窗口名字为项目名字
            self.NAME = name
            self.comboBox.setEnabled(True)
            # self.textEdit_4.append('<font color=black>' + '已创建并进入新项目:   ' + '</font>' + '<font color=red>' + self.NAME + '</font>')
            # 在结果文件夹中创建名字为项目名字的文件夹以及该文件夹下的输出结构(all和各类缺陷文件夹)
            self.create_dir()           # 创建数据库表
            # 将一些组件恢复到初始状态
            self.pushButton.setEnabled(True)
            self.listWidget.clear()
            self.listWidget_2.clear()
            self.label.setPixmap(QPixmap('../res/label_background.png'))
            self.textEdit_3.clear()
        # elif self.NAME == '':
        #     select = QMessageBox.warning(None, '警告', '您必须输入一个项目名,否则将无法使用本系统.', QMessageBox.Yes)
        #     self.getname()

    def create_dir(self):                   # 根据创建的项目名,创建存储检测结果的目录
        path = self.OUT + self.NAME + '/'
        if os.path.exists(path):
           select = QMessageBox.warning(None, '警告', '项目名 '+self.NAME+' 已存在,请修改项目名称.', QMessageBox.Yes)
           self.getname()
        else:
            self.textEdit_4.append(
                '<font color=black>' + '已创建并进入新项目:   ' + '</font>' + '<font color=red>' + self.NAME + '</font>')
            os.makedirs(path)           # 创建结果主文件夹
            os.makedirs(path + 'cr/')   # 创建结果子文件夹
            os.makedirs(path + 'in/')
            os.makedirs(path + 'pa/')
            os.makedirs(path + 'ps/')
            os.makedirs(path + 'rs/')
            os.makedirs(path + 'sc/')
            os.makedirs(path + 'all/')
            os.makedirs(path + 'perfect/')
            # 创建数据库表
            self.helper.create_table(self.NAME)
            self.helper.insert_new_project_message(self.NAME, time.ctime())         # 在数据库中加入新建的项目名

    def predict(self):             # 检测
        file_list = torch.load('../cache/detect_list.pt')       # 读取要识别的图片列表
        if file_list != []:
            self.listWidget_2.clear()
            self.progressBar.show()         # 显示进度条
            lens = len(file_list)           # 选择的需要进行目标检测的照片总数
            number_completes = 0                      # 目前已经检测完成的照片总数
            pic_sum = 0        # 用来统计目前检测到第几张图片
            for i in range(len(file_list)):                 # 遍历每一张图片
                pic = (self.ROAD)+str(file_list[i])         # 格式类似于../datasets/NEU/test/images/scratches_297.jpg
                results = self.model.predict(source=pic, save=True, save_txt=True)  # 进行识别
                pic_sum += 1
                number_completes += 1
                self.flash_progressBar(lens, number_completes)
                for result in results:
                    types = result.boxes.cls            # 存储本次检测的图片的类别列表([0., 0.])

                    self.arrange_data(self.NAME, types, str(file_list[i]), result)       # 将每张图片的数据存储到数据库

                    if 0.0 in types:
                        shutil.copyfile('./runs/detect/predict/' + str(file_list[i]), '../data_out/' + self.NAME + '/cr/'+str(file_list[i]))        # 将识别结果转存到输出文件夹
                        shutil.copyfile('./runs/detect/predict/' + str(file_list[i]), '../data_out/' + self.NAME + '/all/' + str(file_list[i]))       # 结果不仅存到对应类别的文件夹,还存到总文件夹
                        # self.return_journal(str(file_list[i]), '裂纹')
                    if 1.0 in types:
                        shutil.copyfile('./runs/detect/predict/'+str(file_list[i]), '../data_out/' + self.NAME + '/in/'+str(file_list[i]))
                        shutil.copyfile('./runs/detect/predict/' + str(file_list[i]), '../data_out/' + self.NAME + '/all/' + str(file_list[i]))
                        # self.return_journal(str(file_list[i]), '夹杂')
                    if 2.0 in types:
                        shutil.copyfile('./runs/detect/predict/'+str(file_list[i]), '../data_out/' + self.NAME + '/pa/'+str(file_list[i]))
                        shutil.copyfile('./runs/detect/predict/' + str(file_list[i]), '../data_out/' + self.NAME + '/all/' + str(file_list[i]))
                        # self.return_journal(str(file_list[i]), '斑块')
                    if 3.0 in types:
                        shutil.copyfile('./runs/detect/predict/'+str(file_list[i]), '../data_out/' + self.NAME + '/ps/'+str(file_list[i]))
                        shutil.copyfile('./runs/detect/predict/' + str(file_list[i]), '../data_out/' + self.NAME + '/all/' + str(file_list[i]))
                        # self.return_journal(str(file_list[i]), '麻点')
                    if 4.0 in types:
                        shutil.copyfile('./runs/detect/predict/'+str(file_list[i]), '../data_out/' + self.NAME + '/rs/'+str(file_list[i]))
                        shutil.copyfile('./runs/detect/predict/' + str(file_list[i]), '../data_out/' + self.NAME + '/all/' + str(file_list[i]))
                        # self.return_journal(str(file_list[i]), '磨花')
                    if 5.0 in types:
                        shutil.copyfile('./runs/detect/predict/'+str(file_list[i]), '../data_out/' + self.NAME + '/sc/'+str(file_list[i]))
                        shutil.copyfile('./runs/detect/predict/' + str(file_list[i]), '../data_out/' + self.NAME + '/all/' + str(file_list[i]))
                        # self.return_journal(str(file_list[i]), '划痕')
                    if len(types) == 0:
                        shutil.copyfile('./runs/detect/predict/' + str(file_list[i]), '../data_out/' + self.NAME + '/perfect/' + str(file_list[i]))
                        shutil.copyfile('./runs/detect/predict/' + str(file_list[i]),'../data_out/' + self.NAME + '/all/' + str(file_list[i]))
                        # self.return_journal(str(file_list[i]), '没有缺陷')
                    shutil.rmtree('./runs/detect/predict')          # 删除默认的结果文件夹,从而避免目录名称变化
            self.flash()        # 刷新检测结果展示界面
            self.progressBar.hide()   # 隐藏进度条
            for i in os.listdir(self.OUT + self.NAME + '/all'):          # 将所有图片的大小更改为321x321
                image = Image.open(self.OUT + self.NAME + '/all' + '/'+i)
                image_size = image.resize((321, 321), Image.ANTIALIAS)
                image_size.save(self.OUT + self.NAME + '/all' + '/'+i)
        else:
            self.textEdit_4.clear()
            self.textEdit_4.append('<font color=red>' + '请选择要检测的图像' + '</font>')


    def start_detect(self):                     # 点击开始检测按钮
        self.comboBox.setCurrentIndex(0)  # 将下拉框设置为显示全部结果
        self.textEdit_4.append('--------------------')
        self.textEdit_4.append(time.ctime())
        self.textEdit_4.append('<font color=blue>' + '开始检测......' + '</font>')
        self.textEdit_4.append('<font color=red>' + '检测中......' + '</font>')
        # file_list = torch.load('../cache/detect_list.pt')  # 读取要识别的图片列表
        self.DETECT = 'True'
        t1 = time.time()
        pro = threading.Thread(target=self.predict)  # 开始检测的子进程
        pro.start()        # 调用开始检测的子线程

        pro2 = threading.Thread(target=self.writedown)  # 记录cpu\内存\gpu使用率的子线程
        pro2.start()  # 调用开始检测的子线程

        pro.join()          # 在子线程完成后调用下面的语句
        self.DETECT = 'False'
        t2 = time.time()
        t = t2 - t1
        torch.save(t, '../cache/detect_time.pt')  # 记录检测总时间
        self.textEdit_4.append('--------------------')
        self.textEdit_4.append(time.ctime())
        self.textEdit_4.append('<font color=red>' + '检测完成' + '</font>')
        self.textEdit_4.append('<font color=black>' + '本次检测的结果存储在' + '</font>')
        self.textEdit_4.append('<font color=red>' + self.OUT + self.NAME + '</font>')

        data_num = os.listdir('../data_out/' + self.NAME + '/all')          # 获取项目中文件的数量

        self.helper.update_project_message(self.NAME, time.ctime(), len(data_num))             # 更新项目最后的更新时间
        self.pushButton_3.setEnabled(True)
        self.pushButton_4.setEnabled(True)

    def writedown(self):            # 存储检测过程中cpu\内存\gpu的占用率
        nvmlInit()
        def sleeptime(hour, min, sec):
            return hour * 3600 + min * 60 + sec
        second = sleeptime(0, 0, 0.2)
        cpu_count = []
        memory_count = []
        gpu_count = []
        while self.DETECT == 'True':
            time.sleep(second)
            cpu = cpu_percent(interval=2)
            memory = virtual_memory()[2]
            handle = nvmlDeviceGetHandleByIndex(0)
            info = nvmlDeviceGetMemoryInfo(handle)
            gpu = info.used / info.total

            cpu_count.append(cpu)
            memory_count.append(memory)
            gpu_count.append(gpu)

        torch.save(cpu_count, '../cache/cpu_count.pt')  # 存储cpu占用率
        torch.save(memory_count, '../cache/memory_count.pt')  # 内存
        torch.save(gpu_count, '../cache/gpu_count.pt')  # gpu

    def flash_progressBar(self, lens, completes):       # 调整进度条百分比
        flag = int(completes / lens * 100)
        self.progressBar.setValue(flag)

    def save_result(self):      # 将结果文件夹转存到用户选择的位置
        dir = QFileDialog.getExistingDirectory(None, '清选择要将检测结果保存到哪个文件夹下', os.getcwd())
        if dir:
            # with open('../cache/detect_name.py', 'r+') as f:
            #     name = f.read()
            name = self.NAME
            if os.path.exists(dir + '/' + name):
                shutil.rmtree(dir + '/' + name)  # 删除默认的结果文件夹,从而避免目录名称变化
                shutil.copytree('../data_out/' + name + '/', dir + '/' + name)
            else:
                shutil.copytree('../data_out/' + name + '/', dir + '/' + name)
            self.textEdit_4.append('--------------------')
            self.textEdit_4.append('本次缺陷检测的结果已保存到 ')
            self.textEdit_4.append('<font color=red>' + dir + '</font>' + '<font color=red>' + '/' + '</font>' + '<font color=red>' + name + '</font>')

    def show_detect_result(self):       # 检测结果展示
        self.listWidget_2.clear()
        if self.comboBox.currentText() == '全部缺陷':
            self.listWidget_2.addItems(os.listdir('../data_out/' + self.NAME + '/cr'))  # 将选择的文件展示在列表中
            self.listWidget_2.addItems(os.listdir('../data_out/' + self.NAME + '/in'))
            self.listWidget_2.addItems(os.listdir('../data_out/' + self.NAME + '/pa'))
            self.listWidget_2.addItems(os.listdir('../data_out/' + self.NAME + '/ps'))
            self.listWidget_2.addItems(os.listdir('../data_out/' + self.NAME + '/rs'))
            self.listWidget_2.addItems(os.listdir('../data_out/' + self.NAME + '/sc'))
        elif self.comboBox.currentText() == '裂纹':
            folder = 'cr'
            self.listWidget_2.addItems(os.listdir('../data_out/' + self.NAME + '/' + folder))
        elif self.comboBox.currentText() == '夹杂':
            folder = 'in'
            self.listWidget_2.addItems(os.listdir('../data_out/' + self.NAME + '/' + folder))
        elif self.comboBox.currentText() == '斑块':
            folder = 'pa'
            self.listWidget_2.addItems(os.listdir('../data_out/' + self.NAME + '/' + folder))
        elif self.comboBox.currentText() == '麻点':
            folder = 'ps'
            self.listWidget_2.addItems(os.listdir('../data_out/' + self.NAME + '/' + folder))
        elif self.comboBox.currentText() == '磨花':
            folder = 'rs'
            self.listWidget_2.addItems(os.listdir('../data_out/' + self.NAME + '/' + folder))
        elif self.comboBox.currentText() == '划痕':
            folder = 'sc'
            self.listWidget_2.addItems(os.listdir('../data_out/' + self.NAME + '/' + folder))

    def show_pic(self, item):       # 展示图片以及图片相关信息
        pic_name = item.text()
        road = '../data_out/' + self.NAME + '/all/' + pic_name
        self.label.setPixmap(QPixmap(road))

        all_message = self.helper.select_all_of_pic(self.NAME, pic_name)        # 关于所选图片的全部信息
        self.textEdit_3.clear()
        self.textEdit_3.append('--------------------')
        self.textEdit_3.append('<font color=blue>' + all_message[0][0] + '</font>' +
                               '具有' + '<font color=red>' + str(all_message[0][1]) + '</font>' + '个缺陷,分别为:\n')

        for i in range(2, 61, 3):
            if all_message[0][i] == 'NULL':
                break
            else:
                self.textEdit_3.append('<font color=red>' + all_message[0][i] + '</font>' + '    位于  ' +
                                       '<font color=blue>' + all_message[0][i+1] + '</font>' + '\n 置信度为   ' + '<font color=red>' + all_message[0][i+2] + '</font>' + '\n')










    def init(self):
        """将页面初始化"""
        self.pushButton.setText("选择检测图像")
        self.pushButton_2.setText("开始检测")
        self.pushButton_2.setEnabled(False)         # 设置按钮为不可点击
        self.pushButton_3.setText("导出训练结果")
        self.pushButton_4.setText("可视化分析")
        self.label.setPixmap(QPixmap('../res/label_background.png'))
        self.label_2.setText('待测图片')
        self.label_3.setText('缺陷情况')
        self.label_4.setText('检测日志')
        self.textEdit_3.setReadOnly(True)
        self.textEdit_4.setReadOnly(True)
        self.pushButton.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.pushButton_4.setEnabled(False)
        self.comboBox.setEnabled(False)

        self.comboBox.addItem("全部缺陷")
        self.comboBox.addItem("裂纹")
        self.comboBox.addItem("夹杂")
        self.comboBox.addItem("斑块")
        self.comboBox.addItem("麻点")
        self.comboBox.addItem("磨花")
        self.comboBox.addItem("划痕")
        torch.save([], '../cache/detect_list.pt')  # 清空待识别图片名字列表文件
        self.progressBar.setValue(0)
        self.progressBar.hide()     # 隐藏进度条
        # self.progressBar.show()     # 显示进度条
        self.setWindowTitle('热轧钢带缺陷检测系统-请新建一个项目')



