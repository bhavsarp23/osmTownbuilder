# || Swami-Shriji ||

# --------------------------------- #
#             Libraries             #
# --------------------------------- #
import shapely.geometry as sg
import shapely.affinity as sa
import shapely.ops as so
import osmElements as oe
import random as rd
import math
import numpy as np

import time
import matplotlib.pyplot as plt

# --------------------------------- #
#             Constants             #
# --------------------------------- #

# --------------------------------- #
#          Common Functions         #
# --------------------------------- #
def sign(x):
  if x > 0:
    return 1
  if x < 0:
    return -1
  else:
    return 0

def getMeterFromCoord(value):
  return value#value*oe.METER_CONV

def getPointFromNode(node):
  x = getMeterFromCoord(float(node.lon))
  y = getMeterFromCoord(float(node.lat))
  return sg.Point(y,x)

def getNodeFromPoint(point):
  return oe.Node(point.x, point.y)

def getAngleOfTwoPoints(a,b,using_degrees=True):
  dy = b.y-a.y
  dx = b.x-a.x
  angle = math.atan2(dy,dx)+math.pi/2
  if using_degrees:
    angle = angle*180/math.pi
  return angle

def getNodeFromCoord(coord):
  return oe.Node(coord[0], coord[1])

def getLineStringFromWay(way):
  points = [getPointFromNode(node) for node in way.refs]
  # for node in way.refs:
  #   points.append(getPointFromNode(node))

  return sg.LineString(points)

def getInterpolatedPointsByDistance(lineString, distanceDelta):
  distances = np.arange(0,line.length,distanceDelta)
  points = []
  for distance in distances:
      points.append(line.interpolate(distance))
  return points

def getWayFromLineString (lineString):
  nodes = []
  for coord in lineString.coords:
    nodes.append(getNodeFromCoord(coord))
  return oe.Way(nodes)

def getAreaFromPolygon (polygon):
  if polygon.geom_type == 'Polygon':
    return oe.Area([getNodeFromCoord(coord) for coord in polygon.exterior.coords])
  else:
    return oe.Area([getNodeFromCoord(coord) for coord in polygon[0].exterior.coords])
  # nodes = []
  # for coord in polygon.exterior.coords:
  #   nodes.append(getNodeFromCoord(coord))
  # return oe.Area(nodes)

def getRectangleFromWh(width, height, anchorPoint=sg.Point(0,0)):
  a = sg.Point(anchorPoint.x - width/2, anchorPoint.y - height/2)
  b = sg.Point(anchorPoint.x + width/2, anchorPoint.y - height/2)
  c = sg.Point(anchorPoint.x + width/2, anchorPoint.y + height/2)
  d = sg.Point(anchorPoint.x - width/2, anchorPoint.y + height/2)
  return sg.Polygon([a,b,c,d])

def getPolarFromCart(x, y):
  r = math.sqrt(x*x+y*y)
  angle = math.atan2(y,x)*180/math.pi
  return[r,angle]

def getCartFromPolar(r, angle, using_degrees=True):
  if using_degrees:
    angle = angle*math.pi/180
  x = r*math.cos(angle)
  y = r*math.sin(angle)
  return [x,y]

def getNeighborsOfPoly(poly, others):
  neighbors = []
  for geom in others:
    if geom is not poly and poly.overlaps(geom):
      neighbors.append(geom)
  return neighbors

def trimNeighbors(poly, others):
  neighbors = getNeighborsOfPoly(poly, others)
  for neighbor in neighbors:
    poly = poly.difference(neighbor)
  return poly

# --------------------------------- #
#              Classes              #
# --------------------------------- #

