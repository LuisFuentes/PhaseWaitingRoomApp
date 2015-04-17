#!flask/bin/python
from app import app
import logging
#app.run(debug=True) #Runs locally, private

# Setup logging
logging.basicConfig(filename='waitingroomlog.log', format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)
logging.info('Starting Waiting Room Flask Webservice.')

app.run(host='0.0.0.0') #Runs externally, public

