# -*- coding: utf-8 -*-
"""
Created on Sun Oct 22 21:16:57 2017

@author: pang
"""
import nltk
import sqlite3
import colorama
from colorama import Fore
from sklearn.naive_bayes import MultinomialNB
from sklearn import neighbors
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cross_validation import train_test_split

#conn=sqlite3.connect("fypDatabase.db",timeout=10)
#
#c=conn.cursor()




resValue=[]
#############################################################################
def getComment(cursor,userid):
    cursor.execute("SELECT comment FROM userComment WHERE userid=? ORDER BY date DESC",(userid,))
    comment=cursor.fetchall()
    return comment

def getRes(cursor,userid):
    cursor.execute("SELECT resID FROM userComment WHERE userid=?",(userid,))
    resid=cursor.fetchall()
    return resid

def getRating(cursor,userid):
    cursor.execute("SELECT rating FROM userComment WHERE userid=?",(userid,))
    rating=cursor.fetchall()
    return rating

def getAllUser(cursor):
    cursor.execute("SELECT userID FROM user")
    user=cursor.fetchall()
    return user
#############################################################################
def fetchData(cursor,x):
    cursor.execute('SELECT * FROM '+x)
    fetchRes=cursor.fetchall()
    #print(fetchRes)
    return fetchRes 
#############################################################################
def predictPosNeg(c,data_comment,r):

    
    data_pos=fetchData(c,"posdata")
    data_pos=[i[0] for i in data_pos]
    data_pos=[x.strip(' ') for x in data_pos]
    data_neg=fetchData(c,"negdata")
    data_neg=[i[0] for i in data_neg]
    data_neg=[x.strip(' ') for x in data_neg]
    data_med=fetchData(c,"meddata")
    data_med=[i[0] for i in data_med]
    data_med=[x.strip(' ') for x in data_med]
        
    x=0
    p=0
    n=0
    #print('3...')
    while x<len(data_comment):
        y=0
        while y<len(data_pos) :
            #print('4...')
#            print(data_comment[x])
#            print(Fore.CYAN + data_pos[y])
            if(data_comment[x]==data_pos[y])==True:
                p+=1
                y+=1
                
            else:
                y+=1
            
            
        z=0
        while z<len(data_neg):
            #print('5...')
#            print(data_comment[x])
#            print(Fore.GREEN + data_neg[z])
            if(data_comment[x]==data_neg[z])==True:
                n+=1
                z+=1
            else:
                z+=1
                
            
        c=0
        while c<len(data_med):
            #print('6...')
            if(data_comment[x]==data_med[c])==True:
                if(r>=3):
                    p+=r
                    n=n+1
                    c+=1
                if(r<3):
                    n+=r
                    p=p+1
                    c+=1
            else:
                c+=1
        
        x+=1
        
    #print('7...')
    if(n==0 and p==0):
        print(Fore.BLUE+ 'p='+str(p))
        print(Fore.RED+ 'n='+str(n))
        return str(0)
    if(n==0):
        p=p/(p+n)
        print(Fore.BLUE+'p='+str(p))
        print(Fore.RED+'n='+str(n))
        return str(p)
    if(p==0):
        n=n/(p+n)
        print(Fore.BLUE+'p='+str(p))
        print(Fore.RED+'n='+str(n))
        return str(-n)
    else:
        p=p/(p+n)
        n=n/(p+n)
        print(Fore.BLUE+"p="+str(p))
        print(Fore.RED+"n="+str(n))
        if(p==n):
            return str(0)
        if(p>n):
            p=p/(p+n)
            return str(p)
        if(n>p):
            n=n/(p+n)
            return str(-n)
##############################################################################
def prediction(cursor,comment,resid,rating):
    result=[]
    for x in range(0,len(comment)):
       
        temp_list=[]
        temp_list=comment[x]
        res=resid[x]
        print(res)
        r=rating[x]
        for y in range(0,len(temp_list)):
            #print('1...')
            temp_list=str(temp_list).strip('[]')
            temp_list=str(temp_list).strip('()')
            temp_list=temp_list.replace(',','')
            temp_list=temp_list.replace("'","")
            temp_list=temp_list.split()
    
            for i in range(0,len(temp_list)):
                #print('2...')
                temp_list[i]=temp_list[i].lower()
                    
            resScore=predictPosNeg(cursor,temp_list,r)
            
            print(Fore.CYAN+ "res score ="+str(resScore))
            if(float(resScore) > 0):
                print(Fore.GREEN + 'recorded')
                result.append(res)
                resValue.append(resScore)
                
#    print(len(result))
#    print(len(resValue))
    return result                
############################################################################
def getPreference(cursor,res):
    res=str(res)
    try: 
        cursor.execute("SELECT f.foodtype FROM restaurant r, foodType f WHERE  f.resID == r.resID AND f.resID=? ",(res,))
        sendData=''
        fetchData=cursor.fetchall()
        for row in range(len(fetchData)):
            for col in range(len(fetchData[row])):
                sendData=sendData+str(fetchData[row][col])
                if(len(fetchData[row])!=col+1):
                    sendData=sendData+":"
            sendData=sendData+"\n"
            
        
#        print(sendData)
        return sendData
    except Exception as e:
        print(e)
       
        

############################################################################
def finalizePreference(c,u,r):
    r=[i[0] for i in r]
    
    userPf=[]
    e=0
    while e<len(r):
        f=r[e]
        data=getPreference(c,f)
        data=str(data).strip("[]")
        data=str(data).strip("()")
        data=data.split()
        userPf=userPf+data
        e+=1
    
    PF_result=[]
    PF_result=freqDist(userPf)
