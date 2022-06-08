# || Swami-Shriji ||

# --------------- #
#    Libraries    #
# --------------- #
import pandas as pd
import random as rd
from lxml import etree as et

# --------------- #
#   Definitions   #
# --------------- #
NAME_LIST_PATH = './names/englishHindiNouns.csv'

# Probability weights
ROAD_SUFFIX_THRSH = 0.25
COMPOUND_WORD_THRSH = 0.75

# Road suffixes
MARG = 'मार्ग'
SADAK = 'सड़क'
SHERI = 'शेरी'
POL = 'पोल'
GULLY = 'गली'
VITHI = 'वीथी'
RASTA = 'रास्ता'
PATH = 'पथ'
STREET_SUFFIXES = [MARG,SADAK,SHERI,POL,GULLY,VITHI,RASTA,PATH]

# --------------- #
#    Functions    #
# --------------- #
# Return a list of Hindi words as well as its part of speech
def getDictionary (namePath):

  nameFrame = pd.read_csv(namePath)
  nameList = nameFrame['hword'].to_list()
  partList = nameFrame['egrammar'].to_list()
  return nameList, partList

def getStreetName(nameList):
  # Get a random name
  randomIndex = rd.randrange(0,len(nameList))
  streetName = nameList[randomIndex]
                  
  # If compound, add another word
  if rd.random() > COMPOUND_WORD_THRSH:
    randomIndex = rd.randrange(0,len(nameList))
    streetName += ' ' + nameList[randomIndex]
    
  # Add road suffix if needed
  if rd.random() > ROAD_SUFFIX_THRSH:
    randomIndex = rd.randrange(0,len(STREET_SUFFIXES))
    streetName += ' ' + STREET_SUFFIXES[randomIndex]
    
  return streetName

# Return true if the given way is an unnamed street
def checkForUnnamedStreet(way):
  if len(way.findall('tag')) == 0:
    return False
  
  # Check if the given way has a valid highway type
  for element in way.findall('tag'):
    k = element.get('k')
    v = element.get('v')
    print(k,v)
    if not ((k == 'highway' and v == 'pedestrian') or
            (k == 'highway' and v == 'living_street') or
            (k == 'highway' and v == 'residential')):
          # If not, return false
          return False
  
  # If the given way has a tag with name, return false
  for element in way.findall('tag'):
    if (element.get('k') == 'name') == True:
      return False
    
  # Otherwise, return true
  return True

# ------------------- #
#    Main function    #
# ------------------- #
# Get lists
nameList, partList = getDictionary(NAME_LIST_PATH)

# Find unnamed highways
osmFile = 'output.osm'
tree = et.parse(osmFile)
osmRoot = tree.getroot()
# Find ways in OSM file
for way in osmRoot.findall('way'):
  # Find unnamed valid highways in OSM file
  if checkForUnnamedStreet(way):
    # Get a random name
    name = getStreetName(nameList)
    # Add name to way
    nameElement = et.Element('tag')
    nameElement.set('k','name')
    nameElement.set('v',name)
    way.append(nameElement)

tree.write('z.osm',pretty_print=True)

#print(getStreetName(nameList))

