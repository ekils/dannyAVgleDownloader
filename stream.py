#coding=utf-8


from bs4 import BeautifulSoup
from pip._vendor.distlib.compat import raw_input
from selenium import webdriver
import requests
import os
import re

# 產生虛擬 borwser：
driver = webdriver.PhantomJS(executable_path='/usr/local/Cellar/phantomjs/2.1.1/bin/phantomjs')

# 輸入網址：
url= raw_input('Paste website adress:\n')
pat2= re.compile('https://avgle.com/video/[0-9]*')
filename= pat2.search(url).group().split('https://avgle.com/video/')[1]


# 用beautifulsoup去擷取資訊
page1= driver.get(url)
soup1 = BeautifulSoup(driver.page_source, "lxml")

# 去找尋 tag:source 下的 src
videopath = soup1.find("source").get('src')

# 下載 m3u8檔：
file = requests.get(videopath )
with open("torrent.m3u8", 'wb') as f:
    f.write(file.content)

print (f)

# 開啟下載的文字檔 找到要的網址資訊：
pat= re.compile('.*.mp4')
filescript= []
with open('torrent.m3u8','r') as f:
    data= f.readlines()
data= [i for i in data if pat.search(i)!=None]
data = data[0].split('.mp4')[0]
dataurl= data+'.m3u8'



# 轉 .mp4檔
os.system("ffmpeg -i  {}   -c copy {}.mp4".format(dataurl,filename ))



# 刪除 m3u8檔：
currentpath= os.getcwd()
try:
    os.remove(currentpath+'/torrent.m3u8')
    print ('clear !')
except:
    print ('Empty file !')