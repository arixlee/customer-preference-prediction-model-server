# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#!/usr/bin/python           # This is server.py file
import sqlite3
import socket            # Import socket module
import pandas as pd
from sklearn import neighbors
import datetime
import classify_comment

s = socket.socket()         # Create a socket object
host = socket.gethostbyname('192.168.0.107') # Get local machine name
port = 12345                # Reserve a port for your service.
s.bind((host, port))        # Bind to the port


s.listen(5)                 # Now wait for client connection.

def predict(x,y):
    neighbor=len(x)
    if(neighbor>3):
        neighbor=3
    knn = neighbors.KNeighborsClassifier(n_neighbors=neighbor)
    knn.fit(x,y)
    
    #result=knn.predict(generateUserPreference())
    #print('predicted class: ',result)
    
    #finalResult=knn.predict_proba([[0.25,0.75,0.25,0.5,0.5,0.5,1,1,0,0.875,0.125,1,0.25,0.375,0.125,0.5,0.25,0.625,0.375,0.625,0.875,0.625,0.25,0.25]])
    userPreference=generateUserPreference()
    if(len(userPreference)==0 ):
        print('predict empty')
        return userPreference
    finalResult=knn.predict_proba(userPreference)
    finalResult=pd.DataFrame(finalResult)
    finalResult.loc[len(finalResult)]=knn.classes_
    
    print(finalResult)
    return finalResult

def generateUserPreference():
    conn=sqlite3.connect("fypDatabase.db",timeout=10)
    c=conn.cursor()
    try:
        
        preferenceValue=[]
        preferenceValue.append([])
        c.execute("SELECT r.* FROM resDetail r, viewHistory h WHERE r.resID==h.resID ORDER BY h.timestamp DESC LIMIT 6 ")
        resdata=c.fetchall()
        if(len(resdata)==0):
            print('preference empty')
            c.close()
            conn.commit()
            conn.close()
            return resdata
        resdata=pd.DataFrame(resdata)
            
        resdata.__delitem__(0)
        for index in range(len(resdata.columns)):
            preferenceValue[0].append(resdata[index+1].mean())
        c.close()
        conn.commit()
        conn.close()
        return preferenceValue
    except:
        c.close()
        conn.commit()
        conn.close()
        
def insertViewHistory(userid,resid,timer,likelihood):
    conn=sqlite3.connect("fypDatabase.db",timeout=10)
    c=conn.cursor()
    parameter=(userid,resid,float(timer),float(likelihood),str(datetime.datetime.now()))
    
        
    try:
        if(float(timer)>0.08):#sec/60=5sec/60=0.08
            
            
            c.execute("INSERT INTO viewHistory VALUES (?,?,?,?,?)",parameter)
            c.execute("SELECT * FROM viewHistory")
#            print(c.fetchall())
            c.close()
            conn.commit()
            conn.close()
        else:
            c.close()
            conn.commit()
            conn.close()

    except:
        c.close()
        conn.commit()
        conn.close()
        
def insertComment(userid,resid,comment,date,rate):
    conn=sqlite3.connect("fypDatabase.db",timeout=10)
    c=conn.cursor()
#    c_1=conn.cursor()
    
#    
#    c_1.execute("SELECT * FROM userComment WHERE resID=?",(resid,))
#    testEmpty=c_1.fetchall()
    
    try:
    
        parameter=(userid,resid,comment,date,rate)
        c.execute("INSERT INTO usercomment VALUES (?,?,?,?,?)",parameter) 
        
        c.close()
        conn.commit()
        conn.close()
    except:
        c.close()
        conn.commit()
        conn.close()
        
def getHistory(userid):
    conn=sqlite3.connect("fypDatabase.db",timeout=10)
    c=conn.cursor()
    userid=str(userid)
    try:
       
        c.execute('SELECT r.resName, v.viewTimer, v.likelihoodValue FROM restaurant r, viewHistory v WHERE r.resID = v.resID AND v.userID=?',(userid,))
        sendData=''
       
        fetchData=c.fetchall()
        
        for row in range(len(fetchData)):
            for col in range(len(fetchData[row])):
                sendData=sendData+str(fetchData[row][col])
                if(len(fetchData[row])!=col+1):
                    sendData=sendData+":"
            sendData=sendData+"\n"
        
        c.close()
        conn.commit()
        conn.close()
       
        return sendData
    except:  
        c.close()
        conn.commit()
        conn.close()

def getRestComment(resid):
    conn=sqlite3.connect("fypDatabase.db",timeout=10)
    print('1')
    c=conn.cursor()
    print('2')
    resid=str(resid)
    try:
        print('3')
        c.execute('SELECT  u.date, u.userid, u.comment FROM restaurant r, userComment u WHERE r.resID = u.resID AND u.resID=?',(resid,))
        sendData=''
       
        fetchData=c.fetchall()
        
        for row in range(len(fetchData)):
            for col in range(len(fetchData[row])):
                sendData=sendData+str(fetchData[row][col])
                if(len(fetchData[row])!=col+1):
                    sendData=sendData+":"
            sendData=sendData+"\n"
        
        c.close()
        conn.commit()
        conn.close()
        print('4')
        return sendData
    except Exception as e:
        print(e)
        c.close()
        conn.commit()
        print('5')
        conn.close()    
