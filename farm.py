# || Swami-Shriji ||

import shapely.geometry as sg
import shapely.affinity as sa
import shapely.ops as so

import numpy as np
import random

import matplotlib.pyplot as plt
import math

import orthogonalizePolygon as op

def plot_poly(poly):
  plt.plot(*poly.exterior.coords.xy)

def get_angle_of_poly(poly) -> float:
  # Minimum rot rec
  mrr = poly.minimum_rotated_rectangle
  return angle_of_two_points(mrr.exterior.coords[0], mrr.exterior.coords[1])

def get_rectangle(w, h):
  x = w/2
  y = h/2
  return sg.Polygon([(-x,-y),(x,-y),(x,y),(-x,y)])

def angle_of_two_points(a, b, using_degrees=False):
  if using_degrees:
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
  return math.atan2(b[1] - a[1], b[0] - a[0])

def random_polygon(area: float):

  num_points = random.randint(25,30)

  points = [(random.uniform(0,1), random.uniform(0,1)) for i in range(num_points)]
  angles = [angle_of_two_points(points[0], points[i]) for i in range(num_points)]

  # Sort points by angles
  sorted_points = [point for _, point in sorted(zip(angles,points))]

  polygon = sg.Polygon(sorted_points)
  scale = area / polygon.area
  return sa.scale(polygon, scale, scale)

def get_width(poly) -> float:
  # Sauthi nanu pharelu samchatu prapta karo
  mrr = poly.minimum_rotated_rectangle
  # Pahelu bindu ane biju binduni vachchhe antar
  width = sg.Point(mrr.exterior.coords[0]).distance(sg.Point(mrr.exterior.coords[1]))
  # Pacho apide
  return width

def get_height(poly) -> float:
  # Sauthi nanu pharelu samchatu prapta karo
  mrr = poly.minimum_rotated_rectangle
  # Pahelu bindu ane biju binduni vachchhe antar
  height = sg.Point(mrr.exterior.coords[1]).distance(sg.Point(mrr.exterior.coords[2]))
  # Pacho apide
  return height


def get_farm() -> sg.Polygon:
  a = random_polygon(3)
  b = a.convex_hull
  c = op.orthogonalize_polygon(b, 30, 30)
  d = c.buffer(-0.1)
  e = d.buffer(0.1)
  angle = get_angle_of_poly(e)
  f = sa.rotate(e, -1 * angle, use_radians=True)
  return f


if __name__ == "__main__":

  # Create envelope
  envelope = get_rectangle(1000, 1000)

  cumulative_spacing = 0

  farms = [get_farm() for i in range(10)]
  for i, farm in enumerate(farms):
    cumulative_spacing += get_width(farm)
    farms[i] = sa.translate(farm, cumulative_spacing, -1*get_height(farm)/2)
    plot_poly(farms[i])
  plt.show()


