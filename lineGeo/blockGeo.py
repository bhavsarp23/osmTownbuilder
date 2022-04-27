from shapely.geometry import *
from shapely.geometry import LineString
from shapely.geometry import LinearRing
from shapely.ops import unary_union
from shapely.ops import voronoi_diagram
from shapely import affinity
import numpy as np
import lineGeo.lineGeo as lg
#import lineGeo as lg
import math
import matplotlib.pyplot as plt
import random

from scipy.spatial import Voronoi

def getRectanglePolygon (width, length, center=Point(0,0), angle=0):
    point1 = affinity.translate(center, -1*width/2, -1*length/2)
    point2 = affinity.translate(center, width/2, -1*length/2)
    point3 = affinity.translate(center, width/2, length/2)
    point4 = affinity.translate(center, -1*width/2, length/2)
    poly = Polygon([point1, point2, point3, point4])
    poly = affinity.rotate(poly, angle)
    return poly


class Lot:

  def __init__ (self, poly):
    self.poly = poly

  def makeRearEnclave(self, w, l):
    w = w




class Zone:

  def __init__ (self, line, depth):
    self.depth = depth
    self.frontBoundary = line
    self.rearBoundary = line.parallel_offset(depth, 'right')
    frontPoints = [point for point in self.frontBoundary.coords]
    rearPoints = [point for point in self.rearBoundary.coords]
    #rearPoints.reverse()
    points = frontPoints + rearPoints
    self.poly = Polygon(points)

  def subdivideEvenly (self, numberOfPoints):
    # Get mid boundary
    self.midBoundary = self.frontBoundary.parallel_offset(self.depth/2, 'right')

    # Get interpolated points
    self.lotPoints = lg.getInterpolatedPointsByNumber(self.midBoundary, numberOfPoints)

    # Voronoi the lots
    vor = voronoi_diagram(self.lotPoints)
    self.lots = []
    for lot in vor:
      aa = lot.intersection(self.poly)
      #aa = lot
      self.lots.append(aa)

      plt.plot(*aa.exterior.xy)

    plt.plot(*self.poly.exterior.xy)
    plt.show()





