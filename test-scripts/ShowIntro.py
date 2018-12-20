#import urllib2
#content = urllib2.urlopen("http://localhost:5000").read()
#print content

# Let's send POST dummy data to our Waiting room app
import requests, sys

r = requests.get("http://localhost:5000/ShowIntroPage")

print(r.status_code, r.reason, r.text)
