''' Imports '''
# Import the application and the facts lists
from app import app, generalFactsList, healthcareFactsList, windowsQueue, \
    appConfigXML, numberOfWindows 

# Import for handling requests & Rendering HTML Template
from flask import request, render_template, make_response

# Import for opening a web browser, getting file pathes, and JS format
import webbrowser, os.path, json, logging, datetime, time

# Import for accessing the config xml file
import xml.etree.ElementTree as ET

''' Private Functions '''
def ConstructWaitingRoomHTML(htmlText, filename):
    '''
    Function shall create the file that holds
    the waiting room html using the HTML text
    '''
    logging.info(("Attempting to construct HTML page "
        "to display to the waiting room."))

    output = open(filename,"w")
    output.write(htmlText)
    output.close()
    
    logging.info(("Successfully created/updated "
        "the HTML page to display to the waiting room."))

def UpdateWaitingRoomQueue(windowNumber, patientChartId):
    '''
    Function updates the queue for a given window and adds the
    patient chart id into that window's queue
    '''
    # First check if the pt is already on a window's queue (cannot have duplicates)
    if patientChartId in windowsQueue["WindowQueue1"].values() \
            or patientChartId in windowsQueue["WindowQueue2"].values() \
            or patientChartId in windowsQueue["WindowQueue3"].values():
        # Pt is on queue
        logging.error("Patient %s is already in a window's queue %s"
                % (patientChartId, json.dumps(windowsQueue)))
        return;

    tempWindowQueue = windowsQueue["WindowQueue" + windowNumber]

    if len(tempWindowQueue.keys()) == 3:
        # Queue is full, pop off the oldest ID and push each ID up
        tempWindowQueue["3"] = tempWindowQueue["2"]
        tempWindowQueue["2"] = tempWindowQueue["1"]
        tempWindowQueue["1"] = patientChartId
    else:
        # Else, move all pts down one spot and add newest pt to the top
        if "2" in tempWindowQueue.keys():
            # Move 2nd pt to 3rd spot
            tempWindowQueue["3"] = tempWindowQueue["2"]
        if "1" in tempWindowQueue.keys():
            # Move 1st pt to 2nd spot
            tempWindowQueue["2"] = tempWindowQueue["1"]
       
        
        # TODO: Get the time now and in 5 mins. Get the difference in minutes

        expirationTime = time.mktime(
                (datetime.datetime.now() + datetime.timedelta(minutes=5)).timetuple())
        

        # Add newest pt to the top of queue
        tempWindowQueue["1"] = {
                "ID" : patientChartId,
                "ExpirationTime" : expirationTime }

    # Update the window's queue
    windowsQueue["WindowQueue" + windowNumber] = tempWindowQueue


''' HTTP Public Functions '''
@app.route('/')
@app.route('/index')
def Index():
    ''' Default page '''
    return ("Hello, World! This is a confirmation page to show "
        "that the default Waiting Room URL can be reached.")

@app.route('/Update/Windows/<int:newNumberOfWindows>', methods=['POST'])
def UpdateNumberOfWindows(newNumberOfWindows):
    '''
        Function handles updating the config file's count for the
        number of windows at this clinic. Expects an int and the
        value must be 1, 2, or 3.
    '''
    global numberOfWindows
    
    if newNumberOfWindows < 1 or newNumberOfWindows > 3:
        # Bad number of windows
        log.error("Cannot update the number of windows this clinic has "
                "since the value passed in is not within 1 to 3, value is %s."
                % (newNumberOfWindows))
        return "Bad number of windows submitted."

    # Update the window count for the XML file
    appConfigXML.getroot().find('Windows').text = str(newNumberOfWindows)
    appConfigXML.write('./app/config/AppConfig.xml')
    numberOfWindows = newNumberOfWindows
    return "Updated the number of windows for the clinic to %s" % (newNumberOfWindows)

