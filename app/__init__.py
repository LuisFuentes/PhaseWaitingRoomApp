from flask import Flask

import xml.etree.ElementTree as ET #For traverseing our facts XMLs

# First, load in the config files

# Next, load in the XML fact files
generalTree = ET.parse('./app/static/WaitingRoom_GeneralFacts.xml')
healthcareTree = ET.parse('./app/static/WaitingRoom_HealthcareFacts.xml')

genRoot = generalTree.getroot()
healthRoot = healthcareTree.getroot()

generalList = [] #List of all general facts
healthcareList = [] #List of all healthcare facts

for child in genRoot:
    generalList.append(child.text)

for child in healthRoot:
    healthcareList.append(child.text)

app = Flask(__name__)
from app import views