#    print('#############@@@@@@@@@@@@@@############')
#    print(r)
    train(trial1,userPf,userPf)
    record_userPF(c,u,PF_result)
    inputResPre_1(c,u,r,resValue)
############################################################################        
def freqDist(data):
    all_words=nltk.FreqDist(data)
    print(all_words.most_common(5))
    all_words.plot(10,cumulative=False)
    
    return list(all_words.most_common(5))
############################################################################
def train(classifier, X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=20)
 
    classifier.fit(X_train, y_train)
    print ("Accuracy: %s" % classifier.score(X_test, y_test))
    print(classifier.predict(X))
    return classifier


trial1 = Pipeline([
    ('vectorizer', TfidfVectorizer()),
    ('classifier', MultinomialNB()),
     #('classifier', knn),
])
############################################################################
def record_userPF(cursor,u,p):
    p=str(p).strip('[]')
    parameter=(u,p)
    parameter2=(p,u)
    u=str(u)
    testEmpty=''
    cursor.execute("SELECT * FROM userPreference WHERE userid =?",(u,))
    testEmpty=cursor.fetchall()
    
    if(len(testEmpty)==0):
        try:
            cursor.execute("INSERT INTO userPreference VALUES(?,?)",parameter)    
        except Exception as e:
            print(e)
    else:
        try:    
            cursor.execute("UPDATE userPreference SET prefer_food_type =? WHERE userid =?",parameter2)
        except Exception as e:
            print(e)
            
            
############################################################################
#def inputResPre(cursor,userid,rp,rv):
#    rp=str(rp).strip('[]')
#    rp=str(rp).strip('"')
#    rv=str(rv).strip('[]')
#    
#    
#    print('2')
#    parameter=(userid,rp,rv)
#    print(rp)
#    parameter2=(rp,rv,userid)
#    print('3')
#    cursor.execute("SELECT * FROM userResPf WHERE userid =?",(userid,))
#    print('4')
#    testEmpty=cursor.fetchall()
#    if(len(testEmpty)==0):
#        try:
#            print('5')
#            cursor.execute("INSERT INTO userResPf VALUES(?,?,?)",parameter)  
#            print('6') 
#        except Exception as e:
#            print(e)
#    else:
#        try:
#            cursor.execute("UPDATE userResPf SET res=? AND resScore=? WHERE userID=?",parameter2) 
#            cursor.execute("UPDATE userResPf SET resScore=? WHERE userID=?",parameter3)   
#        except Exception as e:
#            print(e)
#     
############################################################################
def inputResPre_1(cursor,userid,rp,rv):
#    rp=str(rp).strip('[]')
#    rp=str(rp).strip('"')
#    rv=str(rv).strip('[]')
#    print(rp)
#    print('2')
#    print(rv)
#    print('3')
    cursor.execute("SELECT res FROM userResPf_1 WHERE userid =?",(userid,))
#    print('4')
    testEmpty=cursor.fetchall()
    if(len(testEmpty)==0):
        testEmpty=str(testEmpty).strip("[]")
        testEmpty=str(testEmpty).strip("()")
        testEmpty=str(testEmpty).replace("'",' ')
        testEmpty=str(testEmpty).replace(",",' ')
        testEmpty=str(testEmpty).split()    
        try:
#            print('5')
#                print(rp[i])
#                print(rv[i])
            for i in range(0,len(rp)):
                parameter=(userid,rp[i],rv[i])
                cursor.execute("INSERT INTO userResPf_1 VALUES(?,?,?)",parameter)  
#            print('6') 
        except Exception as e:
            print(e)
    else:
        for i in range(0,len(rp)):
            if(testEmpty.__contains__(rp[i])==True):
                try:
#                    print('7')
#                    print(rp[i])
    #                print(rv[i])
                    parameter=(rp[i],userid)
                    parameter2=(rv[i],userid,rp[i])
    #                print(parameter)
    #                cursor.execute("UPDATE userResPf_1 SET res=? WHERE userID=?",parameter) 
#                    print('8')
                    cursor.execute("UPDATE userResPf_1 SET resValue=? WHERE userID=? AND res=?",parameter2)  
#                    print('11')
                except Exception as e:
                        print(e)
            else:
                
                try:
#                    print('9')
                    parameter(userid,rp[i],rv[i])
                    cursor.execute("INSERT userResPf_1 VALUES(?,?,?)",parameter)
#                    print('10')
                except Exception as e:
                    print(e)
        
            
#    print(testEmpty)
#    print(testEmpty[0])
           
############################################################################


    
############################################################################    
def start(u):
    
    conn=sqlite3.connect("fypDatabase.db",timeout=10)

    c=conn.cursor()
    
    userid=u
    comment=getComment(c,userid)
    resid=getRes(c,userid)
    rating=getRating(c,userid)
    rate=[i[0] for i in rating]
    newid=[]
    newcomment=[]
    newrate=[]
    for i in range(0,len(comment)):
        if(newid.__contains__(resid[i])==False):
            newid.append(resid[i])
            newcomment.append(comment[i])
            newrate.append(rate[i])
    
#    print('resid = ')
#    print(newid)
#    print(len(newid))
#    print(len(newcomment))
#    print(len(newrate))
    Res=prediction(c,newcomment,newid,newrate)
    #Res=list(set(Res))
    #Res=[i[0] for i in Res]
    finalizePreference(c,userid,Res)

#print(data_pos)
#print(data_neg)
#print(data_med)

    c.close()
    conn.commit()
    conn.close()
    
#start('user001')
