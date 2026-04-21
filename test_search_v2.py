import requests

bearer = "AAAAAAAAAAAAAAAAAAAAAC0S8QEAAAAAhad%2B7SrSIQC4JI5YdguDnOExFeo%3DqORLHE8Pt6MydU3m1HIAQ69t4dSiiI0eCrX9z9bAdZbi00qlLt"
headers = {"Authorization": f"Bearer {bearer}"}
resp = requests.get("https://api.twitter.com/2/tweets/search/recent?query=税金高い&max_results=10", headers=headers)
print(resp.json())
