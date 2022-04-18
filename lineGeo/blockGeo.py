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

from scipy.spatial import Voronoi

class Lot:

  def __init__ (self, poly):
    self.poly = poly


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

      # for lot in self.lots:
      #   plt.plot(*lot.poly.exterior.xy)


      # plt.plot(*self.outerBoundary.xy)
      # plt.plot(*self.innerBoundary.xy)
      # for point in self.lotPoints:
      #   plt.scatter(*point.xy)
      # plt.show()


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
