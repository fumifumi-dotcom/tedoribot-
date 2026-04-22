import tweepy

API_KEY = "UHvEB9eE3lyWM4zPARambujIa"
API_SECRET = "VUivkTp42P0PaNoOzlglsxnfPViMFLKHQybs8I8IreFUpaSnwn"
ACCESS_TOKEN = "1924677045784838144-hrHWl35Sim0p9PW5WUUSaXYUzUW1n0"
ACCESS_SECRET = "Vs1qPPGRMtyRU9sacMBqA59ppnMrNZLe9iWDvoiTtRpf6"

client = tweepy.Client(
    consumer_key=API_KEY, consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET
)

text = """経理やってて本当に思うけど、年収550万の人が国に年124万円も持っていかれてるのに「ふるさと納税」やってないのマジで勿体ない。

実質2,000円で高級肉もカニももらえるのに…🥺
https://tedori-keisan.com/furusato.html

#ふるさと納税 #手取り計算"""

try:
    response = client.create_tweet(text=text)
    print(f"✅ 投稿成功! Tweet ID: {response.data['id']}")
except Exception as e:
    print(f"❌ Error: {e}")
