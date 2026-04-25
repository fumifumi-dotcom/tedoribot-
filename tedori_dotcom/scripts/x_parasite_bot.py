import os
import sys
import time
import random
import urllib.parse
from playwright.sync_api import sync_playwright

USER_DATA_DIR = os.path.expanduser("~/money-tools/tedori_dotcom/scripts/x_bot_profile")
SEARCH_QUERY = urllib.parse.quote("手取り 少ない OR 給料 絶望 OR 手取り 絶望")

# 寄生URL（診断ページへ直接飛ばす）
PARASITE_URL = "https://tedori-keisan.com/diagnosis.html"

REPLY_TEXTS = [
    f"今のうちに、自分が将来どれくらいお金が足りなくなるか「生涯手取りの欠損額」を計算しておいた方がいいですよ… \n{PARASITE_URL}",
    f"手取りが少ないと本当に将来詰みます。老後破産の確率と「適正年収」を無料で計算できるので試してみてください↓\n{PARASITE_URL}",
    f"自分の社畜偏差値を計算したら絶望しました😇 同年代と比べてどれくらいヤバいか、ここで計算できます\n{PARASITE_URL}"
]

def is_logged_in(page):
    try:
        # ログイン画面固有の要素や、未ログイン時のサインアップポップアップを探す
        page.wait_for_selector("a[data-testid='loginButton'], div[data-testid='SideNav_AccountSwitcher_Button']", timeout=5000)
        return page.locator("div[data-testid='SideNav_AccountSwitcher_Button']").count() > 0
    except:
        return False

def run():
    print("🚀 Starting X Parasite Bot...")
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False, # 凍結リスク低減と初回ログインのため
            viewport={"width": 1280, "height": 720}
        )
        page = browser.new_page()
        
        page.goto("https://twitter.com/home")
        time.sleep(4)
        
        if not is_logged_in(page):
            print("⚠️ [未ログイン] X (Twitter) にログインしていません。")
            if sys.stdin.isatty():
                print("手動でログインを完了させてください。完了したらターミナルで Enter を押してください。")
                input("Press Enter after login...")
            else:
                print("自動実行モードのため、ログインが必要です。初回のみターミナルから手動で起動してください。")
                browser.close()
                return

        print("✅ ログイン確認完了")
        print(f"🔍 検索中: 手取り 絶望 / 少ない...")
        
        # 検索ページ（最新タブ）へ
        page.goto(f"https://twitter.com/search?q={SEARCH_QUERY}&src=typed_query&f=live")
        time.sleep(5)
        
        tweets = page.locator("article[data-testid='tweet']")
        tweet_count = tweets.count()
        print(f"📝 発見したターゲットポスト数: {tweet_count}")
        
        max_replies = 3 # 凍結防止のため1回3件まで
        replied = 0
        
        for i in range(min(tweet_count, 15)):
            if replied >= max_replies:
                break
                
            tweet = tweets.nth(i)
            try:
                tweet.scroll_into_view_if_needed()
                time.sleep(1)
                
                # 返信ボタンをクリック
                reply_btn = tweet.locator("button[data-testid='reply']")
                if reply_btn.count() == 0:
                    continue
                
                reply_btn.first.click()
                time.sleep(2)
                
                # 返信テキストエリアを探して入力
                textbox = page.locator("div[data-testid='tweetTextarea_0']")
                if textbox.count() == 0:
                    # エラーでポップアップが出ない場合
                    continue
                    
                reply_text = random.choice(REPLY_TEXTS)
                textbox.fill(reply_text)
                time.sleep(random.uniform(1.5, 3.5))
                
                # 送信（リプライ）
                send_btn = page.locator("button[data-testid='tweetButton']")
                send_btn.click()
                print(f"🎯 寄生完了（リプライ送信）: {reply_text[:15]}...")
                replied += 1
                
                # 連続投稿によるスパム判定を避けるため待機
                wait_time = random.uniform(8, 15)
                print(f"⏳ {int(wait_time)}秒待機中...")
                time.sleep(wait_time)
                
            except Exception as e:
                print(f"⚠️ スキップ: {e}")
                # ポップアップが開いていたら閉じる
                try:
                    page.keyboard.press("Escape")
                except:
                    pass

        print("🏁 全ターゲットへの寄生が完了しました。終了します。")
        browser.close()

if __name__ == "__main__":
    run()
