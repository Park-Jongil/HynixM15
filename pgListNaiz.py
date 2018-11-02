import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import sqlite3
from sqlite3 import Error
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

def Check_CameraList_Update_False(conn):
    try :
        cur = conn.cursor()
        cur.execute("Update cameralist Set checkupdate = 0")
        conn.commit()
    except :
        return None

def Check_CameraList_Update_True(conn , key):
    try :
        cur = conn.cursor()
        cur.execute("Update cameralist Set checkupdate = 1 Where seq="+str(key))
        conn.commit()
    except :
        return None

def select_name_by_key(conn, key):
    try :
        cur = conn.cursor()
        cur.execute("select seq,device_name,ip_addr from cameralist where seq="+str(key) )
        row = cur.fetchone()
        if (row==None) : return None
        return row[1].strip()
    except :
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

def insert_CameraUpdate_by_key(conn,key,name,pipaddr,prtsp1,prtsp2,cipaddr,crtsp1,crtsp2,appendmode,prevName):
    try :
        CheckTime = datetime.today().strftime("%Y/%m/%d %H:%M:%S")
        cur = conn.cursor()
        sql_stmt = "INSERT INTO public.cameraupdate(checktime, seq, device_name, prev_ip_addr, prev_rtsp_url1, prev_rtsp_url2, curr_ip_addr, curr_rtsp_url1, curr_rtsp_url2, append, prevname) "
        sql_stmt = sql_stmt + "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        cur.execute( sql_stmt , (CheckTime,str(key),name,pipaddr,prtsp1,prtsp2,cipaddr,crtsp1,crtsp2,appendmode,prevName) )
        conn.commit()
    except :
        print("Postgres DB insert into cameraupdate Error")
        return None


def main():
    ChkDB = 0
    if (len(sys.argv) > 1) : ChkDB = int(sys.argv[1])
    naiz_url = 'http://10.236.1.100:80/camera/list.cgi?id=admin&password=spdlwm1234&key=all&method=get'
#    naiz_url = 'http://naiz.re.kr:8001/camera/list.cgi?id=admin&password=admin&key=all&method=get'
#    Naiz_DB = create_postgres_connection("127.0.0.1","NaizCamera","postgres","postgres","5432")
    Naiz_DB = create_postgres_connection("10.236.1.42","NaizCamera","postgres","postgres","5432")
    cur = Naiz_DB.cursor()

# 카메라리스트 테이블의 CheckUpdate 값을 0 으로 초기화한다. 리스트에서 확인되면 1 로 변경.
# 프로그램 수행후 값이 0 이면 삭제된 것으로 판단할수 있다.    
    if (ChkDB == 1) : Check_CameraList_Update_False( Naiz_DB )

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
                findname = select_name_by_key( Naiz_DB , UniqueKey )
                if (findname==None) :
                    print("UniqueKey(추가) = " + UniqueKey + " :\t" + RTSP_URL1)
                    vms_ip = RTSP_URL1.replace('rtsp://',"") 
                    vms_ip = vms_ip[0:vms_ip.find(":")]
                    vms_ch = RTSP_URL1.replace('rtsp://',"") 
                    vms_ch = vms_ch[vms_ch.find("/")+1:]
                    vms_ch = vms_ch.replace('stream1',"") 
                    vms_ch = vms_ch.replace('/',"") 
                    cur = Naiz_DB.cursor()
                    sql_stmt = "INSERT INTO public.cameralist(seq,device_name,ip_addr,rtsp_url1,rtsp_url2,vms_ip,vms_ch) VALUES (%s,%s,%s,%s,%s,%s,%s);"
                    cur.execute( sql_stmt , (str(UniqueKey),Name,IP_Addr,RTSP_URL1,RTSP_URL2,vms_ip,str(vms_ch) ) )
                    Naiz_DB.commit()
                    print("  Insert Name = " + Name)
                    print("  Address = " + IP_Addr)
                    print("  RTSP_URL #1 = " + RTSP_URL1)
                    print("  RTSP_URL #2 = " + RTSP_URL2)
                    insert_CameraUpdate_by_key(Naiz_DB,UniqueKey,Name,"","","",IP_Addr,RTSP_URL1,RTSP_URL2,"추가","")
                else :
# 해당키로 기존에 있는 리스트라면 CheckUpdate 값을 1 로 변경                
                    if (ChkDB == 1) : Check_CameraList_Update_True( Naiz_DB , UniqueKey )
                    ipaddr = select_ipaddr_by_key( Naiz_DB , UniqueKey )
                    rtsp1 = select_rtspurl_by_key( Naiz_DB , UniqueKey )
                    if (findname != Name) or (ipaddr != IP_Addr) or (rtsp1 != RTSP_URL1) :
                        print("UniqueKey(변경) = " + UniqueKey)
                        print("  Update Name = " + Name)
                        sql_stmt = "update cameralist set device_name='"+Name+"',ip_addr='"+IP_Addr+"',rtsp_url1='"+RTSP_URL1+"',rtsp_url2='"+RTSP_URL2+"' where seq = "+UniqueKey+";"
                        cur.execute( sql_stmt )
                        Naiz_DB.commit()
                        insert_CameraUpdate_by_key(Naiz_DB,UniqueKey,Name,ipaddr,rtsp1,"",IP_Addr,RTSP_URL1,RTSP_URL2,"변경",findname)
            except :
                print(" DB 에러 ")

    print("\n전체갯수 = " + str(iCount))
    Naiz_DB.close()

if __name__ == '__main__':
    main()
    
    
