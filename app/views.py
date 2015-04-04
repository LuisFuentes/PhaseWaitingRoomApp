from app import app

#For handling GET/POST requests & Rendering HTML Template
from flask import request, render_template, make_response

import pygame #For Sound

import webbrowser #For Opening up browser window
import os.path #For tranversing the file directory

# private functions
def ConstructWaitingRoomHTML(htmlText, filename):
    # Function shall create the file that holds
    # the waiting room html using the template
    output = open(filename,"w")
    output.write(htmlText)
    output.close()

@app.route('/')
@app.route('/index')
def TestPlaySound():
    # Play some sound if this page is visited
    pygame.mixer.init()
    pygame.mixer.music.load("./app/static/OOT_Secret.wav")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue

    return "Hello, World!"

# Route for waiting room POST
# Accepts a patient Chart ID to display on the screen.
@app.route('/WaitingRoom/<patientChartId>', methods=['POST'])
def NotifyWaitingRoom(patientChartId):
    # Verify this is a POST & The 'patientChartId' is not null
    if request.method == 'POST' and patientChartId:
        # Play some sound if this page is visited
        pygame.mixer.init()
        pygame.mixer.music.load("./app/static/OOT_Secret.wav")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue

        # First, let's render the HTML Template we have for the
        # Waiting Room html page.
        
        # Render the HTML temlate & pass in the patient chart id
        # Store the template's html (string)
        templateHTML = render_template('WaitingRoomTemplate.html', patientChartId=patientChartId)

        # For testing, url=html online/local page
        # webbrowser.get('firefox').open(url) 
         
        # Next, generate a temporary HTML page & open the new temp file
        # through Firefox

        filename = 'tempWaitingRoomPage.html' #temp template HTML file
        ConstructWaitingRoomHTML(templateHTML, filename)
        
        # Finally, open in firefox the HTML File
        webbrowser.get('firefox').open("file://" + os.path.abspath(filename))
        
        return "Chart Id: " + str(patientChartId)
    else:
        return "Error!!!"

