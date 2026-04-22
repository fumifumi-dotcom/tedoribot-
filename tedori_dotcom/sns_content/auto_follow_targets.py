import tweepy
import random
import os
from datetime import datetime

# ==========================================
# X API Credentials
# ==========================================
API_KEY = "UHvEB9eE3lyWM4zPARambujIa"
API_SECRET = "VUivkTp42P0PaNoOzlglsxnfPViMFLKHQybs8I8IreFUpaSnwn"
ACCESS_TOKEN = "1924677045784838144-hrHWl35Sim0p9PW5WUUSaXYUzUW1n0"
ACCESS_SECRET = "Vs1qPPGRMtyRU9sacMBqA59ppnMrNZLe9iWDvoiTtRpf6"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAC0S8QEAAAAAhad%2B7SrSIQC4JI5YdguDnOExFeo%3DqORLHE8Pt6MydU3m1HIAQ69t4dSiiI0eCrX9z9bAdZbi00qlLt"

STATE_FILE = "followed_users.txt"
LOG_FILE = "bot.log"

def log_msg(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [FOLLOW] {msg}"
    print(formatted)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

def load_followed_history():
    if not os.path.exists(STATE_FILE):
        return set()
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def save_followed_history(user_id):
    with open(STATE_FILE, "a", encoding="utf-8") as f:
        f.write(f"{user_id}\n")

def main():
    try:
        # V2 Client using Bearer token for search, and User Context for following
        client = tweepy.Client(
            bearer_token=BEARER_TOKEN,
            consumer_key=API_KEY, 
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN, 
            access_token_secret=ACCESS_SECRET
        )
        
        # ターゲットとなるキーワード（リツイートやリプライは除外）
        query = "(手取り OR 税金高い OR 住民税高い OR 天引き) -is:retweet -is:reply"
        
        log_msg("Searching for targets...")
        response = client.search_recent_tweets(query=query, max_results=10, expansions=["author_id"])
        
        if not response.data:
            log_msg("No relevant tweets found right now.")
            return

        followed_history = load_followed_history()
        candidates = []
        
        for tweet in response.data:
            if tweet.author_id:
                author_id = str(tweet.author_id)
                if author_id not in followed_history:
                    candidates.append(author_id)
                
        if not candidates:
            log_msg("All found users have already been followed recently.")
            return
            
        # 安全のため、1回の実行（1日3回）でフォローするのは1名のみ
        target_id = random.choice(candidates)
        
        # フォロー実行
        res = client.follow_user(target_user_id=target_id)
        if res.data and res.data.get('following') or res.data.get('pending_follow'):
            log_msg(f"✅ Successfully followed user ID: {target_id}")
            save_followed_history(target_id)
        else:
            log_msg(f"⚠️ Failed to follow user ID: {target_id}")
            
    except Exception as e:
        log_msg(f"❌ Error during auto-follow: {e}")

if __name__ == "__main__":
    main()
