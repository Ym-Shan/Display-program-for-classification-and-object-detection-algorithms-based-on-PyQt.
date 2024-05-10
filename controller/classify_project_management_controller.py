import os
import threading
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
from view_py.classify_project_management import Ui_MainWindow
from PyQt5.QtGui import QPixmap
from model.classify_project_management_helper import classify_project_management_helper
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import *
from controller.MainWindow_controller import MainWindow as main
import shutil


class MainWindow(Ui_MainWindow):
    FATHER = ''             # 用来调用前一个页面的方法

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.tableWidget.resizeColumnToContents(True)
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # 不可修改
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)  # 整行选中
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)             # 使窗口始终在顶层
        self.toolBar.addAction(QtGui.QIcon('../res/新建文件.png'), '新增项目')
        self.toolBar.addAction(QtGui.QIcon('../res/删除.png'), '删除项目')
        self.toolBar.addAction(QtGui.QIcon('../res/编辑.png'), '修改项目名字')
        self.toolBar.addAction(QtGui.QIcon('../res/导出.png'), '结果导出')
        self.toolBar.addAction(QtGui.QIcon('../res/可视化分析.png'), '可视化分析')
        self.setWindowTitle('项目管理')

        self.helper = classify_project_management_helper()
        self.flash_table()


        self.toolBar.actionTriggered[QtWidgets.QAction].connect(self.getvalue)          # 工具栏的监听
        self.center()           # 将窗口移动到屏幕正中央



    def flash_table(self):
        self.tableWidget.clear()
        row = self.helper.get_row()  # 获取行数
        result = self.helper.get_all_project_data()  # 获取列表

        self.tableWidget.setRowCount(row)  # 设置行数
        self.tableWidget.setColumnCount(4)  # 设置列数
        self.tableWidget.setHorizontalHeaderLabels(['项目名字', '拥有图片数量', '创建时间', '最后修改时间'])
        for i in range(row):
            for j in range(4):
                data = QTableWidgetItem(str(result[i][j]))
                self.tableWidget.setItem(i, j, data)

    def center(self):       # 将窗口显示在屏幕正中间
        # 获取屏幕的尺寸信息
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口的尺寸信息
        size = self.geometry()
        # 将窗口移动到指定位置
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)


    def getvalue(self, m):
        message = m.text()

        if message == '新增项目':
            self.net_project()
        elif message == '删除项目':
            self.delete_project()
        elif message == '修改项目名字':
            self.change_project_name()
        elif message == '结果导出':
            self.out_result()
        elif message == '可视化分析':
            self.view_analyse()

    def net_project(self):
        self.close()
        self.FATHER.getname()           # 调用生成这个页面的页面的getname()方法


    def center_layout(self, object):
        # 获取屏幕的尺寸信息
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口的尺寸信息
        size = object.geometry()
        # 将窗口移动到指定位置
        object.move((screen.width() - size.width()) / 2 + 200, (screen.height() - size.height()) / 2 + 200)       # +200是因为对话框窗口会随着文字的大小而改变,默认大小大概是967x578,但在它缩小后仍检测到大小是这么大


    def delete_project(self):
        if self.tableWidget.selectedItems():
            title = self.tableWidget.selectedItems()[0].text()
            self.helper.delete_tabel(title)
            self.helper.delete_notes_in_project(title)
            shutil.rmtree('../classify_data_out/' + title)  # 删除默认的结果文件夹

            # 一个对话框
            q_message = QMessageBox()
            q_message.setIcon(QtWidgets.QMessageBox.Information)
            self.center_layout(q_message)
            q_message.setWindowTitle('提示')
            q_message.setText('项目 ' + title + ' 已删除')
            q_message.exec_()
            self.flash_table()

    def change_project_name(self):
        if self.tableWidget.selectedItems():
            title = self.tableWidget.selectedItems()[0].text()
            name, ok = QInputDialog.getText(self, "请输入新项目名", "为项目 " + title + " 设定一个新项目名.", QtWidgets.QLineEdit.Normal, '')
            if name and ok:
                self.helper.set_new_project_name(title, name)
                self.helper.set_new_table_name(title, name)
                # 修改本地文件夹的名字
                os.rename('../classify_data_out/' + title, '../classify_data_out/' + name)
                self.flash_table()

                # 一个对话框
                q_message = QMessageBox()
                q_message.setIcon(QtWidgets.QMessageBox.Information)
                self.center_layout(q_message)
                q_message.setWindowTitle('提示')
                q_message.setText('项目 ' + title + ' 的名字已修改为 ' + name)
                q_message.exec_()


    def out_result(self):
        if self.tableWidget.selectedItems():
            name = self.tableWidget.selectedItems()[0].text()
            dir = QFileDialog.getExistingDirectory(None, '清选择要将检测结果保存到哪个文件夹下', os.getcwd())
            if dir:
                # with open('../cache/detect_name.py', 'r+') as f:
                #     name = f.read()
                if os.path.exists(dir + '/' + name):
                    shutil.rmtree(dir + '/' + name)  # 删除默认的结果文件夹,从而避免目录名称变化
                    shutil.copytree('../classify_data_out/' + name + '/', dir + '/' + name)
                else:
                    shutil.copytree('../classify_data_out/' + name + '/', dir + '/' + name)

                # 一个对话框
                q_message = QMessageBox()
                q_message.setIcon(QtWidgets.QMessageBox.Information)
                self.center_layout(q_message)
                q_message.setWindowTitle('提示')
                q_message.setText('项目 ' + name + ' 已被导出到 ' + dir + '/' + name)
                q_message.exec_()



    def view_analyse(self):
        if self.tableWidget.selectedItems():
            title = self.tableWidget.selectedItems()[0].text()
            import classify_data_visualization_controller
            self.new_window = classify_data_visualization_controller.MainWindow(title)
            self.new_window.show()

