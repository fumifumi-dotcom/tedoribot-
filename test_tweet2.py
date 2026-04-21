import os
import tweepy

API_KEY = "UHvEB9eE3lyWM4zPARambujIa"
API_SECRET = "VUivkTp42P0PaNoOzlglsxnfPViMFLKHQybs8I8IreFUpaSnwn"
ACCESS_TOKEN = "1924677045784838144-hrHWl35Sim0p9PW5WUUSaXYUzUW1n0"
ACCESS_SECRET = "Vs1qPPGRMtyRU9sacMBqA59ppnMrNZLe9iWDvoiTtRpf6"

client = tweepy.Client(
    consumer_key=API_KEY, consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET
)

try:
    response = client.create_tweet(text="【悲報】年収500万円の真実\n\n日本の「累進課税」の威力を見逃していませんか？\n\n・額面：500万円\n・手取り：359万円（手取り率71.8%）\n・税＋保険料：141万円\n\n頑張って年収を上げても手取りが増えない理由がこれです💸\n\n#手取り計算 #年収 #お金の勉強")
    print(f"✅ Success: {response.data}")
except Exception as e:
    print(f"❌ Error: {e}")
