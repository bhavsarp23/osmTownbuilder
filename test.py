from xmlOsm.xmlOsm import *
from shapelyOsm.shapelyOsm import *
from house.houseBuilder import *
from random import randrange
from farms.farmBuilder import *
from shapely.geometry import MultiPoint
import numpy as np
import numpy.random
from xmlOsm import xmlOsm


STREET_WIDTH = 8
BLOCK_WIDTH = 75

a = ShapelyMap ()

pointA =  (0,10)
pointB =  (10,10)
pointC =  (10,0)
pointD =  (0,0)

areaABCD = Polygon([pointA, pointB, pointC, pointD])

houses = []

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

for j in range(0,9):
    for i in range(0, 9):
        house = House(random.randrange(1,6),0,0).poly
        if (house != 1):
            # forward facing house
            angle = 0
            setback = -1*(house.exterior.bounds[1]-STREET_WIDTH)+j*BLOCK_WIDTH
            house = translate(house, i*15+150, setback)
            house = rotate(house, angle, Point(0,0))
            houses.append(house)
        house = House(random.randrange(1,6),0,0).poly
        if (house != 1):
            # backward facing house
            angle = 180
            setback = -1*(house.exterior.bounds[1]-STREET_WIDTH)+j*BLOCK_WIDTH
            house = rotate(house, angle, Point(0,0))
            house = translate(house, i*15+150, setback+30)
            houses.append(house)


for house in houses:
    a.addPolygon(house, xmlOsm.Tag('building','yes'))


x = np.linspace(0,10,10)
y = np.linspace(0,10,10)

xs, ys = np.meshgrid(x,y,sparse=True)
points = [(0,0)]


# for i in range (0,len(x)):
#     for j in range(0,len(y)):
#         nx = x[i] + 150*random.random()
#         ny = y[j] + 150*random.random()
#         points.append((nx,ny))

for i in range (0,2):
    for j in range (0,8):
        x = 10*i #+ random.randint(-1,1)
        y = 10*j #+ random.randint(-1,1)
        points.append((x,y))
    

points = MultiPoint(points)

farms = Farmland(points)

# houserow = HouseRow(5)

# for house in houserow.houses:
#     a.addPolygon(house.poly, xmlOsm.Tag('building','yes'))

# for farm in farms.regions:
#     # farm = farm.buffer(3)
#     # farm = farm.buffer(-5)
#     farm.simplify(0.4, preserve_topology=False)
#     a.addPolygon(farm, xmlOsm.Tag('building','yes'))

# b = MultiPoint([(1,0),(3,4),(4,1)]).convex_hull
# a.addPolygon(b, xmlOsm.Tag('building','yes'))


a.exportToXml()
