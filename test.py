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
import shapely.ops as ops
import math


SETBACK = 10

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
    resLinesL = (street.parallel_offset(SETBACK, 'left'))
    resLinesR = (street.parallel_offset(SETBACK, 'right'))
    # Flip the multipoint
    #resLinesL = ops.transform(lg.reverse, resLinesL)

    # Append multipoints into resLines
    resLines.append(resLinesR)
    resLines.append(resLinesL)

resPoints = []

# Interpolate all streets
for resLine in resLines:
    resPoints.append(lg.getRandomInterpolationPoints(resLine,0,10,100))

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
            print(angle)
            #angle = math.atan2(dy1, dx1)*180/math.pi
            #print(angle)
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

# Invert the streetlines
for i in range (0, len(streetLines)):
    streetLines[i] = ops.transform(lg.flip, streetLines[i])

for i in range(0, len(resPoints)):
    for j in range (0, len(resPoints[i])):
        x = resPoints[i][j].x
        y = resPoints[i][j].y
        points.append(Point(x,y))
        angle = (-1*(resPointAngles[i][j])+90)
        house = House(random.randint(0,0),y,x).poly
        house = Home2(random.uniform(10,15), random.uniform(15,25), sg.Point(y,x), angle)
        if random.random() > 0.5:
            house.makeRearEnclave()
        #house.rotate(angle)
        #shouse.setback(2)
        house = house.poly
        for h in houses:
            house = house.difference(h)
        if (j > 1) and (house.intersects(houses[-1])):
            if random.random() > 0.7:
                # Union
                house = house.union(houses[-1])
                houses.pop()
                #print('union')
            else:
                # Difference
                house = house.difference(houses[-1])
                #print('difference')
        if ((j != 0) and (j != len(resPoints[i]))):
            houseValid = True
            # Check if the house intersects a street
            for street in streetLines:
                if street.intersects(house):
                    # If it does, indicate
                    houseValid = False
            if houseValid == True:
                houses.append(house)


plt.show()

#blockLine = sg.LineString([(0,0),(100,0),(100,100),(0,100)])
#block = bg.Block(blockLine)
#block.populateWithTownhouses(20, 15)

a = ShapelyMap ()

# for lot in block.lots:
#     a.addPolygon(lot.poly, Tag('building', 'yes'))

for house in houses:
    if (house.geom_type == 'Polygon'):
        if(len(house.exterior.coords)) != 0:
            a.addPolygon(house, Tag('building','yes'))

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
    g.createCourtyard(random.randint(22,28))
    g.distortCourtyard(15)
    courtyard = sg.Polygon(g.innerBoundary.coords)
    a.addPolygon(courtyard, Tag('a', 'a'))
    g.subdivideBlockEvenly(random.randint(50,55))
    for lot in g.lots:
        # for lot in block.lots:
        if lot.poly.geom_type == 'Polygon':
            tag = Tag('building', 'yes')
            a.addPolygon(lot.poly, tag)

a.exportToXml('z.osm')


