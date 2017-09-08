#coding=utf-

from PyQt5 import QtWidgets
from PyQt5.QtCore import  pyqtSignal
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QMainWindow,QMessageBox
from test import Ui_MainWindow
import subprocess

from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import os
import re
import sys



# 產生虛擬 borwser：
driver = webdriver.PhantomJS(executable_path='/usr/local/Cellar/phantomjs/2.1.1/bin/phantomjs')


class DoneWindow(QtWidgets.QWidget):
    def __init__(self):
        super(DoneWindow, self).__init__()

    def msg(self):
        msgbox= QMessageBox.information(self,'提示',"下載完成",QMessageBox.Ok | QMessageBox.Cancel)
        if msgbox==QMessageBox.Ok:
            answer = 'ok'
        else:
            answer = 'cancle'
        return answer


class WaringWindow(QtWidgets.QWidget):
    def __init__(self):
        super(WaringWindow, self).__init__()
    def warning(self):
        QMessageBox.warning(self,'warning',"ERROR_ blank URL.",QMessageBox.Ok )

    def warning2(self):
        QMessageBox.warning(self,'warning',"Wrong URL, make sure again.",QMessageBox.Ok)




class PyMainWindow(QMainWindow,Ui_MainWindow):

    def __init__(self):
        super(PyMainWindow, self).__init__()
        self.setupUi(self)
        self.progressBar.setValue(0)
        self.pushButton.clicked.connect(self.go_button)
        self.lcdNumber_2.display(0)   # 總秒數
        self.lcdNumber.display(0)      # 浮動秒數

    def go_button(self):
        qq= WaringWindow()
        urls= [self.lineEdit.text()]

        pat5 = re.compile('https://avgle.com/video/[0-9]*')

        if urls[0]=="":
            qq.warning()

        elif pat5.search(urls[0]) == None :
            qq.warning2()

        else:
            self.pushButton.setText("Downloading...")
            self.threads= []
            only_count_for_all_number= 0
            for url in urls :
                downloader= WorkerThread(url)
                downloader.data_downloaded.connect(self.send_signal)
                self.threads.append(downloader)
                downloader.start()

    def set_all_number(self,data):
        self.lcdNumber_2.display(data)


    def send_signal(self,data): # data 對應的是emit裡所有的參數 下面再由if來判斷
        if data.idx == 0:
            self.lcdNumber_2.display(data.allnumber)

        if data.idx == 1:
            self.lcdNumber.display(data.count_second)
            progress_percent= round((data.count_second/data.allnumber)*100,1)
            print ('persent: {}% '.format(progress_percent))
            self.progressBar.setValue(progress_percent)

            if progress_percent == 100:
                done= DoneWindow()
                if done.msg()=='ok':
                    print('OK')
                    self.reset()
                    self.pushButton.setText("GO")
                else:
                    print('CANCLE')
                    self.pushButton.setText("GO")

    def reset(self):
        print ('RESET')
        self.progressBar.setValue(0)
        self.lcdNumber.display(0)
        self.lcdNumber_2.display(0)
        self.lineEdit.clear()



class WariningThread(QThread):

    def __init__(self,url):
        QThread.__init__(self)
        self.url=url





class WorkerThread(QThread):
    data_downloaded = pyqtSignal(object)

    def __init__(self,url):  #  pyqtSignal(object) 的object 會傳給初始化的url
        QThread.__init__(self)
        self.url=url
        self.count = 0
        self.count_second = 0
    def run(self):

        # 用beautifulsoup去擷取資訊
        driver.get(self.url)
        soup1 = BeautifulSoup(driver.page_source, "html.parser")
        pat2 = re.compile('https://avgle.com/video/[0-9]*')

        self.filename = pat2.search(self.url).group().split('https://avgle.com/video/')[1]

        # 去找尋 tag:source 下的 src
        videopath = soup1.find("source").get('src')
        # 下載 m3u8檔：
        file = requests.get(videopath)
        with open("torrent.m3u8", 'wb') as f:
            f.write(file.content)
        print(f)

        # 開啟下載的文字檔 找到要的網址資訊：
        pat = re.compile('.*.mp4')
        filescript = []
        with open('torrent.m3u8', 'r') as f:
            data = f.readlines()
        data_ = [i for i in data if pat.search(i) != None]
        data = data_[0].split('.mp4')[0]
        dataurl = data + '.m3u8'



        # 若已有相同檔名檔案，刪除之：
        currentpath = os.getcwd()
        if os.path.isfile(currentpath + '/{}.mp4'.format(self.filename)):
            os.remove(currentpath + '/{}.mp4'.format(self.filename))
            print('clear old file !')
        else:
            pass

        # 轉 .mp4檔
        p = subprocess.Popen(['ffmpeg', '-i', dataurl, '-c', 'copy', '{}.mp4'.format(self.filename)], stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, universal_newlines=True)

        pat3 = re.compile('Duration: [0-9]*:[0-9]*:[0-9]*')

        if p.stdout is not None:
            while True:
                line =p.stdout.readline()
                if not line:
                    break
                try:
                    pat3_list= pat3.search(str(line)).group().split(':')
                    allnumber =int(pat3_list[1])*60*60 + int(pat3_list[2])*60 + int(pat3_list[3])

                    self.idx = 0
                    self.allnumber = allnumber
                    self.data_downloaded.emit(self)  # 直接丟 self 就是整個def的參數都丟過去給connect去對應
                except:
                    pass
                pat4= re.compile('[0-9]*:[0-9]*:[0-9]*')
                if 'frame' in str(line):
                    # self.count= self.count + all_parts_persent
                    pat4_list= pat4.search(str(line)).group().split(':')
                    count_number= int(pat4_list[0])*60*60 + int(pat4_list[1])*60 + int(pat4_list[2])
                    self.count_second= count_number
                    print('Total second: {} sec '.format(self.count_second))


                    self.idx = 1
                    self.data_downloaded.emit(self)  # emit出來的值會在connect那邊接收 ,所以connect裡面要放的容器 就是要去承接emit出來的值
                else:
                    pass

        else:
            print("error")

        # 刪除 m3u8檔：
        try:
            os.remove(currentpath + '/torrent.m3u8')
            print('clear !')
            # self.count= 100
            # self.data_downloaded.emit(self)
        except:
            print('Empty file !')

        self.terminate()   # 關閉 thread











if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = PyMainWindow()
    ui.show()
    sys.exit(app.exec_())