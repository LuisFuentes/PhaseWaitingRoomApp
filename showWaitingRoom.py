'''
    Show the HTML page with the waiting
    room app loaded in.
'''
f = open('ShowWaitingRoomlog.log', 'w')
f.write("Displaying default waiting room display...")

try:
    import requests
    r= requests.post("http://localhost:5000/ShowWaitingRoomPage")
    f.write("Status: " + str(r.status_code) \
            + " | " + str(r.reason) + " | " + str(r.text))
except Exception as e:
    f.write("Exception found: " + str(e))

f.close()
