import requests
from concurrent.futures import ThreadPoolExecutor


def get_answer(prompt):
    response = requests.get("http://127.0.0.1:8080", params={"prompt": prompt})
    if response.status_code == 200:
        return response.text
    else:
        print(f"Request failed with status code {response.status_code}")


prompts = ["What is Task Decomposition?", "What is AI?", "What is Python?", "What is C++?", "What is USTC?"]

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {executor.submit(get_answer, prompt): prompt for prompt in prompts}
    for future in futures:
        result = future.result()
        answer = result[:-10]
        time = result[-10:]
        print(f"Answer for '{futures[future]}': {answer}, Inference time: {time}s")
