# -*- coding: utf-8 -*-
"""
Created on Sun Dec 19 19:33:20 2021

@author: User
"""

"""
1.超過十個交易日股價橫向整理
2.在整理期間成交量明顯萎縮
3.以中長紅的姿態突破整理
4.突破時帶著比先前多出不少的成交量
"""
import warnings

# basic
import numpy as np
import pandas as pd
# get data
import pandas_datareader as pdr
# visual
import matplotlib.pyplot as plt
import mpl_finance as mpf
%matplotlib inline
import seaborn as sns
#time
import datetime as datetime
#talib
import talib

#===可調整參數===================================
rule1_1=1.02
rule1_2=0.98
rule2=0.8
rule3=1.01
rule4=1.2
stoploss = 0.97
stopgain = 1.13
TC = 0.001425*0.2*2+0.003
#===用網頁爬蟲取出0050成分股+持股比例=============
import urllib.request,re 
import ssl

context = ssl._create_unverified_context()
x = urllib.request.urlopen("https://www.cnyes.com/twstock/ingredient.aspx?code=0050",context = context).read().decode("utf-8")
y=x.split('持股比例%')[3]
y1=y.split('</td>\r\n\t\t<td></td>\r\n\t\t<td></td>\r\n\t</tr>\r\n</table>\r\n\r\n</div></div>\r\n\r\n<div class="returnTop">')[0]
y2=y1.split('.htm">')
y3=[i.split('</a>')[0] for i in y2]
codelist=y3[1:-1]#0050成分股
#percentage=y1.split('class="alignr">')
#percentage=[i.split('</td>')[0] for i in percentage]
#percentage=percentage[1:-1]#持股比例

