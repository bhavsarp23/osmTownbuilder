from shapely.geometry import *
from shapely.geometry import LineString
from shapely.ops import unary_union
import numpy as np
import math

# Returns a cartesian point based on a polar pair
def polarToCart (rho, angle):
    x = rho * math.cos (angle)
    y = rho * math.sin (angle)
    return Point (x,y)

def getMidpointOfTwoPoints (point1, point2):
    return Point ((point1.x + point2.x)/2, (point1.y + point2.y)/2)

# Return the angle of a line segment of two points
def getAngleOfTwoPoints (point1, point2):
    dy = point2.y - point1.y
    dx = point2.x - point1.x
    return math.atan2 (dy,dx)

# Returns the slope from point 1 to point 2
def getSlopeOfTwoPoints (point1, point2):
    return ((point2.y - point1.x) / (point2.x - point1.x))

# Interpolate the given line with a new point at a fixed distance
def getInterpolatedPointsByDistance (line, distanceDelta):
    distances = np.arange(0,line.length,distanceDelta)
    points = []
    for distance in distances:
        points.append (line.interpolate (distance) )
    multipoint = unary_union(points)
    return multipoint

# Returns the third point of an isosceles triangle given a height and two points
def getNormalOffsetPoint (point1, point2, offset):
    angle = getAngleOfTwoPoints (point1, point2)
    normalAngle = angle - math.pi/2
    normalAngle*180/math.pi
    point3Relative = polarToCart (offset, normalAngle)
    point3Base = getMidpointOfTwoPoints (point1, point2)
    point3 = Point (point3Base.x + point3Relative.x, point3Base.y + point3Relative.y)
    return point3







