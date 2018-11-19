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

def Execute_Postgres_DataBase(conn , sql_stmt):
    try :
        cur = conn.cursor()
        cur.execute( sql_stmt )
        conn.commit()
    except :
        return None

def Search_DataBase_Check_byKey(conn, key):
    try :
        cur = conn.cursor()
        stmt = "SELECT TA.assets_no, TA.assets_name, TB.device_sn_value	FROM secuiot.tb_assets_mstr as TA, secuiot.tb_video_security_equip as TB "
        stmt = stmt + "WHERE TA.assets_no=TB.video_security_equip_no and TB.device_sn_value='" + str(key) + "'"
        cur.execute( stmt )
        row = cur.fetchone()
        if (row==None) : return None
        return row[1]
    except :
        print("Postgres DB Query Error")
        return None

def Search_Max_id_assets_mstr(conn):
    try :
        cur = conn.cursor()
        cur.execute( "select max(assets_no) as max_id from secuiot.tb_assets_mstr;"  )
        row = cur.fetchone()
        if (row==None) : return None
        return row[0]+1
    except :
        return None

def Insert_assets_mstr(conn,MaxID,CamID,CamName):
    try :
        cur = conn.cursor()
        stmt = "INSERT INTO secuiot.tb_assets_mstr(assets_no,assets_id, assets_name,assets_reg_clas_code,assets_own_clas_code,equip_dstnct_code,assets_reg_date,lic_exp_date,equip_model_no,assets_natv_no_type_code,assets_natv_no_value,use_yn,reg_usr_no,reg_date) "
        stmt = stmt + "VALUES (%s,%s,%s,'03','C','VMS',now(),now(),13,'MNG',1,'Y','2147480000',now())"
        cur.execute( stmt , ( str(MaxID),CamID,CamName ) )
        conn.commit()
        return True
    except :
        return None

def Insert_video_security_equip(conn,MaxID,DevIP,VMS_ID,GRP_ID,DEV_SN,DEV_CH):
    try :
        cur = conn.cursor()
        stmt = "INSERT INTO secuiot.tb_video_security_equip(video_security_equip_no, equip_ip, vms_id, group_sn_value, device_sn_value, device_channel_no, use_yn, reg_date,reg_usr_no ) "
        stmt = stmt + "VALUES (%s,%s,%s,%s,%s,%s,'y',now(),'00')"
        cur.execute( stmt , ( str(MaxID),str(DevIP),str(VMS_ID),str(GRP_ID),str(DEV_SN),str(DEV_CH) ) )
        conn.commit()
        return True
    except :
        return None

def Update_video_security_equip(conn,DevName,VMS_ID,GRP_ID,DEV_SN,DEV_CH):
    try :
        cur = conn.cursor()
        stmt = "UPDATE secuiot.tb_assets_mstr AS TA SET assets_name = %s FROM ( "
        stmt = stmt + "SELECT video_security_equip_no FROM secuiot.tb_video_security_equip 	WHERE device_sn_value=%s) AS TB "
        stmt = stmt + "WHERE TA.assets_no=TB.video_security_equip_no;"
        cur.execute( stmt , ( str(DevName),str(DEV_SN) ) )
        conn.commit()
        return True
    except :
        return None


def main():
    Secu_DB = Config_get_DB_Info("Secu_DB")
    Nubi_DB = Config_get_DB_Info("Nubi_DB")
    if (Secu_DB==None or Nubi_DB==None) :
        print("Postgres DB 서버에 접속할수 없습니다.")
        return
    cur = Nubi_DB.cursor()
    cur.execute("SELECT * FROM tb_skh_point_cctv;")
    rows = cur.fetchall()
    if (rows != None and len(rows) > 0) :
        for row in rows :
            CheckKey = Search_DataBase_Check_byKey( Secu_DB , str(row[7]) )
            if (CheckKey != None) : 
                if (CheckKey != str(row[3])) :
                    Update_video_security_equip(Secu_DB,str(row[3]),str(row[5]),str(row[6]),str(row[7]),str(row[8]) )
                    print( "이름이변경됨 = " + str(row[3]) + "\t<== " + CheckKey )
            else :
                MaxID = Search_Max_id_assets_mstr(Secu_DB)
                CamID = "Naiz_" + str(row[0])
                Insert_assets_mstr(Secu_DB,MaxID,CamID,str(row[3]))
                Insert_video_security_equip(Secu_DB,MaxID,str(row[4]),str(row[5]),str(row[6]),str(row[7]),str(row[8])  )
                print( "데이터추가됨 = " + str(MaxID) + "\tName = " + str(row[3]) )

    Nubi_DB.close()    
    Secu_DB.close()    

 
if __name__ == '__main__':
    main()
