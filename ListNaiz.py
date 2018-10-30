import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import sqlite3
from sqlite3 import Error

tblCameraName = "CameraList"
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None

def CheckTable_Exist_CameraList(conn):
    try :
        cur = conn.cursor()
        sql_stmt = "Select count(*) from sqlite_master Where Name = '" + tblCameraName + "'"
        cur.execute(sql_stmt)
        row = cur.fetchone()
        if (row[0]==0) :
            cur = conn.cursor()
            sql_stmt = "CREATE TABLE " + tblCameraName + "( `seq` INTEGER NOT NULL, `name` TEXT, `ip_addr` TEXT, `rtsp_url1` TEXT, `rtsp_url2` TEXT, `status` INTEGER, `cntError` INTEGER, `vms_ip` TEXT, `vms_ch` TEXT, `Last_Alive` TEXT, `Last_Dead` TEXT, `CheckUpdate` INTEGER )"
            cur.execute(sql_stmt)
            conn.commit()
    except :
        return None

def Check_CameraList_Update_False(conn):
    try :
        cur = conn.cursor()
        cur.execute("Update CameraList Set CheckUpdate = 0")
        conn.commit()
    except :
        return None

def Check_CameraList_Update_True(conn , key):
    try :
        cur = conn.cursor()
        cur.execute("Update CameraList Set CheckUpdate = 1 Where seq=?",(int(key),))
        conn.commit()
    except :
        return None

def select_name_by_key(conn, key):
    try :
        cur = conn.cursor()
        cur.execute("select seq,name,ip_addr from " + tblCameraName + " where seq=?",(int(key),) )
        row = cur.fetchone()
        if (row==None) : return None
        return row[1]
    except :
        return None

def select_ipaddr_by_key(conn, key):
    try :
        cur = conn.cursor()
        cur.execute("select seq,name,ip_addr from " + tblCameraName + " where seq=?",(int(key),) )
        row = cur.fetchone()
        if (row==None) : return None
        return row[2]
    except :
        return None

def select_rtspurl_by_key(conn, key):
    try :
        cur = conn.cursor()
        cur.execute("select seq,name,rtsp_url1 from " + tblCameraName + " where seq=?",(int(key),) )
        row = cur.fetchone()
        if (row==None) : return None
        return row[2]
    except :
        return None

def insert_CameraUpdate_by_key(conn,key,name,pipaddr,prtsp1,prtsp2,cipaddr,crtsp1,crtsp2,appendmode,prevName):
    try :
        if (tblCameraName=="CameraList") :
            CheckTime = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
            cur = conn.cursor()
            sql_stmt = "insert into CameraUpdate(CheckTime,seq,name,prev_ip_addr,prev_rtsp_url1,prev_rtsp_url2,curr_ip_addr,curr_rtsp_url1,curr_rtsp_url2,append,prevName) values(?,?,?,?,?,?,?,?,?,?,?)"
            cur.execute( sql_stmt,(CheckTime,int(key),name,pipaddr,prtsp1,prtsp2,cipaddr,crtsp1,crtsp2,appendmode,prevName))
            conn.commit()
    except :
        return None

def main():
    database = "NaizDB.db"
    naiz_url = 'http://10.236.1.100:80/camera/list.cgi?id=admin&password=spdlwm1234&key=all&method=get'
#    naiz_url = 'http://naiz.re.kr:8001/camera/list.cgi?id=admin&password=admin&key=all&method=get'
    conn = create_connection(database)

# 카메라 리스트테이블이 존재하는지 확인하여 없으면 생성한다.
    CheckTable_Exist_CameraList(conn)
# 카메라리스트 테이블의 CheckUpdate 값을 0 으로 초기화한다. 리스트에서 확인되면 1 로 변경.
# 프로그램 수행후 값이 0 이면 삭제된 것으로 판단할수 있다.    
    Check_CameraList_Update_False( conn )
    cur = conn.cursor()
    file = urllib.request.urlopen( naiz_url ).read().decode('euc-kr')
    root = ET.fromstring(file)
    iCount = 0
    for child in root :
        for sub in child :
            for item in sub :
                if (item.tag == 'Key') :      
                    UniqueKey = item.text
                if (item.tag == 'Name') :      
                    Name = item.text
                if (item.tag == 'Address') :      
                    IP_Addr = item.text
                if (item.tag == 'RTSP_URL1') :    
                    RTSP_URL1 = item.text  
                if (item.tag == 'RTSP_URL2') :      
                    RTSP_URL2 = item.text  
            iCount = iCount + 1
    # sqlite test.db 에 해당내용 저장        
            try :
                findname = select_name_by_key( conn , UniqueKey )
                if (findname==None) :
                    print("UniqueKey = " + UniqueKey)
                    sql_stmt = "insert into CameraList(seq,name,ip_addr,rtsp_url1,rtsp_url2,status) values(?,?,?,?,?,?)"
                    cur.execute( sql_stmt,(int(UniqueKey),Name,IP_Addr,RTSP_URL1,RTSP_URL2,0))
                    conn.commit()
                    print("Insert Name = " + Name)
                    print("Address = " + IP_Addr)
                    print("RTSP_URL #1 = " + RTSP_URL1)
                    print("RTSP_URL #2 = " + RTSP_URL2)
                else :
                    Check_CameraList_Update_True(conn,UniqueKey)
                    ipaddr = select_ipaddr_by_key( conn , UniqueKey )
                    rtsp1 = select_rtspurl_by_key( conn , UniqueKey )
                    if (findname != Name) or (ipaddr != IP_Addr) or (rtsp1 != RTSP_URL1) :
                        print("UniqueKey = " + UniqueKey)
                        sql_stmt = "update CameraList set name=?,ip_addr=?,rtsp_url1=?,rtsp_url2=? where seq = ?"
                        cur.execute( sql_stmt,(Name,IP_Addr,RTSP_URL1,RTSP_URL2,int(UniqueKey)))
                        conn.commit()
                        print("Update Name = " + Name)
            except :
                print(" DB 에러 ")

    print("\n전체갯수 = " + str(iCount))
    conn.close()

if __name__ == '__main__':
    main()
    
