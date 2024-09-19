# || Swami-Shriji ||

import matplotlib.pyplot as plt
import numpy as np
import shapely.geometry as sg
import random
from collections import defaultdict
import time

def plot_point(*points):
  for point in points:
    plt.scatter(point.x, point.y)

def plot_poly(*polys):
  for poly in polys:
    plt.plot(*poly.exterior.xy)

def plot_line(*lines):
  for line in lines:
    plt.plot(*line.xy)

BOUND_X = 1000
BOUND_Y = 1000
GRID_SIZE = 20
NUM_BOXES = 1200

def get_bounds():
  w = random.uniform(0, 10)
  h = random.uniform(0, 10)
  x = random.uniform(0,BOUND_X)
  y = random.uniform(0,BOUND_X)
  minx = x - w/2
  miny = y - h/2
  maxx = x + w/2
  maxy = y + h/2
  return [minx, miny, maxx, maxy]

def naive_collision_check(boxes):
  count1 = 0
  for box1 in boxes:
    for box2 in boxes:
      if box1 is box2:
        continue
      if box1.intersects(box2):
        count1 += 1

  return count1

def get_box_hash(box) -> int:
  xi = np.floor(box.centroid.x/GRID_SIZE)
  yi = np.floor(box.centroid.y/GRID_SIZE)
  return yi * np.ceil(BOUND_X/GRID_SIZE) + xi

def get_adjacent_hashes(og_hash):
  rows = np.ceil(BOUND_X / GRID_SIZE)
  cols = np.ceil(BOUND_Y / GRID_SIZE)
  row = og_hash // cols
  col = og_hash % cols

  adjacent_hashes = []

  directions = [
    (0, 0), (-1, 0), (1, 0), (0, -1), (0, 1),  # self, up, down, left, right
    (-1, -1), (-1, 1), (1, -1), (1, 1)  # diagonals: top-left, top-right, bottom-left, bottom-right
  ]

  for dr, dc in directions:
    new_row = row + dr
    new_col = col + dc

    if 0 <= new_row < rows and 0 <= new_col < cols:
      adjacent_index = new_row * cols + new_col
      adjacent_hashes.append(adjacent_index)

  adjacent_hashes.sort()
  return adjacent_hashes

def get_adjacent_boxes(h, hash_boxes):
  hashes = get_adjacent_hashes(h)
  adjacent_boxes = []
  for h in hashes:
    adjacent_boxes.extend(hash_boxes.get(h))
  return adjacent_boxes

def spatial_hashing_collision_check(boxes) -> int:
  count = 0

  # Create a grid-based dict with each coord being a key
  w = np.ceil(BOUND_X / GRID_SIZE)
  h = np.ceil(BOUND_Y / GRID_SIZE)
  hash_boxes = {k : [] for k in range(int(w*h))}

  # Fill in each coord with boxes with centroids in that coord
  for box in boxes:
    hash_boxes[get_box_hash(box)].append(box)

  # Check for collisions within the same hash
  for h in hash_boxes:
    adjacent_boxes = get_adjacent_boxes(h, hash_boxes)

    for box1 in hash_boxes[h]:
      for box2 in adjacent_boxes:
        if box1 is box2:
          continue
        if box1.intersects(box2):
          count += 1

  return count

if __name__ == "__main__":

  # Make a bunch of boxes in random places
  boxes = [sg.box(*get_bounds()) for i in range(NUM_BOXES)]

  # Naive collision check
  start_time = time.time()
  count = naive_collision_check(boxes)
  print("{} boxes collide. Took {} seconds.".format(count, time.time() - start_time))

  # Spatial hashing collision check
  start_time = time.time()
  count = spatial_hashing_collision_check(boxes)
  print("{} boxes collide. Took {} seconds.".format(count, time.time() - start_time))


  # Plot the boxes
  plot_poly(*boxes)
  plt.show()