class Block:

  courtyardExists = False
  direction = 'right'
  lots = []


  def __init__ (self, poly):
    self.outerBoundary = LinearRing(poly)

  def createCourtyard (self, depth):
    self.depth = depth
    self.courtyardExists = True
    innerBoundaryL = self.outerBoundary.parallel_offset (depth, 'left')
    innerBoundaryR = self.outerBoundary.parallel_offset (depth, 'right')
    if innerBoundaryL.length < innerBoundaryR.length:
      self.innerBoundary = LinearRing(innerBoundaryL)
      self.direction = 'left'
    else:
      self.innerBoundary = LinearRing(innerBoundaryR)
      self.direction = 'right'

  # def

  def distortCourtyard (self, maxDistortion=0):
    # Randomly interpolate the inner boundary
    enclaveCenterPoints = lg.getRandomInterpolationPoints(self.innerBoundary, 20)

    courtyard = Polygon(self.innerBoundary)
    # Get roughly the preceding of each point
    for i in range(0, len(enclaveCenterPoints)):
      p1 = enclaveCenterPoints[i]
      p2 = enclaveCenterPoints[i-1]
      angle = (lg.getAngleOfTwoPoints(p1,p2))
      if random.random() > 0.5:
        w = random.uniform(3, maxDistortion)
        l = random.uniform(3, maxDistortion)
        enclave = getRectanglePolygon(w,l,enclaveCenterPoints[i],angle)
        # Add each enclave to the inner boundary
        courtyard = unary_union([courtyard, enclave])

    self.innerBoundary = LinearRing(courtyard.exterior)

  def subdivideBlockEvenly (self, numberOfLots):
    if self.courtyardExists == True:
      # Create a lineString between the two boundaries
      if self.direction == 'right':
        self.midBoundary = self.outerBoundary.parallel_offset (self.depth/2, 'right')
      if self.direction == 'left':
        self.midBoundary = self.outerBoundary.parallel_offset (self.depth/2, 'left')
      # Interpolate that boundary
      self.lotPoints = lg.getInterpolatedPointsByNumber (self.midBoundary, numberOfLots)
      # Multipolygon of inner and outer boundaries
      # Voronoi the multipolygon
      vor = voronoi_diagram (self.lotPoints, envelope=Polygon(self.outerBoundary))
      self.lots = []
      for lot in vor:
        aa = lot.intersection (Polygon(self.outerBoundary))
        bb = aa.difference(Polygon(self.innerBoundary))
        self.lots.append(Lot(bb))

  def subdivideBlockRandomly (self, numberOfLots):
    if self.courtyardExists == True:
      # Create a lineString between the two boundaries
      if self.direction == 'right':
        self.midBoundary = self.outerBoundary.parallel_offset (self.depth/2, 'right')
      if self.direction == 'left':
        self.midBoundary = self.outerBoundary.parallel_offset (self.depth/2, 'left')
      # Interpolate that boundary
      self.lotPoints = MultiPoint(lg.getRandomInterpolationPoints (self.midBoundary, numberOfLots))
      # Multipolygon of inner and outer boundaries
      # Voronoi the multipolygon
      vor = voronoi_diagram (self.lotPoints, envelope=Polygon(self.outerBoundary))
      self.lots = []
      for lot in vor:
        aa = lot.intersection (Polygon(self.outerBoundary))
        bb = aa.difference(Polygon(self.innerBoundary))
        self.lots.append(Lot(bb))

  def subdivideIntoGrid (self, gridDistance=1):
    if self.courtyardExists == False:
      return 0

    # Calculate number of rings in grid
    numberOfRings = int(self.depth/gridDistance)
    gridPoints = []

    # Create grid of points
    for i in range(1, numberOfRings):
      # Create parallel offset ring by i meters
      ring = self.outerBoundary.parallel_offset(i*gridDistance, self.direction)
      # Interpolate each ring by grid distance
      points = lg.getInterpolatedPointsByDistance(ring, gridDistance)
      gridPoints.extend(points)

    # Voronoi the points
    vor = voronoi_diagram (MultiPoint(gridPoints), envelope=Polygon(self.outerBoundary))
    for lot in vor:
      aa = lot.intersection (Polygon(self.outerBoundary))
      bb = aa.difference(Polygon(self.innerBoundary))
      self.lots.append(Lot(bb))

    print(len(gridPoints))

    for lot in self.lots:
      plt.plot(*lot.poly.exterior.xy)

    for point in gridPoints:
        plt.scatter(*point.xy)

    plt.plot(*self.outerBoundary.xy)
    plt.plot(*self.innerBoundary.xy)
    plt.show()

  def subdivideBlockByWidths (self, widths):
    if self.courtyardExists == False:
      return

    # Get middle boundary
    self.midBoundary = self.outerBoundary.parallel_offset(self.depth/2, self.direction)

    # If sum of width is more than boundary distance
    if sum(widths) > self.midBoundary.length:
      print("too long.")
      return

    # Interpolation distance
    distance = 0

    # Interpolate by widths
    self.lotPoints = []
    for width in widths:
      distance += width
      point = self.midBoundary.interpolate(distance)
      self.lotPoints.append(self.midBoundary.interpolate(distance))

    # Voronoi the points
    vor = voronoi_diagram (MultiPoint(self.lotPoints), envelope=Polygon(self.outerBoundary))
    for lot in vor:
      aa = lot.intersection (Polygon(self.outerBoundary))
      bb = aa.difference(Polygon(self.innerBoundary))
      if bb.geom_type == 'MultiPolygon':
        # Split each of bb
        for poly in bb:
          self.lots.append(Lot(poly))

    for lot in self.lots:
        plt.plot(*lot.poly.exterior.xy)
    plt.plot(*self.outerBoundary.xy)
    plt.plot(*self.innerBoundary.xy)
    plt.show()




  def subdivideBlockS (self, numberOfLots):
    if self.courtyardExists == False:
      return 0

    # Create a lineString between the two boundaries
    self.midBoundary = self.outerBoundary.parallel_offset (self.depth/2, self.direction)


    # Interpolate both boundaries by a fixed distance
    self.lotPoints = lg.getInterpolatedPointsByNumber (self.midBoundary, numberOfLots)


      # for lot in cc:
      #   plt.plot(*lot.exterior.xy)


      # plt.plot(*self.outerBoundary.xy)
      # plt.plot(*self.innerBoundary.xy)
      # for point in self.lotPoints:
      #   plt.scatter(*point.xy)
      # plt.show()
