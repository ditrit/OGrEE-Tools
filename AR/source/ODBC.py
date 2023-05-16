import pyodbc

driver="{PostgreSQL ANSI}"
server="chibois.net"
port="2235"
database="raritan"
uid="odbcuser"
pwd="dcTrack$1"
def Init(server,uid,pwd,database="raritan",driver="{PostgreSQL ANSI}",port="2235"):
    global cnxn
    cnxn = pyodbc.connect(f'Driver={driver};Server={server};Port={port};Database={database};Uid={uid};Pwd={pwd};')
    # Python 3.x
    cnxn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
    cnxn.setencoding(encoding='utf-8')

def test():
    if "cnxn" not in globals():
        Init(server,uid,pwd,database,driver,port)

    # Create a cursor from the connection
    cursor = cnxn.cursor()
    cursor.execute('SELECT * from "dcFloormapObjects" where "ItemID" = 3951 ')
    row = cursor.fetchone()
    while row:
        print(row)
        row = cursor.fetchone()