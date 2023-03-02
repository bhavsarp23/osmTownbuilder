# || Swami-Shriji ||

import numpy as np
import matplotlib.pyplot as plt
import math

import shapely.geometry as sg
import shapely.affinity as sa
import shapely.ops as so

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
    if poly.geom_type == 'MultiPolygon':
      for p in poly.geoms:
        x,y = p.exterior.xy
        plt.plot(x,y, pattern)
    else:
      x,y = poly.exterior.xy
      plt.plot(x,y, pattern)

    #  p0 ---- p1 ---- p2 ---- p3
    #  |                        |
    #  |                        |
    #  p11                     p4
    #  |                        |
    #  |                        |
    #  p10                     p5
    #  |                        |
    #  |                        |
    #  p9 ---- p8 ---- p7 ---- p6
    #
def get_anchors(envelope):
  # Get the minimum rotated rectangle of the envelope
  boundary = envelope.minimum_rotated_rectangle

  # Divide each side of the boundary into thirds
  top_left = sg.Point(boundary.exterior.coords[0])
  top_left_v = sg.LineString(
    [boundary.exterior.coords[0],
    boundary.exterior.coords[3]]
  ).interpolate(1/3, normalized=True)
  top_left_h = sg.LineString(
    [boundary.exterior.coords[0],
    boundary.exterior.coords[1]]
  ).interpolate(1/3, normalized=True)

  top_right = sg.Point(boundary.exterior.coords[1])
  top_right_v = sg.LineString(
    [boundary.exterior.coords[1],
    boundary.exterior.coords[2]]
  ).interpolate(1/3, normalized=True)
  top_right_h = sg.LineString(
    [boundary.exterior.coords[1],
    boundary.exterior.coords[0]]
  ).interpolate(1/3, normalized=True)

  bottom_right = sg.Point(boundary.exterior.coords[2])
  bottom_right_v = sg.LineString(
    [boundary.exterior.coords[2],
    boundary.exterior.coords[1]]
  ).interpolate(1/3, normalized=True)
  bottom_right_h = sg.LineString(
    [boundary.exterior.coords[2],
    boundary.exterior.coords[3]]
  ).interpolate(1/3, normalized=True)

  bottom_left = sg.Point(boundary.exterior.coords[3])
  bottom_left_v = sg.LineString(
    [boundary.exterior.coords[3],
    boundary.exterior.coords[0]]
  ).interpolate(1/3, normalized=True)
  bottom_left_h = sg.LineString(
    [boundary.exterior.coords[3],
    boundary.exterior.coords[2]]
  ).interpolate(1/3, normalized=True)

  # Nearest points
  p0 = so.nearest_points(envelope, top_left)[0]
  p1 = so.nearest_points(envelope, top_left_h)[0]
  p2 = so.nearest_points(envelope, top_right_h)[0]
  p3 = so.nearest_points(envelope, top_right)[0]
  p4 = so.nearest_points(envelope, top_right_v)[0]
  p5 = so.nearest_points(envelope, bottom_right_v)[0]
  p6 = so.nearest_points(envelope, bottom_right)[0]
  p7 = so.nearest_points(envelope, bottom_right_h)[0]
  p8 = so.nearest_points(envelope, bottom_left_h)[0]
  p9 = so.nearest_points(envelope, bottom_left)[0]
  p10 = so.nearest_points(envelope, bottom_left_v)[0]
  p11 = so.nearest_points(envelope, top_left_v)[0]


  return [p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11]