def searchFunction(searchValue,cont):
    conn=sqlite3.connect("fypDatabase.db",timeout=10)
    c=conn.cursor()
    
    inputPara=str(searchValue)
    #parameter=(inputPara,inputPara,inputPara)
    try:
        c.execute("SELECT s.*, r.resName, r.noGoodReview, i.imageSize, i.imageFile FROM restaurant r, resDetail s, restaurantImage i WHERE r.resID == s.resID AND r.resID == i.resID AND r.resName LIKE '%"+ inputPara+"%' ESCAPE '-' ")
        sendData=''
        resdata=c.fetchall()
        resdata=pd.DataFrame(resdata)
        y=resdata[0]
        dataToMobileApp=resdata[[25,26,27,28]]
        fetchData=resdata[[25,26,27,28]]
        fetchData=fetchData.sort_values([26],ascending=[False])
        fetchData=fetchData.values.tolist()
        dataToMobileApp["likelihood"]=0
        resdata.__delitem__(0)
        resdata.__delitem__(26)
        resdata.__delitem__(25)
        resdata.__delitem__(27)
        resdata.__delitem__(28)
#        print('done load 1')
        x=resdata
        result=predict(x,y)
        if(len(result)!=0):
            for index in range(len(result.columns)):
                dataToMobileApp.ix[index,"likelihood"]=result.iat[0,index]
        
            dataToMobileApp=dataToMobileApp.sort_values(["likelihood",26],ascending=[False,False])
            dataToMobileApp.__delitem__("likelihood")
                        
                
            fetchData=dataToMobileApp.values.tolist()
            
        #print('done load 2') 
