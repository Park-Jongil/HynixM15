import sys
import xml.etree.ElementTree as ET
from datetime import datetime
import sqlite3
from sqlite3 import Error
import psycopg2


def Config_get_DB_Info(DB_Name) :
    root = ET.parse('config.xml').getroot()
    db_config = root.find("db_config")
    if (db_config != None) :
        db_conn = db_config.find(str(DB_Name))
        if (db_conn != None) :
            DB_Host = db_conn.findtext("Host")
            DB_Name = db_conn.findtext("Name")
            DB_User = db_conn.findtext("User")
            DB_Pass = db_conn.findtext("Password")
            DB_Port = db_conn.findtext("Port")
            post_db = create_postgres_connection(DB_Host,DB_Name,DB_User,DB_Pass,DB_Port)
            return post_db
    return None

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


def main():
    iModifyCount = 0
    iAppendCount = 0
    iDeleteCount = 0
    CheckDate = "2018/09/01"
    if (len(sys.argv) > 1) : CheckDate = (sys.argv[1])
    if (len(sys.argv) == 1) : 
        print("Usage UpdateTrace.py  [Date] ")
        print("      UpdateTrace.py  2018/10/01  <== Check after 2018/10/01 ")
        return

#    Naiz_DB = create_postgres_connection("127.0.0.1","NaizCamera","postgres","postgres","5432")
#    Naiz_DB = create_postgres_connection("10.236.1.42","NaizCamera","postgres","postgres","5432")
    Naiz_DB = Config_get_DB_Info("Naiz_DB")
    cur = Naiz_DB.cursor()
    cur.execute("SELECT CheckTime,seq,prevname,device_name FROM cameraupdate Where append = '변경' AND checktime > '"+CheckDate+"'")
    rows = cur.fetchall()
    if (rows != None and len(rows) > 0) :
        print("변경된 내역")
        print(" CheckTime\t\tSequence    Name  <==  PrevName")
        for row in rows :
            print(row[0]+"\t"+str(row[1])+"\t"+row[3].strip()+"\t\t<==\t"+row[2].strip() )
            iModifyCount = iModifyCount + 1

    cur = Naiz_DB.cursor()
    cur.execute("SELECT CheckTime,seq,device_name,curr_rtsp_url1 FROM cameraupdate Where append = '추가' AND checktime > '"+CheckDate+"'")
    rows = cur.fetchall()
    if (rows != None and len(rows) > 0) :
        print("\n추가된 내역")
        print(" CheckTime\t\tSequence    RTSP Url#1\t\t\t\tName")
        for row in rows :
            print(row[0]+"\t"+str(row[1])+"\t"+row[3].strip()+"\t"+row[2].strip() )
            iAppendCount = iAppendCount + 1

    cur.execute("SELECT seq,device_name,rtsp_url1 FROM cameralist Where checkupdate = 0")
    rows = cur.fetchall()
    if (rows != None and len(rows) > 0) :
        print("\n삭제된 내역")
        print("Seq \tRTSP_Url#1\t\t\t\tName")
        for row in rows :
            print(str(row[0])+"\t"+row[2].strip()+"\t"+row[1].strip() )
            iDeleteCount = iDeleteCount + 1

    Naiz_DB.close()    
    print("\n변경된 작업내용 = " + str(iModifyCount))
    print("추가된 작업내용 = " + str(iAppendCount))
    print("삭제된 작업내용 = " + str(iDeleteCount))

if __name__ == '__main__':
    main()
