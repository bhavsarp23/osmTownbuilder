# || Swami-Shriji ||
# ----------------- #
#     Libraries     #
# ----------------- #
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib
import shapely.geometry as sg
import shapely.affinity as sa
import shapely.ops as so
import random
import osmElements as oe
import shapelyElements as se

matplotlib.use('TkAgg')

def rad_to_deg(rad):
  return (rad/math.pi*180)%360

def plot_poly(*args, **kwargs):
  pattern = kwargs.get('pattern', '')
  for poly in args:
    if poly.geom_type == 'MultiPolygon' or poly.geom_type == 'GeometryCollection':
      for p in poly.geoms:
        if p.geom_type != 'Polygon':
          continue
        x,y = p.exterior.xy
        plt.plot(x,y, pattern)
    elif poly.geom_type == 'Polygon':
      x,y = poly.exterior.xy
      plt.plot(x,y, pattern)
    else:
      pass

def rectangle(w, h, cx=0, cy=0, angle=0) -> sg.Polygon:
  a = sg.Polygon([(0,0), (0,h), (w,h), (w,0)])
  a = sa.translate(a, cx - w/2, cy - h/2)
  return sa.rotate(a, angle)

def recursive_bisect(poly, max_area):
  polys = []
  if poly.area > max_area:
    mrr = poly.minimum_rotated_rectangle
    r = random.uniform(0.5, 1)
    p1 = mrr.exterior.interpolate(r)
    p2 = mrr.exterior.interpolate(r-0.5)
    midsection = sg.LineString([p1, p2])
    polys.append(so.split(poly, midsection).geoms)
  else:
    polys = [poly]
  return polys


def get_random_angle(length, bend_radius):
  max_angle = math.atan2(length, bend_radius)
  coeff = random.randint(-1,1)
  return coeff * random.random() * max_angle

def angle_of_two_points(p1, p2):
  dy = p2.y - p1.y
  dx = p2.x - p1.x
  return math.atan2(dy, dx)

# class Vector:
#   def __init__(self, magnitude, angle):
#     self.magnitude = magnitude
#     self.angle = angle

class Branch:

  @property
  def geom(self):
    if len(self.points) > 1:
      return sg.LineString(self.points)
    raise RuntimeError("Not enough points.")
    return None

  def __init__(self, start_point, **kwargs):
    self.points = [start_point]
    self.current_angle = kwargs.get('angle', 0)

  def get_next_point(self, previous_point):
    d = random.random() * self.segment_length
    self.current_angle += get_random_angle(d, self.bend_radius)
    dx = d*math.cos(self.current_angle)
    dy = d*math.sin(self.current_angle)
    return sa.translate(previous_point, dx, dy)

  def plot(self):
    try:
      self.line_string = sg.LineString(self.points)
    except:
      pass
    try:
      pass
      #plt.plot(*self.line_string.xy)
    except:
      pass
  def is_valid(self):
    if len(self.points) < 2:
      return True
    # Check if linestring is self crossing
    return sg.LineString(self.points).is_simple

  def crosses(self, other):
    try:
      return self.geom.crosses(other.geom)
    except:
      return False

  def check_crosses(self, others):
    for i, other in enumerate(others):
      if self == other:
        continue
      if self.crosses(other):
        return True, self.geom.intersection(other.geom)

    return False, None

  def draw(self, envelope, **kwargs):

    self.segment_length = kwargs.get("segment_length", 20)
    iterations = kwargs.get('iterations', 10)
    self.bend_radius = kwargs.get('bend_radius', 10)
    others = kwargs.get('others', [])

    random.random()*self.segment_length
    self.angle = 0

    # for i in range(iterations):
    #   self.points.append(self.get_next_point(self.points[-1]))

    while self.is_valid():
      self.points.append(self.get_next_point(self.points[-1]))
      if self.geom.intersects(envelope.exterior):
        self.points.pop()
        break
      crosses, intersection = self.check_crosses(others)
      if crosses:
        self.points.pop()
        self.points.append(intersection)
        break


  def interpolate(self, distance, normalized=True):
    point = self.geom.interpolate(distance, normalized=normalized)
    p1 = self.geom.interpolate(distance+0.01, normalized=normalized)
    p2 = self.geom.interpolate(distance-0.01, normalized=normalized)
    angle = angle_of_two_points(p1,p2)
    return point, angle

  def create_child_nodes(self, **kwargs):
    cumalative_length = 0
    child_points_angles = []
    try:
      self.geom
    except:
      return [[],[]]

    while cumalative_length < self.geom.length:
      cumalative_length += random.random() * 200 #self.segment_length
      child_points_angles.append(self.interpolate(cumalative_length, normalized=False))

    child_points = [row[0] for row in child_points_angles]
    child_angles = [row[1] for row in child_points_angles]
    print(len(child_points_angles))
    return child_points, child_angles

  # def create_children(self, num_children=1, **kwargs):
  #   children = []
  #   others = kwargs.get('others', [])
  #   envelope = rectangle(1000, 1000)
  #   for i in range(num_children):
  #     start_point = self.interpolate(random.uniform(0.1, 0.9))
  #     angle = self.current_angle + random.choice([-1,1]) * math.pi/2 + random.randint(-1,1) * random.random() * math.pi/2
  #     b = Branch(start_point, angle=angle)
  #     b.draw(envelope, iterations=100, bend_radius=175, segment_length=20, others=others)
  #     b.plot()
  #     children.append(b)
  #     global_branches.append(b)
  #   return children

  def __repr__(self):
    return f'Branch has points {self.points}'

