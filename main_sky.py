#coding=utf-

# import test
from PyQt5 import QtCore, QtGui, QtWidgets
# from PyQt5.QtCore import QObject, pyqtSignal
# from PyQt5.QtCore import QThread
# from PyQt5.QtWidgets import QApplication, QMainWindow
# from test import Ui_MainWindow
import subprocess


from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import os
import re
import sys
# import urllib2


# 產生虛擬 borwser：
driver = webdriver.PhantomJS(executable_path='/usr/local/Cellar/phantomjs/2.1.1/bin/phantomjs')

class DownloadThread(QtCore.QThread):

    data_downloaded = QtCore.pyqtSignal(object)

    def __init__(self, url):
        QtCore.QThread.__init__(self)
        self.url = url
        self.count = 0

    def run(self):
        # info = urllib2.urlopen(self.url).info()
        # self.data_downloaded.emit('%s\n%s' % (self.url, info))
        # 用beautifulsoup去擷取資訊
        page1 = driver.get(self.url)
        soup1 = BeautifulSoup(driver.page_source,"html.parser" )
        pat2 = re.compile('https://avgle.com/video/[0-9]*')
        filename = pat2.search(self.url).group().split('https://avgle.com/video/')[1]

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

        # 找到影片總共被切割成幾部分：
        split_1= data_[-1].split('.mp4/')
        split_2= split_1[1].split('seg-')
        split_3= split_2[1].split('-')
        all_parts= float(split_3[0])
        # 轉換成 每一part 佔多少百分比：
        all_parts_persent1=  float(100/(3*all_parts))
        all_parts_persent= round(all_parts_persent1,2)

        # print('data_[-1]:{}'.format(data_[-1]))
        # print('split_1:{}'.format(split_1))
        # print('split_2:{}'.format(split_2))
        # print('split_3:{}'.format(split_3))
        # print('all_parts:{}'.format(all_parts))
        # print('all_parts_persent1:{}'.format(all_parts_persent1))

        print ("{}%".format(all_parts_persent))
        print('{}.mp4'.format(filename))

        # 若已有相同檔名檔案，刪除之：
        currentpath = os.getcwd()
        if os.path.isfile(currentpath + '/{}.mp4'.format(filename)):
            os.remove(currentpath + '/{}.mp4'.format(filename))
            print('clear file !')
            self.data_downloaded.emit(0)
        else:
            pass

        # 轉 .mp4檔
        p = subprocess.Popen(['ffmpeg', '-i', dataurl, '-c', 'copy', '{}.mp4'.format(filename)], stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, universal_newlines=True)


        if p.stdout is not None:
            #self.count = 0
            while True:
                line = p.stdout.readline()
                #print ('line :{}'.format(line))
                if not line: break
            # for line in p.stdout:
                if 'frame' in str(line):
                    self.count = self.count + all_parts_persent
                    print(self.count)
                    # print(line)
                    #self.progressbar_button()
                    #self.work.progressUpdated.connect(self.pro)
                    # self.work.progressUpdated.emit(self.count)
                    self.data_downloaded.emit(self.count)




        else:
            print("error")

        # 刪除 m3u8檔：
        try:
            os.remove(currentpath + '/torrent.m3u8')
            print('clear !')
            self.data_downloaded.emit(100)
            # self.progress= self.progressBar.setValue(100)
        except:
            print('Empty file !')
    # def run(self):
    #     info = urllib2.urlopen(self.url).info()
    #     self.data_downloaded.emit('%s\n%s' % (self.url, info))

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.list_widget = QtWidgets.QListWidget()
        self.progressBar = QtWidgets.QProgressBar()
        self.button = QtWidgets.QPushButton("Start")
        self.button.clicked.connect(self.start_download)
        self.lineEdit = QtWidgets.QLineEdit()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.lineEdit)
        layout.addWidget(self.button)
        layout.addWidget(self.progressBar)
        # layout.addWidget(self.list_widget)
        self.setLayout(layout)

    def start_download(self):
        urls = [self.lineEdit.text()]
        # urls = ['http://google.com', 'http://twitter.com', 'http://yandex.ru',
        #         'http://stackoverflow.com/', 'http://www.youtube.com/']
        self.threads = []
        for url in urls:
            downloader = DownloadThread(url)
            downloader.data_downloaded.connect(self.on_data_ready)
            self.threads.append(downloader)
            downloader.start()

    def on_data_ready(self, data):
        # print data
        # self.list_widget.addItem(unicode(data))
        self.progressBar.setValue(data)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.resize(640, 480)
    window.show()
    sys.exit(app.exec_())



