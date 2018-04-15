import os;
import urllib2
import re;
from bs4 import BeautifulSoup

request = urllib2.Request("https://bj.5i5j.com/ershoufang/o8/")
response = urllib2.urlopen(request)
html = response.read()
soup = BeautifulSoup(html)

[script.extract() for script in soup.findAll('script')]

plist_all = soup.find_all("ul", class_="pList")

for plist in plist_all:
    li_all = plist.findAll("li")
    for li in li_all:
        divlistImg=li.find("div",{"class":"listImg"})
        a=divlistImg.find("a");
        href=a.get("href")
        houseid=re.findall(r"\d+",href)
        link="https://bj.5i5j.com/ershoufang/"+houseid[0]+".html"
        print(link)
        document = open("soup.txt", "w+");
        document.write(str(li));
        document.close();

