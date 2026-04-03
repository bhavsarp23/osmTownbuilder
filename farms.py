# || Swami-Shriji ||

import shapely.geometry as sg
import shapely.affinity as sa
import shapely
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
import math
from collections import Counter
import random
import numpy as np

green_shades = [
    'forestgreen', 'olivedrab', 'darkseagreen',
    'limegreen', 'darkgreen',
    'yellowgreen', 'honeydew', 'palegreen'
]

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

def plot_polygons(polygons, title="Processed Polygons"):
    fig, ax = plt.subplots(figsize=(8, 8))

    for poly in polygons:
        # 1. Extract coordinates
        # If it's a MultiPolygon, we need to iterate through its parts
        parts = poly.geoms if hasattr(poly, 'geoms') else [poly]

        # 2. Pick a random color for this specific shape
        color = random.choice(green_shades)

        for part in parts:
            # Get the exterior coordinates for the fill
            x, y = part.exterior.xy

            # Create the patch (closed=True ensures the last point connects to the first)
            patch = MplPolygon(np.column_stack((x, y)),
                               facecolor=color,
                               edgecolor='black',
                               alpha=0.6,
                               linewidth=.1)
            ax.add_patch(patch)

    # 3. Auto-scale the view
    ax.autoscale()
    ax.set_aspect('equal')
    plt.title(title)

def plot_points(*args, **kwargs):
  for p in args:
    plt.scatter(p.x, p.y)
  # for p in args:
  #   if p.geom_type == "MultiPoint":
  #     plot_points(p.geom)
  #   if p.geom_type == "Point":
  #     plt.scatter(p.x, p.y)

def get_angle_of_line_at_point(geom, point):

  # Get the projection of the point
  projection = geom.project(point)

  # Get two additional points
  p1 = geom.interpolate(projection + 0.01)
  p2 = geom.interpolate(projection - 0.01)

  # Get angle
  dy = p2.y - p1.y
  dx = p2.x - p1.x

  return math.atan2(dy,dx)

def get_angles_of_poly(poly: sg.Polygon):

  # Interpolate random points on the polygon
  normalized_points = [random.uniform(0,1) for _ in range(50)]
  points = [poly.exterior.interpolate(p, normalized=True) for p in normalized_points]

  # Get the angle at those points
  angles = [get_angle_of_line_at_point(poly.exterior, point) for point in points]
  angles_deg = [math.degrees(angle) for angle in angles]

  # Round them to the nearest .5
  rounded_angles = [round(deg/2)*2 for deg in angles_deg]

  # List how many of what angle were detected
  results = dict(Counter(rounded_angles))


  return results

class SpaceHash:


  def __init__(self, envelope, r=10, c=10):
    self.mrr = envelope.minimum_rotated_rectangle
    self.r = r
    self.c = c
    self.objs = self.__initialize_hash__()
    self.angle = get_angle_of_line_at_point(self.mrr.exterior, self.mrr.exterior.interpolate(.01))
    self.w, self.h = self.__get_wh__(self.mrr)

  def __initialize_hash__(self):
    indices = range(self.r * self.c)
    objs = {index: [] for index in indices}
    return objs

  def __xy2uv__(self, x, y):
    u = x*math.cos(self.angle) - y*math.sin(self.angle)
    v = x*math.sin(self.angle) + y*math.cos(self.angle)
    u, v = x, y
    return u, v

  def __get_wh__(self, mrr):
    minx, miny, maxx, maxy = mrr.bounds
    dy = maxy - miny
    dx = maxx - minx
    w, h = self.__xy2uv__(dx, dy)
    return w, h

  def __hash__(self, point):
    u, v = self.__xy2uv__(point.x, point.y)
    pr = int(self.w/u)
    pc = int(self.h/v)
    return pr, pc

  def add(self, obj):
    pr, pc = self.__hash__(obj.centroid)
    print('pr', pr, 'pc', pc)
    key = pr * (self.r-1) + pc
    print("key", key)
    try:
      self.objs[key].append(obj)
    except:
      print("key is too big")

  def __str__(self):
    return f'{self.objs}'


# Rejection sampling
def generate_random_points(poly, num_points):
  points = []
  min_x, min_y, max_x, max_y = poly.bounds

  while len(points) < num_points:
      # Generate a random candidate point within the bounding box
      random_point = sg.Point(random.uniform(min_x, max_x),
                            random.uniform(min_y, max_y))

      # Check if the point is actually inside the polygon
      if poly.contains(random_point):
          points.append(random_point)

  return points

