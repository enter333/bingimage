# coding : utf-8

import requests
import json
import os
import csv
import codecs

from PIL import Image, ImageDraw, ImageFont, ImageEnhance

'''
{"images":[
    {"startdate":"20190428",
    "fullstartdate":"201904281600",
    "enddate":"20190429",
    "url":"/th?id=OHR.BabySloth_ZH-CN8329403615_1920x1080.jpg&rf=LaDigue_1920x1080.jpg&pid=hp",
    "urlbase":"/th?id=OHR.BabySloth_ZH-CN8329403615",
    "copyright":"棕色褐喉树懒幼崽与妈妈，哥斯达黎加树懒保护区 (© Suzi Eszterhas/Minden Pictures)",
    "copyrightlink":"/search?q=%e6%a3%95%e8%89%b2%e8%a4%90%e5%96%89%e6%a0%91%e6%87%92&form=hpcapt&mkt=zh-cn",
    "title":"",
    "quiz":"/search?q=Bing+homepage+quiz&filters=WQOskey:%22HPQuiz_20190428_BabySloth%22&FORM=HPQUIZ",
    "wp":true,
    "hsh":"bf21ce5e063d35e9e4a7afdd9cf2a7ae",
    "drk":1,"top":1,"bot":1,"hs":[]}
    ],
    "tooltips":{
        "loading":"正在加载...",
        "previous":"上一个图像",
        "next":"下一个图像",
        "walle":"此图片不能下载用作壁纸。",
        "walls":"下载今日美图。仅限用作桌面壁纸。"
        }}
'''
'''
目前已知图片分辨率
1920x1200   1920x1080    1366x768   1280x768    
1024x768    800x600       800x480   768x1280  
720x1280    640x480       480x800   400x240     
320x240     240x320 
'''