def distort(point: sg.Point, envelope) -> sg.Point:

  bounds = envelope.minimum_rotated_rectangle

  # Get anchors
  [top_left, top_left_h, top_right_h, top_right, top_right_v, bottom_right_v,
   bottom_right, bottom_right_h, bottom_left_h, bottom_left, bottom_left_v,
   top_left_v] = get_anchors(envelope)

  # Normal computation
  boundary_width = max(bounds.exterior.xy[0]) - min(bounds.exterior.xy[0])
  boundary_height = max(bounds.exterior.xy[1]) - min(bounds.exterior.xy[1])
  normal_x = (point.x - bounds.centroid.x) / boundary_width
  normal_y = (point.y - bounds.centroid.y) / boundary_height

  normal = sg.Point(normal_x, normal_y)
  normal_squared = sg.Point(normal_x**2, normal_y**2)
  normal_cubed = sg.Point(normal_x**3, normal_y**3)

  reverse_normal = sg.Point(1 - normal_x, 1 - normal_y)
  reverse_normal_squared = sg.Point((1 - normal_x)**2, (1 - normal_y)**2)
  reverse_normal_cubed = sg.Point((1 - normal_x)**3, (1 - normal_y)**3)

  # Cubic interpolate the left anchor node
  left_anchor_x = (
    (top_left.x * reverse_normal_cubed.y) +
    (3 * top_left_v.x * normal.y * reverse_normal_squared.y) +
    (3 * bottom_left_v.x * normal_squared.y * reverse_normal.y) +
    (bottom_left.x * normal_cubed.y)
    )

  left_anchor_y = (
    (top_left.y * reverse_normal_cubed.x) +
    (3 * top_left_v.y * normal.y * reverse_normal_squared.y) +
    (3 * bottom_left_v.y * normal_squared.y * reverse_normal.y) +
    (bottom_left.y * normal_cubed.y)
    )

  left_anchor = sg.Point(left_anchor_x, left_anchor_y)

  # Linear interpolate the left handle node
  left_handle_x = (top_left_h.x * reverse_normal.y) + (bottom_left_h.x * normal.y)
  left_handle_y = (top_left_h.y * reverse_normal.y) + (bottom_left_h.y * normal.y)
  left_handle = sg.Point(left_handle_x, left_handle_y)

  # Linear interpolate the right handle node
  right_handle_x = (top_right_h.x * reverse_normal.y) + (bottom_right_h.x * normal.y)
  right_handle_y = (top_right_h.y * reverse_normal.y) + (bottom_right_h.y * normal.y)
  right_handle = sg.Point(right_handle_x, right_handle_y)

  # Cubic interpolate the right anchor node
  right_anchor_x = (
    (top_right.x * reverse_normal_cubed.y) +
    (3 * top_right_v.x * normal.y * reverse_normal_squared.y) +
    (3 * bottom_right_v.x * normal_squared.y * reverse_normal.y) +
    (bottom_right.x * normal_cubed.y)
    )

  right_anchor_y = (
    (top_right.y * reverse_normal_cubed.x) +
    (3 * top_right_v.y * normal.y * reverse_normal_squared.y) +
    (3 * bottom_right_v.y * normal_squared.y * reverse_normal.y) +
    (bottom_right.y * normal_cubed.y)
  )

  right_anchor = sg.Point(right_anchor_x, right_anchor_y)

  # Cubic interpolate the final result
  result_x = (
    (left_anchor.x * reverse_normal_cubed.x) +
    (3 * left_handle.x * normal.x * reverse_normal_squared.x) +
    (3 * right_handle.x * normal_squared.x * reverse_normal.x) +
    (right_anchor.x * normal_cubed.x)
  )

  result_y = (
    (left_anchor.y * reverse_normal_cubed.x) +
    (3 * left_handle.y * normal.x * reverse_normal_squared.x) +
    (3 * right_handle.y * normal_squared.x * reverse_normal.x) +
    (right_anchor.y * normal_cubed.x)
  )

  return sg.Point(result_x, result_y)

def distort_polygon(poly, envelope):

  return sg.Polygon([distort(sg.Point(point), envelope) for point in poly.exterior.coords])

if __name__ == "__main__":

  a = sg.Point(1,1)
  envelope = sg.Polygon([
    (0,0), (4,0), (4,3), (2,4), (0,4)
  ])
  N = 100

  r = rectangle(1,1)

  circle_distored = sg.Polygon([
    distort(sg.Point(point), envelope) for point in r.exterior.coords
  ])


  plot_poly(r, circle_distored)
  plt.show()
