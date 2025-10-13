import requests

headers = {
    "Authorization" : "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEyLCJleHAiOjE3NjAzMDE1ODF9.1joxHdhk66dhcLjE2zJrKJ5SBEY-GA8ljGPyzI5W2sA"
}

requisicao = requests.get("http://127.0.0.1:8000/auth#/refresh", headers=headers)
print(requisicao)
print(requisicao.json())