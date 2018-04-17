# /usr/env/bin python
# -*- coding:utf-8 -*-

import os;
import urllib2
import re;
import StringIO;
import gzip
import time
import random
import sqlite3
import traceback

from bs4 import BeautifulSoup

class HouseDB:
    createhouse='create table house (id interger primary key, estateid interger,total float,area float)'
    createestate='create table estate (id interger primary key, year interger,name text,trafic text,avasold float,recentsold float,recentrent float)'
    checkhouse='select *  from sqlite_master where type=\'table\' and name = \'house\''
    checkestate='select *  from sqlite_master where type=\'table\' and name = \'estate\''
    def __init__( self, dbname):
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()
        self.cursor.execute(HouseDB.checkhouse)
        values = self.cursor.fetchall()
        if len(values)<=0:
            self.cursor.execute(HouseDB.createhouse)
        self.cursor.execute(HouseDB.checkestate)
        values = self.cursor.fetchall()
        if len(values)<=0:
            self.cursor.execute(HouseDB.createestate)
            
    def inserthouse(self,id,estateid,total,area):
        sql='insert into house (id, estateid,total,area) values (%d,%d,%f,%f)'%(id,estateid,total,area)
        self.cursor.execute(sql)
        self.conn.commit()
        
    def insertestate(self,id,year,name,trafic,avasold,recentsold,recentrent):
        sql='insert into estate (id,name,year,trafic,avasold,recentsold,recentrent) values (%d,%d,\'%s\',\'%s\',%f,%f,%f)'%(id,year,name,trafic,avasold,recentsold,recentrent)
        self.cursor.execute(sql)
        self.conn.commit()
        
    def close(self):
        self.cursor.close()
        self.conn.close()
        
    def ishouseexist(self,id):
        sql='select * from house where id=%d'%id
        self.cursor.execute(sql)
        values = self.cursor.fetchall()
        if len(values)<=0:
            return 0
        else:
            return 1
        
    def isestateexist(self,id):
        sql='select * from estate where id=%d'%id
        self.cursor.execute(sql)
        values = self.cursor.fetchall()
        if len(values)<=0:
            return 0
        else:
            return 1
    def getestateinfo(self,id):
        sql='select avasold,recentsold,recentrent from house where id=%d'%id
        self.cursor.execute(sql)
        values = self.cursor.fetchall()
        return values[0],values[1],values[2]
    def getallestate(self):
        sql='select id,name,year,trafic,avasold,recentsold,recentrent from estate'
        self.cursor.execute(sql)
        values = self.cursor.fetchall()
        return values

houseDB = HouseDB('house.db')

def browseestate(estateid):
    link="https://bj.5i5j.com/xiaoqu/"+str(estateid)+".html"
    request = urllib2.Request(link)
    response = urllib2.urlopen(request)
    html = response.read()
    soup = BeautifulSoup(html)

    xqjpriceinfo = soup.find_all("div",{"class":"xqjprice"})
    #小区均价
    xqjprice = re.findall(r"\d+",str(xqjpriceinfo[0]));
    #二手房成交
    soldp = 0
    soldpcount = 0
    jqsoldp = 0
    leased = 0
    leasedcount =0
    jqleasedp=0
    cjinfoall = soup.find_all("ul",{"class":"yizucontent"})
    for cjinfo in cjinfoall:
        if str(cjinfo).find("sold") >= 0:
            #总价
            sp = cjinfo.find_all("li",{"class":"f5"})
            sp = re.findall(r"^(\d+)",sp[0].text.encode('utf8'))
            #面积
            sa = cjinfo.find_all("li",{"class":"f2"})
            sa = re.findall(r"^(\d+.*\d+)",sa[0].text.encode('utf8'))
            #日期
            sd = cjinfo.find_all("li",{"class":"f3"})
            #print(sp[0],sa[0],sd[0].text.encode('utf8'))
            soldp = soldp + float(sp[0])/float(sa[0])
            soldpcount += 1;
        elif str(cjinfo).find("leased") >= 0:
            #租金
            rp = cjinfo.find_all("li",{"class":"f5"})
            rp = re.findall(r"^(\d+)",rp[0].text.encode('utf8'))
            #面积
            ra = cjinfo.find_all("li",{"class":"f2"})
            ra = re.findall(r"^(\d+.*\d+)",ra[0].text.encode('utf8'))
            #日期
            rd = cjinfo.find_all("li",{"class":"f4"})
            #print(rp[0],ra[0],rd[0].text.encode('utf8'))
            leased = leased + float(rp[0])/float(ra[0])
            leasedcount += 1;
    #近期二手房成交均价
    if soldpcount > 0:
        jqsoldp = soldp/soldpcount*10000
    #近期租房成交均价
    if leasedcount > 0:
        jqleasedp = leased/leasedcount
    return (xqjprice[0],jqsoldp,jqleasedp)
    
