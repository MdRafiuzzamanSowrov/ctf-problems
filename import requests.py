import requests

s = requests.Session()

while True:
    r = s.get("http://<host>/play", cookies={"session": "YOUR_SESSION_HERE"})
    if r.status_code == 401:
        print("Session expired.")
        break
    data = r.json()
    print(data)
    if "flag" in str(data).lower():
        print("🎉 FLAG FOUND:", data)
        break

