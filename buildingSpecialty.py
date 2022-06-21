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
AMENITY_LIST_PATH = './names/amenityList.csv'
SHOP_LIST_PATH = './names/shopList.csv'

# Probability weights
ROAD_SUFFIX_THRSH = 0.25
COMPOUND_WORD_THRSH = 0.75
AMENITY_THRSH = 0.1

# Road suffixes
MARG = 'भवन'
SADAK = 'इमारत'
SHERI = 'गृह'
POL = 'वास्तु'
GULLY = 'मकान'
VITHI = 'घर'
RASTA = 'सदन'
PATH = 'शाला'
STREET_SUFFIXES = [MARG,SADAK,SHERI,POL,GULLY,VITHI,RASTA,PATH]

# Building specialities
SHOP = 'shop'
AMENITY = 'amenity'
OFFICE = 'office'
LEISURE = 'leisure'
BUILDING_SPECIALTIES = [AMENITY, LEISURE, OFFICE, SHOP]

# --------------- #
#    Functions    #
# --------------- #
# Return a list of Hindi words as well as its part of speech
def getDictionary (namePath):

  nameFrame = pd.read_csv(namePath)
  nameList = nameFrame['hword'].to_list()
  partList = nameFrame['egrammar'].to_list()
  return nameList, partList

def getList(namePath, key):
  listFrame = pd.read_csv(namePath)
  return listFrame[key].to_list(), listFrame['weight'].to_list()

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
def checkForUnusedBuilding(way):
  # Check if the way has any tag at all; if not, return false
  if len(way.findall('tag')) == 0:
    return False

  # Check if way is a building; if not, return false
  for element in way.findall('tag'):
    k = element.get('k')
    v = element.get('v')
    if not ((k == 'building' and v == 'yes')):
          # If not, return false
          return False

  # Check if there is any specialty tag associated with the building; if so, return false
  for element in way.findall('tag'):
    k = element.get('k')
    if k in BUILDING_SPECIALTIES:
      return False

  # Otherwise, return true
  return True

# ------------------- #
#    Main function    #
# ------------------- #
# Get lists
nameList, partList = getDictionary(NAME_LIST_PATH)
amenityList, weights = getList(SHOP_LIST_PATH, SHOP)

# Find unnamed highways
osmFile = 'output.osm'
tree = et.parse(osmFile)
osmRoot = tree.getroot()
# Find ways in OSM file
for way in osmRoot.findall('way'):
  # Find unnamed valid highways in OSM file
  if checkForUnusedBuilding(way):
    # If past the amenity threshold
    if rd.random() > AMENITY_THRSH:
      # Get a random type of amenity
      amenity = rd.choices(amenityList,weights=weights)[0]

      # Get a random name
      name = rd.choice(nameList)

      # Add name and amenity to way
      nameElement = et.Element('tag')
      nameElement.set('k','name')
      nameElement.set('v',name)
      amenityElement = et.Element('tag')
      amenityElement.set('k', SHOP)
      amenityElement.set('v', amenity)
      way.append(nameElement)
      way.append(amenityElement)
    else:
      tag = way.findall('tag')[0]
      tag.set('v', 'residential')

tree.write('z.osm',pretty_print=True)

#print(getStreetName(nameList))

