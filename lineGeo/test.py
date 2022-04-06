from shapely.geometry import *
from shapely.geometry import LineString
import math
import numpy as np
from lineGeo import *

a = Point (0,0)
b = Point (0,50)
c = Point (50,50)
d = Point (100,100)
ab = LineString (MultiPoint ([a,b,c,d]))
#ab = LineString ([(0,0),(1,1)])
d = getInterpolatedPointsByDistance (ab,15)
e = []
for i in range (1,len(d)):
    e.append (getNormalOffsetPoint (d[i-1], d[i],1))

f = MultiPoint(e)
print(d)
print(f)

