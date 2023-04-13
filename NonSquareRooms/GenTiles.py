import argparse
import json
import os
from shapely.geometry import Polygon, box, Point
from shapely import affinity
import turtle

# Generates the coordinates of the squares rotated by angle that can fit into the room. Starts From the first corner in the room's corner list
def GenTilesFromFirstCorner(
    room: Polygon, tileSize: float, angle: float, offset: tuple[float, float]
) -> list[Polygon]:

    # Rotated Bounding Box of the room but realigned to the original axis
    b = RotatedBBox(room, angle)

    # First corner of the room as defined in the JSON
    origin = affinity.rotate(
        Point(room.exterior.xy[0][0], room.exterior.xy[1][0]), -angle, b.centroid
    )
    squares = []

    # We check tiles lines by lines (not column by column). As we start from a corner of the room which can be in the middle of the bounding box,
    # we have to go left-right/up-down to fully cover the bounding box.

    # We start by going right
    x = origin.x + offset[0]

    # Until we reach the bounding box's right side
    while x < b.bounds[2]:
        # We start by going up
        y = origin.y + offset[1]

        # Until we reach the bounding box's top side
        while y < b.bounds[3]:
            square = affinity.rotate(
                box(x, y, x + tileSize, y + tileSize),
                angle,
                b.centroid,
            )
            if room.contains(square.buffer(-1e-10)):
                squares.append(square)
            y += tileSize

        # Then we go down
        y = origin.y + offset[1]

        # Until we reach the bottom side
        while y > b.bounds[1]:
            square = affinity.rotate(
                box(x, y, x + tileSize, y + tileSize),
                angle,
                b.centroid,
            )
            if room.contains(square.buffer(-1e-10)):
                squares.append(square)
            y -= tileSize
        x += tileSize

    # Then we go left
    x = origin.x + offset[0]

    # Until we reach the left side
    while x > b.bounds[0]:

        x -= tileSize
        # We do the same thing vertically
        y = origin.y + offset[1]
        while y < b.bounds[3]:
            square = affinity.rotate(
                box(x, y, x + tileSize, y + tileSize),
                angle,
                b.centroid,
            )
            if room.contains(square.buffer(-1e-10)):
                squares.append(square)
            y += tileSize
        y = origin.y + offset[1]
        while y > b.bounds[1]:
            square = affinity.rotate(
                box(x, y, x + tileSize, y + tileSize),
                angle,
                b.centroid,
            )
            if room.contains(square.buffer(-1e-10)):
                squares.append(square)
            y -= tileSize
    return squares


# Returns a rectangle Polygon which is the bounding box of polygon aligned with an axis set rotated by theta from the orignal axis x and y.
# However, the bounding box is rotated back (by -theta) to be aligned with the orignal axis. So, in most cases, it is not a bounding box of polygon
def RotatedBBox(polygon: Polygon, theta: float) -> Polygon:

    # First, we compute the bounding box of the polygon without rotation
    rectangle = box(
        polygon.bounds[0],
        polygon.bounds[1],
        polygon.bounds[2],
        polygon.bounds[3],
    )

    # We rotate the rectangle by the angle theta and construct the minimum rotated rectangle that contains polygon.
    # This can be done by creating a rectangle with side length equal to the maximum dimension of the rotated bounding box, and rotating it by theta degrees.
    bbox = affinity.rotate(rectangle, theta).bounds
    rectangle = box(
        bbox[0],
        bbox[1],
        bbox[2],
        bbox[3],
    )

    # Finally, we return the non rotated rectangle, which is our desired result
    return rectangle


# Generates the coordinates of the squares rotated by angle that can fit into the room. Starts From the down/left corner of the room's rotated bounding box + (offsetX,offsetY)
def GenTilesWithOffset(
    room: Polygon, tileSize: float, angle: float, offsetX: float, offsetY: float
) -> list[Polygon]:
    b = RotatedBBox(room, angle)
    squares = []

    # Start from the down/left corner of the Bounding box so we don't have to go left or down to cover all the bounding box
    x = b.bounds[0] + offsetX
    while x < b.bounds[2]:
        y = b.bounds[1] + offsetY
        while y < b.bounds[3]:
            square = affinity.rotate(
                box(x, y, x + tileSize, y + tileSize),
                angle,
                b.centroid,
            )
            if room.contains(square.buffer(-1e-10)):
                squares.append(square)
            y += tileSize
        x += tileSize
    return squares


# Returns the tiling with the most tiles of the room by checking different angle/offset combinations
def GetBestTiling(room: Polygon, tileSize: float) -> tuple[list[Polygon], float]:
    bestTiling = []
    bestangle = 0
    totalSteps = 1200  # 12 * 10 * 10
    step = 1

    # Check 12 different angles
    for angle in range(0, 360, 30):
        offsetX = 0

        # offset should not be more than tileSize because we'll just be losing a tile
        while offsetX < tileSize:
            offsetY = 0
            while offsetY < tileSize:
                tiling = GenTilesWithOffset(room, tileSize, angle, offsetX, offsetY)
                if len(tiling) > len(bestTiling):
                    bestTiling = tiling
                    bestangle = angle

                # check 10 different offsetX
                offsetY += tileSize / 10
                print(f"step {step} of {totalSteps} : {len(tiling)} tiles")
                step += 1

            # check 10 different offsetX
            offsetX += tileSize / 10
    return (bestTiling, bestangle)


