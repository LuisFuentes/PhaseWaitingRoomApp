from app import app
from flask import request #For handling GET/POST requests
import pygame #For Sound
import webbrowser #For Opening up browser window

@app.route('/')
@app.route('/index')
def TestPlaySound():
    # Play some sound if this page is visited
    pygame.mixer.init()
    pygame.mixer.music.load("Bowed-Bass-C2.wav")
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
        pygame.mixer.music.load("Bowed-Bass-C2.wav")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue
        
        # url = "http://www.google.com" #For testing
        # open up the Phase Waiting Room HTML page
        url = "/home/odroid/Phase_Waiting_Room_App/Test.html"

        # open the url in the Firefox browser, opening a new tab if possible
        webbrowser.get('firefox').open(url)

        return "Chart Id: " + str(patientChartId)
    else:
        return "Error!!!"

