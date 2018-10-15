from datetime import datetime
import sqlite3
from sqlite3 import Error
import psycopg2
import pandas as pd

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None

def pg_create_connection(user,password,host,dbname,port):
    try:
        product_connection_string = "dbname={dbname} user={user} host={host} password={password} port={port}"\
                            .format(dbname=dbname,
                                    user=user,
                                    host=host,
                                    password=password,
                                    port=port)   
        product = psycopg2.connect(product_connection_string)
        return product
    except Error as e:
        print(e)
    return None


def main():
    database = "NaizDB.db"

# Sqlite Connection    
    conn = create_connection(database)
# Postgres Connection    
    pg_con = None
#    pg_con = pg_create_connection("admin","admin","10.236.1.42","postgres",542)

    cur = conn.cursor()
    cur.execute("SELECT seq,prevName,name,CheckTime FROM CameraUpdate Where append = '변경' and CheckTime > '2018/09/21'")
    rows = cur.fetchall()

    if (len(rows) != 0) :
        print("변경된 내역")
        print(" Sequence    Name  <==  PrevName")
        for row in rows :
            sql_stmt = "Update tb_skh_point_cctv set  device_name = '" + row[2] + "' Where id = " + str(row[0]) + ";"
            print( sql_stmt )
            if (pg_con != None):
                try: 
                    cur_pg = pg_con.cursor()
                    cur_pg.execute(sql_stmt)
                except:
                    print("Postgres Error")

    else :
        print("변경된 내역이 존재하지 않습니다.")
    conn.close()    


if __name__ == '__main__':
    main()
