# || Swami-Shriji ||

# --------------------------------- #
#             Libraries             #
# --------------------------------- #
import shapely.geometry as sg
import osmElements as oe

# --------------------------------- #
#             Constants             #
# --------------------------------- #

# --------------------------------- #
#          Common Functions         #
# --------------------------------- #
def getNodeFromPoint(point):
  return oe.Node(point.x, point.y)

def getNodeFromCoord(coord):
  return oe.Node(coord[0], coord[1])

def getWayFromLineString (lineString):
  nodes = []
  for coord in lineString.coords:
    nodes.append(getNodeFromCoord(coord))
  return oe.Way(nodes)

def getAreaFromPolygon (polygon):
  nodes = []
  for coord in polygon.exterior.coords:
    nodes.append(getNodeFromCoord(coord))
  return oe.Area(nodes)

def getRectangleFromWh(width, height, anchorPoint, angle):
  sg.Point(anchorPoint.x - width/2)
  

# --------------------------------- #
#              Classes              #
# --------------------------------- #

class House:

  def getPolygon(self):


  def __init__(self, width=10, height=10, anchorPoint=sg.Point(0,0),angle=0):




