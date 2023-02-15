# || Swami-Shriji ||

import shapely.geometry as sg
import shapely.affinity as sa
import shapely.ops as so

import numpy as np
import random

import matplotlib.pyplot as plt
import math

def angle_of_two_points(a, b, using_degrees=False):
  if using_degrees:
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
  return math.atan2(b[1] - a[1], b[0] - a[0])

class Parcel:

  def get_angle(self):
    a, b = self.poly.minimum_rotated_rectangle.exterior.coords[0:2]
    angle = angle_of_two_points(a,b)
    return angle

  def add_building(self, **kwargs):
    courtyard = kwargs.get('courtyard', False)
    front_enclave = kwargs.get('front_enclave', 0)
    real_enclave = kwargs.get('real_enclave', 0)

  def __init__(self, poly, **kwargs):
    self.poly = poly
    self.angle = kwargs.get('angle', self.get_angle())

  def to_area(self):
    pass

  def add_tags(self, tags):
    self.tags.extend(tags)

def get_rectangle(w, h, cx, cy, angle) -> sg.Polygon:
  x = w/2
  y = h/2
  poly = sg.Polygon([(-x,-y),(x,-y),(x,y),(-x,y)])
  poly = sa.translate(poly, cx, cy)
  poly = sa.rotate(poly, angle, use_radians=True)
  return poly

def get_parcels(line, **kwargs):

  right = kwargs.get('right', True)
  left = kwargs.get('left', True)
  front_offset = kwargs.get('front_offset', 10)
  rear_offset = kwargs.get('real_offset', 30)
  mid_offset = (rear_offset - front_offset)/2
  parcel_spacing = kwargs.get('parcel_spacing', lambda: 20)

  r_parcels = []
  l_parcels = []

  if right:
    # Create offsets
    print(front_offset, rear_offset)
    rf = line.parallel_offset(front_offset, 'right')
    rm = line.parallel_offset(mid_offset, 'right')
    rr = line.parallel_offset(rear_offset, 'right')

    # Create zone
    r_zone = sg.Polygon([*list(rf.coords), *list(rr.coords[::-1])])
    # Create points
    cumulative_spacing = parcel_spacing()
    rm_points = []
    while cumulative_spacing < rm.length:
      rm_points.append(rm.interpolate(cumulative_spacing))
      cumulative_spacing += parcel_spacing()
    rm_points = sg.MultiPoint(rm_points)
    # Create a voronoi of the polygon
    r_polys = so.voronoi_diagram(rm_points, envelope=r_zone)
    # Trim the voronoi polys
    r_parcels = [poly.intersection(r_zone) for poly in r_polys.geoms]

  if left:
    # Create offsets
    lf = line.parallel_offset(front_offset, 'left')
    lm = line.parallel_offset(mid_offset, 'left')
    lr = line.parallel_offset(rear_offset, 'left')
    # Create zone
    l_zone = sg.Polygon([*list(lf.coords), *list(lr.coords[::-1])])
    # Create points
    cumulative_spacing = parcel_spacing()
    lm_points = []
    while cumulative_spacing < lm.length:
      lm_points.append(lm.interpolate(cumulative_spacing))
      cumulative_spacing += parcel_spacing()
    lm_points = sg.MultiPoint(lm_points)
    # Create a voronoi of the polygon
    l_polys = so.voronoi_diagram(lm_points, envelope=l_zone)
    # Trim the voronoi polys
    l_parcels = [poly.intersection(l_zone) for poly in l_polys.geoms]

  return r_parcels, l_parcels


if __name__ == "__main__":

  # Make a polyline segment
  a = sg.Point(0,0)
  b = sg.Point(100,0)
  c = sg.Point(200,100)
  d = sg.Point(300,100)

  e = sg.Point(100,100)
  f = sg.Point(0,100)
  g = sg.Point(0, 0)
  h = sg.Point(-100, -100)

  abcd = sg.LineString([a,b,c,d])
  # efgh = sg.LineString([e,f,g,h])

  r_parcels, l_parcels = get_parcels(abcd)

  # Plot angles
  for parcel in r_parcels:
    plt.plot(*parcel.exterior.coords.xy)

  for parcel in l_parcels:
    plt.plot(*parcel.exterior.coords.xy)

  # Make a house at the center of each parcel
  for parcel in r_parcels:
    centroid = parcel.centroid
    angle = Parcel(parcel).get_angle()
    rect = get_rectangle(15,15,centroid.x, centroid.y, angle)
    house = rect.intersection(parcel)
    plt.plot(*house.exterior.coords.xy)



  plt.show()



  # # Create two parallel offsets of abc (front and rear)
  # front = abcd.parallel_offset(10, 'right')
  # mid = abcd.parallel_offset(20, 'right')
  # rear = abcd.parallel_offset(30, 'right')

  # # Create a polygon using the points of front and rear
  # zone = sg.Polygon([*list(front.coords), *list(rear.coords[::-1])])

  # # Interpolate randomly spaced points on mid
  # spacing = lambda: random.uniform(1,30)
  # cumulative_spacing = spacing()
  # mid_points = []

  # while cumulative_spacing < mid.length:
  #   mid_points.append(mid.interpolate(cumulative_spacing))
  #   cumulative_spacing += spacing()

  # mid_points = sg.MultiPoint(mid_points)
  # #mid_point_angles = [angle_of_two_points(a,b) for a,b in mid_]

  # # Create a voronoi of the polygon
  # parcels = so.voronoi_diagram(mid_points, envelope=zone)

  # for polygon in parcels.geoms:
  #   poly = polygon.intersection(zone)
  #   plt.plot(*poly.exterior.xy)
