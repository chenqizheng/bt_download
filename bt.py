#coding=utf-8
#!/usr/bin/env python
#-*- coding:utf-8 -*-
import urllib,HTMLParser
import urllib2
import cookielib
import json
import re
from StringIO import StringIO
import gzip
import sys
from HTMLParser import HTMLParser
class BT_Download:
    def __init__(self):
        cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(self.opener)
        self.opener.addheaders = [('User-agent', 'IE'),
                                  ('Host','bt.orzx.im'),
                                  ('Cache-Control','no-cache'),
                                  ('Accept-Language','zh-CN,zh;q=0.8,ja;q=0.6,en;q=0.4')]
    
    def request(self,url):
        req = urllib2.Request(url)
        try:
            fd = self.opener.open(req)
        except Exception, e:
            print(u'网络连接错误！')
        #buf = StringIO( fd.read())
        #f = gzip.GzipFile(fileobj=buf)
        data = fd.read()
        fd.close()
        return data

    def getArticleList(self,boradId,page):
        url = 'http://bt.orzx.im/list.php?BoardID='+str(boradId)+'&Page=' + str(page)
        return self.request(url)

    def getArticleDetail(self,url):
        url = url.replace("display", "view");
        url = 'http://bt.orzx.im/' + url
        #print url
        return self.request(url)
        

class ArticleListParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []
    def reset(self):
        HTMLParser.reset(self)
    def handle_starttag(self, tag, attrs):
        # 这里重新定义了处理开始标签的函数
        if tag == 'a':
            # 判断标签<a>的属性
            for name,value in attrs:
                if name == 'href' and value.find('display.php')<>-1 and value not in self.links:
                    self.links.append(value)

class ArticleDetailParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.article = Article("","")
        

    def handle_starttag(self,tag,attrs):
        if tag == 'meta':
            #判断meta标签
            isName = False
            for name,value in attrs:
                if name == 'name' and value == 'keywords':
                    isName = True
                if isName and name == 'content' :
                    self.article.name = value
                
                    
                    

class Article():
    def __init__(self,name,hashcode):
        self.name = name
        self.hashcode=hashcode
                    
def writeFile(filepath,content):
    file_obj = open(filepath,'a')
    try:
        file_obj_content = file_obj.write(content)
    finally:
        file_obj.close()

if __name__ == '__main__':  
    l = BT_Download()
    boradId = 1
    page = 1
    if len(sys.argv) >=3 :
        boradId = sys.argv[1]
        page = sys.argv[2]
    content = l.getArticleList(boradId,page)
    #print content
    bParser = ArticleListParser()
    bParser.feed(content)
    bParser.close()
    links = bParser.links
    for link in links :
        try:
            detailContent = l.getArticleDetail(link)
            aParser = ArticleDetailParser()
            print link
            aParser.feed(detailContent)
            aParser.close()
            #print aParser.article.name
            index = aParser.article.name.find(',')
            index1 = aParser.article.name.find('哈希校验：')
            if index == -1 or index1 == -1:
                pass
            writeFile('bt_'+ str(boradId) + '_' + str(page) +'.txt',aParser.article.name[:index].replace('种子名称：',"") + "∆")
            writeFile('bt_'+ str(boradId) + '_' + str(page) +'.txt',aParser.article.name[index1:].replace('哈希校验：','magnet:?xt=urn:btih:') + "\n")
        except Exception , e:
            print '编码错误'
            print link
            pass
    print 'finish'

        
    
