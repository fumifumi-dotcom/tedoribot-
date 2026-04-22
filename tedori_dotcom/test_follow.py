import os
import tweepy

API_KEY = "UHvEB9eE3lyWM4zPARambujIa"
API_SECRET = "VUivkTp42P0PaNoOzlglsxnfPViMFLKHQybs8I8IreFUpaSnwn"
ACCESS_TOKEN = "1924677045784838144-hrHWl35Sim0p9PW5WUUSaXYUzUW1n0"
ACCESS_SECRET = "Vs1qPPGRMtyRU9sacMBqA59ppnMrNZLe9iWDvoiTtRpf6"

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

try:
    # Try following a benign active account, e.g. Elon Musk or just NASA
    api.create_friendship(screen_name="NASA")
    print("✅ Successfully followed via V1.1 API!")
except Exception as e:
    print(f"❌ Error following via V1.1: {e}")
