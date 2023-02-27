# || Swami-Shriji ||

import random
import shapely.geometry as sg
import shapely.affinity as sa
import math

import matplotlib.pyplot as plt

class RoadSegment:

  def __init__(self, geometry, lean_iteration):

    self.geometry = geometry
    self.lean_iteration = lean_iteration

    self.lean_left = False
    self.lean_right = False
    self.end_segment = False

  def get_direction_angle(self) -> float:
    dx = self.geometry.coords[1][0] - self.geometry.coords[0][0]
    dy = self.geometry.coords[1][1] - self.geometry.coords[0][1]
    print(math.atan2(dy,dx)/math.pi*180)
    return math.atan2(dy, dx)

  def plot(self):
    print(*self.geometry.xy)
    plt.plot(*self.geometry.xy)

class MajorGenerator:

  def __init__(self, **kwargs):

    # Get kwargs
    self.seed = kwargs.get('seeds', 0)
    self.map_size = kwargs.get('map_size', 100)
    self.max_angle = kwargs.get('max_angle', math.pi/2)
    self.branch_probability = kwargs.get('branch_probability', lambda: 1)
    self.road_length = kwargs.get('road_length', 10)
    self.max_segments = kwargs.get('max_segments', 20)

    self.queue = []
    self.global_goal_roads = []
    self.segments = []

  def run(self):

    # Add start segments
    start_segments = self.generate_start_segments()
    self.queue.extend(start_segments)

    while(len(self.queue) != 0 and len(self.segments) < self.max_segments):

      current = self.queue.pop()
      self.segments.append(current)
      self.global_goals(current)



  def global_goals(self, segment: RoadSegment):

    if segment.end_segment:
      return

    self.global_goal_roads = []
    dir_angle = segment.get_direction_angle()

    # Branching
    if self.branch_probability() > 0.3:
      max_int = 6
    elif self.branch_probability() < 0.03:
      max_int = 100
    else:
      max_int = int(round(3/self.branch_probability(), 0))

    branch_random = random.randint(0, max_int)

    # Road branches to the right
    if branch_random == 1:
      normal_angle = dir_angle - math.pi/2
      branched_segment = self.generate_road_segment(segment.geometry.coords[1], normal_angle, 0)
      self.global_goal_roads.append(branched_segment)

    # Road branches to the left
    if branch_random == 2:
      normal_angle = dir_angle + math.pi/2
      branched_segment = self.generate_road_segment(segment.geometry.coords[1], normal_angle, 0)
      self.global_goal_roads.append(branched_segment)

    # Road branches to the right and left
    if branch_random == 2:
      right_angle = dir_angle - math.pi/2
      left_angle = dir_angle + math.pi/2
      branched_segment_left = self.generate_road_segment(segment.geometry.coords[1], left_angle, 0)
      branched_segment_right = self.generate_road_segment(segment.geometry.coords[1], right_angle, 0)
      self.global_goal_roads.append(branched_segment_left)
      self.global_goal_roads.append(branched_segment_right)

    # Road continues
    self.global_goal_roads.append(self.get_continuing_segment(segment))
    self.queue.extend(self.global_goal_roads)

  def get_continuing_segment(self, segment) -> RoadSegment:

    start_point = segment.geometry.coords[1]

    dir_angle = segment.get_direction_angle()
    if self.max_angle < math.pi/4:
      return self.generate_road_segment(start_point, dir_angle, 0)

    # A new lean is needed
    if segment.lean_iteration == 3:
      seed = random.randint(0, 3)

      if seed == 1:
        dir_angle += random.uniform(0-self.max_angle, 0)
        new_segment = self.generate_road_segment(start_point, dir_angle, 0)
        new_segment.lean_right = True
        return new_segment

      elif seed == 2:
        dir_angle += random.uniform(0,self.max_angle)
        new_segment = self.generate_road_segment(start_point, dir_angle, 0)
        new_segment.lean_left = True
        return new_segment

      else:
        return self.generate_road_segment(start_point, dir_angle, 0)

    else:

      if segment.lean_right:
        dir_angle += random.uniform(0-self.max_angle, 0)
        segment1 = self.generate_road_segment(start_point, dir_angle, segment.lean_iteration + 1)
        segment1.lean_right = True
        return segment1

      elif segment.lean_left:
        dir_angle += random.uniform(0, self.max_angle)
        segment1 = self.generate_road_segment(start_point, dir_angle, segment.lean_iteration + 1)
        segment1.lean_left = True
        return segment1
      else:
        return self.generate_road_segment(start_point, dir_angle, segment.lean_iteration + 1)



  def generate_start_segments(self) -> list[RoadSegment]:
    # Generate a point in the middle quarter of the map
    sample_x = random.uniform(self.map_size/2, 3*self.map_size/4)
    sample_y = random.uniform(self.map_size/2, 3*self.map_size/4)
    start_point = sg.Point(sample_x, sample_y)
    print(start_point)

    # Generate the next two points
    dir_angle = random.uniform(0, 2*math.pi)
    dx = self.road_length * math.cos(dir_angle)
    dy = self.road_length * math.sin(dir_angle)
    p1 = sa.translate(start_point, dx, dy)
    p2 = sa.translate(start_point, -1*dx, -1*dy)

    # Generate start segments
    s1 = RoadSegment(sg.LineString([start_point, p1]), 0)
    s2 = RoadSegment(sg.LineString([start_point, p2]), 0)

    return [s1, s2]

  def generate_road_segment(self,
                            start_point: sg.Point,
                            dir_angle: float,
                            lean_iteration: int
                            ) -> RoadSegment:
    dx = self.road_length * math.cos(dir_angle)
    dy = self.road_length * math.sin(dir_angle)
    next_point = (start_point[0] + dx, start_point[1] + dy)
    #next_point = sa.translate(start_point, dx, dy)
    segment = sg.LineString([start_point, next_point])
    return RoadSegment(segment, lean_iteration)


if __name__ == "__main__":

  m = MajorGenerator(max_angle=math.pi/2, max_segments=400,
                     branch_probability=lambda: 3*random.random()
                     )
  m.run()
  for segment in m.segments:
    segment.plot()

  plt.show()
