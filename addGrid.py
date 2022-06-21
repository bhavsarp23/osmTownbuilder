from xmlOsm import xmlOsm as xo
import lineGeo.lineGeo as lg
import shapely.geometry as sg
import shapelyOsm.shapelyOsm as so
import shapely.affinity as sa


nx = 5
ny = 5
dx = 80
dy = 180
angle = 327.15
startPoint = sg.Point(0,0)

class Grid:


  def __init__(self, nx, ny, dx=100, dy=100, angle=0, startPoint=sg.Point(0,0)):

    self.gridLines = []
    # Get first x line from start to ny*dy + startPoint translated by angle
    r = ny*dy
    endPointX = lg.polarToCart(r, 90-angle)
    endPointX = sa.translate(endPointX, startPoint.x, startPoint.y)
    xLine = sg.LineString([startPoint, endPointX])

    r = nx*dx
    endPointY = lg.polarToCart(r, 180-angle)
    endPointY = sa.translate(endPointY, startPoint.x, startPoint.y)
    yLine = sg.LineString([startPoint, endPointY])

    for i in range(0, nx):
      line = xLine.parallel_offset(dx*i, 'left')
      self.gridLines.append(line)

    for i in range(0, ny):
      line = yLine.parallel_offset(dy*i, 'right')
      self.gridLines.append(line)

  def getGrid(self):
    return self.gridLines

  def addGrid(self, otherGrid):
    otherGrid = otherGrid.getGrid()
    # New grid
    newGrid = []
    # Get convex hull of self grid
    hull = sg.MultiLineString(self.gridLines).convex_hull
    # Iterate through other grid
    for otherLine in otherGrid:
      newLine = otherLine.difference(hull)
      if newLine.geom_type == 'LineString':
        newGrid.append(newLine)

    return newGrid + self.gridLines


g = Grid(nx, ny, dx, dy, angle, startPoint)
h = Grid(4,4,80,80,325, sg.Point(200,-200))
gridLines = g.getGrid()
a = so.ShapelyMap ()
tag = xo.Tag('highway', 'construction')

for line in gridLines:
    a.addLinestring(line, tag)

a.exportToXml('z.osm')
