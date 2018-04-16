# /usr/env/bin python
# -*- coding:utf-8 -*-

import os;
import urllib2
import re;
import StringIO;
import gzip
import time
import random

from bs4 import BeautifulSoup

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
    estate=a.text

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

    #小区均价，近期二手房成交均价，近期租房成交均价
    estatejj,jqsoldp,jqleasedp = browseestate(estateid[0])
    #租售比
    zsper = 0
    if jqsoldp > 0:
        zsper = jqleasedp*12/jqsoldp
    
    document = open("soup.txt", "a+");
    
    document.write(estate.encode('utf8')+",");
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
    
    return;

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
            print(houseid)
            browsehouse(houseid[0])
            time.sleep(random.randint(1,9))
    return 1;

document = open("soup.txt", "w+");
document.write("小区名称,建筑年代,总价,面积,单价,地铁,小区均价,近期二手房均价,近期租房均价,租售比\n");
document.close();

page_error=[]         
for i in range(1,100):
    try:  
        re = browsehouselist(i)
        if re == 0:
            break;
    except:  
        page_error.append(i)

