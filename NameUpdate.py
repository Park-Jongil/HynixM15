from datetime import datetime
import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None

def Update_Nubicom_DataBase(conn , sql_stmt):
    try :
        cur = conn.cursor()
        cur.execute( sql_stmt )
        conn.commit()
    except :
        return None

def main():
    database = "NaizDB.db"

    conn = create_connection(database)
    cur = conn.cursor()
    cur.execute("SELECT seq,prevName,name,CheckTime FROM CameraUpdate Where append = '변경' and CheckTime > '2018/10/02'")
    rows = cur.fetchall()
    print("변경된 내역")
    print(" Sequence    Name  <==  PrevName")
    for row in rows :
        sql_stmt = "Update tb_skh_point_cctv set  device_name = '" + row[2] + "' Where id = " + str(row[0]) + ";"
#        print( row[3] )
        print( sql_stmt )
        sql_stmt = "Update tbl_NubicomDB set  device_name = '" + row[2] + "' Where id = " + str(row[0]) + ";"
        Update_Nubicom_DataBase( conn , sql_stmt )

    conn.close()    


if __name__ == '__main__':
    main()