def browsehouse( houseid ):
    link="https://bj.5i5j.com/ershoufang/"+houseid+".html"
    request = urllib2.Request(link)
    response = urllib2.urlopen(request)
    html = response.read()
    soup = BeautifulSoup(html)

    housesty = soup.find_all("div",class_="housesty")

    #总价，单价，面积
    jlinfo = re.findall(r"jlinfo\">(.*)<\/",str(housesty[0]))

    zushous = soup.find_all("div",class_="zushous")
    a=zushous[0].find("a");
    #小区链接
    href=a.get("href")
    estateid=re.findall(r"\d+",href)
    #小区名称
    estate=a.text.encode('utf8')

    #年代
    yearinfo = re.findall(r"年代：<\/span>(.*)年<\/li>",str(zushous[0]))
    year="未知"
    if len(yearinfo) > 0:
        year = yearinfo[0]

    #地铁
    traffic = zushous[0].find("li",class_="traffic");
    subwayinfo = re.findall(r"<\/span>(.*)<\/li>",str(traffic))
    subway="无"
    if len(subwayinfo) > 0:
        subway = subwayinfo[0]
    
    #保存房源到数据库
    houseDB.inserthouse(int(houseid),int(estateid[0]),float(jlinfo[0]),float(jlinfo[2]))

    #小区均价，近期二手房成交均价，近期租房成交均价
    estatejj=0
    jqsoldp=0
    jqleasedp=0
    if int(houseDB.isestateexist(int(estateid[0]))) == 0:
        print("new estate %s"%estateid[0])
        try:
            estatejj,jqsoldp,jqleasedp = browseestate(estateid[0])
        except Exception as e:
            print("异常的类型是:%s"%type(e))
            print("异常对象的内容是:%s"%e)
            traceback.print_exc()
        #保存小区数据到数据库
        houseDB.insertestate(int(estateid[0]),int(year),str(estate),str(subway),float(estatejj),float(jqsoldp),float(jqleasedp))
    else:
        print("estate %s is exist"%estateid[0])
        estatejj,jqsoldp,jqleasedp = houseDB.getestateinfo(int(estateid[0]))
    
    #租售比
    zsper = 0
    if jqsoldp > 0:
        zsper = jqleasedp*12/jqsoldp
    
    document = open("soup.txt", "a+");
    
    document.write(estate+",");
    document.write(year+",");
    document.write(str(jlinfo[0])+",");
    document.write(str(jlinfo[2])+",");
    document.write(str(jlinfo[1])+",");
    document.write(str(subway)+",");
    document.write(str(estatejj)+",");
    document.write(str(jqsoldp)+",");
    document.write(str(jqleasedp)+",");
    document.write(str(zsper)+"\n");
    document.close();

url = "https://bj.5i5j.com/ershoufang/o8n%d/"
headers = {  
    'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
    'Host':'bj.5i5j.com',
    'Referer':'http://bj.5i5j.com/ershoufang',
    'Upgrade-Insecure-Requests':'1'
}

def browsehouselist(page):
    print(url%page)
    request = urllib2.Request(url%page,headers=headers)
        
    response = urllib2.urlopen(request)
    html = response.read()
    #html = StringIO.StringIO(html)
    #gzipper = gzip.GzipFile(fileobj=html)
    #html = gzipper.read()
    soup = BeautifulSoup(html, fromEncoding='utf8')

    plist_all = soup.find_all("ul", class_="pList")
    if len(plist_all) <= 0:
        print(html)
        return 0;
    
    time.sleep(5)

    for plist in plist_all:
        li_all = plist.findAll("li")
        for li in li_all:
            divlistImg=li.find("div",{"class":"listImg"})
            a=divlistImg.find("a");
            href=a.get("href")
            houseid=re.findall(r"\d+",href)
            result=int(houseDB.ishouseexist(int(houseid[0])))
            if result == 0:
                print("new house %s"%houseid[0])
                browsehouse(houseid[0])
                time.sleep(random.randint(1,9))
            else:
                print("houseid %s exist"%houseid[0])
    return 1;

def browseall():
    page_error=[]         
    for i in range(1,100):
        try:  
            re = browsehouselist(i)
            if re == 0:
                break;
        except Exception as e:
            print("异常的类型是:%s"%type(e))
            print("异常对象的内容是:%s"%e)
            traceback.print_exc()
            page_error.append(i)

def dumpfile():
    estateall = houseDB.getallestate();
    for estate in estateall:
        divlistImg=li.find("div",{"class":"listImg"})
        a=divlistImg.find("a");
        href=a.get("href")
         houseid=re.findall(r"\d+",href)
            
    print(estateall)
    document = open("soup.txt", "w+");
    document.write("小区编号,小区名称,建筑年代,地铁,小区均价,近期二手房均价,近期租房均价,租售比\n");
    document.write("%d,%s,%d,%s,%f,%f,%f,%f"%(estate[0],estate[2],estate[1],estate[3],estate[4],estate[5],))
    document.close();
    
#browseall()
dumpfile()

houseDB.close()
