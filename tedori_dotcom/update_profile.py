import tweepy

API_KEY = "UHvEB9eE3lyWM4zPARambujIa"
API_SECRET = "VUivkTp42P0PaNoOzlglsxnfPViMFLKHQybs8I8IreFUpaSnwn"
ACCESS_TOKEN = "1924677045784838144-hrHWl35Sim0p9PW5WUUSaXYUzUW1n0"
ACCESS_SECRET = "Vs1qPPGRMtyRU9sacMBqA59ppnMrNZLe9iWDvoiTtRpf6"

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

new_name = "あなたの本当の手取り額｜税金の絶望"
new_description = "頑張って働いているのに、なぜかお金が貯まらない方へ。\n実はあなたの給与、知らぬ間に国に恐ろしい額を搾取されています。\n\n「自分の手取り・搾取額」を1円単位で計算できるシステムを作りました。\n現実を知って絶望したい方は以下のリンクからどうぞ👇（※ショック注意）"
new_url = "https://tedori-keisan.com"

try:
    api.update_profile(name=new_name, description=new_description, url=new_url)
    print("✅ Profile updated!")
except Exception as e:
    print(f"❌ Error: {e}")
