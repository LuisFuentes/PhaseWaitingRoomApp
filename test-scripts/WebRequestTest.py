#import urllib2
#content = urllib2.urlopen("http://localhost:5000").read()
#print content

# Let's send POST dummy data to our Waiting room app
import requests, sys

# Get from command line args

patientChartId = sys.argv[1]
windowNumber = sys.argv[2]

r = requests.post("http://localhost:5000/WaitingRoom/" + windowNumber + "/" + patientChartId)

print(r.status_code, r.reason, r.text)
