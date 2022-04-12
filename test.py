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
        house = House(0,y,x).poly        
        angle = (-1*(resPointAngles[i][j])+90)
        house = af.rotate(house, angle)
        if ((j != 0) and (j != len(resPoints[i]))):
            houses.append(house)
        
blockLine = sg.LineString([(0,0),(100,0),(100,100),(0,100)])
block = bg.Block(blockLine)
block.populateWithTownhouses(20, 15)

a = ShapelyMap ()

# for lot in block.lots:
#     a.addPolygon(lot.poly, Tag('building', 'yes'))

for house in houses:
    if (house.geom_type == 'Polygon'):
        a.addPolygon(house, Tag('building','yes'))
        print('yes')

for point in points:
    a.addPoint(point)

a.exportToXml('a.osm')

# STREET_WIDTH = 8
# BLOCK_WIDTH = 75

# a = ShapelyMap ()

# pointA =  (0,10)
# pointB =  (10,10)
# pointC =  (10,0)
# pointD =  (0,0)

# areaABCD = Polygon([pointA, pointB, pointC, pointD])

# houses = []

# for j in range(0,9):
#     for i in range(0, 9):
#         house = House(random.randrange(1,6),0,0).poly
#         if (house != 1):
#             # forward facing house
#             angle = 0
#             setback = -1*(house.exterior.bounds[1]-STREET_WIDTH)+j*BLOCK_WIDTH
#             house = translate(house, i*15, setback)
#             house = rotate(house, angle, Point(0,0))
#             houses.append(house)
#         house = House(random.randrange(1,6),0,0).poly
#         if (house != 1):
#             # backward facing house
#             angle = 180
#             setback = -1*(house.exterior.bounds[1]-STREET_WIDTH)+j*BLOCK_WIDTH
#             house = rotate(house, angle, Point(0,0))
#             house = translate(house, i*15, setback+30)
#             houses.append(house)

# for j in range(0,9):
#     for i in range(0, 9):
#         house = House(random.randrange(1,6),0,0).poly
#         if (house != 1):
#             # forward facing house
#             angle = 0
#             setback = -1*(house.exterior.bounds[1]-STREET_WIDTH)+j*BLOCK_WIDTH
#             house = translate(house, i*15+150, setback)
#             house = rotate(house, angle, Point(0,0))
#             houses.append(house)
#         house = House(random.randrange(1,6),0,0).poly
#         if (house != 1):
#             # backward facing house
#             angle = 180
#             setback = -1*(house.exterior.bounds[1]-STREET_WIDTH)+j*BLOCK_WIDTH
#             house = rotate(house, angle, Point(0,0))
#             house = translate(house, i*15+150, setback+30)
#             houses.append(house)


# for house in houses:
#     a.addPolygon(house, xmlOsm.Tag('building','yes'))


# x = np.linspace(0,10,10)
# y = np.linspace(0,10,10)

# xs, ys = np.meshgrid(x,y,sparse=True)
# points = [(0,0)]


# # for i in range (0,len(x)):
# #     for j in range(0,len(y)):
# #         nx = x[i] + 150*random.random()
# #         ny = y[j] + 150*random.random()
# #         points.append((nx,ny))

# for i in range (0,2):
#     for j in range (0,8):
#         x = 10*i #+ random.randint(-1,1)
#         y = 10*j #+ random.randint(-1,1)
#         points.append((x,y))
    

# points = MultiPoint(points)

# farms = Farmland(points)

# # houserow = HouseRow(5)

# # for house in houserow.houses:
# #     a.addPolygon(house.poly, xmlOsm.Tag('building','yes'))

# # for farm in farms.regions:
# #     # farm = farm.buffer(3)
# #     # farm = farm.buffer(-5)
# #     farm.simplify(0.4, preserve_topology=False)
# #     a.addPolygon(farm, xmlOsm.Tag('building','yes'))

# # b = MultiPoint([(1,0),(3,4),(4,1)]).convex_hull
# # a.addPolygon(b, xmlOsm.Tag('building','yes'))


# a.exportToXml()
