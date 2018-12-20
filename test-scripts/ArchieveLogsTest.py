import requests

r = requests.post("http://localhost:5000/ArchiveLogs")

print(r.status_code, r.reason, r.text)
