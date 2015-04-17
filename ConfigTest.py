#import urllib2
#content = urllib2.urlopen("http://localhost:5000").read()
#print content

# Let's send POST dummy data to our Waiting room app
import requests

numberOfWindows = 2
r = requests.post("http://localhost:5000/Update/Windows/%s" % (numberOfWindows))

print(r.status_code, r.reason)
