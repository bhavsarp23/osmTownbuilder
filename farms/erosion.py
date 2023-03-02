# || Swami-Shriji ||

import numpy as np
import matplotlib.pyplot as plt
import math
import random
import time

import shapely.geometry as sg
import shapely.affinity as sa
import shapely.ops as so

from perlin_noise import PerlinNoise

from envelopeWarp import distort

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

def erode(polygon):

  noise = PerlinNoise(octaves=10, seed=1)
  perimeter = 400
  noise_vector = [noise(i/perimeter) for i in range(perimeter)]

  max_segment = polygon.exterior.length/20
  cumalitive_len = 0
  points = []
  while cumalitive_len < polygon.exterior.length:
    cumalitive_len += max_segment * random.random()
    p = polygon.exterior.interpolate(cumalitive_len)
    noise_index = int(len(noise_vector) * cumalitive_len/polygon.exterior.length) % len(noise_vector)
    p = sa.translate(p, 1*noise_vector[noise_index], 1*noise_vector[noise_index])
    points.append(p)

  return sg.Polygon(points)


if __name__ == "__main__":

  noise = PerlinNoise(octaves=10, seed=1)
  perimeter = 400
  pic = [noise(i/perimeter) for i in range(perimeter)]

  r = rectangle(100,100)
  r2 = sg.Polygon(erode(r, pic))

  plot_poly(r, r2)
  plt.show()