class Street:

  def isOneway(self):
    for tag in self.tags:
      if tag.k == 'oneway' and tag.v == 'yes':
        return True
    return False

  def getTypeOfStreet(self):
    for tag in self.tags:
      if tag.k == 'construction':
        return tag.v
    return 'none'

  def __parseWay(self, way):
    self.tags = way.tags
    self.lineString = getLineStringFromWay(way)

  def getHouses(self, setback=10, lot_size=15):
    # Get parallel offsets of the street
    rightString = self.lineString.parallel_offset(setback, 'right')

    cumalativeWidth = 0
    houses = []

    houseAnchor = sg.Point(rightString.coords[0])

    while cumalativeWidth < rightString.length:

      print(cumalativeWidth, rightString.length)

      # Determine width of the house
      width = rd.uniform(10, 20)
      height = rd.uniform(25, 35)

      # Interpolate the first point at width
      newHouseAnchor = sg.Point(rightString.interpolate(cumalativeWidth+width/2))
      cumalativeWidth += width

      # Get angle of newHouseAnchor and previous point
      angle = getAngleOfTwoPoints(newHouseAnchor, houseAnchor)
      houseAnchor = newHouseAnchor

      house = House(width, height, houseAnchor)
      house.rotate(angle)
      house.setback(height/2)
      houses.append(house)

    if not self.isOneway():
      leftString = self.lineString.parallel_offset(setback, 'left')

      houseAnchor = sg.Point(rightString.coords[0])

      cumalativeWidth = 0

      while cumalativeWidth < leftString.length:

        # Determine width of the house
        width = rd.uniform(10, 20)
        height = rd.uniform(25, 35)

        # Interpolate the first point at width
        newHouseAnchor = sg.Point(leftString.interpolate(cumalativeWidth+width/2))
        cumalativeWidth += width

        # Get angle of newHouseAnchor and previous point
        angle = getAngleOfTwoPoints(newHouseAnchor, houseAnchor)
        houseAnchor = newHouseAnchor

        house = House(width, height, houseAnchor)
        house.rotate(angle)
        house.setback(height/2)
        houses.append(house)

    return houses

  def __init__(self, geom):
    if type(geom) == oe.Way:
      self.__parseWay(geom)

    elif type(geom) == sg.LineString:
      self.lineString = geom
      self.tags = [oe.Tag('highway', 'residential')]

class House:

  def getPolygon(self):
    pass

  def translate(self, dx, dy):
    self.poly = sa.translate(self.poly, dx, dy)
    self.anchorPoint = sa.translate(self.anchorPoint, dx, dy)

  def rotate(self, angle, origin='centroid'):
    self.angle = (self.angle + angle)%360
    self.poly = sa.rotate(self.poly, angle, origin)

  def setback(self,setback):
    dx, dy = getCartFromPolar(setback, self.angle+90, using_degrees=True)
    self.translate(dx,dy)

  def slide(self, delta):
    dx, dy = getCartFromPolar(delta, self.angle)
    self.translate(dx, dy)

  def __init__(self, width=10, height=10, anchorPoint=sg.Point(0,0),angle=0):
    self.width = width
    self.height = height
    self.anchorPoint = anchorPoint
    self.angle = 0
    self.poly = getRectangleFromWh(width, height, anchorPoint)
    self.tags = [oe.Tag('building', 'residential')]
    # Setback
    #self.translate(0, height/2)
    self.rotate(angle+90)

  def difference(self, other):
    if other.poly.geom_type == 'Polygon':
      self.poly = self.poly.difference(other.poly)
    elif other.poly.geom_type == 'MultiPolygon':
      for geom in other.poly.geoms:
        self.poly = self.poly.difference(geom)
    
  def union(self, other):
    poly = so.unary_union([self.poly, other.poly])
    if poly.geom_type == 'Polygon':
      self.poly = poly
      return True
    return False

  def intersects(self, other):
    return self.poly.intersects(other.poly)    

  def makeRearEnclave(self):
    # Get width & height
    width = rd.uniform(self.width/4, 2*self.width/3)
    height = rd.uniform(self.height/6, self.height)

    # Get back of house
    backOfHouse = sg.LineString([self.poly.exterior.coords[2],self.poly.exterior.coords[3]])
    
    # Get point on back of house
    #distance = rd.uniform(0, self.width)
    distance = rd.choice([0, self.width/2, self.width])
    enclaveCenter = backOfHouse.interpolate(distance)

    # Get rectangle
    enclave = getRectangleFromWh(width, height, enclaveCenter)
    enclave = sa.rotate(enclave, self.angle)

    # Make difference with poly
    self.poly = self.poly.difference(enclave)

  def getOsmElement(self):
    way = getAreaFromPolygon(self.poly)
    way.addTags(self.tags)
    return way

class Keepout:

  def __init__(self, poly):
    self.poly = poly

  def add(self, other):
    self.poly = so.unary_union([self.poly, other.poly])

if __name__ == "__main__":
  start_time = time.time()

  streetWays = oe.getConstructionStreets()
  houses = []
  for streetWay in streetWays:
    street = Street(getLineStringFromWay(streetWay))
    houses.extend(street.getHouses(12))
  houseWays = []

  keepout = []
  streetLines = [getLineStringFromWay(way) for way in streetWays]

  for i, house in enumerate(houses):
    house_invalid=False
    for line in streetLines:
      if house.poly.intersects(line):
        house_invalid = True
    if house_invalid == False:
      house.makeRearEnclave()
      keepout.append(house.poly)
      house.poly = trimNeighbors(house.poly, keepout)
      #house.tags.extend([oe.Tag('addr:housenumber', str(453-i*2))])
      houseWays.append(house.getOsmElement())

  map = oe.OsmMap()

  map.addWays(houseWays)
  map.writeToFile('z.osm')

  print((time.time() - start_time)*1000, "ms")
