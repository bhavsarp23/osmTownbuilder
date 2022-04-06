from shapely.geometry import *
from shapely.ops import unary_union
from shapely.affinity import rotate
from shapely.affinity import translate
import random
from shapely.ops import voronoi_diagram
from shapely.geometry import MultiPoint


class Farmland:
    
    def __init__(self, points):
        self.points = points
        self.regions = voronoi_diagram(points)
        #regions = [farm.buffer(-10) for farm in regions]


