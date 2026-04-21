import os
import tweepy
import sys

API_KEY = "UHvEB9eE3lyWM4zPARambujIa"
API_SECRET = "VUivkTp42P0PaNoOzlglsxnfPViMFLKHQybs8I8IreFUpaSnwn"
ACCESS_TOKEN = "1924677045784838144-hrHWl35Sim0p9PW5WUUSaXYUzUW1n0"
ACCESS_SECRET = "Vs1qPPGRMtyRU9sacMBqA59ppnMrNZLe9iWDvoiTtRpf6"

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

banner_path = "/Users/imamichifumitaka/Downloads/ミカタ_経理/今道_生活を豊かに/money-tools/images/x_header_clean.png"

try:
    print(f"Uploading {banner_path}...")
    api.update_profile_banner(filename=banner_path)
    print("✅ Successfully updated X (Twitter) profile banner!")
except Exception as e:
    print(f"❌ Failed to update banner: {e}")
    sys.exit(1)
