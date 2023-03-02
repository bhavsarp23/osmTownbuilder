# || Swami-Shriji ||

import numpy as np
import matplotlib.pyplot as plt
import math
import random
import time

import shapely.geometry as sg
import shapely.affinity as sa
import shapely.ops as so

from envelopeWarp import distort_polygon
from iterated import iterated_subdivisions
from erosion import erode
from orthogonalize import orthogonalize_polygon

def rectangle(w, h, cx=0, cy=0) -> sg.Polygon:
  p1 = (0,0)
  p2 = (w,0)
  p3 = (w,h)
  p4 = (0,h)
  poly = sg.Polygon([p1,p2,p3,p4])
  poly = sa.translate(poly, -w/2 + cx, -h/2 + cy)
  return poly

def plot_poly(*args, **kwargs):
  pattern = kwargs.get('pattern', '')
  for poly in args:
    if poly.geom_type == 'MultiPolygon' or poly.geom_type == 'GeometryCollection':
      for p in poly.geoms:
        x,y = p.exterior.xy
        plt.plot(x,y, pattern)
    elif poly.geom_type == 'Polygon':
      x,y = poly.exterior.xy
      plt.plot(x,y, pattern)
    else:
      pass


if __name__ == "__main__":

  # Make a bigass rectangle
  r = rectangle(100, 100)
  print(1)

  # Recursively bisect the rectangle
  sub_rs = iterated_subdivisions(r, 0.1, 80)
  print(2)

  # Create an warped envelope
  envelope = sg.Polygon([(0,0), (100,0), (100,95), (50,100), (0,100)])
  print(3)

  # Warp the farms
  warped_rs = [distort_polygon(sub_r, envelope) for sub_r in sub_rs]
  print(4)

  trans_rs = [sa.translate(poly, 5*random.random(), 5*random.random()) for poly in warped_rs]

  ortho_rs = []
  # # Orthogonalize the farms
  # for i, poly in enumerate(warped_rs):
  #   print(i)
  # try:
  #   ortho_rs.append(orthogonalize_polygon(poly))
  # except:
  #   print("Unable to orthogonalize. Moving on.")

  erode_rs = [erode(polygon) for polygon in trans_rs]

  # Difference of shapes
  # for i, shape in enumerate(erode_rs):
  #   colliding_shapes = [s for s in erode_rs if s.intersects(shape)]
  #   for colliding_shape in colliding_shapes:
  #     try:
  #       erode_rs[i] = colliding_shape.difference(shape)
  #     except:
  #       pass

  for i, shape in enumerate(erode_rs):
    plot_poly(shape)


  plt.show()
