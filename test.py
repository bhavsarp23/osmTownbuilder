from xmlOsm.xmlOsm import *
from shapelyOsm.shapelyOsm import *
from house.houseBuilder import *
from random import randrange
from farms.farmBuilder import *
from shapely.geometry import MultiPoint
import shapely.geometry as sg
import numpy as np
import numpy.random
from xmlOsm import xmlOsm as xo
import lineGeo.lineGeo as lg
import shapely.affinity as af
import lineGeo.blockGeo as bg

import math



streets = xo.getConstructionStreets()
streetLines = []

# Turn streets into lineString
for street in streets:
    points = []
    # Turn nodes into points
    for node in street:
        point = Point(float(node.lon), float(node.lat))
        points.append(point)
    streetLine = LineString(MultiPoint(points))
    streetLines.append(streetLine)

resLines = []

# Offset all streets on both sides
for street in streetLines:
    resLines.append(street.parallel_offset(20, 'left'))
    resLines.append(street.parallel_offset(20, 'right'))

resPoints = []

# Interpolate all streets
for resLine in resLines:
    resPoints.append(lg.getInterpolatedPointsByDistance(resLine,20))

resPointAngles = []

# Get tangent angles of those points
for multipoint in resPoints:
    multipointAngles = []
    for i in range(0, len(multipoint)):
        # If it is not the first or last poinft
        point = multipoint[i]
        if ((i != 0) and (i != len(multipoint)-1)):
            dx1 = multipoint[i-1].x - multipoint[i].x
            dy1 = multipoint[i-1].y - multipoint[i].y
            dx2 = multipoint[i].x - multipoint[i+1].x
            dy2 = multipoint[i].y - multipoint[i+1].y
            angle1 = math.atan2(dy1, dx1)
            angle2 = math.atan2(dy2, dx2)
            angle = ((angle1+angle2)/2)*180/math.pi
        else:
            angle = 0
        multipointAngles.append(angle)
    resPointAngles.append(multipointAngles)



houses = []
points = []
# for multipoint in resPoints:
#     for point in multipoint:
#         house = House(0,point.y, point.x)
#         houses.append(house)

for i in range(0, len(resPoints)):
    for j in range (0, len(resPoints[i])):
        x = resPoints[i][j].x
        y = resPoints[i][j].y
        points.append(Point(x,y))
        house = House(random.randint(0,0),y,x).poly
        angle = (-1*(resPointAngles[i][j])+90)
        house = af.rotate(house, angle)
        if ((j != 0) and (j != len(resPoints[i]))):
            houses.append(house)

#blockLine = sg.LineString([(0,0),(100,0),(100,100),(0,100)])
#block = bg.Block(blockLine)
#block.populateWithTownhouses(20, 15)

a = ShapelyMap ()

# for lot in block.lots:
#     a.addPolygon(lot.poly, Tag('building', 'yes'))

for house in houses:
    if (house.geom_type == 'Polygon'):
        a.addPolygon(house, Tag('building','yes'))
        print('yes')

for point in points:
    a.addPoint(point)


blocks = xo.getConstructionBlocks ()
blockRings = []

for block in blocks:
    # Turn nodes into linearRing
    points = []
        # Turn nodes into points
    for node in block:
        point = Point(float(node.lat), float(node.lon))
        points.append(point)
    blockRing = LineString(MultiPoint(points))
    blockRings.append(blockRing)


blockLots = []

for block in blockRings:
    g = bg.Block(block)
    g.createCourtyard(random.randint(22,24))
    g.subdivideBlockEvenly(random.randint(21,25))
    for lot in g.lots:
        # for lot in block.lots:
        if lot.poly.geom_type == 'Polygon':
            a.addPolygon(lot.poly, Tag('building', 'yes'))

a.exportToXml('a.osm')