class LSystem:

  def __get_random_start_point__(self):
    exterior = self.envelope.buffer(-1).exterior
    normalized_distance = random.uniform(0,1)
    start_point = exterior.interpolate(normalized_distance, normalized=True)

    # Get the angle by local linearization
    p1 = exterior.interpolate(normalized_distance + 0.01, normalized=True)
    p2 = exterior.interpolate(normalized_distance - 0.01, normalized=True)
    angle = angle_of_two_points(p1, p2)

    return start_point, angle

  def create_branches(self, **kwargs):

    num_main = kwargs.get('num_main', 4)
    levels = 2

    for j in range(levels):
      for i in range(num_main):
        start_point, angle = self.__get_random_start_point__()
        # Perpendicular angle with some randomness
        angle += math.pi/2 + random.random() * math.pi/6
        branch = Branch(start_point, angle=angle)
        branch.draw(self.envelope, bend_radius=500, segment_length=20, others=self.branches)
        branch.plot()
        self.branches.append(branch)

  def create_children(self, **kwargs):
    levels = 2
    self.segment_length = 20

    num_branches = len(self.branches)

    for i in range(levels):
      for j in range(num_branches):
        branch = self.branches[j]
        child_points, child_angles = branch.create_child_nodes()
        for i, child_point in enumerate(child_points):
          angle = child_angles[i] + math.pi/2
          child_branch = Branch(start_point=child_point, angle=angle)
          child_branch.draw(self.envelope, others=self.branches, bend_radius=50)
          child_branch.plot()
          self.branches.append(child_branch)

  def __init__(self, envelope, **kwargs):
    self.envelope = envelope
    self.levels = kwargs.get('levels', 3)
    self.branches = []
    self.create_branches()
    self.create_children()


if __name__ == "__main__":

  envelope_nodes = oe.getConstructionBlocks()[0]
  keepout_ways = oe.getConstructionStreets()
  keepout_lines = [se.getLineStringFromWay(way) for way in keepout_ways]
  envelope = sg.Polygon([se.getPointFromNode(node) for node in envelope_nodes])
  #envelope = rectangle(400,400)
  l = LSystem(envelope)

  # Cut envelope using the branches in l
  line_cuts = [envelope.exterior]
  line_cuts.extend(keepout_lines)
  for branch in l.branches:
    try:
      line_cuts.append(branch.geom)
    except:
      pass
  line_areas = [line.buffer(1) for line in line_cuts]
  #polys = sg.Polygon(so.polygonize(line_cuts))
  polys = sg.MultiPolygon([sg.Polygon(p) for p in so.unary_union(line_areas).interiors])

  #polys = [so.polygonize(poly) for poly in polys]
  #plot_poly(polys)
  #plt.show()

  areas = [se.getAreaFromPolygon(poly) for poly in polys.geoms]
  tag = [oe.Tag('landuse', 'farmland')]
  for area in areas:
    area.addTags(tag)
  osm_map = oe.OsmMap()
  osm_map.addWays(areas)
  osm_map.writeToFile('z.osm')