def generate_poisson_points(poly, min_dist, max_attempts=30):
    points = []
    min_x, min_y, max_x, max_y = poly.bounds

    # We use a while loop to keep trying until we can't fit any more
    # or reach a target. For simplicity, let's try to fill the space.
    active_list = [] # Points to "grow" from

    # Start with one random point inside
    while True:
        first_pt = sg.Point(random.uniform(min_x, max_x), random.uniform(min_y, max_y))
        if poly.contains(first_pt):
            points.append(first_pt)
            break

    # Rejection sampling with a distance check
    # Note: For many points, use a spatial index (like rtree) for distance checks!
    for _ in range(500): # Limit iterations for example
        candidate = sg.Point(random.uniform(min_x, max_x), random.uniform(min_y, max_y))

        if poly.contains(candidate):
            # Check if candidate is too close to any existing point
            if all(candidate.distance(p) >= min_dist for p in points):
                points.append(candidate)

    return points

def generate_polygon(angles_deg, max_area):

    # 1. Sort angles to ensure a clean perimeter
    angles = np.sort(np.radians(angles_deg))

    # 2. Calculate the angular differences between adjacent vertices
    # We include the gap between the last and first angle
    rolled_angles = np.roll(angles, -1)
    diffs = (rolled_angles - angles) % (2 * np.pi)

    # 3. Solve for r: Area = 0.5 * r^2 * sum(sin(delta_theta))
    sum_sin = np.sum(np.sin(diffs))
    r = lambda: np.sqrt((2 * max_area) / sum_sin)*random.random()

    # 4. Generate Cartesian coordinates (x, y)
    x = r() * np.cos(angles)
    y = r() * np.sin(angles)

    vertices = list(zip(x, y))
    return sg.Polygon(vertices)

def generate_farm(base_poly, angles, iterations=10):

  min_x, min_y, max_x, max_y = base_poly.bounds

  for _ in range(iterations):
    pass

def polygon_from_angles(angles, max_area, edge_length=1.0):
    """
    angles: list of angles in degrees (absolute directions or cumulative turns)
    max_area: maximum allowed area
    edge_length: initial edge length
    """

    # Step 1: build points
    x, y = 0.0, 0.0
    points = [(x, y)]

    for angle in angles:
        rad = math.radians(angle)
        dx = edge_length * math.cos(rad)
        dy = edge_length * math.sin(rad)
        x += dx
        y += dy
        points.append((x, y))

    # Step 2: close polygon
    poly = sg.Polygon(points)

    if not poly.is_valid:
        poly = poly.buffer(0)  # fix self-intersections if possible

    # Step 3: scale to fit max_area
    current_area = poly.area
    if current_area == 0:
        raise ValueError("Degenerate polygon (area = 0)")

    scale_factor = math.sqrt(max_area / current_area)

    if scale_factor < 1:
        poly = scale(poly, xfact=scale_factor, yfact=scale_factor, origin='centroid')

    return poly

def iterative_polygon(angles):
  x, y = 0,0
  r = lambda: random.random()
  points = []
  angles = np.radians(angles)

  for angle in angles:
    points.append(sg.Point(x,y))
    dist = r()
    x = x + dist*math.cos(angle)
    y = y + dist*math.sin(angle)

  return sg.Polygon(points)

def triangle(angle, base, point):
  height = math.tan(angle) * base
  p1 = sg.Point(point.x, point.y + height)

def gen_polygon(w,h,x=0,y=0,angle=0,iterations=0):
  poly = shapely.box(x-w/2,y-h/2,x+w/2,y+h/2)

  for _ in range(iterations):
    p = poly.exterior.interpolate(random.uniform(0,1), normalized=True)
    sw = w*random.random()
    sh = h*random.random()
    s = shapely.box(p.x-sw/2,p.y-sh/2,p.x+sw/2,p.y+sh/2)
    if random.random() > 0.8:
      coords = list(s.exterior.coords)
      coords.pop()
      coords.pop(2)
      print(f'Coords: {coords}')
      s = sg.Polygon(coords)
    poly = unary_union([poly, s])

  poly = sa.rotate(poly, angle)
  return poly

