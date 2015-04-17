from flask import Flask
import xml.etree.ElementTree as ET #For loading our facts XMLs

# Next, load in the XML fact files
generalTree = ET.parse('./app/static/WaitingRoom_GeneralFacts.xml')
healthcareTree = ET.parse('./app/static/WaitingRoom_HealthcareFacts.xml')

genRoot = generalTree.getroot()
healthRoot = healthcareTree.getroot()

generalFactsList = [] #List of all general facts
healthcareFactsList = [] #List of all healthcare facts

for child in genRoot:
    generalFactsList.append(child.text)

for child in healthRoot:
    healthcareFactsList.append(child.text)

# Store in memory the current queue
windowsQueue = { 'WindowQueue1' : {}, 'WindowQueue2' : {}, 'WindowQueue3' : {} }

# Store in memory the pointer to the XML file and the # of windows
appConfigXML= ET.parse('./app/config/AppConfig.xml')
numberOfWindows = int(appConfigXML.getroot().find('Windows').text)




app = Flask(__name__)
from app import webservice
