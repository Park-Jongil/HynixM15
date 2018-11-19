import xml.etree.ElementTree as ET
from datetime import datetime
import sqlite3
from sqlite3 import Error
import psycopg2
import sys

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

def Update_Nubicom_DataBase(conn , sql_stmt):
    try :
        cur = conn.cursor()
        cur.execute( sql_stmt )
        conn.commit()
    except :
        return None

def Nubicom_DataBase_Check_byKey(conn, key):
    try :
        cur = conn.cursor()
        cur.execute("select id,device_name from tb_skh_point_cctv where id="+key )
        row = cur.fetchone()
        if (row==None) : return None
        return row[0]
    except :
        print("Postgres DB Query Error")
        return None

def main():
#    Naiz_DB = create_postgres_connection("127.0.0.1","NaizCamera","postgres","postgres","5432")
#    Nubi_DB = create_postgres_connection("127.0.0.1","postgres","postgres","postgres","5432")
#    Naiz_DB = create_postgres_connection("10.236.1.42","NaizCamera","postgres","postgres","5432")
#    Nubi_DB = create_postgres_connection("10.236.1.42","postgres","postgres","postgres","5432")
    Naiz_DB = Config_get_DB_Info("Naiz_DB")
    Nubi_DB = Config_get_DB_Info("Nubi_DB")
    
    iCnt_Modify = 0
    iCnt_Append = 0
    iCnt_Exist = 0
    iDeleteCount = 0

    CheckDate = "2018/09/01"
    Del_Mark = ""
    if (len(sys.argv) > 1) : CheckDate = (sys.argv[1])
    if (len(sys.argv) > 2) : Del_Mark  = (sys.argv[2])
    if (len(sys.argv) == 1) : 
        print("Usage DB_Sync.py  [Date] [Delete]")
        print("      DB_Sync.py  2018/10/01 <== Check after 2018/10/01 ")
        print("      DB_Sync.py  2018/10/01 Delete <== Check after 2018/10/01 and Unused Camera Delete" )
        return

    if (Naiz_DB != None and Nubi_DB != None) :
        cur = Naiz_DB.cursor()
        cur.execute("SELECT A.seq,A.device_name,A.curr_ip_addr,B.vms_ip,B.vms_ch FROM cameraupdate AS A , cameralist as B Where B.checkupdate <> 0 AND A.seq=B.seq AND A.append = '추가' and A.checktime > '"+ CheckDate + "'")
        rows = cur.fetchall()
        if (rows != None and len(rows) > 0) :
            print("추가된 내역")
            for row in rows :
                CheckKey = Nubicom_DataBase_Check_byKey( Nubi_DB , str(row[0]) )
                if (CheckKey==None) :
                    print("  추가가 필요 = " + str(row[0]) + " : " + row[1] )
                    sql_stmt = "insert into tb_skh_point_cctv(id,campus_id,building,device_name,device_ip,vms_id,grp_serial,dev_serial,dch_ch,vms_ip,vms_ch,geom,layer,floor,pkuid) values"
                    sql_para = "(" + str(row[0]) + ",'4','','" + row[1] + "','" + row[2]+"',100371,1,0,0,'"+row[3]+"','"+row[4]+"','0101000020E61000000ED7195C95DB5F40AE63955A21544240',-10,-10,-10)"
                    Update_Nubicom_DataBase( Nubi_DB , (sql_stmt + sql_para) )
                    iCnt_Append = iCnt_Append + 1
                else :
                    print("  이미 존재함 = " + str(row[1]) + " : " + row[2] )
                    iCnt_Exist = iCnt_Exist + 1

        cur = Naiz_DB.cursor()
        cur.execute("SELECT seq,prevname,device_name,checktime,curr_ip_addr FROM cameraupdate Where append = '변경' and checktime > '"+ CheckDate + "'")
        rows = cur.fetchall()
        if (rows != None and len(rows) > 0) :
            print("변경된 내역")
            for row in rows :
                sql_stmt = "  Update public.tb_skh_point_cctv set device_name='"+row[2]+"',device_ip='"+row[4]+"' Where id = " + str(row[0]) + ";"
                print( sql_stmt )
                Update_Nubicom_DataBase( Nubi_DB , sql_stmt )
                iCnt_Modify = iCnt_Modify + 1

        if (Del_Mark=="Delete") :
            cur = Naiz_DB.cursor()
            cur.execute("SELECT seq,device_name,rtsp_url1 FROM cameralist Where checkupdate = 0")
            rows = cur.fetchall()
            if (rows != None and len(rows) > 0) :
                print("삭제한 내역")
                for row in rows :
                    CheckKey = Nubicom_DataBase_Check_byKey( Nubi_DB , str(row[0]) )
                    if (CheckKey!=None) :
                        sql_stmt = "  delete from public.tb_skh_point_cctv Where id = " + str(row[0]) + ";"
                        print( sql_stmt )
                        Update_Nubicom_DataBase( Nubi_DB , sql_stmt )
                        iDeleteCount = iDeleteCount + 1

    Nubi_DB.close()    
    Naiz_DB.close()    
    if (iCnt_Modify != 0) : print("변경된 항목 = "+str(iCnt_Modify))
    if (iCnt_Append != 0) : print("추가된 항목 = "+str(iCnt_Append))
    if (iCnt_Exist  != 0) : print("기반영 항목 = "+str(iCnt_Exist))
    if (iDeleteCount!= 0) : print("삭제한 항목 = "+str(iDeleteCount))


if __name__ == '__main__':
    main()
