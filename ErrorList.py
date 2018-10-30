import sys
import sqlite3
from sqlite3 import Error
from datetime import datetime

def Check_ErrorList_Update(conn):
    try :
        tablename = "StatusChange" + datetime.today().strftime("%Y%m%d")
        cur = conn.cursor()
        cur.execute("update CameraList set cntError = ( Select count(CameraID) from " + tablename + " where " + tablename + ".CameraName==CameraList.name group by CameraID)")
        conn.commit()
    except :
        print("StatusCamera.py First !!!")
        return None

def main():
    Limit = 0
    isStatus = -1
    if (len(sys.argv) > 1) : Limit = int(sys.argv[1])
    if (len(sys.argv) > 2) : isStatus = int(sys.argv[2])
    db_file = "NaizDB.db"
    conn = sqlite3.connect(db_file)

    Check_ErrorList_Update( conn )
    try :
        cur = conn.cursor()
        cur.execute("SELECT * FROM CameraList order by cntError desc")
        rows = cur.fetchall()
        iTotal = len(rows)
        iTCnt = 0
        iTLive = 0
        iCount = 0
        isAlive = 0
        isMark = 0
        print("인덱스,카메라이름,장비주소,스트림#1,스트림#2,활성여부,에러횟수,NVR_IP,NVR_CH,최근동작시간,최근종료시간")
        for row in rows :
            if (row[1].startswith("*") != True) :
                isMark = isMark + 1
                if (row[5]==1) : iTLive = iTLive + 1
                if ((row[2].startswith("10.")) == True) :
                    if (row[5]==1) : isAlive = isAlive + 1
                    iCount = iCount + 1
                if (len(sys.argv) > 2)  :
                    if (int(row[5])==isStatus) : print( row )
                else :
                    print( row )
            iTCnt = iTCnt + 1
            if (iTCnt==Limit) : break

        conn.close()
        print("전체 리스트  = " + str(iTotal))
        print("별표제외숫자 = " + str(isMark))
        print("전체(활성화) = " + str(iTLive))
        print("===========================================")
        print("4캠(전  체)  = " + str(iCount))
        print("4캠(활성화)  = " + str(isAlive))
        print("===========================================")
        print("전체(비활성) = " + str(isMark-iTLive))
        print("4캠(비활성)  = " + str(iCount-isAlive))
    except :
        print("Execute Error")
        return None

if __name__ == '__main__':
    main()
