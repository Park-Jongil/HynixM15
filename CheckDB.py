import sqlite3
from sqlite3 import Error

db_file = "NaizDB.db"
conn = sqlite3.connect(db_file)

cur = conn.cursor()
cur.execute("SELECT seq,rtsp_url1 FROM CameraList")
rows = cur.fetchall()
iTotal = len(rows)
for row in rows :
    rtsp1 = row[1]
    vms_ip = rtsp1.replace('rtsp://',"") 
    vms_ip = vms_ip[0:vms_ip.find(":80")]
    vms_ch = rtsp1[rtsp1.find(":80")+3:]
    vms_ch = vms_ch.replace('stream1',"") 
    vms_ch = vms_ch.replace('/',"") 

    sql_stmt = "update CameraList set vms_ip=?,vms_ch=? where seq = ?"
    cur.execute( sql_stmt,(vms_ip,vms_ch,int(row[0])))
    conn.commit()

    print("Vms_IP = " + vms_ip)
    print("Vms_Ch = " + vms_ch)

#        print( row )

conn.close()
#for row in rows :  print( row )
#rtsp://172.18.200.35:80/112/stream1
