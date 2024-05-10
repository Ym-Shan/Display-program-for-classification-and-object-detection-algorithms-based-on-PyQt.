import os
import threading
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
from view_py.data_visualization import Ui_MainWindow
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
# 设置中文字体
matplotlib.rc("font", family='AR PL UKai CN')


class MainWindow(Ui_MainWindow):


    def __init__(self, name, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)


        self.name = name
        self.tabWidget.setTabText(0, '缺陷类别分析')
        self.tabWidget.setTabText(1, '缺陷位置分析')
        self.tabWidget.setTabText(2, '资源占用分析')
        self.tabWidget.setTabText(3, '资源占用分析')
        self.setWindowTitle('可视化分析')

        self.helper = data_visualization_helper()

        self.draw_picture_of_type() # 缺陷类别分析界面绘图
        self.draw_picture_of_located()  # 缺陷位置分析界面绘图
        self.draw_source()  # 资源占用分析

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
        save_road = '../data_out/' + self.name + '/'
        plt.savefig(save_road + 'cpu_count.png')  # 保存图像，dpi可以调整图像的像素大小
        self.label_5.setPixmap(QPixmap(save_road + 'cpu_count.png'))

        matplotlib.rc("font", family='AR PL UKai CN')
        plt.figure(figsize=(3.51, 3.51))
        plt.plot(x, memory_count)
        # plt.ylabel('占用率(%)')  # y轴
        # plt.yticks(fontsize=8)          # 调整y轴刻度字体大小
        plt.title('内存资源消耗折线图')
        save_road = '../data_out/' + self.name + '/'
        plt.savefig(save_road + 'memory_count.png')  # 保存图像，dpi可以调整图像的像素大小
        self.label_6.setPixmap(QPixmap(save_road + 'memory_count.png'))

        matplotlib.rc("font", family='AR PL UKai CN')
        plt.figure(figsize=(3.51, 3.51))
        plt.plot(x, gpu_count)
        # plt.ylabel('占用率(%)')  # y轴
        # plt.yticks(fontsize=8)          # 调整y轴刻度字体大小
        plt.title('gpu资源消耗折线图')
        save_road = '../data_out/' + self.name + '/'
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



    def draw_picture_of_located(self):
        data = self.get_scatter_data()      # 一个列表,拥有x和y坐标(值的含义是缺陷的中心点)
        matplotlib.rc("font", family='AR PL UKai CN')
        plt.figure(figsize=(4.31, 3.81))
        plt.scatter(data[0], data[1], s=1)
        plt.title('缺陷位置分布散点图')
        save_road = '../data_out/' + self.name + '/'
        plt.savefig(save_road + 'scatter.png')  # 保存图像，dpi可以调整图像的像素大小
        self.label_3.setPixmap(QPixmap(save_road + 'scatter.png'))

        ne, nw, se, sw = 0, 0, 0, 0
        for i in range(len(data[0])):
            if data[0][i]>=0.5 and data[1][i]>=0.5:
                ne += 1
            elif data[0][i]>0.5 and data[1][i]<=0.5:
                se += 1
            elif data[0][i]<=0.5 and data[1][i]>=0.5:
                nw += 1
            elif data[0][i]<0.5 and data[1][i]<=0.5:
                sw += 1
        add = len(data[0])
        NE = ne/add     # 在第一象限的数据比例
        NW = nw/add     # 在第二象限的数据比例
        SE = se/add     # 在第四象限的数据比例
        SW = sw/add     # 在第三象限的数据比例

        # 设置画布
        plt.figure(figsize=(4.31, 3.81))
        # 获取坐标轴对象
        axes = plt.gca()
        # 去掉右边框和上边框颜色
        axes.spines['right'].set_color('none')
        axes.spines['top'].set_color('none')
        # 设置坐标轴范围
        axes.set_xlim(0, 1)
        axes.set_ylim(0, 1)
        plt.title('缺陷在各象限分布比例图')
        plt.plot([0, 1], [0.5, 0.5], color='blue')
        plt.plot([0.5, 0.5], [0, 1], color='blue')
        plt.text(0.60, 0.70, str(round(NE * 100, 3)) + '%', fontsize=18, color='red')       # 横纵坐标相比中心分别减15和5
        plt.text(0.10, 0.70, str(round(NW * 100, 3)) + '%', fontsize=18, color='red')
        plt.text(0.60, 0.20, str(round(SE * 100, 3)) + '%', fontsize=18, color='red')
        plt.text(0.10, 0.20, str(round(SW * 100, 3)) + '%', fontsize=18, color='red')

        # plt.text(8, -1, 'X轴', fontsize=18)
        save_road = '../data_out/' + self.name + '/'
        plt.savefig(save_road + 'scale.png')  # 保存图像，dpi可以调整图像的像素大小
        self.label_4.setPixmap(QPixmap(save_road + 'scale.png'))

        self.textEdit_2.append('<font color=black size=4>' + '在本项目的全部输入图像中,共检测到: ' + '</font>' +
                             '<font color=red size=4>' + str(
            add) + '</font>' + '<font color=black size=4>' + ' 个缺陷, 其中:' + '</font>')
        self.textEdit_2.append('<font color=blue size=4>' + '第一象限' + '</font>' + '  ' + '<font color=red size=4>'
                             + str(ne) + '</font>' + '<font color=blue size=4>' + ' 个,         占比 ' + '</font>'
                             + '<font color=red size=4>' + str(round(NE * 100, 3)) + '%' + '</font>')
        self.textEdit_2.append('<font color=blue size=4>' + '第二象限' + '</font>' + '  ' + '<font color=red size=4>'
                             + str(nw) + '</font>' + '<font color=blue size=4>' + ' 个,         占比 ' + '</font>'
                             + '<font color=red size=4>' + str(round(NW * 100, 3)) + '%' + '</font>')
        self.textEdit_2.append('<font color=blue size=4>' + '第三象限' + '</font>' + '  ' + '<font color=red size=4>'
                             + str(sw) + '</font>' + '<font color=blue size=4>' + ' 个,         占比 ' + '</font>'
                             + '<font color=red size=4>' + str(round(SW * 100, 3)) + '%' + '</font>')
        self.textEdit_2.append('<font color=blue size=4>' + '第四象限' + '</font>' + '  ' + '<font color=red size=4>'
                             + str(se) + '</font>' + '<font color=blue size=4>' + ' 个,         占比 ' + '</font>'
                             + '<font color=red size=4>' + str(round(SE * 100, 3)) + '%' + '</font>')

    def center(self):       # 将窗口显示在屏幕正中间
        # 获取屏幕的尺寸信息
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口的尺寸信息
        size = self.geometry()
        # 将窗口移动到指定位置
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

    def draw_picture_of_type(self):
        # 获取y轴数据
        self.defect = self.count_num_of_type(self.name)

        matplotlib.rc("font", family='AR PL UKai CN')
        cell = ['裂纹', '夹杂', '斑块', '麻点', '磨花', '划痕']
        pvalue = self.defect
        width = 0.50
        index = np.arange(len(cell))
        plt.figure(figsize=(4.31, 3.81))
        plt.bar(index, pvalue, width, color="#87CEFA")  # 绘制柱状图
        sns.set(color_codes=True)
        # plt.xlabel('cell type') #x轴
        plt.ylabel('缺陷数量')  # y轴
        plt.title('缺陷数量柱状图')  # 图像的名称
        plt.xticks(index, cell, fontsize=10)  # 将横坐标用cell替换,fontsize用来调整字体的大小
        # plt.legend()  # 显示label
        for a, b in zip(index, pvalue):
            plt.text(a - 0.36, b + 0.55, b)
        save_road = '../data_out/' + self.name + '/'
        plt.savefig(save_road + 'histogram.png')  # 保存图像，dpi可以调整图像的像素大小

        add = 0         # 记录缺陷总数
        for i in range(len(pvalue)):
            add += pvalue[i]

        # 绘制饼图
        matplotlib.rc("font", family='AR PL UKai CN')
        # plt.figure(figsize=(9.63, 9.63))
        plt.figure(figsize=(4.31, 3.81))
        # plt.figure(figsize=(6.42, 6.42))
        percentage = self.count_percentage(self.defect)
        labels = ['裂纹', '夹杂', '斑块', '麻点', '磨花', '划痕']
        sizes = percentage

        matplotlib.rc("font", family='AR PL UKai CN')
        # 数据
        data = self.defect
        # 类别名称
        categories = ['裂纹', '夹杂', '斑块', '麻点', '磨花', '划痕']
        fig, ax = plt.subplots(figsize=(4.31, 3.81))
        plt.title('缺陷数量扇形图')  # 图像的名称
        ax.pie(data, labels=categories, autopct='%1.1f%%')
        ax.axis('equal')
        ax.legend(title='图例', loc='center left', bbox_to_anchor=(1.2, 0.5))

        plt.savefig(save_road + 'pi.png')  # 保存图像，dpi可以调整图像的像素大小

        self.label.setPixmap(QPixmap(save_road + 'histogram.png'))
        self.label_2.setPixmap(QPixmap(save_road + 'pi.png'))

        self.textEdit.append('<font color=black size=4>' + '在本项目的全部输入图像中,共检测到: ' + '</font>' +
                             '<font color=red size=4>' + str(add) + '</font>' + '<font color=black size=4>' + ' 个缺陷, 其中:' + '</font>')
        for i in range(len(pvalue)):
            self.textEdit.append('<font color=blue size=4>' + labels[i] + '</font>' + '  ' + '<font color=red size=4>'
                             + str(pvalue[i]) + '</font>' + '<font color=blue size=4>' + ' 个,         占比 ' + '</font>'
                             + '<font color=red size=4>' + str(round(percentage[i] * 100, 1)) + '%' + '</font>')


    def count_num_of_type(self, name):
        list = self.helper.get_num_of_every_type(name)

        self.defect = [0, 0, 0, 0, 0, 0]  # 第0-5种缺陷 和 没有缺陷的金属数量

        for i in range(len(list)):
            for j in range(2, len(list[0]), 3):
                if list[i][j] != 'NULL':
                    if list[i][j] == '裂纹':
                        self.defect[0] += 1
                    elif list[i][j] == '夹杂':
                        self.defect[1] += 1
                    elif list[i][j] == '斑块':
                        self.defect[2] += 1
                    elif list[i][j] == '麻点':
                        self.defect[3] += 1
                    elif list[i][j] == '磨花':
                        self.defect[4] += 1
                    elif list[i][j] == '划痕':
                        self.defect[5] += 1
        return self.defect

    def count_percentage(self, defect_num):
        add = 0
        percentage = []
        for i in range(len(defect_num)):
            add += defect_num[i]
        for i in range(len(defect_num)):
            percentage.append(round(defect_num[i]/add, 3))          # 保留三位小数

        return percentage


    def get_scatter_data(self):
        list = self.helper.get_num_of_every_type(self.name)
        mid_x = []
        mid_y = []
        t = 0
        for i in range(len(list)):
            for j in range(3, len(list[0]), 3):
                if list[i][j] != 'NULL':
                    # result_x.append(list[i][j].split('(')[1][:-3])
                    # result_y.append(list[i][j].split('(')[2][:-1])

                    x = list[i][j].split('(')[1][:-3]
                    y = list[i][j].split('(')[2][:-1]

                    mid_x.append(round(float((y.split(',')[0])) - float((x.split(',')[0])), 3))
                    mid_y.append(round(float((y.split(',')[1])) - float((x.split(',')[1])), 3))
        result = []
        result.append(mid_x)
        result.append(mid_y)
        return result


