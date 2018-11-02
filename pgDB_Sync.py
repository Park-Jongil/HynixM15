from datetime import datetime
import sqlite3
from sqlite3 import Error
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
    Naiz_DB = create_postgres_connection("10.236.1.42","NaizCamera","postgres","postgres","5432")
    Nubi_DB = create_postgres_connection("10.236.1.42","postgres","postgres","postgres","5432")
    if (Naiz_DB != None and Nubi_DB != None) :
        cur = Naiz_DB.cursor()
        cur.execute("SELECT seq,prevname,device_name,checktime,curr_ip_addr FROM cameraupdate Where append = '변경' and checktime > '2018/10/02'")
        rows = cur.fetchall()
        if (rows != None and len(rows) > 0) :
            print("변경된 내역")
            print("  Sequence    Name  <==  PrevName")
            for row in rows :
                sql_stmt = "Update tb_skh_point_cctv set  device_name = '" + row[2] + "' Where id = " + str(row[0]) + ";"
                print( sql_stmt )
                if (Nubi_DB != None) :
                    sql_stmt = "Update public.tb_skh_point_cctv set device_name='"+row[2]+"',device_ip='"+row[4]+"' Where id = " + str(row[0]) + ";"
                    Update_Nubicom_DataBase( Nubi_DB , sql_stmt )

        cur = Naiz_DB.cursor()
        cur.execute("SELECT A.seq,A.device_name,A.curr_ip_addr,B.vms_ip,B.vms_ch FROM cameraupdate AS A , cameralist as B Where A.seq=B.seq AND A.append = '추가' and A.checktime > '2018/10/02'")
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
                else :
                    print("  이미 존재함 = " + str(row[1]) + " : " + row[2] )

    Nubi_DB.close()    
    Naiz_DB.close()    


if __name__ == '__main__':
    main()
