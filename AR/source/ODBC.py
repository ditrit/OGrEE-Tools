"""
ODBC module for dcTrack
"""
import pyodbc
from common.Utils import ReadEnv
import os

env = ReadEnv(f"{os.path.dirname(__file__)}/../.env.json")["odbc"]


def Init(
    server: str,
    uid: str,
    pwd: str,
    database: str = "raritan",
    driver: str = "{PostgreSQL ANSI}",
    port: str = "2235",
):
    """Initialise the ODBC connection

    :param server: server address
    :type server: str
    :param uid: user ODBC login
    :type uid: str
    :param pwd: user ODBC password
    :type pwd: str
    :param database: database name, defaults to "raritan"
    :type database: str, optional
    :param driver: driver name, defaults to "{PostgreSQL ANSI}"
    :type driver: str, optional
    :param port: port number, defaults to "2235"
    :type port: str, optional
    """
    global cnxn
    cnxn = pyodbc.connect(
        driver=driver, server=server, port=port, database=database, uid=uid, pwd=pwd
    )
    # Python 3.x
    cnxn.setdecoding(pyodbc.SQL_WCHAR, encoding="utf-8")
    cnxn.setencoding(encoding="utf-8")


def GetPosition(rackName:str=None, rackID:str=None)->list:
    """Get the position of a rack in its room

    :param rackName: name of the rack, used if rackID is None, defaults to None
    :type rackName: str, optional
    :param rackID: ID of the rack, used if not None, defaults to None
    :type rackID: str, optional
    :raises Exception: If rackName and rackID are None
    :return: A list containing the MinY, MinX and Frontfaces lines of the rack
    :rtype: list
    """
    if "cnxn" not in globals():
        Init(
            env["server"],
            env["uid"],
            env["pwd"],
            env["database"],
            env["driver"],
            env["port"],
        )
    if rackID is None and rackName is None:
        raise Exception("Must give an id or a rack name")
    cursor = cnxn.cursor()
    if rackID is not None:
        return cursor.execute(
            f'SELECT "MinY","MinX","FrontFaces" from "dcFloormapObjects" where "ItemID" = {rackID}'
        ).fetchone()
    return cursor.execute(
        f'SELECT "MinY","MinX","FrontFaces" from "dcFloormapObjects" where "ItemName" =\'{rackName}\''
    ).fetchone()


def GetRoomOrientation(roomName:str=None, roomID:str=None)->list:
    """Get the orientation of a room

    :param roomName: name of the room, used if roomID is None, defaults to None
    :type roomName: str, optional
    :param roomID: ID of the room, used if not None, defaults to None
    :type roomID: str, optional
    :raises Exception: If roomName and roomID are None
    :return: A list containing the OrientationNorthSouth and OrientationEastWest lines of the room
    :rtype: list
    """
    if "cnxn" not in globals():
        Init(
            env["server"],
            env["uid"],
            env["pwd"],
            env["database"],
            env["driver"],
            env["port"],
        )
    if roomID is None and roomName is None:
        raise Exception("Must give an id or a room name")
    cursor = cnxn.cursor()
    if roomID is not None:
        request = cursor.execute(
            f'SELECT "OrientationNorthSouth","OrientationEastWest" from "dcRooms" where "ID" = {roomID}'
        ).fetchone()
    else:
        request = cursor.execute(
            f'SELECT "OrientationNorthSouth","OrientationEastWest" from "dcRooms" where "LocationName" =\'{roomName}\''
        ).fetchone()
    return (True if request[0] == "1" else False, True if request[1] == "1" else False)
