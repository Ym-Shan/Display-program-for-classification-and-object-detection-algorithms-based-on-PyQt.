import threading
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
from view_py.classify_MainWindow import Ui_MainWindow
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
from model.classify_MainWindow_helper import classify_MainWindow_helper
import classify.resnet18_cifar10_classify
import classify.resnet18_fashionmnist_classify
from pynvml import *
from psutil import *
class MainWindow(Ui_MainWindow):
    ROAD = ''       # 存储待识别照片的位置
    TYPE = 'cifar10'
    OUT = '../classify_data_out/'
    NAME = ''
    DETECT = 'False'
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.init()

        self.pushButton.clicked.connect(self.select_data)
        self.action.triggered.connect(self.getname)
        self.helper = classify_MainWindow_helper()
        self.comboBox_2.currentIndexChanged.connect(self.change_data_type)  # 下拉框的监听
        self.pushButton_2.clicked.connect(self.start_classify)  # 开始检测
        self.comboBox.currentIndexChanged.connect(self.show_classify_result)  # 下拉框的监听
        self.listWidget_2.itemClicked.connect(self.show_pic)
        self.listWidget_2.doubleClicked.connect(self.delete)
        self.pushButton_3.clicked.connect(self.save_result)  # 保存检测结果
        self.pushButton_4.clicked.connect(self.data_visualization)  # 进行数据可视化
        self.action_2.triggered.connect(self.open_project)  # 打开项目
        self.action_5.triggered.connect(self.close_project)  # 关闭项目
        self.action_3.triggered.connect(self.open_project_management_face)  # 项目管理
        self.action_6.triggered.connect(self.model_data)  # 查看模型数据

    def delete(self):
        # pic_name = item.text()
        os.remove(self.ROAD + self.listWidget_2.currentItem().text())


    def model_data(self):
        import classify_model_data_controller
        self.new_window = classify_model_data_controller.MainWindow()
        self.init_project()
        self.new_window.show()

    def open_project_management_face(self):
        self.init_project()
        import classify_project_management_controller
        self.new_window = classify_project_management_controller.MainWindow()
        self.new_window.FATHER = self
        self.new_window.show()


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


    def open_project(self):
        dir = QFileDialog.getExistingDirectory(None, '清选择要打开的项目', directory='../classify_data_out')
        name = (dir.split('/'))[-1]
        if dir:
            self.setWindowTitle('视觉图像分类系统-' + name)  # 设置窗口名字为项目名字
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

    def data_visualization(self):
        import classify_data_visualization_controller
        self.new_window = classify_data_visualization_controller.MainWindow(self.NAME)
        self.init_project()
        self.new_window.show()


    def save_result(self):      # 将结果文件夹转存到用户选择的位置
        dir = QFileDialog.getExistingDirectory(None, '清选择要将检测结果保存到哪个文件夹下', os.getcwd())
        if dir:
            name = self.NAME
            if os.path.exists(dir + '/' + name):
                shutil.rmtree(dir + '/' + name)  # 删除默认的结果文件夹,从而避免目录名称变化
                shutil.copytree('../classify_data_out/' + name + '/', dir + '/' + name)
            else:
                shutil.copytree('../classify_data_out/' + name + '/', dir + '/' + name)
            self.textEdit_4.append('--------------------')
            self.textEdit_4.append('本次缺陷检测的结果已保存到 ')
            self.textEdit_4.append('<font color=red>' + dir + '</font>' + '<font color=red>' + '/' + '</font>' + '<font color=red>' + name + '</font>')


    def show_pic(self, item):       # 展示图片以及图片相关信息
        pic_name = item.text()
        if self.TYPE == 'cifar10':
            road = self.OUT + self.NAME + '/物体_all/' + pic_name
        elif self.TYPE == 'fashionmnist':
            road = self.OUT + self.NAME + '/服饰_all/' + pic_name

        self.label.setPixmap(QPixmap(road))

        all_message = self.helper.select_all_of_pic(self.NAME, pic_name)        # 关于所选图片的全部信息

        self.textEdit_3.clear()
        self.textEdit_3.append('--------------------')
        if self.TYPE == 'cifar10':
            self.textEdit_3.append('<font color=blue>' + all_message[0][0] + '</font>' + '是一个物体。\n')
        elif self.TYPE == 'fashionmnist':
            self.textEdit_3.append('<font color=blue>' + all_message[0][0] + '</font>' + '是一件服饰。\n')
        self.textEdit_3.append('分类该图片所使用的模型在' + '<font color=red>' + all_message[0][1] + '</font>' + '数据集上训练。\n')

        self.textEdit_3.append('其类别为：' + '<font color=red>' + all_message[0][2] + '</font>' + '\n')


    def show_classify_result(self):       # 检测结果展示
        self.listWidget_2.clear()
        if self.TYPE == 'cifar10':
            if self.comboBox.currentText() == '全部类别':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/飞机'))  # 将选择的文件展示在列表中
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/汽车'))
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/鸟'))
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/猫'))
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/鹿'))
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/狗'))
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/青蛙'))
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/马'))
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/船'))
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/卡车'))

            elif self.comboBox.currentText() == '飞机':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/飞机'))
            elif self.comboBox.currentText() == '汽车':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/汽车'))
            elif self.comboBox.currentText() == '鸟':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/鸟'))
            elif self.comboBox.currentText() == '猫':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/猫'))
            elif self.comboBox.currentText() == '鹿':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/鹿'))
            elif self.comboBox.currentText() == '狗':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/狗'))
            elif self.comboBox.currentText() == '青蛙':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/青蛙'))
            elif self.comboBox.currentText() == '马':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/马'))
            elif self.comboBox.currentText() == '船':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/船'))
            elif self.comboBox.currentText() == '卡车':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/卡车'))
        elif self.TYPE == 'fashionmnist':
            if self.comboBox.currentText() == '全部类别':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/T恤'))  # 将选择的文件展示在列表中
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/牛仔裤'))
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/套衫'))
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/连衣裙'))
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/外套'))
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/凉鞋'))
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/衬衫'))
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/运动鞋'))
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/包'))
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/短靴'))

            elif self.comboBox.currentText() == 'T恤':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/T恤'))
            elif self.comboBox.currentText() == '牛仔裤':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/牛仔裤'))
            elif self.comboBox.currentText() == '套衫':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/套衫'))
            elif self.comboBox.currentText() == '连衣裙':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/连衣裙'))
            elif self.comboBox.currentText() == '外套':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/外套'))
            elif self.comboBox.currentText() == '凉鞋':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/凉鞋'))
            elif self.comboBox.currentText() == '衬衫':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/衬衫'))
            elif self.comboBox.currentText() == '运动鞋':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/运动鞋'))
            elif self.comboBox.currentText() == '包':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/包'))
            elif self.comboBox.currentText() == '短靴':
                self.listWidget_2.addItems(os.listdir(self.OUT + self.NAME + '/短靴'))


    def start_classify(self):
        self.comboBox.setCurrentIndex(0)  # 将下拉框设置为显示全部结果
        self.textEdit_4.append('--------------------')
        self.textEdit_4.append(time.ctime())
        self.textEdit_4.append('<font color=blue>' + '开始分类......' + '</font>')
        self.textEdit_4.append('<font color=red>' + '分类中......' + '</font>')
        # file_list = torch.load('../cache/detect_list.pt')  # 读取要识别的图片列表
        self.DETECT = 'True'
        t1 = time.time()
        if self.TYPE == 'cifar10':
            pro = threading.Thread(target=self.cifar10_predict)  # 开始检测的子进程

        elif self.TYPE == 'fashionmnist':
            pro = threading.Thread(target=self.fashionmnist_predict)  # 开始检测的子进程

        pro.start()  # 调用开始检测的子线程
        pro2 = threading.Thread(target=self.writedown)  # 记录cpu\内存\gpu使用率的子线程
        pro2.start()  # 调用开始检测的子线程

        pro.join()  # 在子线程完成后调用下面的语句
        self.DETECT = 'False'
        t2 = time.time()
        t = t2 - t1
        torch.save(t, '../cache/detect_time.pt')  # 记录检测总时间
        self.textEdit_4.append('--------------------')
        self.textEdit_4.append(time.ctime())
        self.textEdit_4.append('<font color=red>' + '分类完成' + '</font>')
        self.textEdit_4.append('<font color=black>' + '本次检测的结果存储在' + '</font>')
        self.textEdit_4.append('<font color=red>' + self.OUT + self.NAME + '</font>')

        data_num_1 = os.listdir('../classify_data_out/' + self.NAME + '/物体_all')  # 获取项目中文件的数量
        data_num_2 = os.listdir('../classify_data_out/' + self.NAME + '/服饰_all')  # 获取项目中文件的数量
        data_num = data_num_1 + data_num_2

        self.helper.update_project_message(self.NAME, time.ctime(), len(data_num))  # 更新项目最后的更新时间
        self.pushButton_3.setEnabled(True)
        self.pushButton_4.setEnabled(True)


    def cifar10_predict(self):             # 检测
        file_list = torch.load('../cache/classify_list.pt')       # 读取要识别的图片列表
        if file_list != []:
            self.listWidget_2.clear()
            self.progressBar.show()         # 显示进度条
            lens = len(file_list)           # 选择的需要进行目标检测的照片总数
            number_completes = 0                      # 目前已经检测完成的照片总数
            pic_sum = 0        # 用来统计目前检测到第几张图片
            for i in range(len(file_list)):                 # 遍历每一张图片
                pic = (self.ROAD) + str(file_list[i])         # 格式类似于../datasets/NEU/test/images/scratches_297.jpg
                result = classify.resnet18_cifar10_classify.classify(pic)
                pic_sum += 1
                number_completes += 1
                self.flash_progressBar(lens, number_completes)


                if result == 0:
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/飞机/' +str(file_list[i]))        # 将识别结果转存到输出文件夹
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/物体_all/' +str(file_list[i]))
                    self.helper.insert_data_in_db(self.NAME, str(file_list[i]), 'cifar10', '飞机')  # 将每张图片的数据存储到数据库
                if result == 1:
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/汽车/' +str(file_list[i]))        # 将识别结果转存到输出文件夹
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/物体_all/' +str(file_list[i]))
                    self.helper.insert_data_in_db(self.NAME, str(file_list[i]), 'cifar10', '汽车')  # 将每张图片的数据存储到数据库
                if result == 2:
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/鸟/' +str(file_list[i]))        # 将识别结果转存到输出文件夹
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/物体_all/' +str(file_list[i]))
                    self.helper.insert_data_in_db(self.NAME, str(file_list[i]), 'cifar10', '鸟')  # 将每张图片的数据存储到数据库
                if result == 3:
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/猫/' +str(file_list[i]))        # 将识别结果转存到输出文件夹
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/物体_all/' +str(file_list[i]))
                    self.helper.insert_data_in_db(self.NAME, str(file_list[i]), 'cifar10', '猫')  # 将每张图片的数据存储到数据库
                if result == 4:
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/鹿/' +str(file_list[i]))        # 将识别结果转存到输出文件夹
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/物体_all/' +str(file_list[i]))
                    self.helper.insert_data_in_db(self.NAME, str(file_list[i]), 'cifar10', '鹿')  # 将每张图片的数据存储到数据库
                if result == 5:
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/狗/' +str(file_list[i]))        # 将识别结果转存到输出文件夹
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/物体_all/' +str(file_list[i]))
                    self.helper.insert_data_in_db(self.NAME, str(file_list[i]), 'cifar10', '狗')  # 将每张图片的数据存储到数据库
                if result == 6:
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/青蛙/' +str(file_list[i]))        # 将识别结果转存到输出文件夹
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/物体_all/' +str(file_list[i]))
                    self.helper.insert_data_in_db(self.NAME, str(file_list[i]), 'cifar10', '青蛙')  # 将每张图片的数据存储到数据库
                if result == 7:
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/马/' +str(file_list[i]))        # 将识别结果转存到输出文件夹
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/物体_all/' +str(file_list[i]))
                    self.helper.insert_data_in_db(self.NAME, str(file_list[i]), 'cifar10', '马')  # 将每张图片的数据存储到数据库
                if result == 8:
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/船/' +str(file_list[i]))        # 将识别结果转存到输出文件夹
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/物体_all/' +str(file_list[i]))
                    self.helper.insert_data_in_db(self.NAME, str(file_list[i]), 'cifar10', '船')  # 将每张图片的数据存储到数据库
                if result == 9:
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/卡车/' +str(file_list[i]))        # 将识别结果转存到输出文件夹
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/物体_all/' +str(file_list[i]))
                    self.helper.insert_data_in_db(self.NAME, str(file_list[i]), 'cifar10', '卡车')  # 将每张图片的数据存储到数据库


            self.flash()        # 刷新检测结果展示界面
            self.progressBar.hide()   # 隐藏进度条
            for i in os.listdir(self.OUT + self.NAME + '/物体_all'):          # 将所有图片的大小更改为321x321
                image = Image.open(self.OUT + self.NAME + '/物体_all' + '/'+i)
                image_size = image.resize((321, 321), Image.ANTIALIAS)
                image_size.save(self.OUT + self.NAME + '/物体_all' + '/'+i)
        else:
            self.textEdit_4.clear()
            self.textEdit_4.append('<font color=red>' + '请选择要分类的图像' + '</font>')


    def fashionmnist_predict(self):             # 检测
        file_list = torch.load('../cache/classify_list.pt')       # 读取要识别的图片列表
        if file_list != []:
            self.listWidget_2.clear()
            self.progressBar.show()         # 显示进度条
            lens = len(file_list)           # 选择的需要进行目标检测的照片总数
            number_completes = 0                      # 目前已经检测完成的照片总数
            pic_sum = 0        # 用来统计目前检测到第几张图片
            for i in range(len(file_list)):                 # 遍历每一张图片
                pic = (self.ROAD) + str(file_list[i])         # 格式类似于../datasets/NEU/test/images/scratches_297.jpg
                result = classify.resnet18_fashionmnist_classify.classify(pic)
                pic_sum += 1
                number_completes += 1
                self.flash_progressBar(lens, number_completes)


                if result == 0:
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/T恤/' +str(file_list[i]))        # 将识别结果转存到输出文件夹
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/服饰_all/' +str(file_list[i]))
                    self.helper.insert_data_in_db(self.NAME, str(file_list[i]), 'fashionmnist', 'T恤')  # 将每张图片的数据存储到数据库
                if result == 1:
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/牛仔裤/' +str(file_list[i]))        # 将识别结果转存到输出文件夹
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/服饰_all/' +str(file_list[i]))
                    self.helper.insert_data_in_db(self.NAME, str(file_list[i]), 'fashionmnist', '牛仔裤')  # 将每张图片的数据存储到数据库
                if result == 2:
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/套衫/' +str(file_list[i]))        # 将识别结果转存到输出文件夹
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/服饰_all/' +str(file_list[i]))
                    self.helper.insert_data_in_db(self.NAME, str(file_list[i]), 'fashionmnist', '套衫')  # 将每张图片的数据存储到数据库
                if result == 3:
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/连衣裙/' +str(file_list[i]))        # 将识别结果转存到输出文件夹
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/服饰_all/' +str(file_list[i]))
                    self.helper.insert_data_in_db(self.NAME, str(file_list[i]), 'fashionmnist', '外套')  # 将每张图片的数据存储到数据库
                if result == 4:
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/外套/' +str(file_list[i]))        # 将识别结果转存到输出文件夹
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/服饰_all/' +str(file_list[i]))
                    self.helper.insert_data_in_db(self.NAME, str(file_list[i]), 'fashionmnist', '外套')  # 将每张图片的数据存储到数据库
                if result == 5:
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/凉鞋/' +str(file_list[i]))        # 将识别结果转存到输出文件夹
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/服饰_all/' +str(file_list[i]))
                    self.helper.insert_data_in_db(self.NAME, str(file_list[i]), 'fashionmnist', '凉鞋')  # 将每张图片的数据存储到数据库
                if result == 6:
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/衬衫/' +str(file_list[i]))        # 将识别结果转存到输出文件夹
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/服饰_all/' +str(file_list[i]))
                    self.helper.insert_data_in_db(self.NAME, str(file_list[i]), 'fashionmnist', '衬衫')  # 将每张图片的数据存储到数据库
                if result == 7:
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/运动鞋/' +str(file_list[i]))        # 将识别结果转存到输出文件夹
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/服饰_all/' +str(file_list[i]))
                    self.helper.insert_data_in_db(self.NAME, str(file_list[i]), 'fashionmnist', '运动鞋')  # 将每张图片的数据存储到数据库
                if result == 8:
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/包/' +str(file_list[i]))        # 将识别结果转存到输出文件夹
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/服饰_all/' +str(file_list[i]))
                    self.helper.insert_data_in_db(self.NAME, str(file_list[i]), 'fashionmnist', '包')  # 将每张图片的数据存储到数据库
                if result == 9:
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/短靴/' +str(file_list[i]))        # 将识别结果转存到输出文件夹
                    shutil.copyfile((self.ROAD) + str(file_list[i]), self.OUT + self.NAME + '/服饰_all/' +str(file_list[i]))
                    self.helper.insert_data_in_db(self.NAME, str(file_list[i]), 'fashionmnist', '短靴')  # 将每张图片的数据存储到数据库


            self.flash()        # 刷新检测结果展示界面
            self.progressBar.hide()   # 隐藏进度条
            for i in os.listdir(self.OUT + self.NAME + '/服饰_all'):          # 将所有图片的大小更改为321x321
                image = Image.open(self.OUT + self.NAME + '/服饰_all' + '/'+i)
                image_size = image.resize((321, 321), Image.ANTIALIAS)
                image_size.save(self.OUT + self.NAME + '/服饰_all' + '/'+i)
        else:
            self.textEdit_4.clear()
            self.textEdit_4.append('<font color=red>' + '请选择要分类的图像' + '</font>')

    def flash(self):                # 检测结束后刷新界面
        self.comboBox.setCurrentIndex(2)    # 刷新检测结果界面
        self.comboBox.setCurrentIndex(0)  # 将下拉框设置为显示全部结果


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

    def change_data_type(self):       # 检测结果展示
        if self.NAME != '':
            self.listWidget_2.clear()
            if self.comboBox_2.currentText() == '物体':
                self.TYPE = 'cifar10'
                self.ROAD = '../cifar10_data_in/'
                self.comboBox.clear()
                self.comboBox.addItem("全部类别")
                self.comboBox.addItem("飞机")
                self.comboBox.addItem("汽车")
                self.comboBox.addItem("鸟")
                self.comboBox.addItem("猫")
                self.comboBox.addItem("鹿")
                self.comboBox.addItem("狗")
                self.comboBox.addItem("青蛙")
                self.comboBox.addItem("马")
                self.comboBox.addItem("船")
                self.comboBox.addItem("卡车")

            elif self.comboBox_2.currentText() == '服饰':
                self.TYPE = 'fashionmnist'
                self.ROAD = '../fashionmnist_data_in/'
                self.comboBox.clear()
                self.comboBox.addItem("全部类别")
                self.comboBox.addItem("T恤")
                self.comboBox.addItem("牛仔裤")
                self.comboBox.addItem("套衫")
                self.comboBox.addItem("连衣裙")
                self.comboBox.addItem("外套")
                self.comboBox.addItem("凉鞋")
                self.comboBox.addItem("衬衫")
                self.comboBox.addItem("运动鞋")
                self.comboBox.addItem("包")
                self.comboBox.addItem("短靴")
        else:
            self.getname()  # 提示用户输入项目名称

    def select_data(self):      # 选择需要缺陷检测的图片
        if self.NAME == '':
            self.getname()  # 提示用户输入项目名称
        from PyQt5.QtWidgets import QFileDialog
        self.listWidget.clear()         # 清空文本框
        torch.save([], '../cache/classify_list.pt')  # 清空待识别图片名字列表文件
        dir = QFileDialog()         # 创建文件对话框
        dir.setFileMode(QFileDialog.ExistingFiles)      # 设置多选
        if self.TYPE == 'cifar10':
            dir.setDirectory('../cifar10_data_in')
        elif self.TYPE == 'fashionmnist':
            dir.setDirectory('../fashionmnist_data_in')
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
            torch.save(final_file, '../cache/classify_list.pt')       # 将要识别的图片名字列表存储
            self.textEdit_4.append('--------------------')
            self.textEdit_4.append(time.ctime())
            self.textEdit_4.append('<font color=blue>' + '共选择了 ' + '</font>' + '<font color=red>' + str(len(final_file)) + '</font>' + '<font color=blue>' + ' 张图片' + '</font>')
        else:
            self.pushButton_2.setEnabled(False)  # 设置按钮为不可点击


    def getname(self):          # 通过对话框获取项目名字
        name, ok = QInputDialog.getText(self, "请输入项目名", "设定一个项目名以更方便的观测预测结果.", QtWidgets.QLineEdit.Normal, '')
        if ok and name:
            if self.NAME != '':
                self.textEdit_4.append('--------------------')
                self.textEdit_4.append(time.ctime())
                self.textEdit_4.append('<font color=blue>' + '项目 ' + self.NAME + ' 已关闭' + '</font>')
            with open('../cache/classify_name.py', 'w+') as f:
                f.write(name)
            self.setWindowTitle('视觉图像分类系统-' + name)        # 设置窗口名字为项目名字
            self.NAME = name
            self.comboBox.setEnabled(True)
            # self.textEdit_4.append('<font color=black>' + '已创建并进入新项目:   ' + '</font>' + '<font color=red>' + self.NAME + '</font>')
            # 在结果文件夹中创建名字为项目名字的文件夹以及该文件夹下的输出结构(all和各类缺陷文件夹)
            self.create_dir()           # 创建数据库表
            # 将一些组件恢复到初始状态
            self.pushButton.setEnabled(True)
            self.listWidget.clear()
            self.listWidget_2.clear()
            self.comboBox.setCurrentIndex(0)
            self.comboBox_2.setCurrentIndex(0)
            self.label.setPixmap(QPixmap('../res/label_background.png'))
            self.textEdit_3.clear()

    def create_dir(self):
        path = self.OUT + self.NAME + '/'
        if os.path.exists(path):
            select = QMessageBox.warning(None, '警告', '项目名 ' + self.NAME + ' 已存在,请修改项目名称.',
                                         QMessageBox.Yes)
            self.getname()
        else:
            self.textEdit_4.append(
                '<font color=black>' + '已创建并进入新项目:   ' + '</font>' + '<font color=red>' + self.NAME + '</font>')
            os.makedirs(path)  # 创建结果主文件夹
            os.makedirs(path + '物体_all/')
            os.makedirs(path + '飞机/')  # 创建结果子文件夹
            os.makedirs(path + '汽车/')
            os.makedirs(path + '鸟/')
            os.makedirs(path + '猫/')
            os.makedirs(path + '鹿/')
            os.makedirs(path + '狗/')
            os.makedirs(path + '青蛙/')
            os.makedirs(path + '马/')
            os.makedirs(path + '船/')
            os.makedirs(path + '卡车/')

            os.makedirs(path + '服饰_all/')
            os.makedirs(path + 'T恤/')
            os.makedirs(path + '牛仔裤/')
            os.makedirs(path + '套衫/')
            os.makedirs(path + '连衣裙/')
            os.makedirs(path + '外套/')
            os.makedirs(path + '凉鞋/')
            os.makedirs(path + '衬衫/')
            os.makedirs(path + '运动鞋/')
            os.makedirs(path + '包/')
            os.makedirs(path + '短靴/')

            # 创建数据库表
            self.helper.create_table(self.NAME)
            self.helper.insert_new_project_message(self.NAME, time.ctime())  # 在数据库中加入新建的项目名


    def init_project(self):         # 初始化项目
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.pushButton_4.setEnabled(False)
        self.comboBox.setEnabled(False)
        self.listWidget.clear()
        self.listWidget_2.clear()
        self.label.setPixmap(QPixmap('../res/label_background.png'))
        self.textEdit_3.clear()
        torch.save([], '../cache/detect_list.pt')  # 清空待识别图片名字列表文件
        self.progressBar.setValue(0)
        self.progressBar.hide()  # 隐藏进度条
        self.setWindowTitle('视觉图像分类系统-请新建一个项目')
        self.NAME = ''



    def init(self):
        """将页面初始化"""
        self.TYPE = 'cifar10'
        self.ROAD = '../cifar10_data_in/'
        self.pushButton.setText("选择分类图像")
        self.pushButton_2.setText("开始检测")
        self.pushButton_2.setEnabled(False)         # 设置按钮为不可点击
        self.pushButton_3.setText("导出训练结果")
        self.pushButton_4.setText("可视化分析")
        self.label.setPixmap(QPixmap('../res/label_background.png'))
        self.label_2.setText('待测图片')
        self.label_3.setText('分类情况')
        self.label_4.setText('日志')
        self.label_5.setText('任务')
        self.textEdit_3.setReadOnly(True)
        self.textEdit_4.setReadOnly(True)
        self.pushButton.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.pushButton_4.setEnabled(False)
        self.comboBox.setEnabled(False)

        self.comboBox.addItem("全部类别")
        self.comboBox.addItem("飞机")
        self.comboBox.addItem("汽车")
        self.comboBox.addItem("鸟")
        self.comboBox.addItem("猫")
        self.comboBox.addItem("鹿")
        self.comboBox.addItem("狗")
        self.comboBox.addItem("青蛙")
        self.comboBox.addItem("马")
        self.comboBox.addItem("船")
        self.comboBox.addItem("卡车")

        self.comboBox_2.addItem("物体")
        self.comboBox_2.addItem("服饰")

        # self.comboBox_2.addItem("全部类别")
        # self.comboBox_2.addItem("T恤")
        # self.comboBox_2.addItem("牛仔裤")
        # self.comboBox_2.addItem("套衫")
        # self.comboBox_2.addItem("连衣裙")
        # self.comboBox_2.addItem("外套")
        # self.comboBox_2.addItem("凉鞋")
        # self.comboBox_2.addItem("衬衫")
        # self.comboBox_2.addItem("运动鞋")
        # self.comboBox_2.addItem("包")
        # self.comboBox_2.addItem("短靴")



        # torch.save([], '../cache/detect_list.pt')  # 清空待识别图片名字列表文件
        # self.pushButton.setEnabled(True)
        self.progressBar.setValue(0)
        self.progressBar.hide()     # 隐藏进度条
        # self.progressBar.show()     # 显示进度条
        self.setWindowTitle('视觉图像分类系统-请新建一个项目')



