import os
import threading
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
from view_py.classify_model_data import Ui_MainWindow
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
        self.label.setPixmap(QPixmap('../res/classify/cifar10数据集'))
        self.label_3.setText('<font color=red size=20>' + 'cifar10数据集所含样本类别' + '</font>')
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)

        self.pic = ['../res/classify/cifar10数据集.png', '../res/classify/fashionmnist数据集.png',
                    '../res/classify/脉冲神经网络原理.jpg',
                    '../res/classify/stbp.jpg',
                    '../res/classify/TLIF神经元.jpg',
                    '../res/classify/基于事件的编码.jpg',
                    '../res/classify/cifar10脉冲激发频率.png', '../res/classify/fashionmnist脉冲激发频率.png']

        self.label_text = ['cifar10数据集所含样本类别', 'fashionmnist数据集所含样本类别',
                           '脉冲神经网络原理', '模型所用的反向传播方法',
                           'TLIF神经元', '模型使用的基于事件的编码方式',
                           '模型在cifar10数据集上的脉冲激发频率', '模型在fashionmnist数据集上的脉冲激发频率']
        self.setWindowTitle('模型数据展示')

    def init_picture_size(self):
        for i in os.listdir('../res/classify'):  # 将所有图片的大小更改为321x321
            image = Image.open('../res/classify' + '/' + i)
            image_size = image.resize((1181, 741), Image.ANTIALIAS)
            image_size.save('../res/classify' + '/' + i)


    def right_change_pic(self):
        if self.flag != 7:
            self.flag += 1
            self.label.setPixmap(QPixmap(self.pic[self.flag]))
            self.label_3.setText('<font color=red size=20>' + self.label_text[self.flag] + '</font>')
            self.page += 1
            self.label_2.setText(str(self.page) + ' / 8')

    def left_change_pic(self):
        if self.flag != 0:
            self.flag -= 1
            self.label.setPixmap(QPixmap(self.pic[self.flag]))
            self.label_3.setText('<font color=red size=20>' + self.label_text[self.flag] + '</font>')
            self.page -= 1
            self.label_2.setText(str(self.page) + ' / 8')