#===取得0050資料=====================================
start = datetime.datetime(2020,1,1)
end = datetime.datetime(2020,12,29)
df = pdr.DataReader('0050.TW', 'yahoo', start=start,end=end)
df=df.dropna(axis=0)#刪除移漏值
x=[df.index,df['Volume'],df['Open'], df['High'],df['Low'],df['Close']]
x=np.transpose(x)
info0050=[[pd.Timestamp(test[0]).date(),test[1],round(test[2],2),round(test[3],2),round(test[4],2),round(test[5],2)]for test in x]
#===寫入excel=====================================    
path= r'C:\Users\User\Documents'
file='\\'+'stockprofit.csv'
f=open(path+file , 'w')
f.write("code")
f.write(',')
f.write("date")
f.write(',')
f.write("profit")
f.write('\n')
#===策略績效分析=======================================
#策略1-1固定持有2天
overallprofit=[]
overallcost=[]
#策略3-1當該股於回測期間內第一次條件觸發，則買進該股一張持有至期間結束
holdprofit=[]
holdcost=[]
#策略3-2當該股於回測期間內第一次條件觸發，以該股一張的價格買進對應的0050張數(設可以以零股交易)，並持有至期間結束
hold0050profit=[]
hold0050cost=[]
#codenum=-1#查詢持股比例用
#===抓取股價資料=======================================
for code in codelist:
    if(code == '2823'):
        continue
    #codenum+=1#查詢持股比例用
    #codepercentage=percentage[codenum]#該股於0050的持股比例
    firsttrade=True
    profitlist=[]
    costlist=[]
    target_date=[]
    print("code:",code)
    codestr=code+'.TW'

    df = pdr.DataReader(codestr, 'yahoo', start=start,end=end)
    df=df.dropna(axis=0)#刪除移漏值
    x=[df.index,df['Volume'],df['Open'], df['High'],df['Low'],df['Close']]
    x=np.transpose(x)
    target_info=[[pd.Timestamp(test[0]).date(),test[1],round(test[2],2),round(test[3],2),round(test[4],2),round(test[5],2)]for test in x]

    #===匯入資料庫=====================================
    import pymysql
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='A09140914',
                                 db='stock')
    sql = "create table "+'s'+str(code)+"(date char(15),volumn int,open float,high float,low float,close float);"
    sql2="drop table if exists "+'s'+str(code)+";"
    cursor=connection.cursor()#建立連接點
    cursor.execute(sql2)#先刪除table如果有同檔名
    cursor.execute(sql)
    connection.commit()    

    # Insert to the database
    try:
        with connection.cursor() as cursor:
            for row in target_info:
                sql = "INSERT INTO "+'s'+str(code)+" VALUES (%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql, (row[0],row[1],row[2],row[3],row[4],row[5]))
        connection.commit()
    finally:
        connection.close()
    #===回測=====================================
    trade = False
    outsign = False
    
    for i in range(12,len(target_info)-2):
        minp=[]
        maxp=[]
        closep=[]
        select=True 
        if(trade == True):
            if(cost*stoploss > target_info[i][5]):
                outdate = None
                trade = False
                profit=target_info[i][5]-cost
                profitlist.append(profit*(1-TC))
                target_date.append(target_info[i][0])
                print("Ordertime:",date,"Covertime:",target_info[i][0],"buyprice:",cost,"gain:",round(profit,3))  
                f.write(str(codestr))
                f.write(',')
                f.write(str(target_info[i][0]))
                f.write(',')
                f.write(str(profit))
                f.write('\n')
            elif(cost*stopgain < target_info[i][5]):
                outdate = None
                trade = False
                profit=target_info[i][5]-cost
                profitlist.append(profit*(1-TC))
                target_date.append(target_info[i][0])
                print("Ordertime:",date,"Covertime:",target_info[i][0],"buyprice:",cost,"gain:",round(profit,3)) 
                f.write(str(codestr))
                f.write(',')
                f.write(str(target_info[i][0]))
                f.write(',')
                f.write(str(profit))
                f.write('\n')
        
        if(trade==True):
            if(i == len(target_info)-1):
                outdate = None
                trade = False
                outsign = False
                profit=target_info[i][5]-cost
                profitlist.append(pprofit*(1-TC))
                target_date.append(target_info[i][0])
                print("Ordertime:",date,"Covertime:",target_info[i][0],"buyprice:",cost,"gain:",round(profit,3))     
                f.write(str(codestr))
                f.write(',')
                f.write(str(target_info[i][0]))
                f.write(',')
                f.write(str(profit))
                f.write('\n')
            
        

        if(target_info[i][5]<target_info[i][2]*rule3):#3.以"中長紅"的姿態突破整理
            continue
        else:#4.突破時帶著比先前多出不少的成交量
            if(target_info[i][1]<target_info[i-1][1]*rule4):
                continue
            for test in range(1,12):#1.超過十個交易日股價橫向整理-1
                minp.append(target_info[i-test][4])   
                maxp.append(target_info[i-test][3]) 
                closep.append(target_info[i-test][5]) 
            periodmax=max(maxp)
            periodmin=min(minp)
            average_close=np.mean(closep)
            if(periodmax>average_close*rule1_1 and periodmin<average_close*rule1_2):
                continue
            for back in range(1,12):
                if(target_info[i][2]<target_info[i-back][3]):#3.以中長紅的姿態"突破"整理
                    select=False
                    break
                if(target_info[i-back][1]>target_info[i][1]*rule2):#2.在整理期間成交量明顯萎縮
                    select=False
                    break
            
        if(firsttrade==True and select==True):#該股第一次進場
            firsttrade=False
            holdprofit.append(target_info[len(target_info)-1][5]-target_info[i][5])
            holdcost.append(target_info[i][5])
            hold0050profit.append((info0050[len(target_info)-1][5]-info0050[i][5])*(target_info[i][5]/info0050[i][5]))#以該股的價格買進對應的0050張數(設可以以零股交易)
            hold0050cost.append(target_info[i][5])
            #print(target_info[len(target_info)-1][5],"+",target_info[i][5])
            
        if(trade == False and select == True):    
            trade = True
            outdate = i
            overallcost.append(target_info[i][5])
            costlist.append(target_info[i][5])
            cost = target_info[i][5]
            date = target_info[i][0]
            continue
        

        


    if(len(profitlist)!=0):
        overallprofit.append(sum(profitlist))
        print("total gain:",round(sum(profitlist),2))
        print("return:",round(sum(profitlist)/sum(costlist),5))
        print("\n")
    else:
        print("nothing match the condition!\n")


print("--------------------------------------------")     
print(" overall gain:",sum(overallprofit))
print(" return:",sum(overallprofit)/sum(overallcost)) 
print("--------------------------------------------")  
print("(buy and hold) overall gain:",sum(holdprofit))
print("(buy and hold) return:",sum(holdprofit)/sum(holdcost))
print("--------------------------------------------")  
print("(hold 0050 instead) overall gain:",sum(hold0050profit))
print("(hold 0050 instead) return:",sum(hold0050profit)/sum(hold0050cost))
f.close() 
#===畫圖=====================================
for idate in target_date:

    start = idate-datetime.timedelta(days=20)
    end = idate+datetime.timedelta(days=30)
    df = pdr.DataReader(codestr, 'yahoo', start=start,end=end)
    df=df.dropna(axis=0)#刪除移漏值

    df.index = df.index.format(formatter=lambda x: x.strftime('%Y-%m-%d')) 

    fig = plt.figure(figsize=(24, 8))

    ax = fig.add_subplot(1, 1, 1)
    ax.set_xticks(range(0, len(df.index), 10))
    ax.set_xticklabels(df.index[::10])
    mpf.candlestick2_ochl(ax, df['Open'], df['Close'], df['High'],
                          df['Low'], width=0.6, colorup='r', colordown='g', alpha=0.75);