# || Swami-Shriji ||

from lxml import etree as et
import time


METER_CONV = 111139

class OsmMap:
    nodeList = []
    wayList = []
    relationList = []
    referenceList = []
    tagList = []
    root = et.Element('osm')
    tree = et.ElementTree(root)
    root.set('version','0.6')
    root.set('generator','script')


    def __init__(self):
        self.nodeList = self.nodeList

    def addNode(self, node):
        self.nodeList.append(et.SubElement(self.root,"node"))
        self.nodeList[-1].set("id",node.id)
        self.nodeList[-1].set('action',node.action)
        self.nodeList[-1].set('visible',node.visible)
        self.nodeList[-1].set('lat',node.lat)
        self.nodeList[-1].set('lon',node.lon)
        # for tag in node.tagList:
        #     self.tagList.append(et.SubElement(self.nodeList[-1],'tag'))
        #     self.tagList[-1].set('k',tag.k)
        #     self.tagList[-1].set('v',tag.v)

    def removeLastNode(self):
        self.nodeList.pop()

    def exportToXml (self, filename="output.osm"):
        self.tree.write(filename,pretty_print=True)

    def addWay(self, way):
        self.wayList.append(et.SubElement(self.root,"way"))
        self.wayList[-1].set('id',way.id)
        self.wayList[-1].set('action',way.action)
        self.wayList[-1].set('visible',way.visible)

        for Node in way.nodeList:
            self.addNode(Node)
            self.referenceList.append(et.SubElement(self.wayList[-1],'nd'))
            self.referenceList[-1].set('ref',Node.id)
        
        for tag in way.tagList:
            self.tagList.append(et.SubElement(self.wayList[-1],'tag'))
            self.tagList[-1].set('k',tag.k)
            self.tagList[-1].set('v',tag.v)

    def addArea(self, area):
        self.wayList.append(et.SubElement(self.root,"way"))
        self.wayList[-1].set('id',area.id)
        self.wayList[-1].set('action',area.action)
        self.wayList[-1].set('visible',area.visible)

        
        for Node in area.nodeList:
            self.referenceList.append(et.SubElement(self.wayList[-1],'nd'))
            self.referenceList[-1].set('ref',Node.id)

        # Remove the last Node as it would be added twice
        area.nodeList.pop()

        for Node in area.nodeList:
            self.addNode(Node)

        for tag in area.tagList:
            self.tagList.append(et.SubElement(self.wayList[-1],'tag'))
            self.tagList[-1].set('k',tag.k)
            self.tagList[-1].set('v',tag.v)
#
# Node(lat, lon)
class Node:
    id = '0'
    action = 'modify'
    visible = 'true'
    lat = '0'
    lon = '0'
    tagList = []

    # Init function
    def __init__(self):
        self.id = self.id

    # Init function overload with latitude and longitude
    def __init__(self, lat, lon):
        # ID is based on ID of Node class instance
        self.lat = str(lat/METER_CONV)
        self.lon = str(lon/METER_CONV)
        self.id = str(-1*abs(hash(self.lat+self.lon+"node")))

    def coordinates(self, lat, lon):
        self.lat = str(lat/METER_CONV)
        self.lon = str(lon/METER_CONV)

    def addTags (self,tags):
        self.tagList.append(tags)

class Way:
    id = 0
    action = 'modify'
    visible = 'true'
    nodeList = []
    tagList = []

    def __init__(self, nodeList):
        self.id = str(-1*abs(hash(time.time())))
        #self.id = str(-1*id(self))
        self.nodeList = nodeList

    def addNodes(self, nodeList):
        self.nodeList.append(nodeList)

    def addTags(self, tagList):
        self.tagList.append(tagList)
        
class Area(Way):
    def __init__(self, nodeList):
        self.id = str(-1*abs(hash(time.time())))
        self.nodeList = nodeList
        self.nodeList.append(nodeList[0])

class Tag:
    k = ''
    v = ''
    def __init__(self,k,v):
        self.k = k
        self.v = v

class Member:
    object_ref = ''
    type = ''
    role = ''
    def __init__(self):
        object_ref = ''

class Relation:
    id = 0
    action = 'modify'
    visible = 'true'
    member_list = []
    tag_list = []

    def __init__(self):
        self.id = str(-1*id(self))

    def addMembers(self, member_list):
        self.member_list = member_list
    
    def addTags(self, tag_list):
        self.tag_list = tag_list

class xmlObject:
    a = 0

def parseOsm (osmFile):
    tree = et.parse(osmFile)

    root = tree.getroot()

    map = OsmMap()

    # Get all nodes in osm
    for item in root.findall('node'):
        id = item.get('id')
        tags = []
        lat = float(item.get('lat'))
        lon = float(item.get('lon'))
        node = Node(lat, lon)
        # Find tags
        for element in item.findall('tag'):
            k = (element.get('k'))
            v = (element.get('v'))
            tags.append(Tag(k,v))
        print(tags)
        node.id = id
        # node.addTags(tags)
        map.addNode(node)

    # Get ways
    for item in root.findall('way'):
        id = item.get('id')
        tags = []
        nodes = []
        for element in item.findall('tag'):
            k = (element.get('k'))
            v = (element.get('v'))
            tags.append(Tag(k,v))

        for element in item.findall('nd'):
            nodeRef = (element.get('ref'))
            # Look for the nodes by reference in nodeList
            # Duplicate them for the way
            for node in map.nodeList:
                if node.get('id') == nodeRef:
                    print(float(node.get('lat'))*METER_CONV, node.get('lon'))
            
            nodes.append(node)
        # way = Way()
        # map.addWay(item)
    return map

def checkForResidentialHighway (way):
    for element in way.findall('tag'):
        if ((element.get('k') == 'highway') & (element.get('v') == 'residential')):
            return True
        else:
            return False

def checkForConstructionHighway (way):
    for element in way.findall('tag'):
        if ((element.get('k') == 'highway') & (element.get('v') == 'construction')):
            return True
        else:
            return False

def getNodesByRef (osmRoot, refs):
    nodes = []
    for ref in refs:
        for item in osmRoot.findall('node'):
            if item.get('id') == ref:
                lat = float(item.get('lat'))*METER_CONV*METER_CONV
                lon = float(item.get('lon'))*METER_CONV*METER_CONV
                nodes.append(Node(lat,lon))
    return nodes


def getResidentialStreets ():
    osmFile = 'output.osm'

    tree = et.parse(osmFile)

    osmRoot = tree.getroot()

    ways = []
    # Find all ways
    for item in osmRoot.findall('way'):
        nodeIds = []
        # Find ways with the tag highway=residential
        if checkForResidentialHighway(item) == True:
            # Add get all nodes in the way
            for element in item.findall('nd'):
                nodeIds.append(element.get('ref'))
            # Make a lineString based on the nodes
            ways.append(getNodesByRef(osmRoot, nodeIds))
    return (ways)

def getConstructionStreets ():
    osmFile = 'output.osm'

    tree = et.parse(osmFile)

    osmRoot = tree.getroot()

    ways = []
    # Find all ways
    for item in osmRoot.findall('way'):
        nodeIds = []
        # Find ways with the tag highway=residential
        if checkForConstructionHighway(item) == True:
            # Add get all nodes in the way
            for element in item.findall('nd'):
                nodeIds.append(element.get('ref'))
            # Make a lineString based on the nodes
            ways.append(getNodesByRef(osmRoot, nodeIds))
    return (ways)