# class superr(QMainWindow,Ui_MainWindow,QThread):


#     def __init__(self):
#         super(superr, self).__init__()
#         self.setupUi(self)
#         self.progressBar.setValue(0)
#         self.pushButton.clicked.connect(self.go_button)
#         self.count = 0

#         self.work = WorkerThread()
#         self.work.progressUpdated.connect(self.progressbar_button)

#     def go_button(self):
#         # 輸入網址：
#         self.url= self.lineEdit.text()
#         pat2 = re.compile('https://avgle.com/video/[0-9]*')
#         self.filename = pat2.search(self.url).group().split('https://avgle.com/video/')[1]
#         if self.url =="":
#             print ('ERROR\n')
#         else:
#             #print (self.url)
#             self.info()
#         #self.pushButton.clicked.connect(MainWindow.close)


#     def info(self):

#         # 用beautifulsoup去擷取資訊
#         page1 = driver.get(self.url)
#         soup1 = BeautifulSoup(driver.page_source,"html.parser" )

#         # 去找尋 tag:source 下的 src
#         videopath = soup1.find("source").get('src')

#         # 下載 m3u8檔：
#         file = requests.get(videopath)
#         with open("torrent.m3u8", 'wb') as f:
#             f.write(file.content)
#         print(f)
#         self.download()


#     def download(self):
#         # 開啟下載的文字檔 找到要的網址資訊：
#         pat = re.compile('.*.mp4')
#         filescript = []
#         with open('torrent.m3u8', 'r') as f:
#             data = f.readlines()
#         data_ = [i for i in data if pat.search(i) != None]
#         data = data_[0].split('.mp4')[0]
#         dataurl = data + '.m3u8'

#         # 找到影片總共被切割成幾部分：
#         split_1= data_[-1].split('.mp4/')
#         split_2= split_1[1].split('seg-')
#         split_3= split_2[1].split('-')
#         all_parts= int(split_3[0])
#         # 轉換成 每一part 佔多少百分比：
#         all_parts_persent1=  float(1/(2*all_parts))*100
#         all_parts_persent= round(all_parts_persent1,2)

#         print ("{}%".format(all_parts_persent))

#         # 轉 .mp4檔
#         p = subprocess.Popen(['ffmpeg', '-i', dataurl, '-c', 'copy', '{}.mp4'.format(self.filename)], stdout=subprocess.PIPE,
#                              stderr=subprocess.STDOUT, universal_newlines=True)

#         # 若已有相同檔名檔案，刪除之：
#         currentpath = os.getcwd()
#         if os.path.isfile(currentpath + '/{}.mp4'.format(self.filename)):
#             os.remove(currentpath + '/{}.mp4'.format(self.filename))
#             print('clear file !')
#         else:
#             pass


#         if p.stdout is not None:
#             #self.count = 0
#             for line in p.stdout:
#                 if 'frame' in str(line):
#                     print(self.count)
#                     #self.progressbar_button()
#                     self.count = self.count + all_parts_persent
#                     #self.work.progressUpdated.connect(self.pro)
#                     self.work.progressUpdated.emit(self.count)




#         else:
#             print("error")

#         # 刪除 m3u8檔：
#         try:
#             os.remove(currentpath + '/torrent.m3u8')
#             print('clear !')
#             self.progress= self.progressBar.setValue(100)
#         except:
#             print('Empty file !')


#     def start(self):
#         self.work.start()

#     def pro(self):
#         print('  Come to Pro ')
#         self.progressbar_button()

#     def progressbar_button(self):
#         print ('  Come to progressbar_button, var:{} '.format(self.count))
#         self.progress = self.progressBar.setValue(self.count)






# class WorkerThread(QThread):
#     progressUpdated = pyqtSignal(int)

#     def __init__(self,parent= None):
#         QThread.__init__(self, parent)

#     # def run(self):
#     #     self.progressUpdated.emit()
#     #     #self.w.progressbar_button()
#     #     print ('run  ~~  ~~~  ~~~~~')





# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     MainWindow = QMainWindow()
#     ui = superr()
#     ui.show()
#     sys.exit(app.exec_())


