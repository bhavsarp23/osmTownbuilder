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

def getRectangleFromWh(width, height, anchorPoint=sg.Point(0,0)):
  a = sg.Point(anchorPoint.x - width/2, anchorPoint.y - height/2)
  b = sg.Point(anchorPoint.x - width/2, anchorPoint.y + height/2)
  c = sg.Point(anchorPoint.x + width/2, anchorPoint.y - height/2)
  d = sg.Point(anchorPoint.x + width/2, anchorPoint.y + height/2)
  return sg.Polygon([a,b,c,d])

# --------------------------------- #
#              Classes              #
# --------------------------------- #

class House:

  def getPolygon(self):
    pass


  def __init__(self, width=10, height=10, anchorPoint=sg.Point(0,0),angle=0):
    pass




a = getRectangleFromWh(10,20,sg.Point(5,5))
for coord in a.exterior.coords:
  print(coord)




