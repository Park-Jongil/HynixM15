from datetime import datetime
import sqlite3
from sqlite3 import Error
import psycopg2

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None

def create_postgres_connection():
    user = 'postgres'
    password = 'postgres'
    host_product = '10.236.1.42'
    dbname = 'postgres'
    port='5432'
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
    database = "NaizDB.db"

    Nubi_DB = create_postgres_connection()
    conn = create_connection(database)
    cur = conn.cursor()
    cur.execute("SELECT seq,prevName,name,CheckTime FROM CameraUpdate Where append = '변경' and CheckTime > '2018/10/02'")
    rows = cur.fetchall()
    print("변경된 내역")
    print(" Sequence    Name  <==  PrevName")
    for row in rows :
        sql_stmt = "Update tb_skh_point_cctv set  device_name = '" + row[2] + "' Where id = " + str(row[0]) + ";"
        print( sql_stmt )
        if (Nubi_DB != None) :
            sql_stmt = "Update public.tb_skh_point_cctv set  device_name = '" + row[2] + "' Where id = " + str(row[0]) + ";"
            Update_Nubicom_DataBase( Nubi_DB , sql_stmt )

    cur = conn.cursor()
    cur.execute("SELECT * FROM CameraUpdate AS A , CameraList as B Where A.seq==B.seq AND A.append = '추가' and A.CheckTime > '2018/10/02'")
    rows = cur.fetchall()
    print("추가된 내역")
    for row in rows :
        CheckKey = Nubicom_DataBase_Check_byKey( Nubi_DB , str(row[1]) )
        if (CheckKey==None) :
            print("추가가 필요 = " + str(row[1]) + " : " + row[2] )
            sql_stmt = "insert into tb_skh_point_cctv(id,campus_id,building,device_name,device_ip,vms_id,grp_serial,dev_serial,dch_ch,vms_ip,vms_ch,geom,layer,floor,pkuid) values"
            sql_para = "(" + str(row[1]) + ",'4','','" + row[2] + "','" + row[6]+"',100371,1,0,0,'"+row[19]+"','"+row[20]+"','0101000020E61000000ED7195C95DB5F40AE63955A21544240',-10,-10,-10)"
#            print( sql_stmt + sql_para )
            cur = Nubi_DB.cursor()
            cur.execute( sql_stmt + sql_para) 
            Nubi_DB.commit()
        else :
            print("이미 존재함 = " + str(row[1]) + " : " + row[2] )

    conn.close()    


if __name__ == '__main__':
    main()
