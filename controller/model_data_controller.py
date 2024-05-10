import os
import threading
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
from view_py.model_data import Ui_MainWindow
from PyQt5.QtGui import QPixmap
from model.project_management_helper import project_management_helper
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import *
from controller.MainWindow_controller import MainWindow as main
import shutil
from PyQt5.QtGui import QPixmap, QIcon
from PIL import Image

class MainWindow(Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.pushButton.setIcon(QIcon(QPixmap('../res/向左.png')))
        self.pushButton_2.setIcon(QIcon(QPixmap('../res/向右.png')))
        self.pushButton.setText('')
        self.pushButton_2.setText('')
        self.flag = 0

        self.page = 1           # label_2显示的1/8
        self.label_2.setText(str(self.page) + ' / 8')

        self.pushButton_2.clicked.connect(self.right_change_pic)
        self.pushButton.clicked.connect(self.left_change_pic)
        self.init_picture_size()            # 初始化修改图片大小
        self.label.setPixmap(QPixmap('../res/model_res/train/labels.jpg'))
        self.setWindowTitle('模型数据展示')


        self.pic = ['../res/model_res/train/labels.jpg', '../res/model_res/train/labels_correlogram.jpg', '../res/model_res/train/results.png',
                    '../res/model_res/val/confusion_matrix.png', '../res/model_res/val/F1_curve.png',
                    '../res/model_res/val/P_curve.png',
                    '../res/model_res/val/PR_curve.png', '../res/model_res/val/R_curve.png']


    def init_picture_size(self):
        for i in os.listdir('../res/model_res/train'):  # 将所有图片的大小更改为321x321
            image = Image.open('../res/model_res/train' + '/' + i)
            image_size = image.resize((1181, 761), Image.ANTIALIAS)
            image_size.save('../res/model_res/train' + '/' + i)

        for i in os.listdir('../res/model_res/val'):  # 将所有图片的大小更改为321x321
            image = Image.open('../res/model_res/val' + '/' + i)
            image_size = image.resize((1181, 761), Image.ANTIALIAS)
            image_size.save('../res/model_res/val' + '/' + i)

    def right_change_pic(self):
        if self.flag != 7:
            self.flag += 1
            self.label.setPixmap(QPixmap(self.pic[self.flag]))
            self.page += 1
            self.label_2.setText(str(self.page) + ' / 8')

    def left_change_pic(self):
        if self.flag != 0:
            self.flag -= 1
            self.label.setPixmap(QPixmap(self.pic[self.flag]))
            self.page -= 1
            self.label_2.setText(str(self.page) + ' / 8')

