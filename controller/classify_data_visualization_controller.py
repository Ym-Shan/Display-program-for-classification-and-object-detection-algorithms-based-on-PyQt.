import os
import threading
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
from view_py.classify_data_visualization import Ui_MainWindow
from PyQt5.QtGui import QPixmap
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import *
from controller.MainWindow_controller import MainWindow as main
import shutil
from model.classify_data_visualization_helper import classify_data_visualization_helper
import torch
import os
# 输入想要存储图像的路径
# os.chdir('./')
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
# 改变绘图风格
import seaborn as sns
# 设置中文字体
matplotlib.rc("font", family='AR PL UKai CN')


class MainWindow(Ui_MainWindow):


    def __init__(self, name, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)


        self.name = name
        self.tabWidget.setTabText(0, '分类结果分析')
        self.tabWidget.setTabText(1, '资源占用分析')

        self.tabWidget_2.setTabText(0, '物品分类任务')
        self.tabWidget_2.setTabText(1, '服饰分类任务')


        self.helper = classify_data_visualization_helper()

        self.draw_picture_of_type_cifar10() # 缺陷类别分析界面绘图
        self.draw_picture_of_type_fashionmnist()  # 缺陷类别分析界面绘图
        self.draw_source()  # 资源占用分析
        self.setWindowTitle('可视化分析')
        self.center()

    def draw_source(self):
        cpu_count = torch.load('../cache/cpu_count.pt')             # list
        memory_count = torch.load('../cache/memory_count.pt')       # list
        gpu_count = torch.load('../cache/gpu_count.pt')             # list
        time = torch.load('../cache/detect_time.pt')                # float
        length = len(cpu_count)

        max_cpu = 0
        max_gpu = 0
        max_memory = 0
        min_cpu = 100
        min_gpu = 100
        min_memory = 100
        average_cpu = 0
        average_memory = 0
        average_gpu = 0
        for i in range(len(cpu_count)):
            if cpu_count[i] > max_cpu:
                max_cpu = cpu_count[i]
            if gpu_count[i] > max_gpu:
                max_gpu = gpu_count[i]
            if memory_count[i] > max_memory:
                max_memory = memory_count[i]
            if min_cpu > cpu_count[i]:
                min_cpu = cpu_count[i]
            if min_memory > memory_count[i]:
                min_memory = memory_count[i]
            if min_gpu > gpu_count[i]:
                min_gpu = gpu_count[i]
            average_cpu += cpu_count[i]
            average_memory += memory_count[i]
            average_gpu += gpu_count[i]
        average_cpu = average_cpu / len(cpu_count)
        average_gpu = average_gpu / len(gpu_count)
        average_memory = average_memory / len(memory_count)



        for i in range(len(cpu_count)):
            cpu_count[i] = int(round(cpu_count[i], 1))
            gpu_count[i] = int(round(gpu_count[i] * 100, 0))
            memory_count[i] = int(round(memory_count[i], 0))


        x = range(0, length)

        matplotlib.rc("font", family='AR PL UKai CN')
        plt.figure(figsize=(3.51, 3.51))
        plt.plot(x, cpu_count)
        plt.ylabel('占用率(%)')  # y轴
        # plt.yticks(fontsize=8)          # 调整y轴刻度字体大小
        plt.title('cpu资源消耗折线图')
        save_road = '../classify_data_out/' + self.name + '/'
        plt.savefig(save_road + 'cpu_count.png')  # 保存图像，dpi可以调整图像的像素大小
        self.label_5.setPixmap(QPixmap(save_road + 'cpu_count.png'))

        matplotlib.rc("font", family='AR PL UKai CN')
        plt.figure(figsize=(3.51, 3.51))
        plt.plot(x, memory_count)
        # plt.ylabel('占用率(%)')  # y轴
        # plt.yticks(fontsize=8)          # 调整y轴刻度字体大小
        plt.title('内存资源消耗折线图')
        save_road = '../classify_data_out/' + self.name + '/'
        plt.savefig(save_road + 'memory_count.png')  # 保存图像，dpi可以调整图像的像素大小
        self.label_6.setPixmap(QPixmap(save_road + 'memory_count.png'))

        matplotlib.rc("font", family='AR PL UKai CN')
        plt.figure(figsize=(3.51, 3.51))
        plt.plot(x, gpu_count)
        # plt.ylabel('占用率(%)')  # y轴
        # plt.yticks(fontsize=8)          # 调整y轴刻度字体大小
        plt.title('gpu资源消耗折线图')
        save_road = '../classify_data_out/' + self.name + '/'
        plt.savefig(save_road + 'gpu_count.png')  # 保存图像，dpi可以调整图像的像素大小
        self.label_7.setPixmap(QPixmap(save_road + 'gpu_count.png'))

        list = self.helper.get_num_of_every_type(self.name)
        length = len(list)




        self.textEdit_3.append('<font color=black size=4>' + '在对本项目的共计 ' + '</font>' + '<font color=red size=4>'
                               + str(length) + '</font>' + '<font color=black size=4>' + ' 张的输入图像进行检测的过程中: ' + '</font>')

        self.textEdit_3.append('<font color=blue size=4>' + 'cpu' + '</font>' + '<font color=black size=4>' +
                               '占用率的最小值为: ' + '</font>' + '<font color=red size=4>' + str(round(min_cpu, 2)) + '%' + '</font>' +
                               '<font color=black size=4>' + ' 最大值为: ' + '</font>' +
                               '<font color=red size=4>' + str(round(max_cpu, 2)) + '%' + '</font>' + '<font color=black size=4>' + ' 平均值为: ' + '</font>'
                                + '<font color=red size=4>' + str(round(average_cpu, 2)) + '%' + '</font>')
        self.textEdit_3.append('<font color=blue size=4>' + '内存' + '</font>' + '<font color=black size=4>' +
                               '占用率的最小值为: ' + '</font>' + '<font color=red size=4>' + str(round(min_memory, 2)) + '%' + '</font>' +
                               '<font color=black size=4>' + ' 最大值为: ' + '</font>' +
                               '<font color=red size=4>' + str(round(max_memory, 2)) + '%' + '</font>' + '<font color=black size=4>' + ' 平均值为: ' + '</font>'
                               + '<font color=red size=4>' + str(round(average_memory, 2)) + '%' + '</font>')
        self.textEdit_3.append('<font color=blue size=4>' + 'gpu' + '</font>' + '<font color=black size=4>' +
                               '占用率的最小值为: ' + '</font>' + '<font color=red size=4>' + str(round(min_gpu * 100, 2)) + '%' + '</font>' +
                               '<font color=black size=4>' + ' 最大值为: ' + '</font>' +
                               '<font color=red size=4>' + str(round(max_gpu * 100, 2)) + '%' + '</font>' + '<font color=black size=4>' + ' 平均值为: ' + '</font>'
                               + '<font color=red size=4>' + str(round(average_gpu * 100, 2)) + '%' + '</font>')




    def center(self):       # 将窗口显示在屏幕正中间
        # 获取屏幕的尺寸信息
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口的尺寸信息
        size = self.geometry()
        # 将窗口移动到指定位置
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

    def draw_picture_of_type_cifar10(self):
        # 获取y轴数据
        self.defect = self.count_num_of_type(self.name)

        matplotlib.rc("font", family='AR PL UKai CN')
        cell = ['飞机', '汽车', '鸟', '猫', '鹿', '狗', '青蛙', '马', '船', '卡车']
        pvalue = self.defect
        width = 0.50
        index = np.arange(len(cell))
        plt.figure(figsize=(4.61, 4.11))
        plt.bar(index, pvalue, width, color="#87CEFA")  # 绘制柱状图
        # sns.set(color_codes=True)
        # plt.xlabel('cell type') #x轴
        plt.ylabel('数量')  # y轴
        plt.title('物体数量柱状图')  # 图像的名称
        plt.xticks(index, cell, fontsize=10)  # 将横坐标用cell替换,fontsize用来调整字体的大小
        # plt.legend()  # 显示label
        for a, b in zip(index, pvalue):
            plt.text(a - 0.36, b + 0.55, b)
        save_road = '../classify_data_out/' + self.name + '/'
        plt.savefig(save_road + 'histogram.png')  # 保存图像，dpi可以调整图像的像素大小

        add = 0  # 记录缺陷总数
        for i in range(len(pvalue)):
            add += pvalue[i]
        percentage = []

        for i in range(len(pvalue)):
            percentage.append(pvalue[i] / add)


        matplotlib.rc("font", family='AR PL UKai CN')
        # 数据
        data = self.defect
        # 类别名称
        categories = ['飞机', '汽车', '鸟', '猫', '鹿', '狗', '青蛙', '马', '船', '卡车']
        fig, ax = plt.subplots(figsize=(4.61, 4.11))
        plt.title('物体分类扇形图')  # 图像的名称
        ax.pie(data, labels=categories, autopct='%1.1f%%')
        ax.axis('equal')
        ax.legend(title='图例', loc='center left', bbox_to_anchor=(1.2, 0.5))
        plt.savefig(save_road + 'pi.png')  # 保存图像，dpi可以调整图像的像素大小


        self.label_9.setPixmap(QPixmap(save_road + 'histogram.png'))
        self.label_8.setPixmap(QPixmap(save_road + 'pi.png'))

        self.textEdit_5.append('<font color=black size=4>' + '在本项目的全部输入图像中,共存在: ' + '</font>' +
                             '<font color=red size=4>' + str(add) + '</font>' + '<font color=black size=4>' + ' 张物体图像, 其中:' + '</font>')

        for i in range(len(pvalue)):
            self.textEdit_5.append('<font color=blue size=4>' + categories[i] + '</font>' + '  ' + '<font color=red size=4>'
                             + str(pvalue[i]) + '</font>' + '<font color=blue size=4>' + ' 张,         占比 ' + '</font>'
                             + '<font color=red size=4>' + str(round(percentage[i] * 100, 1)) + '%' + '</font>')
        plt.clf()



    def count_num_of_type(self, name):
        list = self.helper.get_num_of_every_type(name)

        self.defect = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # 第0-5种缺陷 和 没有缺陷的金属数量

        for i in range(len(list)):
            if list[i][2] != 'NULL':
                if list[i][2] == '飞机':
                    self.defect[0] += 1
                elif list[i][2] == '汽车':
                    self.defect[1] += 1
                elif list[i][2] == '鸟':
                    self.defect[2] += 1
                elif list[i][2] == '猫':
                    self.defect[3] += 1
                elif list[i][2] == '鹿':
                    self.defect[4] += 1
                elif list[i][2] == '狗':
                    self.defect[5] += 1
                elif list[i][2] == '青蛙':
                    self.defect[6] += 1
                elif list[i][2] == '马':
                    self.defect[7] += 1
                elif list[i][2] == '船':
                    self.defect[8] += 1
                elif list[i][2] == '卡车':
                    self.defect[9] += 1

        return self.defect

    def draw_picture_of_type_fashionmnist(self):
        # 获取y轴数据
        self.defect = self.count_num_of_type_fashionmnist(self.name)

        matplotlib.rc("font", family='AR PL UKai CN')
        cell = ['T恤', '牛仔裤', '套衫', '连衣裙', '外套', '凉鞋', '衬衫', '运动鞋', '包', '短靴']
        pvalue = self.defect
        width = 0.50
        index = np.arange(len(cell))
        plt.figure(figsize=(4.61, 4.11))
        plt.bar(index, pvalue, width, color="#87CEFA")  # 绘制柱状图
        # sns.set(color_codes=True)
        # plt.xlabel('cell type') #x轴
        plt.ylabel('数量')  # y轴
        plt.title('服饰数量柱状图')  # 图像的名称
        plt.xticks(index, cell, fontsize=10)  # 将横坐标用cell替换,fontsize用来调整字体的大小
        # plt.legend()  # 显示label
        for a, b in zip(index, pvalue):
            plt.text(a - 0.36, b + 0.55, b)
        save_road = '../classify_data_out/' + self.name + '/'
        plt.savefig(save_road + 'histogram_fashionmnist.png')  # 保存图像，dpi可以调整图像的像素大小

        add = 0
        for i in range(len(pvalue)):
            add += pvalue[i]
        percentage = []

        for i in range(len(pvalue)):
            percentage.append(pvalue[i] / add)


        matplotlib.rc("font", family='AR PL UKai CN')
        # 数据
        data = self.defect
        # 类别名称
        categories = ['T恤', '牛仔裤', '套衫', '连衣裙', '外套', '凉鞋', '衬衫', '运动鞋', '包', '短靴']
        fig, ax = plt.subplots(figsize=(4.61, 4.11))
        plt.title('服饰分类扇形图')  # 图像的名称
        ax.pie(data, labels=categories, autopct='%1.1f%%')
        ax.axis('equal')
        ax.legend(title='图例', loc='center left', bbox_to_anchor=(1.2, 0.5))



        plt.savefig(save_road + 'pi_fashionmnist.png')  # 保存图像，dpi可以调整图像的像素大小


        self.label_3.setPixmap(QPixmap(save_road + 'histogram_fashionmnist.png'))
        self.label_4.setPixmap(QPixmap(save_road + 'pi_fashionmnist.png'))

        self.textEdit_4.append('<font color=black size=4>' + '在本项目的全部输入图像中,共存在: ' + '</font>' +
                             '<font color=red size=4>' + str(add) + '</font>' + '<font color=black size=4>' + ' 张服饰图像, 其中:' + '</font>')

        for i in range(len(pvalue)):
            self.textEdit_4.append('<font color=blue size=4>' + categories[i] + '</font>' + '  ' + '<font color=red size=4>'
                             + str(pvalue[i]) + '</font>' + '<font color=blue size=4>' + ' 张,         占比 ' + '</font>'
                             + '<font color=red size=4>' + str(round(percentage[i] * 100, 1)) + '%' + '</font>')




    def count_num_of_type_fashionmnist(self, name):
        list = self.helper.get_num_of_every_type(name)

        self.defect = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # 第0-5种缺陷 和 没有缺陷的金属数量

        for i in range(len(list)):
            if list[i][2] != 'NULL':
                if list[i][2] == 'T恤':
                    self.defect[0] += 1
                elif list[i][2] == '牛仔裤':
                    self.defect[1] += 1
                elif list[i][2] == '套衫':
                    self.defect[2] += 1
                elif list[i][2] == '连衣裙':
                    self.defect[3] += 1
                elif list[i][2] == '外套':
                    self.defect[4] += 1
                elif list[i][2] == '凉鞋':
                    self.defect[5] += 1
                elif list[i][2] == '衬衫':
                    self.defect[6] += 1
                elif list[i][2] == '运动鞋':
                    self.defect[7] += 1
                elif list[i][2] == '包':
                    self.defect[8] += 1
                elif list[i][2] == '短靴':
                    self.defect[9] += 1

        return self.defect



