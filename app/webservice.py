from app import app, generalList, healthcareList #The Facts lsts

#For handling GET/POST requests & Rendering HTML Template
from flask import request, render_template, make_response

import webbrowser #For Opening up browser window
import os.path #For tranversing the file directory
import json #For transfer jinja data into JS format

# private functions
def ConstructWaitingRoomHTML(htmlText, filename):
    # Function shall create the file that holds
    # the waiting room html using the template
    output = open(filename,"w")
    output.write(htmlText)
    output.close()

@app.route('/')
@app.route('/index')
def Index():
    return "Hello, World! This is a confirmation that" \
            + " the default Waiting Room URL can be reached."


# Route for waiting room POST
# Accepts a facility name and patient Chart ID to display on the screen.
@app.route('/WaitingRoom/<facilityName>/<patientChartId>', methods=['POST'])
def NotifyWaitingRoom(facilityName, patientChartId):
    # Verify this is a POST & 'patientChartId' and 'facilityName' are not null
    if request.method == 'POST' and patientChartId and facilityName:
        # Render the HTML temlate & pass in the patient chart id
        # using jinja and store the template's html (string)
        templateHTML = render_template('WaitingRoomTemplate.html', \
                patientChartId=patientChartId, facilityName=json.dumps(facilityName),
                generalFactsList=json.dumps(generalList),
                healthcareFactsList=json.dumps(healthcareList))

        # Next, generate a temporary HTML page 
        filename = 'tempWaitingRoomPage.html' #temp template HTML file
        ConstructWaitingRoomHTML(templateHTML, filename)
        # Open the new temp file through Firefox
        webbrowser.get('firefox').open("file://" + os.path.abspath(filename))
        # Respond to the server 
        return "Chart Id: " + patientChartId + " at " + facilityName
    else:
        return "Error on generating Waiting Room Screen on chart ID: " \
                + patientChartId + " at" + facilityName
