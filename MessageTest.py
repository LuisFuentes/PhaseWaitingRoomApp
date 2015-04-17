# Let's send POST dummy data to our Waiting room app
import requests

facilityName = 'Chatsworth'

#appParams = {'Message': 'Hello, World!'}
appParams = {'Message': 'Hello, the dispensary is currently having some issues pumping out Methadone. The issue should be fixed in the next 10 minutes. Thank you for your patience.'}

r = requests.post("http://localhost:5000/WaitingRoom/" + facilityName + "/NotificationMessage", params=appParams)

print(r.status_code, r.reason)
