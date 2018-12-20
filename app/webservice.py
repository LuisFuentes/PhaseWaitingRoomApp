''' Imports '''
# Import the application and the facts lists
from app import app, logger, FactsList, \
        WindowsList, MessagesList, \
        NumberOfWindows, Ticker, Parser, \
        RssLink, WeatherLink, ClinicName, \
        ClinicLongitude, ClinicLatitude, \
        PatientDisplayTime, TickerDisplayTime, \
        WaitingRoomAudioPath, JQueryFilePath

# Import for handling requests & Rendering HTML Template
from flask import jsonify, request, render_template

# Allow Cross-origin resource sharing (to allow Template to do an ajax call)
from flask.ext.cors import cross_origin

# File manipulation
from os import listdir, path
from os.path import isfile, join
import shutil
import time

import webbrowser, json, datetime, random

# Import RSS feed parser
import feedparser

def handle_error(status_code, error_message):
    '''
    Function handles error message and returns the
    response.
    '''
    response = jsonify({'message': error_message})
    response.status_code = status_code
    return response

def construct_waiting_room_html(html_text, filename):
    '''
    Function shall create the file that holds
    the waiting room html using the HTML text
    '''
    logger.debug("Constructing HTML page "
        "to display to the waiting room.")
    try:
        output = open(filename, "w")
        output.write(html_text)
        output.close()
    except Exception as file_exec:
        logger.error("An error occurred when trying to "
            "create the HTML page")

def check_cpu_temperature():
    '''
    Function checks the CPU Temperature and logs any
    high temperature readings.    
    '''
    try:
        for line in open('/sys/class/thermal/thermal_zone0/temp', 'r'):
            cpu_temp = float(line)/1000
            if cpu_temp >= 85:
                logger.warning("CPU TEMPERATURE WARNING! CPU Temp: %s", cpu_temp)
    except:
        logger.error("CPU TEMPERATURE ERROR! Could not read the temperature.")

def update_waiting_room_window(window_number, patient_waiting_room_id):
    '''
    Function updates the window by adding the patient to it.
    Returns an error statement or null if there are no errors.
    '''
    global WindowsList
    logger.info("Updating window %s with patient ID %s.",
            window_number, patient_waiting_room_id)

    # Check for any patients that have expired at the window
    # Get current time & recreate the list,
    # excluding any window's with an expired pt.
    current_time = time.mktime(datetime.datetime.now().timetuple())
    temp_windows_list = WindowsList

    for i, item in enumerate(temp_windows_list):
        if not item is None:
            if current_time >= item["ExpirationTime"]:
                # Expired at window, remove pt
                logger.debug("Patient %s has expired at window %s."
                    "Removing from list.",
                    item["ID"], item["WindowNumber"])
                temp_windows_list[i] = None # Remove pt off window

    WindowsList = temp_windows_list

    # Verify that the pt isn't already on the window or another window.
    for window_item in WindowsList:
        if not window_item is None:
            if patient_waiting_room_id == window_item["ID"]:
                logger.error("Did not add patient, patient ID %s is already"
                    "in window %s. Window list: %s",
                    patient_waiting_room_id, window_number,
                    json.dumps(WindowsList))
                return ("Did not add patient, patient %s is already "
                    "in the window %s" %
                    (patient_waiting_room_id, window_number))

    # Add new patient to the window
    # Set expiry in 1 min
    expiration_time = time.mktime(
            (datetime.datetime.now()
                + datetime.timedelta(seconds=PatientDisplayTime)).timetuple())

    WindowsList[window_number-1] = {
            "ID" : patient_waiting_room_id,
            "ExpirationTime" : expiration_time,
            "WindowNumber" : window_number}
    return None # Return no errors

