# || Swami-Shriji ||

from perlin_noise import PerlinNoise
import matplotlib.pyplot as plt
import random

from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder





def get_topo(w, h):
  noise = PerlinNoise(octaves=10)
  pic = [[200*noise([i/w, j/h])+100 for j in range(w)] for i in range(h)]
  return pic

pic = get_topo(100, 50)
grid = Grid(matrix=pic)
start = grid.node(0,10)
end = grid.node(99, 25)
finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
path, runs = finder.find_path(start, end, grid)
for point in path:
  plt.scatter(point[0], point[1])
print("path", path)
weights = [[node.weight for node in row] for row in grid.nodes]
print(weights)
print(pic)
plt.imshow(pic)
if len(path) > 0:
  pass
plt.show()
