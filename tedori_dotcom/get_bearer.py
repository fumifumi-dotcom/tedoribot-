import requests
import json
import base64

API_KEY = "UHvEB9eE3lyWM4zPARambujIa"
API_SECRET = "VUivkTp42P0PaNoOzlglsxnfPViMFLKHQybs8I8IreFUpaSnwn"

auth_str = f"{API_KEY}:{API_SECRET}"
b64_auth = base64.b64encode(auth_str.encode()).decode()

resp = requests.post(
    "https://api.twitter.com/oauth2/token",
    headers={"Authorization": f"Basic {b64_auth}", "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
    data="grant_type=client_credentials"
)
print(resp.json())
