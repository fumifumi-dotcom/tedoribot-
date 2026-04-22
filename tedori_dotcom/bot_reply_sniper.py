#!/usr/bin/env python3
import time
import random
import tweepy
import os

# 認証情報の読み込み
from auto_x_poster import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET

# 検索用にBearer Tokenが必要
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAC0S8QEAAAAAhad%2B7SrSIQC4JI5YdguDnOExFeo%3DqORLHE8Pt6MydU3m1HIAQ69t4dSiiI0eCrX9z9bAdZbi00qlLt"

# リプライテンプレート群
REPLY_TEMPLATES = [
    "突然すみません🙏 同じように悩む方が多いのですが、実は「年収〇〇万円だから...」と諦める前に、国にいくら持っていかれているか正確な数字を知るのが第一歩です😭 \n\nもし良ければこちらのシミュレーターで現状の「本当の天引き額」を調べてみてください！\nhttps://tedori-keisan.com/",
    "タイムラインから失礼します🙇‍♂️ 税金、本当に高いですよね…。\nただ「なんとなく引かれている」状態が一番損をしてしまいます。\n今の年収でどのくらい搾取されているのか、1秒でわかるツールを作ったのでぜひ現実確認に使ってみてください💸\nhttps://tedori-keisan.com/",
    "通りすがりです！給料の引かれすぎ、エグいですよね😰\n手取りを増やすには、まず「自分が年間いくら国に取られているか（そしていくら取り返せるか）」を知るのがめちゃくちゃ大事です。\n良ければこちらのツールで診断してみてください🙏\nhttps://tedori-keisan.com/"
]

def sniper_reply():
    print("--- [Auto Reply Sniper] Started ---")
    client = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY, 
        consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN, 
        access_token_secret=ACCESS_SECRET
    )

    # 見込み客のペルソナが呟きそうなキーワード
    query = "(手取り 少ない OR 税金 高すぎ OR 給料 少ない OR 手取り 引かれすぎ) -is:retweet -is:reply lang:ja"
    
    try:
        # 直近のツイートを10件取得（API制限を考慮し少なめに）
        response = client.search_recent_tweets(query=query, max_results=10)
    except Exception as e:
        print(f"❌ Search Error: {e}")
        return

    if not response or not response.data:
        print("⚠️ No target tweets found.")
        return

    # スパム判定されないように、1回の実行ではランダムに抽出した「最大2件」にのみリプライする
    targets = random.sample(response.data, min(2, len(response.data)))
    
    success_count = 0
    for tweet in targets:
        reply_text = random.choice(REPLY_TEMPLATES)
        print(f"🎯 Target Acquired: @{tweet.id} / Text: {tweet.text[:20]}...")
        
        # 安全のためのランダムスリープ (5秒〜15秒)
        time.sleep(random.uniform(5, 15))
        
        try:
            client.create_tweet(text=reply_text, in_reply_to_tweet_id=tweet.id)
            print(f"✅ Snipe Successful! Replied to {tweet.id}")
            success_count += 1
        except Exception as e:
            print(f"❌ Snipe Failed for {tweet.id}: {e}")

    print(f"--- [Auto Reply Sniper] Finished. Total snipes: {success_count} ---")

if __name__ == "__main__":
    sniper_reply()
