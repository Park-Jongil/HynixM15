import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import socket
import sqlite3
from sqlite3 import Error
from time import sleep

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None

def CheckTable_Exist(conn,tblname):
    try :
        cur = conn.cursor()
        sql_stmt = "Select count(*) from sqlite_master Where Name = '" + tblname + "'"
        cur.execute(sql_stmt)
        row = cur.fetchone()
        if (row[0]==0) :
            cur = conn.cursor()
            sql_stmt = "CREATE TABLE " + tblname + " ( `CheckTime` TEXT NOT NULL, `CameraID` INTEGER, `CameraName` TEXT, `PrevStatus` INTEGER, `CurrStatus` INTEGER )"
            cur.execute(sql_stmt)        
            conn.commit()
    except :
        return None

def select_status_by_key(conn, key):
    try :
        cur = conn.cursor()
        cur.execute("SELECT seq,status FROM CameraList WHERE seq=?", (key,))
        row = cur.fetchone()
        if (row==None) : return None
        return row[1]
    except :
        return None

def select_name_by_key(conn, key):
    try :
        cur = conn.cursor()
        cur.execute("SELECT seq,name FROM CameraList WHERE seq=?", (key,))
        row = cur.fetchone()
        return row[1]
    except :
        return None

def select_ipaddr_by_key(conn, key):
    try :
        cur = conn.cursor()
        cur.execute("SELECT seq,ip_addr FROM CameraList WHERE seq=?", (key,))
        row = cur.fetchone()
        return row[1]
    except :
        return None

def update_status_by_key(conn, key , status):
    try :
        CheckTime = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
        if (status == 0) :
            cur = conn.cursor()
            cur.execute("UPDATE CameraList SET status=? , Last_Dead=? WHERE seq=?", (status,CheckTime, key))        
            conn.commit()
        else :
            cur = conn.cursor()
            cur.execute("UPDATE CameraList SET status=? , Last_Alive=? WHERE seq=?", (status,CheckTime, key))        
            conn.commit()
    except :
        return

def Insert_StatusChange(conn, TableName, ChkTime , key , name , prev , curr):
    try :
        cur = conn.cursor()
        sql_stmt = "insert into " + TableName + "(CheckTime,CameraID,CameraName,PrevStatus,CurrStatus) values(?,?,?,?,?)"
        cur.execute( sql_stmt,(ChkTime,key,name,prev,curr))
        conn.commit()
    except :
        return

def TcpSocket_AlarmNotify_Status(ip_Addr,port,CamKey,CamStatus):
    try :
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip_Addr, port))
            line = CamKey + "," + CamStatus
            s.send(line)
            s.close()        
    except :
        print(" TCP/IP 통신에러 ")


def main():
    database  = "NaizDB.db"
    tablename = "StatusChange" + datetime.today().strftime("%Y%m%d")
    naiz_url  = 'http://10.236.1.100:80/event/status.cgi?id=admin&password=spdlwm1234&key=all&method=get'
    Notify_Addr = socket.gethostname()
    Notify_Port = 12222

    conn = create_connection(database)
    CheckTable_Exist( conn , tablename )

    file = urllib.request.urlopen( naiz_url ).read().decode('euc-kr')
    root = ET.fromstring(file)
    iCount = 0
    isAlive = 0
    iPrevStatus = 0

    for child in root :
        for sub in child :
            HighStreamConnection = '0'
            LowStreamConnection  = '0'
            iCurrStatus = 0
            for item in sub :
                if (item.tag == 'Key') :      
                    UniqueKey = item.text
                if (item.tag == 'HighStreamConnection') :    
                    HighStreamConnection = item.text  
                if (item.tag == 'LowStreamConnection') :      
                    LowStreamConnection = item.text  
#            if (HighStreamConnection=='1') and (LowStreamConnection=='1')  :
            if (HighStreamConnection=='1') :
                isAlive = isAlive + 1   
                iCurrStatus = 1
            iPrevStatus = select_status_by_key( conn , int(UniqueKey) )
            if (iPrevStatus != iCurrStatus) :
                ipaddr = select_ipaddr_by_key( conn , int(UniqueKey) )
                CameraName = select_name_by_key( conn , int(UniqueKey) )
                if (CameraName != None) :
                    if (iPrevStatus==0 and iCurrStatus==1) : szStatus = "활성"
                    else : szStatus = "단절"
                    try :
                        print(" 상태값 변이 = " + UniqueKey + "[" + szStatus + "] [" + CameraName + "] " )
                    except :
                        print (" Error Invoke ")
#                   if (ipaddr.startswith("10.")) == True : print("   4 Campus = " + ipaddr )    
                    update_status_by_key( conn , int(UniqueKey) , iCurrStatus )
                    CheckTime = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
                    Insert_StatusChange(conn,tablename,CheckTime,int(UniqueKey),CameraName,iPrevStatus,iCurrStatus)

#                   if (Notify_Addr != "") :
#                       TcpSocket_AlarmNotify_Status(Notify_Addr,Notify_Port,UniqueKey,iCurrStatus)
            iCount = iCount + 1
    CheckTime = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
    print("활성화/전체갯수 = " + str(isAlive) + " / " + str(iCount))
    conn.close()

if __name__ == '__main__':
    while True:
        main()
        sleep(5)
    
    
