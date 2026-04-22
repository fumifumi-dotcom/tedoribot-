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
    response = client.create_tweet(text="【夜の部】毎月いくら税金が引かれているか、正確に把握していますか？手取り計算シミュレーターに待望の「月額切り替え」と「絶望のシェア機能」を追加しました💸 自分の本当の手取り水準を知りたい方はプロフのリンクへ👉")
    print(f"✅ Success: {response.data}")
except Exception as e:
    print(f"❌ Error: {e}")