# Move the pen without tracing
def Move(pos: tuple[float, float], t: turtle.Turtle) -> None:
    t.penup()
    t.setposition(pos)
    t.pendown()


# Draw the room with its tiles
def Draw(room: Polygon, squares: list[Polygon]) -> None:

    # Setup turtle
    turtle.TurtleScreen._RUNNING = True
    canvas = turtle.Screen()
    canvas.screensize(20000, 20000)
    t = turtle.Turtle(visible=False)

    # No delay when drawing
    turtle.tracer(0, 0)

    # Coloring tiles in green
    t.fillcolor((0, 0.3, 0))
    for square in squares:
        coord = [
            (square.exterior.coords.xy[0][i] *50, square.exterior.coords.xy[1][i] *50)
            for i in range(len(square.exterior.coords.xy[0]) - 1)
        ]
        Move(coord[0], t)
        t.begin_fill()
        for dot in coord[1:]:
            t.setposition(dot)
        t.setposition(coord[0])
        t.end_fill()
    coord = [
        (room.exterior.coords.xy[0][i] *50, room.exterior.coords.xy[1][i] *50)
        for i in range(len(room.exterior.coords.xy[0]) - 1)
    ]
    Move(coord[0], t)

    # Drawing room walls in bold black
    t.width(3)
    for dot in coord[1:]:
        t.setposition(dot)
    t.setposition(coord[0])
    t.width(1)
    canvas.exitonclick()


# Write a JSON template of a OGrEE room with its tiles, generated according to the parameters
def processJSON(
    path: str,
    tileSize: str | float | None,
    angle: str | float | None,
    offset: str | tuple[float, float] | None,
    draw: bool = False,
    outname: str|None = None,
    opti: bool = False,
) -> None:

    # Convert parameters to correct types
    tileSize = float(tileSize) if tileSize is not None else 0.6
    angle = float(angle) if angle is not None else 0
    offset = (
        tuple(float(s) for s in str(offset).strip("()").split(","))
        if offset is not None
        else (0, 0)
    )

    with open(path) as roomFile:
        room = json.load(roomFile)
    roomPoly = Polygon(room["vertices"])
    if opti:
        tiles, angle = GetBestTiling(roomPoly, tileSize)
    else:
        tiles = GenTilesFromFirstCorner(roomPoly, tileSize, angle, offset)
    new_tiles = []

    correction = (round(tiles[0].centroid.x,2), round(tiles[0].centroid.y,2))

    orientX, orientY = (
        -1 if "-x" in room["axisOrientation"] else 1,
        -1 if "-y" in room["axisOrientation"] else 1,
    )

    for tile in tiles:
        new_tiles.append(
            {
                "location": f"{str(round(tile.centroid.x,4))}/{str(round(tile.centroid.y,4))}",
                "name": "",
                "label": f"{str(orientX *  round((round(tile.centroid.x,2)-correction[0])/tileSize))}/{str(orientY * round((round(tile.centroid.y,2)-correction[1])/tileSize))}",
                "texture": "",
                "color": "",
            }
        )

    room["tiles"] = new_tiles
    room["tileAngle"] = angle
    room["center"] = [round(roomPoly.centroid.x,2), round(roomPoly.centroid.y,2)]
    if outname is None:
        with open(
            f"{os.path.dirname(path)}/{os.path.splitext(os.path.basename(path))[0]}-tiles.json",
            "w",
        ) as file:
            file.write(json.dumps(room, indent=4))
    else:
        with open(f"{os.path.dirname(path)}/{outname}", "w") as file:
            file.write(json.dumps(room, indent=4))

    if draw:
        Draw(Polygon([(corner[0], corner[1]) for corner in room["vertices"]]), tiles)


#########################################################################################################

if __name__ == "__main__":

    # COMMAND OPTIONS
    parser = argparse.ArgumentParser(
        description="Generate the tiles of a non convex room for OGrEE  (all unit are in meter)"
    )

    parser.add_argument("--json", help="""Path of the room JSON""", required=True)
    parser.add_argument("--out", help="""Name of the returned JSON""")
    parser.add_argument("--angle", help="""tiling's angle (0 by default) (degree)""")
    parser.add_argument(
        "--offset", help="""first tile's offset from the first vertex : x,y (m)"""
    )
    parser.add_argument(
        "--draw",
        help="""If you want python to draw the room with turtle""",
        action="store_true",
    )
    parser.add_argument(
        "--opti",
        help="""If you want python iterate through multiple angles and start positions to get the best tiling (SLOW)""",
        action="store_true",
    )

    parser.add_argument("--tileSize", help="""Size of a tile (60cm by default) (m)""")

    args = vars(parser.parse_args())

    processJSON(
        args["json"],
        args["tileSize"],
        args["angle"],
        args["offset"],
        args["draw"],
        args["out"],
        args["opti"],
    )
