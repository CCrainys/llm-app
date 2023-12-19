import requests

response = requests.get("http://127.0.0.1:8080", params={"prompt": "What is programming language PUNQ?"})
if response.status_code == 200:
    print(response.text)
else:
    print("error")