#        column=len(fetchData[0])
#        column=column-1
        sendData=''
        column=len(fetchData[0])
        column=column-1
        column=int(column)
        
        for row in range(len(fetchData)):
            for col in range(column):
                sendData=sendData+str(fetchData[row][col])
                if(column!=col+1):
                    sendData=sendData+":"
            sendData=sendData+"\n"
            sendData=str(sendData)
           
            cont.send(bytes(sendData,'UTF-8'))
            loadStatus='done load restaurant no. '+str(row+1)
            print(loadStatus)
            imageBuff=fetchData[row][column]
            cont.send(bytes(imageBuff))
            sendData=''
            ##wtf='\n'
            #cont.send(bytes(wtf))
           # sendData=sendData+bytes(fetchData[row][col+1])
        print("done load!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    
        c.close()
        conn.commit()
        conn.close()
    except:
        c.close()
        conn.commit()
        conn.close()

def userLogin(u):
    conn=sqlite3.connect("fypDatabase.db",timeout=10)
    c=conn.cursor()
    try:
        c.execute("SELECT * FROM user WHERE userID=?",(u,))
#    data=''
#    data=c.fetchall()  
        sendData=''
        fetchData=c.fetchall()
        for row in range(len(fetchData)):
            for col in range(len(fetchData[row])):
                sendData=sendData+str(fetchData[row][col])
                if(len(fetchData[row])!=col+1):
                    sendData=sendData+":"
            sendData=sendData+"\n"
    
#    x=0
#    while x<len(sendData):
#        if(userid==sendData.)==True:
#            data='valid'
#            x+=1
#            break;
#        else:
#            print(sendData.data[x])
#            data='Invalid'
#            x+=1
#    
        c.close()
        conn.commit()
        conn.close()
#        print(sendData)
        return sendData
    except Exception as e: 
        print(e)
        c.close()
        conn.commit()
        conn.close()



def fetchRestaurant(searchValue):
    conn=sqlite3.connect("fypDatabase.db",timeout=10)
    c=conn.cursor()
    inputPara=str(searchValue)
    parameter=(inputPara,)
    try: 
        c.execute("SELECT r.resName, r.area, r.address, r.minPrice, r.noGoodReview, r.noBadReview, s.dishName, r.resID FROM restaurant r, signDish s WHERE r.resID == s.resID AND r.resName == ?",parameter)

        #fetchData=[]
       # fetchData.append([])
        sendData=''
        fetchData=c.fetchall()
        for row in range(len(fetchData)):
            for col in range(len(fetchData[row])):
                sendData=sendData+str(fetchData[row][col])
                if(len(fetchData[row])!=col+1):
                    sendData=sendData+":"
            sendData=sendData+"\n"
            
        c.close()
        conn.commit()
        conn.close()
        return sendData
    except:
        c.close()
        conn.commit()
        conn.close()

def getUserResPf(u):
    conn=sqlite3.connect("fypDatabase.db",timeout=10)
    c=conn.cursor()
    c.execute("SELECT res FROM userResPf_1 WHERE userID=? ORDER BY resValue DESC",(u,))
    restList=c.fetchall()
    restList=str(restList).strip('()')
    restList=str(restList).replace('"',' ')
    restList=str(restList).replace(',',' ')
    restList=str(restList).replace("'"," ")
    restList=str(restList).split()
    
    return restList

def getAllRes():
    conn=sqlite3.connect("fypDatabase.db",timeout=10)
    c=conn.cursor()
    c.execute("SELECT resID FROM restaurant")
    restList=c.fetchall()
    restList=str(restList).strip('()')
    restList=str(restList).replace('"',' ')
    restList=str(restList).replace(',',' ')
    restList=str(restList).replace("'"," ")
    restList=str(restList).split()
    
    return restList
    
def getRestaurantList(u):
    u=str(u)
#    print('1')
    conn=sqlite3.connect("fypDatabase.db",timeout=10)
    c=conn.cursor()   
   
    all_rest=getAllRes()
    classify_comment.start(u)    
    resid=getUserResPf(u)
#    print(resid)
#    print('2')
    sendData=''    
    try: 
#        print('3')
        
        for i in range(0,len(resid)):
#            print(resid[i])
            c.execute('SELECT resID, resName, area, address, minPrice, noGoodReview, noBadReview FROM restaurant WHERE resID==? ',(resid[i],))
            all_rest.remove(resid[i])
#            print('4')
            fetchData=c.fetchall()
#            print(fetchData)
            for row in range(len(fetchData)):
                for col in range(len(fetchData[row])):
                    sendData=sendData+str(fetchData[row][col])
                    if(len(fetchData[row])!=col+1):
                        sendData=sendData+":"
                sendData=sendData+"\n"
            
        
            
        for i in range(0,len(all_rest)):
#            print(resid[i])
            c.execute('SELECT resID, resName, area, address, minPrice, noGoodReview, noBadReview FROM restaurant WHERE resID==? ',(all_rest[i],))
           
#            print('4')
            fetchData=c.fetchall()
#            print(fetchData)
            for row in range(len(fetchData)):
                for col in range(len(fetchData[row])):
                    sendData=sendData+str(fetchData[row][col])
                    if(len(fetchData[row])!=col+1):
                        sendData=sendData+":"
                sendData=sendData+"\n"
        
        c.close()
#        print('5')
        conn.commit()
        conn.close()
        return sendData
    except Exception as e:
        print (e)
#        print('6')
        c.close()
        conn.commit()
        conn.close()


while True:
   c, addr = s.accept()     # Establish connection with client.
   print ('Got connection from', addr)
   #msg="Thank you for connecting, from server"+"\r\n"
   #sentdata='1234/hahahaha/diulei'
   receivedMsg=c.recv(1024)
   #receiverMsg=str(receivedMsg)
   receivedMsg.decode('utf-8')
   #print(receivedMsg)
   newmsg=str(receivedMsg,'utf-8')[2:]
   newmsg=newmsg.split('+')
   print('\n\nreceived message:'+str(newmsg[0]))
   
   if(newmsg[0]=='history'):
       print("masuk history")
       insertViewHistory(newmsg[1],newmsg[2],newmsg[3],newmsg[4])
       
   if(newmsg[0]=='view'):
        print("get history")
        sendData=getHistory(newmsg[1])
        sendData=str(sendData)
        print(sendData)
        c.send(bytes(sendData,'UTF-8'))
    
   if(newmsg[0]=='login'):
       print('login')
       sendData=userLogin(newmsg[1])
       sendData=str(sendData)
       c.send(bytes(sendData,'UTF-8'))
    
   if(newmsg[0]=='search'):
       print("masuk search")
       sendData=searchFunction(newmsg[1],c)
       #search function
   if(newmsg[0]=='clickRestaurant'):
       print("masuk restaurant")
       print(newmsg)
       sendData=fetchRestaurant(newmsg[1])
       sendData=str(sendData)
       c.send(bytes(sendData,'UTF-8'))
   if(newmsg[0]=='getRestList'):
       print(newmsg)
       sendData=getRestaurantList(newmsg[1])
#       print("6")
       sendData=str(sendData)
#       print("7")
       print("send data = "+sendData)
       c.send(bytes(sendData,'UTF-8'))
   #print (newmsg)
   if(newmsg[0]=='getRestComment'):
       print(newmsg)
       sendData=getRestComment(newmsg[1])
       sendData=str(sendData)
       print(sendData)
       c.send(bytes(sendData,'UTF-8'))
   if(newmsg[0]=='storeComment'):
       print(len(newmsg))
       for x in range(0,len(newmsg)):
           print(newmsg[x])
       insertComment(newmsg[1],newmsg[2],newmsg[3],newmsg[4],newmsg[5])
   
  # c.send(sentdata.encode())
   if(newmsg[0]=='terminate'):
       # Close the connection
       s.close()
       break
   c.close()