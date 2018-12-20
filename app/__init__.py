'''
    Module initializes the Flask application.
    The following variables are utlizied in the
    websevice module, these are imported and kept
    in memory for the duration of the application's
    lifecycle (or until the Flask app is restarted/stopped)
'''
from flask import Flask
from ConfigParser import SafeConfigParser

import logging
import logging.handlers

import webbrowser

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Set the log files to be created under current
# Max size of each log file is 100mb, 5 different log files
handler = logging.handlers.RotatingFileHandler(
    '/home/odroid/WaitingRoomLogs/current/waitingroomlog.log',
    maxBytes=5*1024*1024, backupCount=5)
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

logger.info('Starting Waiting Room Flask Webservice.')

# The following variables are constants (outside a func) and will
# be used in the webservice module

# Read from the app's config file
logger.info('Loading in the configurations...')
Parser = SafeConfigParser()
Parser.read('/home/odroid/WaitingRoomApp/WaitingRoomApp/config.ini')

logger.info('Reading in the configurations...')
try:
    # Store in memory the following
    NumberOfWindows = int(Parser.get("ApplicationSettings", "NumberOfWindows"))
    RssLink = str(Parser.get("ApplicationSettings", "Rss"))
    WeatherLink = str(Parser.get("ApplicationSettings", "Weather"))
    ClinicLongitude = str(Parser.get("ApplicationSettings", "ClinicLongitude"))
    ClinicLatitude = str(Parser.get("ApplicationSettings", "ClinicLatitude"))
    ClinicName = str(Parser.get("ApplicationSettings", "ClinicName"))
    PatientDisplayTime = int(Parser.get
            ("ApplicationSettings", "PatientDisplayTime"))
    TickerDisplayTime = int(Parser.get
            ("ApplicationSettings", "TickerDisplayTime"))
    WaitingRoomAudioPath = str(Parser.get("ApplicationSettings", "WaitingRoomAudioPath"))
    JQueryFilePath = str(Parser.get("ApplicationSettings", "JQueryPath"))
except Exception as e:
    logger.info("Caught an exception while loading config file %s", e)

# Get all facts from Facts file & store the facts in memory
FactsList = []
with open(Parser.get("ApplicationSettings", "FactsFilePath")) as file:
    FactsList = file.readlines()

# Set the limit of the windows list
WindowsList = [None]*NumberOfWindows

# Get all messages from Messages file & store the messages in memory
MessagesList = []
with open(Parser.get("ApplicationSettings", "MessagesFilePath")) as file:
    MessagesList = file.readlines()

# Store the last ticker item in memory
Ticker = {'Text' : '', 'Type' : '', 'ExpirationTime' : 0}

logger.info('Loaded all configurations for Waiting Room Flask Webservice.')

app = Flask(__name__)

# Gunicorn for Upstart auto bootup
from werkzeug.contrib.fixers import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app)

from app import webservice
