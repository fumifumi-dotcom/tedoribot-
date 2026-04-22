import tweepy

API_KEY = "UHvEB9eE3lyWM4zPARambujIa"
API_SECRET = "VUivkTp42P0PaNoOzlglsxnfPViMFLKHQybs8I8IreFUpaSnwn"
ACCESS_TOKEN = "1924677045784838144-hrHWl35Sim0p9PW5WUUSaXYUzUW1n0"
ACCESS_SECRET = "Vs1qPPGRMtyRU9sacMBqA59ppnMrNZLe9iWDvoiTtRpf6"

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)
img_path = "/Users/imamichifumitaka/.gemini/antigravity/brain/bb8ef9f1-8f2f-421d-ba7d-7970f670d546/salaryman_avatar_1776662408829.png"

try:
    api.update_profile_image(filename=img_path)
    print("✅ Real Avatar updated successfully!")
except Exception as e:
    print(f"❌ Error updating avatar: {e}")
