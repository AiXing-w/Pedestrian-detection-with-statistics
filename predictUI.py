from MainWindow import Ui_MainWindow
from CountWindow import Ui_Form
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QGraphicsScene, QGraphicsPixmapItem, QFileDialog
from PyQt5.QtGui import QImage, QPixmap
import sys
import os
import datetime
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from centernet import CenterNet
from DataServer import SaveData, FormetDayTime
import matplotlib.pyplot as plt

centernet = CenterNet()


class countWindow(QWidget, Ui_Form):
    def __init__(self, form):
        self.form = form
        now = datetime.datetime.now()
        time = now.strftime("%Y %m %d %H %M %S")
        timelist = time.split(" ")
        self.year = timelist[0]
        self.mon = timelist[1]
        self.day = timelist[2]
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(lambda: self.plt_plot(0))
        self.pushButton_2.clicked.connect(lambda: self.plt_plot(1))
        self.dateEdit.setDate(now)
        self.plot = False

    def plt_plot(self, opt):
        cntlist = []
        datelist = []
        # timelist = []

        if self.form == 2:
            with open(os.path.join("dayLogs", str(self.year)+"-"+str(self.mon)+"-"+str(self.day)+".txt")) as f:
                for line in f.readlines():
                    cnt, date = line.split()
                    cnt = int(float(cnt))
                    cntlist.append(cnt)
                    h, m = date.split(":")
                    datelist.append(float(h) + float(m) / 100)
        elif self.form == 1:
            cntlist = [0 for i in range(31)]
            for date in os.listdir("dayLogs"):
                print(date)
                year, mon, day = date.split("-")
                day,_ = day.split(".")
                if self.year == year and self.mon == mon:
                    with open(os.path.join("dayLogs", date), 'r') as f:
                        for line in f.readlines():
                            cnt, _ = line.split()
                            print(day, ":", len(cntlist))
                            cntlist[int(day)-1] += int(float(cnt))
            datelist = range(1, 32)

        elif self.form == 0:
            cntlist = [0 for i in range(12)]
            for date in os.listdir("dayLogs"):
                print(date)
                year, mon, _ = date.split("-")
                if self.year == year:
                    with open(os.path.join("dayLogs", date), 'r') as f:
                        for line in f.readlines():
                            cnt, _ = line.split()
                            cntlist[int(mon) - 1] += int(float(cnt))
            datelist = range(1, 13)

        if opt == 0:
            plt.rcParams['font.sans-serif'] = ['SimHei']
            plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
            plt.plot(np.array(datelist), np.array(cntlist), label="人流量变化")
            if self.form == 2:
                plt.xticks(range(0, 24), range(0, 24))
            elif self.form == 1:
                plt.xticks(range(0, 31), range(0, 31))
            elif self.form == 0:
                plt.xticks(range(0, 12), range(0, 12))
            plt.title("人流量统计")
            if self.form == 2:
                plt.xlabel("小时")
            elif self.form == 1:
                plt.xlabel("天")
            elif self.form == 0:
                plt.xlabel("月")
            plt.ylabel("人流量")
            plt.legend()
            # plt.savefig("tmp")
            plt.show()
        elif opt == 1:
            plt.rcParams['font.sans-serif'] = ['SimHei']
            plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
            plt.bar(np.array(datelist), np.array(cntlist), label="人流量变化")
            if self.form == 2:
                plt.xticks(range(0, 24), range(0, 24))
            elif self.form == 1:
                plt.xticks(range(0, 31), range(0, 31))
            elif self.form == 0:
                plt.xticks(range(0, 12), range(0, 12))
            plt.title("人流量统计")
            if self.form == 2:
                plt.xlabel("小时")
            elif self.form == 1:
                plt.xlabel("天")
            elif self.form == 0:
                plt.xlabel("月")
            plt.ylabel("人流量")
            # plt.savefig("tmp")
            plt.legend()
            plt.show()


class predictWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        img_src = cv2.imread("timg.jpg")  # 读取图像
        img_src = cv2.cvtColor(img_src, cv2.COLOR_BGR2RGB)  # 转换图像通道
        label_width = self.label.width()
        label_height = self.label.height()
        temp_imgSrc = QImage(img_src[:], img_src.shape[1], img_src.shape[0], img_src.shape[1] * 3, QImage.Format_RGB888)
        # 将图片转换为QPixmap方便显示
        self.pixmap_imgSrc = QPixmap.fromImage(temp_imgSrc).scaled(label_width, label_height)
        now = datetime.datetime.now()
        time = now.strftime("%Y %m %d %H %M %S")
        timelist = time.split(" ")
        self.mon = int(timelist[1])
        self.isOn = False
        self.videoOn = False
        self.day, self.time = FormetDayTime(timelist)
        self.label.setPixmap(QPixmap(self.pixmap_imgSrc))
        self.pushButton.clicked.connect(lambda: self.CountWindow(2))
        self.pushButton_2.clicked.connect(lambda: self.CountWindow(1))
        self.pushButton_3.clicked.connect(lambda: self.CountWindow(0))
        self.pushButton_4.clicked.connect(self.On_Off)
        self.pushButton_5.clicked.connect(self.videoDetection)

    def videoDetection(self):
        self.videoOn = ~self.videoOn
        if not self.videoOn:
            self.pushButton_5.setText("视频检测")
        else:
            self.pushButton_5.setText("视频检测结束")
        
        if self.videoOn:
            path, ftype = QFileDialog.getOpenFileName(self, "Open File")
            print(path)
            global centernet
            capture = cv2.VideoCapture(path)
            while capture.isOpened() and self.videoOn:
                # 读取某一帧
                ref, frame = capture.read()
                # 转变成Image
                frame = Image.fromarray(np.uint8(frame))
                # 进行检测
                frame, num = centernet.detect_image(frame)
                frame = np.array(frame)

                # RGBtoBGR满足opencv显示格式
                img_src = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                label_width = self.label.width()
                label_height = self.label.height()
                temp_imgSrc = QImage(img_src[:], img_src.shape[1], img_src.shape[0], img_src.shape[1] * 3,
                                     QImage.Format_RGB888)

                # 将图片转换为QPixmap方便显示
                pixmap_imgSrc = QPixmap.fromImage(temp_imgSrc).scaled(label_width, label_height)
                self.label.setPixmap(QPixmap(pixmap_imgSrc))

                if cv2.waitKey(0) & 0xFF == 27:
                    break

            capture.release()
            cv2.destroyAllWindows()
        else:
            self.label.setPixmap(QPixmap(self.pixmap_imgSrc))

    def CountWindow(self, opt):
        self.count = countWindow(opt)
        self.count.show()

    def On_Off(self):
        self.isOn = ~self.isOn
        if not self.isOn:
            self.pushButton_4.setText("开始")
        else:
            self.pushButton_4.setText("结束")
        if self.isOn:
            capture = cv2.VideoCapture(0)
            while True and self.isOn:
                # 获取当前时间
                global centernet
                now = datetime.datetime.now()
                time = now.strftime("%Y %m %d %H %M %S")
                timelist = time.split(" ")
                self.day, self.time = FormetDayTime(timelist)

                # 读取某一帧
                ref, frame = capture.read()
                # 转变成Image
                frame = Image.fromarray(np.uint8(frame))
                # 进行检测
                frame, num = centernet.detect_image(frame)

                # 设置
                draw = ImageDraw.Draw(frame)
                fontStyle = ImageFont.truetype(
                 font="model_data/simhei.ttf", size=30, encoding='utf-8')

                # 绘制框和文本
                draw.rectangle(
                    [tuple((0, 0)), tuple((180, 40))],
                    fill=(255, 255, 255), outline='black')
                draw.rectangle(
                    [tuple((181, 0)), tuple((601, 40))],
                    fill=(255, 255, 255), outline='black')
                draw.text((0, 0), "总人数:" + str(num), (0, 0, 0), font=fontStyle)
                draw.text((200, 0), "时间:" + self.day + " " + self.time, (0, 0, 0), font=fontStyle)

                frame = np.array(frame)

                # RGBtoBGR满足opencv显示格式
                img_src = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                label_width = self.label.width()
                label_height = self.label.height()
                temp_imgSrc = QImage(img_src[:], img_src.shape[1], img_src.shape[0], img_src.shape[1] * 3,
                                     QImage.Format_RGB888)

                # 将图片转换为QPixmap方便显示
                pixmap_imgSrc = QPixmap.fromImage(temp_imgSrc).scaled(label_width, label_height)
                self.label.setPixmap(QPixmap(pixmap_imgSrc))

                if int(timelist[4]) % 5 == 0 and int(timelist[5]) == 0:
                    # 每隔五分钟保存一次
                    SaveData(self.day, self.time, num)
                c = cv2.waitKey(0) & 0xff

                if c == 27:
                    capture.release()
                    break
            capture.release()
            cv2.destroyAllWindows()
        else:
            self.label.setPixmap(QPixmap(self.pixmap_imgSrc))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = predictWindow()
    window.show()
    sys.exit(app.exec_())