def get_fact():
    '''
        Function handles a GET reqest from our javascript/template waiting
        room page and returns a random fact from the facts list.
    '''
    # Get random int from the length of the facts list
    logger.info("Getting random general/healthcare fact.")

    # Check if the fact is dead (TTL has passed)
    current_time = time.mktime(datetime.datetime.now().timetuple())
    if current_time > Ticker['ExpirationTime']:
        # Get new fact
        fact = FactsList[random.randrange(0, len(FactsList))]

        logger.debug("Fact to display: %s", fact)

        # Update the Ticker, keep in memory w/ expiration of 15secs
        Ticker['Type'] = "Fact"
        Ticker['Text'] = fact
        Ticker['ExpirationTime'] = time.mktime(
            (datetime.datetime.now() +
                datetime.timedelta(seconds=TickerDisplayTime)).timetuple())

        logger.info("Sucessfully added fact %s to the ticker", fact)

def get_news():
    '''
        Function handles a GET from the js/template
        and set the ticker to a random news post.
    '''
    logger.info("Getting random new headlines from %s.", RssLink)
    
    feed = feedparser.parse(RssLink)

    # Randomly select a post from the entries
    entry = feed.entries[random.randrange(0, len(feed.entries))]
    news = entry.summary.split('<img ')[0]

    # Add the headlines into a dict for the ticker text
    # Only show text, remove all imgs
    Ticker['Type'] = "News"
    Ticker['Text'] = news
    Ticker['ExpirationTime'] = time.mktime(
            (datetime.datetime.now() +
                datetime.timedelta(seconds=TickerDisplayTime)).timetuple())

    logger.info("Sucessfully added news headline %s to the ticker", news)

def get_weather():
    '''
       Function handles a GET from the js/template
       and set the ticker to display the weather for
       this clinic's zip code
    '''
    logger.info("Getting the weather from %s for clinic %s",
            WeatherLink, ClinicName)

    # Construct the iframe link
    link = WeatherLink + ("#lat=%s&lon=%s&name=%s&color=#00aaff&"
            % (ClinicLatitude, ClinicLongitude, ClinicName))

    # Add the weather into a dict for the ticker text
    # Send the link in the text since the weather will be the website
    # using iframe
    Ticker['Type'] = "Weather"
    Ticker['Text'] = link
    Ticker['ExpirationTime'] = time.mktime(
            (datetime.datetime.now() +
                datetime.timedelta(seconds=TickerDisplayTime)).timetuple())

    logger.info("Successfully added the clinic's weather to the ticker")

def get_message():
    '''
        Function handles a GET from the js/template
        and fetches a random clinic-specific message to
        display to the clinic's waiting room.
    '''
    logger.info("Getting a message from the list %s",
            MessagesList)

    # Randomly select a message from the list
    message = MessagesList[random.randrange(0, len(MessagesList))]

    Ticker['Type'] = "Message"
    Ticker['Text'] = message
    Ticker['ExpirationTime'] = time.mktime(
            (datetime.datetime.now() +
                datetime.timedelta(seconds=TickerDisplayTime)).timetuple())
    logger.info("Sucessfully added message %s to the ticker", message)

def update_page(current_window_called=None):
    '''
        Function sends up the JSON objects and the page for the
        webbrowser to be displayed in.
        Returns an error state if an error was found
    '''

    # Create a dictionary to send to the HTML Template
    template_dict = {}
    template_dict["NumberOfWindows"] = NumberOfWindows
    template_dict["WindowsList"] = json.dumps(WindowsList)
    template_dict["Ticker"] = json.dumps(Ticker)
    template_dict["IsWindowCalled"] = False
    template_dict["WindowNumberCalled"] = None 

    waiting_room_audio = ("%s1.wav" % (WaitingRoomAudioPath)) #default

    if current_window_called:
        template_dict["IsWindowCalled"] = True    
        template_dict["WindowNumberCalled"] = ("%s%s.wav" % (WaitingRoomAudioPath, current_window_called))
		waiting_room_audio = ("%s%s.wav" % (WaitingRoomAudioPath, current_window_called))

    # Render the HTML temlate for the number of windows & pass in any data
    # needed for the template HTML page
    template_html = render_template(
            'WaitingRoomTemplate.html',
            templateDict=json.dumps(template_dict),
            JQueryFilePath=JQueryFilePath,
            WaitingRoomAudioPath=waiting_room_audio)

    # Next, generate a temporary HTML page
    filename = 'tempWaitingRoomPage.html' #temp template HTML file
    construct_waiting_room_html(template_html, filename)
    # Open the new temp file through Firefox
    try:
        # Try to open
        logger.debug("Attempting to open Waiting Room display inside web browser")
        webbrowser.get('firefox').open("file://" + path.abspath(filename))
    except Exception as webbrowser_exception:
        logger.error("Caught an exception %s", webbrowser_exception)
        return 'Failed to display waiting room display'

    return None

