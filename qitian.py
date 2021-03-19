#!/usr/bin/env python3
# coding=utf-8
# author:sakuyo
#----------------------------------
import requests,sys
import time
from bs4 import BeautifulSoup
from selenium import webdriver

class downloader(object):
    def __init__(self,target):#初始化
        self.target = target
        self.chapterNames = []
        self.chapterHrefs = []
        self.chapterNum = 0
        self.session = requests.Session()
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        self.browser = webdriver.Chrome(chrome_options=options)
    def GetChapterInfo(self):#獲取章節名稱和連結
        # req = self.session.get(url=self.target)
        # req.raise_for_status()
        # req.encoding = req.apparent_encoding
        # html = req.text
        self.browser.get(self.target)
        html = self.browser.page_source
        bf = BeautifulSoup(html,"html.parser")
        catalogDiv = bf.find('div',class_='catalog-content-wrap',id='j-catalogWrap')
        print("catalogDiv: ", catalogDiv)
        volumeWrapDiv = catalogDiv.find('div',class_='volume-wrap')
        volumeDivs = volumeWrapDiv.find_all('div',class_='volume')

        for volumeDiv in volumeDivs:
            aList = volumeDiv.find_all('a')
            for a in aList:
                chapterName = a.string
                chapterHref = a.get('href')
                self.chapterNames.append(chapterName)
                self.chapterHrefs.append('https:'+chapterHref)
            self.chapterNum += len(aList)
    def GetChapterContent(self,chapterHref):#獲取章節內容
        req = self.session.get(url=chapterHref)
        req.raise_for_status()
        req.encoding = req.apparent_encoding
        html = req.text
        bf = BeautifulSoup(html,"html.parser")
        mainTextWrapDiv = bf.find('div',class_='main-text-wrap')
        readContentDiv = mainTextWrapDiv.find('div',class_='read-content j_readContent')
        readContent = readContentDiv.find_all('span',class_='content-wrap')
        if readContent == []:
            textContent = readContentDiv.text.replace('<p>','\n')
            textContent = textContent.replace('</p>','')
        else:
            for content in readContent:
                if content.string == '':
                    print('error format')
                else:
                    textContent += content.string + '\n'
        return textContent
    def writer(self, path, name='', content=''):
        write_flag = True
        with open(path, 'a', 1024) as f: #a模式意為向同名檔案尾增加文字
            if name == None:
                name=''
            if content == None:
                content = ''
            f.write(name + '\n')
            f.write(content)
            f.write('\n')

if __name__ == '__main__':#執行層
    target = 'https://book.qidian.com/info/1010868264#Catalog'
    dlObj = downloader(target)
    dlObj.GetChapterInfo()
    print('開始下載：')
    for i in range(dlObj.chapterNum):
        try:
            dlObj.writer( 'test.txt',dlObj.chapterNames[i], dlObj.GetChapterContent(dlObj.chapterHrefs[i]))
        except Exception:
            print('下載出錯，已跳過')
            pass
        sys.stdout.write("  已下載:%.3f%%" %  float(i/dlObj.chapterNum) + '\r')
        sys.stdout.flush()
    print('下載完成')