class bingpic(object):
    def __init__(self):
        self.picurlist = []
        self.bingurl = 'https://cn.bing.com/'
        self.requesturl = 'HPImageArchive.aspx?format=js&idx=0&n=1'
        self.todaypicurl = '{}{}'.format(self.bingurl,self.requesturl)
        self.savepath = '{}\\desktoppic\\'.format(os.getcwd())
        os.makedirs(self.savepath,exist_ok=True)
        self.existpic = os.listdir(self.savepath)

    
    # idx 图片序号 0开始,最大8，0是今天，最大8，超过8天的图片，可以通过增大n来解决，最多能到15天的图片 ,n 获取图片张数，1 ~ 8
    def getnowpic(self,idx,n):
        if n <= 0 :
            print('n must in 1 ~ 8')
            return
        if idx < 0 and idx > 8 :
            print('idx must in 0 ~ 8')
            return 
        self.picurl = '{}HPImageArchive.aspx?format=js&idx={}&n={}'.format(self.bingurl,idx,n)
        # print(self.picurl)
        self.pic = requests.get(self.picurl)
        # print(self.pic.status_code)
        ret = self.pic.content
        retjson = json.loads(ret)
        
        # print(len(retjson['images']))
        self.deslist = []
        for imageurl in retjson['images']:
            listrow = []
            # print(imageurl['copyright'])
            # print(imageurl['enddate'])
            # print(imageurl['url'])
            picname = self._getpicname(imageurl['url'])
            picurl = self._getpicurl(imageurl['url'])
            listrow.append(picname)
            listrow.append(picurl)
            listrow.append(imageurl['startdate'])
            listrow.append(imageurl['enddate'])
            listrow.append(imageurl['copyright'])
            self.deslist.append(listrow)
            self._savepic(picname,picurl)
        self._writecsv(self.deslist)
    
    # 从图片url内获取图片名称
    def _getpicname(self,url):
        i1 = url.find('?') + 1
        s1 = url[i1:]
        s2 = s1.split('&')
        s3 = s2[0].split('=')
        return s3[1]
    
    # 将图片url连接成可以下载的地址
    def _getpicurl(self,picurl):
        return '{}{}'.format(self.bingurl,picurl)

    def _savepic(self,picname,picurl):
        '''
        根据picurl下载图片，保存文件名picname
        如果文件已存在则不下载
        '''
        if picname in self.existpic:
            print('{}已存在。'.format(picname))
            return
        picpath = '{}{}'.format(self.savepath,picname)
        # print(picpath)
        try:
            res = requests.get(picurl)
            if res.status_code == 200:
                # print('ok')
                with open(picpath,'wb') as pf:
                    pf.write(res.content)
                    print('保存{}成功。'.format(picname))
        except:
            print("savepic error!")
        
    def _writecsv(self,deslist):
        self.csvpath = '{}picdes.csv'.format(self.savepath)
        # print(self.csvpath)
        # if not (os.path.exists(self.csvpath)):
        '''
        UnicodeEncodeError: 'gbk' codec can't encode character '\xa9' in position 223: illegal multibyte sequence
        这个错误需要 import codecs
        使用codecs.open带上打开编码
        中文写csv出现乱码 将编码改成:utf-8-sig
        '''
        self._readcsv()
        with codecs.open(self.csvpath,'ab','utf-8-sig') as self.csvfile :
            self.writer = csv.writer(self.csvfile)
            for w in self.deslist:
                if w[0] in self.titlelist:
                    continue
                self.writer.writerow(w)
    
    def _readcsv(self):
        self.csvpath = '{}picdes.csv'.format(self.savepath)
        if not (os.path.exists(self.csvpath)):
            print("csv file not found.")
            return
        with codecs.open(self.csvpath,'r','utf-8-sig') as self.csvfile :
            self.reader = csv.reader(self.csvfile)
            self.titlelist = []
            for r in self.reader:
                self.titlelist.append(r[0])
            return self.titlelist
    
    def _resizepic(self,picpf,percent):
        '''
        降低图片分辨率到percent 75%,50%,25%等值
        '''
        if percent >= 1 or percent < 0.10:
            print('不能大于等于1,值介于0.99 ~ 0.10之间')
            return
        with Image.open(picpf) as im:
            # 创建目录
            path ,z = os.path.split(picpf)
            del z
            pname ,ext = os.path.splitext(picpf)
            sizedir = str(round(percent * 100))
            resizedir50 = '{}\\{}\\'.format(path,sizedir)
            if not (os.path.exists(resizedir50)):
                os.makedirs(resizedir50)
            # 
            z,fname = os.path.split(pname)
            fname,a,b = fname.split('_')
            del a,b
            x50,y50 = int(im.size[0] * percent),int(im.size[1] * percent)
            im50 = im.resize((x50,y50))

            resizepath50 = '{}{}_{}x{}{}'.format(resizedir50,fname,x50,y50,ext)
            im50.save(resizepath50)
            im50.close()
            # im25.close()
            
    
    def watermark(self,imagepath,text):
        '''
        imagepath : 图片路径
        text : 需要水印到图片上的文字
        '''
        # 使用微软雅黑字体
        fontpath = "c:/Windows/fonts/msyh.ttc"
        im = Image.open(imagepath).convert('RGBA')
        # 新建一个与目标图片相同大小的透明图片，用来保存文字
        txtimage=Image.new('RGBA', im.size, (0,0,0,0))
        # 确定文字字体
        fnt=ImageFont.truetype(fontpath, 20)
        d=ImageDraw.Draw(txtimage)
        # 获取文字宽度
        sz = d.textsize(text=text,font=fnt)
        # 图片上绘制文字，根据文字长度计算位置，绘制在右下角
        d.text((txtimage.size[0]- sz[0] ,txtimage.size[1]-sz[1]), text,font=fnt, fill=(255,255,255,255))
        # 合并文字图片到原始图片上
        out=Image.alpha_composite(im, txtimage)
        out.show()

if __name__ == '__main__':
    bingimage = bingpic()
    bingimage.getnowpic(0,3)
    # im = Image.open('f:\\other\\pic.jpg')  #image 对象
    # bingimage._resizepic('F:\\other\\course\\bingpic\\desktoppic\\OHR.CasaBatllo_ZH-CN2826447794_1920x1080.jpg',0.75)
    # bingimage.text_watermark(im, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ') 
    # bingimage.watermark('f:\\other\\pic.jpg','中文，无论多长的字，永远在最右下角，有English和123456等数字也一样。')