@app.route('/')
@app.route('/index')
def index():
    ''' Default page '''
    logger.debug("Hit the default page!")
    return ("Hello, World! This is a confirmation page to show "
        "that the default Waiting Room URL can be reached.")

@app.route('/ShowWaitingRoomPage', methods=['GET'])
def show_waiting_room_page():
    '''
        Show the waiting room page inside the
        web browser
    '''
    logger.debug("Showing the waiting room display.")
    error_state = update_page()
    if error_state:
        return handle_error(500, error_state)

    return 'Displaying the waiting room'

@app.route('/ShowIntroPage', methods=['GET'])
def show_intro_page():
    '''
        Show the introduction page that describes
        the waiting room display before the release
        of the display
    '''
    try:
        # Try to open
        logger.debug("Attempting to open the Intro Waiting Room display inside web browser")
        webbrowser.get('firefox').open("file://" + path.abspath('app/templates/IntroWaitingRoomTemplate.html'))
    except Exception as webbrowser_exception:
        logger.error("Caught an exception %s", webbrowser_exception)
        return handle_error(500, 'Failed to display the Intro waiting room display')

    logger.info("Sucessfully showing the Intro to the Waiting Room.")
    return 'Displaying the waiting room page'

@app.route('/ArchiveLogs', methods=['POST'])
def archive_logs():
    '''
        Function archives the log files currently
        in the logs/current folder into the logs/archived
        folder. The flask app will continue
    '''
    logger.info("Attempting to move the current log files "
            "to the archived folder.")

    # Get all files in the log current folder
    path_to_current_logs = "/home/odroid/WaitingRoomLogs/current/"
    log_files = [cur_file for cur_file in listdir(path_to_current_logs)
            if isfile(join(path_to_current_logs, cur_file))]

    # For each file, move it to the archived folder
    for log_file in log_files:

        old_file_name = path_to_current_logs + log_file
        logger.info("Log file path: %s", old_file_name)

        # Set name of new log file in archive
        new_file_name = "/home/odroid/WaitingRoomLogs/archived/" \
                + datetime.datetime.now().strftime("%Y_%b_%d_%H_%M_%S") \
                + "_" + log_file

        logger.info("New log file path: %s", new_file_name)

        shutil.move(old_file_name, new_file_name)
        logger.info("Moved file '%s' from ~/current to "
            "~/archived", log_file)

    return "Successfully moved the current logs into the archived folder"

@app.route('/WaitingRoom/GetTicker/<ticker_type>', methods=['GET'])
@cross_origin()
def get_ticker(ticker_type):
    '''
        Function GETs the next ticker item to show based on the type
    '''

    if ticker_type == "Fact":
        get_fact()
    elif ticker_type == "News":
        get_news()
    elif ticker_type == "Message":
        get_message()
    else:
        get_weather()
    
    check_cpu_temperature()
    
    return json.dumps(Ticker)

@app.route('/WaitingRoom/UpdateFacts', methods=['POST'])
def update_facts_list():
    '''
        Function updates the fact list from the passed in param.
        When updated, when the waiting room page gets a fact, the list
        will already be updated (don't need to post back to the page since
        the page will do a ajax call to this web service)
    '''
    global FactsList
    # Verify that the facts list was included in the POST
    if not request.args.get('FactsList'):
        # Did not find the messages, log error
        logger.error("No facts list was provided when attempting "
            "to update the facts to show for this clinic.")
        return handle_error( 500, 'No Facts List was provided in the HTTP request')

    # Now, get the list and split by the string delimiter ('||')
    facts_list = request.args.get('FactsList').split('||')

    # Write the contents of the list to the file
    with open(Parser.get("ApplicationSettings", "FactsFilePath"), "w") as facts_file:
        facts_file.truncate() # erase file contents
        last_fact_str = facts_list[-1].encode('UTF-8') #convert it to ascii
        for fact in facts_list:
            fact_str = fact.encode('UTF-8')
            facts_file.write(fact_str)
            # If not the last item on list, add a new line
            if not fact_str == last_fact_str:
                facts_file.write('\n')
    FactsList = facts_list

    logger.info("Successfully updated the clinic's Facts list.")
    return "Successfully updated the clinic's facts."

