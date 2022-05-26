from flask import Flask, redirect, url_for, render_template,request
import requests
from bs4 import BeautifulSoup
import pandas
import re
import random
import time
import sqlite3
import sqlite3 as sql
import sqlite3
from datetime import datetime

app=Flask(__name__) #__name__目前執行模組

@app.route('/', methods=("POST", "GET"))#以函式為基礎，提供附加的功能('/', methods=("POST", "GET"))
def index():
    if request.method == "POST":
        stock = request.form["nm1"] #nm是html提交表格nmae
        return redirect(url_for("get_table",stock_id=stock)) #url_for,後面要是函數
    return render_template("index.html")



@app.route('/stock/<stock_id>') #第2個網頁  
def get_table(stock_id):
    #自動抓取防擋表頭
    headers = {'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'}
    url = f"https://goodinfo.tw/tw/StockDividendPolicy.asp?STOCK_ID={stock_id}"  #goodinfo經營績效
    df10=get_tab01(url,headers) #goodinfo 配息
    time.sleep(random.randrange(1,5 ))  #延遲6-13秒防鎖ip
  #----------------  
     #------------
     #找出公司代碼及公司
    res=requests.get(url,headers=headers)
    res.encoding='utf-8'
    soup = BeautifulSoup(res.text, 'lxml')
    data333=soup.select("table.b0")  #使用bs4以網頁程式碼找出位置
    data66=re.findall('(\d+\D+)',data333[4].text) #正規表達法\d+1個數
    stockname=data66[0].split()[0]+data66[0].split()[1] #顯示公司#先變成字串，以空格拆分，選出要的值
    #-------------------------------------------
    
    #多個網頁合併方式
  
     #第一組資料
    nmp_t0=df10.columns.values.tolist()#標題
    len_0=len(nmp_t0)#標題長度
    nmp0_n=df10.values.tolist()#資料內容


    return render_template("test.html",stockname=stockname,nmp_t0=nmp_t0,nmp_n0=nmp0_n,len_0=len_0)

  
   
def get_tab01(url,headers):#goodinfo經營績效
    res=requests.get(url,headers=headers)
    res.encoding='utf-8'
    soup = BeautifulSoup(res.text, 'lxml')
    data=soup.select_one('#tblDetail') #使用bs4以網頁程式碼找出位置
    dfs = pandas.read_html(data.prettify())#使用pandas
    df=dfs[0]#使用pandas讀資料
    df.columns=df.columns.get_level_values(1)#取第二列為標題
    #df.columns=[]修改標題
    df.columns=['年度','盈餘','公積','現金股利', '盈餘', '公積', '股票股利', '股利  合計', '現金  (億)',
       '股票  (千張)', '填息  花費  日數', '填權  花費  日數', '股價  年度', '最高價', '最低價', '年均',
       '現金殖利率(%)', '股票', '合計', '股利  所屬  期間', 'EPS', '配息', '配股', '合計'] #修改標題
    df2=df.drop(['盈餘', '公積', '盈餘', '公積', '股利  合計', '現金  (億)',
       '股票  (千張)', '填息  花費  日數', '填權  花費  日數', '股價  年度', '年均',
       '股票', '合計', '股利  所屬  期間', '配息', '配股', '合計'],axis=1) #不要的拿掉
    df4 = df2[df2['年度'] != '∟']#把不要消除
    df5 = df4[df4['年度'] != '股 利 政 策']#把不要消除
    df6 = df5[df5['最高價'] != '殖 利 率 統 計']#把不要消除
    df7 = df6[df6['最高價'] != '最高']#把不要消除
    df8 = df7[df7['現金股利'] != '現金股利']#把不要消除   
    df9=df8.reset_index(drop=True)#重製index   
    df9['合計股息'] = df9['現金股利']#新增month
    df9['$領股息'] = df9['合計股息']#新增month
    df9['最高價(獲利%)'] = df9['合計股息']#新增month
    df9['最低價(獲利%)'] = df9['合計股息']#新增month
    df9['(高高)(價差+股利)'] = df9['合計股息']#新增month
    df9['(高低)(價差+股利)'] = df9['合計股息']#新增month
    df9['(低高)(價差+股利)'] = df9['合計股息']#新增month
    df9['(低低)(價差+股利)'] = df9['合計股息']#新增month   
    #把營收資料寫入各陣列中
    year=[] 
    EPS=[]
    lowprice=[]
    highprice=[]
    Dividendcash=[]
    Dividendstcok=[]
    cashperson=[]
    f=len(df9.index)
    if f>=16:#2007以前
        f=16
    else: 
        f=len(df9.index)-1#-1是不要「累計」
    for i in range(0,f): #range(x, y) #for 下一列要縮進喔 range(0,6)整數數列：0,1,2,3,4,5
        if df9['最高價'].loc[i]!="-":#年度太少除錯
            year.append(df9['年度'].loc[i])#year單格資料
            Dividendcash.append(df9['現金股利'].loc[i])#year單格資料
            Dividendstcok.append(df9['股票股利'].loc[i])#year單格資料
            highprice.append(df9['最高價'].loc[i])#highprice單格資料
            lowprice.append(df9['最低價'].loc[i])#year單格資料
            cashperson.append(df9['現金殖利率(%)'].loc[i])#year單格資料
            EPS.append(df9['EPS'].loc[i])#year單格資料

    ### 字串轉換成數字#######
        Dividendcash = list(map(float,Dividendcash)) #字串轉換成數字
        Dividendstcok = list(map(float,Dividendstcok)) #字串轉換成數字
        highprice = list(map(float,highprice)) #字串轉換成數字
        lowprice = list(map(float,lowprice)) #字串轉換成數字
        EPS = list(map(float,EPS)) #字串轉換成數字


    for i in range(0,len(Dividendcash)):#合計股息
        sum=0
        for j in range(0,i+1):#合計股息
            sum+=Dividendcash[j]
        df9['合計股息'][i]=round(sum,1)
        df9['$領股息'][i]=round(sum*1000,1)
        df9['最高價(獲利%)'][i]=round(sum/highprice[i]*100,1)#(round(x,1))留小數1位PE1 #去年本益比
        df9['最低價(獲利%)'][i]=round(sum/lowprice[i]*100,1)#(round(x,1))留小數1位PE1 #去年本益比
        df9['(高高)(價差+股利)'][i]=round((highprice[0]-highprice[i])*1000+df9['$領股息'][i],1)#(round(x,1))留小數1位PE1 #去年本益比
        df9['(高低)(價差+股利)'][i]=round((highprice[0]-lowprice[i])*1000+df9['$領股息'][i],1)#(round(x,1))留小數1位PE1 #去年本益比
        df9['(低高)(價差+股利)'][i]=round((lowprice[0]-highprice[i])*1000+df9['$領股息'][i],1)#(round(x,1))留小數1位PE1 #去年本益比
        df9['(低低)(價差+股利)'][i]=round((lowprice[0]-lowprice[i])*1000+df9['$領股息'][i],1)#(round(x,1))留小數1位PE1 #去年本益比  
    df10=df9.head(len(Dividendcash))
    return df10
      


if __name__=='__main__':
   app.run(debug=True)#啟動
 
 
 
   
 


   