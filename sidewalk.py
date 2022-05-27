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

SETBACK = 7.5

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

a = ShapelyMap ()
tag = Tag('highway', 'path')

for line in resLines:
    a.addLinestring(line, tag)

a.exportToXml('z.osm')