@app.route('/WaitingRoom/UpdateMessages', methods=['POST'])
def update_messages_list():
    '''
        Function updates the message list from the passed in parameter
        argument. This list of messages will be the clinic-specific
        messages that are shown at an interval.
    '''
    global MessagesList

    # Verify that the message was included in the POST
    if not request.args.get('Messages'):
        # Did not find the messages, log error
        logger.error("No message list was provided when attempting "
            "to update the messages to show for this clinic..")
        return handle_error( 500, 'No Message list was provided in the HTTP request')

    # Now, get the list and split by the string delimiter ('||')
    messages_list = request.args.get('Messages').split('||')

    # Write the contents of the list to the file
    with open(Parser.get(
        "ApplicationSettings", "MessagesFilePath"), "w") as messages_file:
        messages_file.truncate() # erase file contents
        for message in messages_list:
            messages_file.write(message)
            # If not the last item on list, add a new line
            if not message == messages_list[-1]:
                messages_file.write('\n')

    MessagesList = messages_list

    logger.info("Successfully updated the clinic's messages list: %s"
            , MessagesList)
    return "Successfully update the clinic's messages."

@app.route('/WaitingRoom/DisplayOneTimeMessage', methods=['POST'])
def display_one_time_message():
    '''
    Function handles displaying a notification message from the clinic to
    show all patients in the clinic's waiting room.
    A message and duration time is expected to be sent in the args
    of the HTTP POST request for the message to be shown.
    '''
    logger.info("One time message will be shown to clinic.")
    # Verify that the message & time was included in the POST
    if not request.args.get('Message'):
        # Did not find the message, log error
        logger.error("No message was provided when attempting "
            "to display notification.")
        return handle_error( 500, 'No message was provided in the HTTP request')

    if not request.args.get('ExpirationTime'):
        # Did not find the duration of the message, log error
        logger.error("No duration time for the message was provided "
            "when attempting to display notification.")
        return handle_error(500, "No expiration time was provided in the HTTP request")

    # Set the new Ticker item to only display the One-time message
    # for the given expiration time
    Ticker['Type'] = "OnetimeMessage"
    Ticker['Text'] = request.args.get('Message')
    Ticker['ExpirationTime'] = request.args.get('ExpirationTime')
    update_page() # Update the page with the template items

    # Respond to the server
    logger.info("Successfully sent the message to display to the "
            "waiting room. Message: %s",
            request.args.get('Message'))

    return ("Sucessfully added the one-time message to display "
            "to the waiting room. Message: %s" %
            (request.args.get('Message')))

@app.route('/WaitingRoom/StopDisplayingOneTimeMessage', methods=['POST'])
def end_display_one_time_message():
    '''
    Function stops displaying the one time message to the waiting room.
    '''
    one_time_message = Ticker['Text']
    logger.info("Stopping the display of the one time message %s.",
            one_time_message)

    # Clear the contents of the ticker
    Ticker['Type'] = ""
    Ticker['Text'] = ""
    Ticker['ExpirationTime'] = ""
    # Update the html page with the new empty ticker
    update_page()

    logger.info("Successfully ended the one time message %s.",
            one_time_message)

    return ("Sucessfully stopped displaying the message (%s) to display "
        "to the waiting room." % one_time_message)

