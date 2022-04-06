from shapely.geometry import *
from shapely.ops import unary_union
from shapely.affinity import rotate
from shapely.affinity import translate
from math import cos, sin, pi, radians
import matplotlib.pyplot as plt
import random

seed = random.randint(1,10)

LOWER_WIDTH = 5
UPPER_WIDTH = 6
LOWER_LENGTH = 7
UPPER_LENGTH = 10

STREET_WIDTH = 20

SEED_1 = 1
SEED_2 = 3
SEED_3 = 5
SEED_4 = 7
SEED_5 = 10
SEED_6 = 10

# class Home:

#     def __init__(self, poly):
        

class House:

    poly = []

    def __init__(self,seed,x,y,angle=0):
        rects = []

        # Create random houses
        # Width is 10 to 12 meters
        # Length is 15 to 20 meters
        # Three seeds:
        # Seed 1 is a simple rectangle house
        if (seed < SEED_1):

            for i in range (0, 1):
                
                width = random.uniform(LOWER_WIDTH,UPPER_WIDTH)
                length = random.uniform(LOWER_LENGTH, UPPER_LENGTH)

                # x = 0
                # y = 0

                p1 = Point(width+x, length+y)
                p2 = Point(width+x, -length+y)
                p3 = Point(-width+x, -length+y)
                p4 = Point(-width+x, length+y)
                rect = Polygon([p1,p2,p3,p4])
                rects.append(rect)
            
        # Seed 2 is a double L compound house
        elif (seed < SEED_2):
            
                flipx = random.choice([-1,1])
                flipy = random.choice([-1,1])
            
                width = random.uniform(LOWER_WIDTH,UPPER_WIDTH)
                length = random.uniform(LOWER_LENGTH, UPPER_LENGTH)

                # x = 0
                # y = 0

                p1 = Point(width+x, length+y)
                p2 = Point(width+x, -length+y)
                p3 = Point(-width+x, -length+y)
                p4 = Point(-width+x, length+y)
                rect = Polygon([p1,p2,p3,p4])
                rects.append(rect)
                
                x = flipx*(width - random.uniform(1,2))
                y = flipy*(length - random.uniform(1,2))
                
                p1 = Point(width+x, length+y)
                p2 = Point(width+x, -length+y)
                p3 = Point(-width+x, -length+y)
                p4 = Point(-width+x, length+y)
                rect = Polygon([p1,p2,p3,p4])
                rects.append(rect)

                
        # Seed 3 is a plus sign house
        elif (seed < SEED_3):
                
            for i in range (0, 3):
                width = random.uniform(LOWER_WIDTH,UPPER_WIDTH)
                length = random.uniform(LOWER_LENGTH, UPPER_LENGTH)

                # x = 0
                # y = 0

                p1 = Point(width+x, length+y)
                p2 = Point(width+x, -length+y)
                p3 = Point(-width+x, -length+y)
                p4 = Point(-width+x, length+y)
                rect = Polygon([p1,p2,p3,p4])
                rects.append(rect)

        # Seed 4 is a octagonal house

        elif (seed < SEED_4):
            
            flipx = random.choice([-1,1])
            flipy = random.choice([-1,1])

            width = random.uniform(LOWER_WIDTH,UPPER_WIDTH)
            length = random.uniform(LOWER_LENGTH, UPPER_LENGTH)

            # x = 0
            # y = 0

            p1 = Point(width+x, length+y)
            p2 = Point(width+x, -length+y)
            p3 = Point(-width+x, -length+y)
            p4 = Point(-width+x, length+y)
            rect = Polygon([p1,p2,p3,p4])
            rects.append(rect)
            
            width2 = random.uniform(LOWER_WIDTH/2,UPPER_WIDTH/2)
            length2 = random.uniform(LOWER_LENGTH/2, UPPER_LENGTH/2)
            
            x = flipx*(width2)/2
            y = flipy*(length2)/2
            
            p1 = Point(width2+x, length2+y)
            p2 = Point(width2+x, -length2+y)
            p3 = Point(-width2+x, -length2+y)
            p4 = Point(-width2+x, length2+y)
            rect = Polygon([p1,p2,p3,p4])
            rects.append(rect)
            
        # Seed 5 is a hexagonal house
        elif (seed < SEED_5):
            
            flipx = random.choice([-1,1])
            flipy = random.choice([-1,1])

            width = random.uniform(LOWER_WIDTH/1,UPPER_WIDTH/1)
            length = random.uniform(LOWER_LENGTH/1, UPPER_LENGTH/1)

            # x = 0
            # y = 0

            p1 = Point(width+x, length+y)
            p2 = Point(width+x, -length+y)
            p3 = Point(-width+x, -length+y)
            p4 = Point(-width+x, length+y)
            rect = Polygon([p1,p2,p3,p4])
            rects.append(rect)
            
            width2 = random.uniform(LOWER_WIDTH/4,UPPER_WIDTH/4)
            length2 = random.uniform(LOWER_LENGTH/4, UPPER_LENGTH/4)
            
            x = flipx*(width - width2)
            y = flipy*(length+length2)
            
            p1 = Point(width2+x, length2+y)
            p2 = Point(width2+x, -length2+y)
            p3 = Point(-width2+x, -length2+y)
            p4 = Point(-width2+x, length2+y)
            rect = Polygon([p1,p2,p3,p4])
            rects.append(rect)
            
        # Seed 6 is bizzaro
        elif (seed < SEED_6):
                
            for i in range (0, random.randrange(3,6)):
                width = random.uniform(LOWER_WIDTH-2,UPPER_WIDTH)
                length = random.uniform(LOWER_LENGTH-2, UPPER_LENGTH)

                x = random.uniform(1,4)
                y = random.uniform(1,4)

                p1 = Point(width+x, length+y)
                p2 = Point(width+x, -length+y)
                p3 = Point(-width+x, -length+y)
                p4 = Point(-width+x, length+y)
                rect = Polygon([p1,p2,p3,p4])
                rects.append(rect)

        self.poly = unary_union(rects)
        
class HouseRow:

    houses = []

    def __init__(self, numHouses):
        x = 0
        y = 0
        for i in range(0, numHouses):
            house = House(1,x,y).poly
            x += house.exterior.bounds[0][0]
            self.houses.append(house)

class CityBlock:

    houses = []

    def __init__(self, x=0, y=0, angle=0, numHouses=6):
        
        # populate houses list
        for i in range(0,numHouses):
            #front facing houses
            house = House(random.randint(0,6),0,0)
            # calculate setback of house
            setback = -1*(house.exterior.bounds[1])
            #translate house
            house = translate(house, setback)
            # set angle of house
            house = rotate(house, angle)
            


