import requests


def get_answer(prompt):
    response = requests.get("http://127.0.0.1:8080", params={"prompt": prompt})
    if response.status_code == 200:
        return response.text
    else:
        print(f"Request failed with status code {response.status_code}")


answer = get_answer("What is Task Decomposition?")
print(answer)
