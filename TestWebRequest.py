#import urllib2
#content = urllib2.urlopen("http://localhost:5000").read()
#print content

# Let's send POST dummy data to our Waiting room app
import requests

patientChartId = str(5001);
r = requests.post("http://localhost:5000/WaitingRoom/" + patientChartId)
print(r.status_code, r.reason)