@app.route('/WaitingRoom/<facilityName>/NotificationMessage', methods=['POST'])
def ShowNotificationMessage(facilityName):
    '''
    Function handles displaying a notification message from the clinic to
    show all patients in the clinic's waiting room. A string is expected to be sent
    in the args of the HTTP POST request.
    '''

    # Verify that the string was included in the POST
    if not request.args.get('Message'):
        # Did not find the message, log error
        logging.error("No message was provided when attempting to display notification.")
        return
   
    # Create a dictionary to send to the HTML Template
    templateDict = {}
    templateDict["PatientChartId"] = None # No pt to show
    templateDict["FacilityName"] = facilityName
    templateDict["GeneralFactsList"] = json.dumps(generalFactsList)
    templateDict["HealthcareFactsList"] = json.dumps(healthcareFactsList)
    templateDict["NotificationMessage"] = request.args.get('Message') 
    templateDict["WindowsQueue"] = json.dumps(windowsQueue)

    # Render the HTML temlate for the number of windows & pass in any data
    # needed for the template HTML page
    templateHTML = render_template(
            ('WaitingRoomTemplate%s.html' % (numberOfWindows)),
            templateDict=json.dumps(templateDict))

    # Next, generate a temporary HTML page 
    filename = 'tempWaitingRoomPage.html' #temp template HTML file
    ConstructWaitingRoomHTML(templateHTML, filename)
    # Open the new temp file through Firefox
    webbrowser.get('firefox').open("file://" + os.path.abspath(filename))
    
    # Respond to the server 
    logging.info("Successfully sent the message to display to the waiting room. Details: \n "
            "Facility Name: %s, Message: %s Current Queue: %s"
        % (templateDict["FacilityName"], templateDict["NotificationMessage"], templateDict["WindowsQueue"]))
    return ("Sucessfully sent the message to display to the waiting room. Message '%s' in %s." 
            % (templateDict["NotificationMessage"], facilityName))
    
@app.route('/WaitingRoom/<facilityName>/<int:patientChartId>', methods=['POST'])
def NotifyWaitingRoom(facilityName, patientChartId):
    '''
    Function handles updating the display for the waiting room application.
    Only handles HTTP POST. Function expects a facilityName and an int for
    the patient chart ID.
    '''
    # Verify that 'patientChartId' and 'facilityName' are not null
    if patientChartId is None or facilityName is None:
        # Incorrect format or bad request
        logging.error("Bad input, either patient chart id or the facility name is null. "
                "Patient chart id is %s and the clinic name is %s"
                % (patientChartId, facilityName))
        return ("Error on generating Waiting Room Screen on chart ID %s for clinic %s"
                % (patientChartId, facilityName))


    # Use global vars for accessing the config xml

    if numberOfWindows > 3 or numberOfWindows < 1:
        # Bad number of windows
        logging.error("Found a bad number of windows for this clinic. "
                "Number of windows given is %s" % (numberOfWindows))
        return ("Bad number of windows was found for this clinic. "
               "The number of windows given is %s" % (numberOfWindows))

    # Create a dictionary to send to the HTML Template
    templateDict = {}
    templateDict["PatientChartId"] = patientChartId
    templateDict["FacilityName"] = facilityName
    templateDict["GeneralFactsList"] = json.dumps(generalFactsList)
    templateDict["HealthcareFactsList"] = json.dumps(healthcareFactsList)
    
    # Check if there's a window attached to the HTTP request args
    if request.args.get('Window'):
        # Found a window to display to, update the window's queue (remove pt. if full)
        UpdateWaitingRoomQueue(request.args.get('Window'), patientChartId)
        templateDict["WindowsQueue"] = json.dumps(windowsQueue)

    # Render the HTML temlate for the number of windows & pass in any data
    # needed for the template HTML page
    templateHTML = render_template(
            ('WaitingRoomTemplate%s.html' % (numberOfWindows)),
            templateDict=json.dumps(templateDict))

    # Next, generate a temporary HTML page 
    filename = 'tempWaitingRoomPage.html' #temp template HTML file
    ConstructWaitingRoomHTML(templateHTML, filename)
    # Open the new temp file through Firefox
    webbrowser.get('firefox').open("file://" + os.path.abspath(filename))
    
    # Respond to the server 
    logging.info("Successfully add patient to the waiting room screen. Details: \n "
        "Patient Chart ID: %s, Facility Name: %s, Current Queue: %s"
        % (templateDict["PatientChartId"], templateDict["FacilityName"], templateDict["WindowsQueue"]))
    return "Sucessfully loaded patient %s in %s " % (patientChartId, facilityName)
    
