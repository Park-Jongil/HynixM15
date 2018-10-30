import sys
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


def main():
    database = "NaizDB.db"

    iModifyCount = 0
    iAppendCount = 0
    iDeleteCount = 0
    CheckDate = "2018/09/01"
    if (len(sys.argv) > 1) : CheckDate = (sys.argv[1])

    conn = create_connection(database)
    cur = conn.cursor()
    cur.execute("SELECT CheckTime,seq,prevName,name FROM CameraUpdate Where append = '변경' AND CheckTime > '"+CheckDate+"'")
    rows = cur.fetchall()
    print("변경된 내역")
    print(" CheckTime\t\tSequence    Name  <==  PrevName")
    for row in rows :
        print(row[0]+"\t"+str(row[1])+"\t"+row[3]+"\t\t<==\t"+row[2] )
        iModifyCount = iModifyCount + 1

    cur = conn.cursor()
    cur.execute("SELECT CheckTime,seq,name,curr_rtsp_url1 FROM CameraUpdate Where append = '추가' AND CheckTime > '"+CheckDate+"'")
    rows = cur.fetchall()
    print("\n추가된 내역")
    print(" CheckTime\t\tSequence    RTSP Url#1\t\t\t\tName")
    for row in rows :
        print(row[0]+"\t"+str(row[1])+"\t"+row[3]+"\t"+row[2] )
        iAppendCount = iAppendCount + 1

    cur.execute("SELECT seq,name,rtsp_url1 FROM CameraList Where CheckUpdate = 0")
    rows = cur.fetchall()
    print("\n삭제된 내역")
    print(" Sequence    RTSP Url#1\t\t\t\tName")
    for row in rows :
        print(str(row[0])+"\t"+row[2]+"\t"+row[1] )
        iDeleteCount = iDeleteCount + 1

    conn.close()    
    print("\n변경된 작업내용 = " + str(iModifyCount))
    print("추가된 작업내용 = " + str(iAppendCount))
    print("삭제된 작업내용 = " + str(iDeleteCount))

if __name__ == '__main__':
    main()