def right_triangle(base, angle, point, using_radians=True):
  if not using_radians:
    angle=np.radians(angle)
  height = base*math.tan(angle)
  p2 = sg.Point(point.x, point.y+height)
  p3 = sg.Point(point.x+width, point.y)
  return sg.Polygon([point, p2, p3])

def destructive_polygon(angles, iterations):
  # Get a random angle
  angles = np.radians(angles)
  base_angle = random.choice(angles)

  # Rectangle
  w = random.uniform(0,1)
  h = random.uniform(0,1)
  base = shapely.box(0,0,w,h)
  base = sa.rotate(base, base_angle, use_radians=True)

  # Interpolate
  dest_points = [base.exterior.interpolate(random.uniform(0,1)) for _ in range(iterations)]
  recs = []

  for p in dest_points:
    # Rectangles of various angle and height at each point
    rec = shapely.box(p.x, p.y, p.x + random.uniform(0,w), p.y + random.uniform(0,h))
    angle = get_angle_of_line_at_point(base.exterior, p)
    rec = sa.rotate(rec, angle)
    recs.append(rec)

  return base, recs

def erode_polygon(poly, iterations=100, noise_fx=lambda: random.random()):

  try:
    length = poly.exterior.length
  except:
    return poly
  avg_pitch = length / iterations
  cumulative_length = 0
  points = []

  while cumulative_length < length:
    cumulative_length += avg_pitch * random.random()
    og_point = poly.exterior.interpolate(cumulative_length)
    new_point = (og_point.x + noise_fx(), og_point.y + noise_fx())
    points.append(new_point)

  return sg.Polygon(points)

from shapely.strtree import STRtree
from shapely.geometry import MultiPolygon
from shapely.ops import unary_union

def get_unique_parts_with_strtree(polygon_list):
    # 1. Clean input to ensure all geometries are valid
    valid_polys = [p.buffer(0) if not p.is_valid else p for p in polygon_list]

    unique_parts = []
    processed_polys = []

    for i, current_poly in enumerate(valid_polys):
        if not processed_polys:
            unique_parts.append(current_poly)
            processed_polys.append(current_poly)
            continue

        # 2. Build the spatial index of what we've already accepted
        tree = STRtree(processed_polys)

        # 3. Find ONLY the previous polygons that intersect the current one
        # This is MUCH faster than checking against every single polygon
        overlapping_indices = tree.query(current_poly, predicate="intersects")
        overlapping_polys = [processed_polys[idx] for idx in overlapping_indices]

        if not overlapping_polys:
            # No overlaps at all? Keep the whole thing.
            unique_parts.append(current_poly)
        else:
            # 4. Subtract only the specific overlapping shapes
            mask = unary_union(overlapping_polys)
            diff = current_poly.difference(mask)

            if not diff.is_empty and diff.area > 1e-9:
                # 5. Explode MultiPolygons to ensure every part is counted
                if isinstance(diff, MultiPolygon):
                    unique_parts.extend(list(diff.geoms))
                else:
                    unique_parts.append(diff)

        # Always add the original current_poly to the processed list
        # so it acts as a mask for the NEXT items in the loop
        processed_polys.append(current_poly)

    return unique_parts

if __name__ == "__main__":

  envelope = sg.Polygon(([0,.5], [1,.2], [1,1],[0,1.1]))

  angles = get_angles_of_poly(envelope)
  base_angle = random.choice(list(angles))

  points = generate_poisson_points(envelope, .1)
  angles = [.3*np.degrees(np.arctan(p.y/p.x))+10*(0.5-1*random.random()) for p in points]

  polys = [gen_polygon(random.uniform(.1,.3), random.uniform(.1, .3), p.x, p.y,
                       angle,iterations=random.randint(0,1)) for p, angle in zip(points, angles)]

  polys = sorted(polys, key=lambda p: p.area, reverse=True)

  polys = get_unique_parts_with_strtree(polys)
  diff_polys = []

  for poly in polys:
    if envelope.contains(poly):
      diff_polys.append(poly)
    else:
      diff_polys.append(envelope.intersection(poly))

  diff_polys = [poly.buffer(random.uniform(0,-.005)) for poly in diff_polys]

  diff_polys = [erode_polygon(poly, iterations=20, noise_fx=lambda: 0.001*random.random()) for poly in diff_polys]

  plot_polygons(diff_polys)
  plot_polygons([envelope])
  plt.axis('equal')
  plt.show()
