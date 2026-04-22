import os
import requests
import json
from datetime import datetime, timedelta

API_TOKEN = os.environ.get("CF_API_TOKEN", "")
ACCOUNT_ID = "90d5062a2063f8319a48d6f48908abe6"

url = "https://api.cloudflare.com/client/v4/graphql"
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# 過去7日間の日付
start_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%dT00:00:00Z")

query = """
query {
  viewer {
    accounts(filter: {accountTag: "%s"}) {
      rumPageloadEventsAdaptiveGroups(
        limit: 20,
        filter: {datetime_geq: "%s"}
        orderBy: [count_DESC]
      ) {
        count
        dimensions {
          requestPath
        }
      }
    }
  }
}
""" % (ACCOUNT_ID, start_date)

response = requests.post(url, headers=headers, json={"query": query})
print(json.dumps(response.json(), indent=2))
