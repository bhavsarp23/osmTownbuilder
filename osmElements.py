# || Swami-Shriji ||

# --------------------------------- #
#             Libraries             #
# --------------------------------- #
import lxml.etree as et
import time

# --------------------------------- #
#             Constants             #
# --------------------------------- #
METER_CONV = 111139

# --------------------------------- #
#          Common Functions         #
# --------------------------------- #
def getRandomId():
  return str(-1*hash(time.time()))

def getCoordinateFromMeter(value):
  return value/METER_CONV

# --------------------------------- #
#              Classes              #
# --------------------------------- #
class Tag:

  def __init__(self, k, v):
    self.k = k
    self.v = v

  def getOsmElement(self):
    element = et.Element('tag')
    element.set('k', self.k)
    element.set('v', self.v)
    return element

class Node:

  def __init__(self, lon, lat, using_meters=True):
    if using_meters:
      lon = getCoordinateFromMeter(lon)
      lat = getCoordinateFromMeter(lat)
    self.lon = format(lon, '.10f')
    self.lat = format(lat, '.10f')
    self.id = getRandomId()
    self.tags = []

  def addTags(self,listOfTags=[]):
    self.tags.extend(listOfTags)

  def addRole(self, role):
    self.role = role

  def getOsmElement(self):
    element = et.Element('node')
    element.set('id', self.id)
    element.set('action', 'modify')
    element.set('visible', 'true')
    element.set('lat', self.lat)
    element.set('lon', self.lon)
    for tag in self.tags:
      element.append(tag.getOsmElement())
    return element

  def getRefElement(self):
    element = et.Element('nd')
    element.set('ref', self.id)
    return element

  def getMemberElement(self):
    element = et.Element('member')
    element.set('type', 'node')
    element.set('ref', self.id)
    if self.role != None:
      element.set('role',self.role)
    return element


class Way:

  def __init__(self, listOfRefs):
    self.refs = listOfRefs
    self.id = getRandomId()
    self.tags = []

  def addTags(self,listOfTags=[]):
    self.tags.extend(listOfTags)

  def addRole(self, role):
    self.role = role

  def getOsmElement(self):
    element = et.Element('way')
    element.set('id', self.id)
    element.set('action', 'modify')
    element.set('visible', 'true')

    for ref in self.refs:
      element.append(ref.getRefElement())

    for tag in self.tags:
      element.append(tag.getOsmElement())

    return element

  def getMemberElement(self):
    element = et.Element('member')
    element.set('type', 'way')
    element.set('ref', self.id)
    if self.role != None:
      element.set('role',self.role)
    return element

class Area(Way):
  def getOsmElement(self):
    element = et.Element('way')
    element.set('id', self.id)
    element.set('action', 'modify')
    element.set('visible', 'true')

    for ref in self.refs:
      element.append(ref.getRefElement())

    # Add the first reference again to complete the loop
    element.append(self.refs[0].getRefElement())

    for tag in self.tags:
      element.append(tag.getOsmElement())

    return element

class Relation:

  def __init__(self, listOfMembers, listOfTags=[]):
    self.members = listOfMembers
    self.tags = listOfTags
    self.id = getRandomId()

  def addTags(self, listOfTags):
    self.tags.extend(listOfTags)

  def getOsmElement(self):
    element = et.Element('relation')
    element.set('id', self.id)
    element.set('action', 'modify')
    element.set('visible', 'true')
    for member in self.members:
      element.append(member.getMemberElement())

    for tag in self.tags:
      element.append(tag.getOsmElement())

    return element

class OsmMap:

  def __init__(self, string=''):
    if string != '':
      pass

    self.nodes = []
    self.ways = []
    self.relations = []

  def getOsmElement(self):
    element = et.Element('osm')
    element.set('version', '0.6')
    element.set('generator', 'script')

    for node in self.nodes:
      element.append(node.getOsmElement())

    for way in self.ways:
      element.append(way.getOsmElement())

    for relation in self.relations:
      element.append(relation.getOsmElement())

    return element

  def addNodes(self,listOfNodes):
    self.nodes.extend(listOfNodes)

  def addWays(self,listOfWays, add_nodes=True):
    self.ways.extend(listOfWays)
    # Add the nodes from the ways into nodes
    if add_nodes:
      for way in listOfWays:
        self.addNodes(way.refs)

  def addRelations(self,listOfRelations, add_members=True):
    self.relations.extend(listOfRelations)
    if add_members:
      for relation in self.relations:
        for member in relation.members:
          if type(member) == Node:
            self.addNodes([Node])
          if (type(member) == Way) or (type(member) == Area):
            self.addWays([member])

  def writeToFile(self, filename='output.osm'):
    root = self.getOsmElement()
    tree = et.ElementTree(root)
    tree.write(filename,pretty_print=True)

if __name__=="__main__":
  map = OsmMap()

  nodeA = Node(0,0)
  nodeB = Node(100,100)
  nodeC = Node(0,100)
  nodeD = Node(10,20)
  nodeE = Node(80,90)
  nodeF = Node(20,90)
  areaABC = Area([nodeA, nodeB, nodeC])
  areaABC.addRole('outer')
  areaDEF = Area([nodeD, nodeE, nodeF])
  areaDEF.addRole('inner')
  relationABCDEF = Relation([areaABC, areaDEF])
  relationABCDEF.addTags([Tag('type', 'multipolygon'), Tag('building', 'yes')])
  map.addWays([areaABC, areaDEF])
  map.addRelations([relationABCDEF])
  map.writeToFile()

