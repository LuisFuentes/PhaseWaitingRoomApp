#!flask/bin/python
from app import app

#app.run(debug=True) #Runs locally, private
app.run(host='0.0.0.0', port=5000) #Runs externally, public
