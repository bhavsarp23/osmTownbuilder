# || Swami-Shriji ||

from lxml import etree as et
import time


METER_CONV = 111000

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



