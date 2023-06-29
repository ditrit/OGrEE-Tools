import pyodbc

driver="{PostgreSQL ANSI}"
server="chibois.net"
port="2235"
database="raritan"
uid="odbcuser"
pwd="dcTrack$1"
def Init(server,uid,pwd,database="raritan",driver="{PostgreSQL ANSI}",port="2235"):
    global cnxn
    cnxn = pyodbc.connect(driver=driver,server=server,port=port,database=database,uid=uid,pwd=pwd)
    # Python 3.x
    cnxn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
    cnxn.setencoding(encoding='utf-8')

def GetPosition(rackName=None,rackID=None):
    if "cnxn" not in globals():
        Init(server,uid,pwd,database,driver,port)
    if (rackID is None and rackName is None):
        raise Exception("Must give an id or a rack name")
    cursor = cnxn.cursor()
    if (rackID is not None):
        return cursor.execute(f'SELECT "MinY","MinX","FrontFaces" from "dcFloormapObjects" where "ItemID" = {rackID}').fetchone()
    return cursor.execute(f'SELECT "MinY","MinX","FrontFaces" from "dcFloormapObjects" where "ItemName" =\'{rackName}\'').fetchone()

def GetRoomOrientation(roomName=None,roomID=None):
    if "cnxn" not in globals():
        Init(server,uid,pwd,database,driver,port)
    if (roomID is None and roomName is None):
        raise Exception("Must give an id or a room name")
    cursor = cnxn.cursor()
    if (roomID is not None):
        request = cursor.execute(f'SELECT "OrientationNorthSouth","OrientationEastWest" from "dcRooms" where "ID" = {roomID}').fetchone()
    else:
        request = cursor.execute(f'SELECT "OrientationNorthSouth","OrientationEastWest" from "dcRooms" where "LocationName" =\'{roomName}\'').fetchone()
    return (True if request[0] == '1' else False,True if request[1] == '1' else False)