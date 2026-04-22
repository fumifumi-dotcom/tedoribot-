#!/usr/bin/env python3
import urllib.request
import xml.etree.ElementTree as ET
import sys
import os

# Import our existing poster logic
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from auto_x_poster import generate_dynamic_tweet, generate_tax_video, post_tweet

def get_current_trend():
    """Yahoo!ニューストピックス(主要)から現在最も注目されているホットワードを抽出"""
    try:
        url = "https://news.yahoo.co.jp/rss/topics/top-picks.xml"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        # 最初のItem（一番話題のニュース）のタイトルを取得
        first_item = root.find('.//item')
        if first_item is not None:
            title = first_item.find('title').text
            # タイトルをそのままハッシュタグ風にするのは長いので、話題として引用
            return title
    except Exception as e:
        print(f"Error fetching trends: {e}")
    return None

def main():
    print("--- [Trend Jacker Engine] Started ---")
    trend_title = get_current_trend()
    
    main_text, reply_text, data, template_id = generate_dynamic_tweet()
    
    if trend_title:
        print(f"🔥 Successfully fetched current trend: {trend_title}")
        # トレンド便乗のためのリード文を合成
        trend_header = f"いま『{trend_title}』が話題ですが、それより我々の税金のほうが大問題です。\n\n"
        
        # Twitterの文字数制限（全角140文字）に注意しつつ合成
        main_text = trend_header + main_text
    else:
        print("⚠️ Could not fetch trend. Proceeding with standard tweet.")

    vid_path = generate_tax_video(data)
    tweet_id = post_tweet(main_text, reply_text, vid_path)
    
    if tweet_id:
        print("✅ Trend Jacking Complete! Forced impressions delivered.")
    else:
        print("❌ Trend Jacking Failed.")

if __name__ == "__main__":
    main()
