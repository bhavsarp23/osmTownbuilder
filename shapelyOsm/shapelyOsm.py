import shapely
from xmlOsm.xmlOsm import *
from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.geometry import LineString


def xyTransposer(x, y):
    coords = []
    if len(x) != len(y):
        return coords
    
    for i in range(0,len(x)):
        coords.append([x[i],y[i]])

    return coords

class ShapelyMap:

    Map = 0

    def __init__ (self):
        self.Map = OsmMap()

    def addPoint (self, point, tags=[]):
        node = Node(point.x, point.y)
        node.addTags(tags)
        self.Map.addNode(node)

    def addLinestring (self, linestring, tags=[]):
        coords = list(linestring.coords)
        coords = [Node(pair[1],pair[0]) for pair in coords]
        way = Way(coords)
        way.addTags(tags)
        self.Map.addWay(way)

    def addPolygon (self, polygon, tags=[]):
        coords = list(polygon.exterior.coords)
        coords = [Node(pair[0],pair[1]) for pair in coords]
        coords.pop()
        area = Area(coords)
        area.addTags(tags)
        self.Map.addArea(area)

    def exportToXml(self, filename='output.osm'):
        self.Map.exportToXml(filename)


