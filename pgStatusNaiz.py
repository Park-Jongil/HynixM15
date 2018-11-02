import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import sqlite3
from sqlite3 import Error
from time import sleep
import sys
import psycopg2


def create_postgres_connection(host_product,dbname,user,password,port):
    try:
        product_connection_string = "dbname={dbname} user={user} host={host} password={password} port={port}"\
                                .format(dbname=dbname,
                                        user=user,
                                        host=host_product,
                                        password=password,
                                        port=port)    
        product = psycopg2.connect(product_connection_string)
        return product
    except:
        print("Postgres DB Connection Error")
        return None

def select_ipaddr_by_key(conn, key):
    try :
        cur = conn.cursor()
        cur.execute("select seq,device_name,ip_addr from cameralist where seq="+str(key) )
        row = cur.fetchone()
        if (row==None) : return None
        return row[2].strip()
    except :
        return None

def select_rtspurl_by_key(conn, key):
    try :
        cur = conn.cursor()
        cur.execute("select seq,device_name,rtsp_url1 from cameralist where seq="+str(key) )
        row = cur.fetchone()
        if (row==None) : return None
        return row[2].strip()
    except :
        return None


def select_status_by_key(conn, key):
    try :
        cur = conn.cursor()
        cur.execute("SELECT seq,status FROM cameralist WHERE seq="+str(key) )
        row = cur.fetchone()
        if (row==None) : return None
        return row[1]
    except :
        return None

def select_name_by_key(conn, key):
    try :
        cur = conn.cursor()
        cur.execute("SELECT seq,device_name FROM cameralist WHERE seq="+str(key))
        row = cur.fetchone()
        return row[1].strip()
    except :
        return None

def update_status_by_key(conn, key , status):
    try :
        CheckTime = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
        if (status == 0) :
            cur = conn.cursor()
            cur.execute("UPDATE cameralist SET status=%s , last_dead=%s WHERE seq=%s", (status,CheckTime,str(key)))        
            conn.commit()
        else :
            cur = conn.cursor()
            cur.execute("UPDATE cameralist SET status=%s , last_alive=%s WHERE seq=%s", (status,CheckTime,str(key)))        
            conn.commit()
    except :
        return

def main():
    naiz_url  = 'http://10.236.1.100:80/event/status.cgi?id=admin&password=spdlwm1234&key=all&method=get'
#    naiz_url  = 'http://naiz.re.kr:8001/event/status.cgi?id=admin&password=admin&key=all&method=get'

#    Naiz_DB = create_postgres_connection("127.0.0.1","NaizCamera","postgres","postgres","5432")
    Naiz_DB = create_postgres_connection("10.236.1.42","NaizCamera","postgres","postgres","5432")

    file = urllib.request.urlopen( naiz_url ).read().decode('euc-kr')
    root = ET.fromstring(file)
    iCount = 0
    isAlive = 0
    iPrevStatus = 0

    for child in root :
        for sub in child :
            HighStreamConnection = '0'
            iCurrStatus = 0
            for item in sub :
                if (item.tag == 'Key') :      
                    UniqueKey = item.text
                if (item.tag == 'HighStreamConnection') :    
                    HighStreamConnection = item.text  
            if (HighStreamConnection=='1') :
                isAlive = isAlive + 1   
                iCurrStatus = 1
            iPrevStatus = select_status_by_key( Naiz_DB , int(UniqueKey) )
            if (iPrevStatus != iCurrStatus) :
                CameraName = select_name_by_key( Naiz_DB , int(UniqueKey) )
                if (CameraName != None) :
                    if (iPrevStatus==0 and iCurrStatus==1) : szStatus = "활성"
                    else : szStatus = "단절"
                    try :
                        print(" 상태값 변이 = " + UniqueKey + "[" + szStatus + "] [" + CameraName + "] " )
                    except :
                        print (" Error Invoke ")
                    update_status_by_key( Naiz_DB , int(UniqueKey) , iCurrStatus )

            iCount = iCount + 1
    print("활성화/전체갯수 = " + str(isAlive) + " / " + str(iCount))
    Naiz_DB.close()

if __name__ == '__main__':
    main()
    
    