@app.route('/WaitingRoom/UpdateConfig', methods=['POST'])
def update_config():
    '''
        Function handles updating the config file with
        the number of windows, patient and ticker display
        timers.
    '''
    global NumberOfWindows, PatientDisplayTime, TickerDisplayTime, \
            ClinicLongitude, ClinicLatitude, ClinicName

    logger.info("Attempting to update the configuration file.")
    # Verify that the number of windows, and patient/ticker display time
    if not request.args.get('NumberOfWindows'):
        # Did not find the message, log error
        logger.error("No Number of windows was provided when attempting "
            "to update the config file.")
        return handle_error(500, 'Number of Windows was not provided in the HTTP request')

    if not request.args.get('PatientDisplayTime'):
        # Did not find the patient display time, log error
        logger.error("No patient display time was provided when attempting "
            "to update the config file.")
        return handle_error(500, 'Patient Display time was not provided in the HTTP request')

    if not request.args.get('TickerDisplayTime'):
        # Did not find the ticker display time, log error
        logger.error("No ticker display time was provided when attempting "
            "to update the config file..")
        return handle_error(500, 'Ticker Display Time was not provided in the HTTP request')

    if not request.args.get('ClinicName'):
        # Did not find the clinic name, log error
        logger.error("No Clinic Name was provided when attempting "
            "to update the config file..")
        return handle_error(500, 'Clinic name was not provided in the HTTP request')
    
    if not request.args.get('ClinicLongitude'):
        # Did not find the clinic name, log error
        logger.error("No Clinic Longitude was provided when attempting "
            "to update the config file..")
        return handle_error(500, 'Clinic Longitude was not provided in the HTTP request')

    if not request.args.get('ClinicLatitude'):
        # Did not find the clinic name, log error
        logger.error("No Clinic Latitude was provided when attempting "
            "to update the config file..")
        return handle_error(500, 'Clinic Latitude was not provided in the HTTP request')

    number_of_windows = request.args.get('NumberOfWindows')
    patient_display_time = request.args.get('PatientDisplayTime')
    ticker_display_time = request.args.get('TickerDisplayTime')
    clinic_name = request.args.get('ClinicName')
    clinic_long = request.args.get('ClinicLongitude')
    clinic_lat = request.args.get('ClinicLatitude')

    # Update all the config items in the config INI file
    Parser.set("ApplicationSettings",
            "NumberOfWindows", number_of_windows)
    Parser.set("ApplicationSettings",
            "PatientDisplayTime", patient_display_time)
    Parser.set("ApplicationSettings",
            "TickerDisplayTime", ticker_display_time)
    Parser.set("ApplicationSettings",
            "ClinicName", clinic_name)
    Parser.set("ApplicationSettings",
            "ClinicLongitude", clinic_long)
    Parser.set("ApplicationSettings",
            "ClinicLatitude", clinic_lat)

    with open(r"config.ini", "wb") as config_file:
        Parser.write(config_file)

    # Update all the variables (in-memory)
    NumberOfWindows = int(number_of_windows)
    PatientDisplayTime = int(patient_display_time)
    TickerDisplayTime = int(ticker_display_time)
    ClinicName = clinic_name
    ClinicLongitude = clinic_long
    ClinicLatitude = clinic_lat

    logger.info("Successfully updated the config file")
    return "Successfully updated the config file"

@app.route('/WaitingRoom/<int:window_number>/<patient_waiting_room_id>',
        methods=['POST'])
def notify_waiting_room(window_number, patient_waiting_room_id):
    '''
    Function handles updating the display for the waiting room application.
    Only handles HTTP POST. Function expects a window to add the patient to
    and an int for the patient chart ID.
    '''
    # Make sure the number of windows is within range
    if NumberOfWindows > 3 or NumberOfWindows < 1:
        # Exceeded the number of windows
        logger.error("Cannot update, the number of "
            "dispensary windows is too large or small. "
            "The number of windows given is %s", NumberOfWindows)
        return handle_error(500, 'Incorrect Number of Windows')

    # Add patient to the window
    error_state = update_waiting_room_window(window_number,
            patient_waiting_room_id)

# There was an error updating waiting room
    if error_state:
        return handle_error(500, error_state)
 
    # Update the page with the JSON template items
    update_page(window_number)

    check_cpu_temperature()    

    # Log it
    logger.info("Successfully added the Patient ID %s "
        "to Window Number %s.",
        patient_waiting_room_id, window_number)
    return ("Sucessfully added the patient to the waiting "
        "room page. %s to window %s."
        % (patient_waiting_room_id, window_number))

