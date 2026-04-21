import os
import json
import tweepy
import random
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
import math
import imageio
import numpy as np

def fetch_external_trend():
    """Yahoo Business RSSから最新の外部トレンド（インバウンド情報）を取得"""
    try:
        url = 'https://news.yahoo.co.jp/rss/topics/business.xml'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            root = ET.fromstring(response.read())
        # 最新のビジネストピックタイトルを取得
        first_item = root.find('.//item/title')
        if first_item is not None:
            return first_item.text.split(' ')[0] # 短めの単語にするため分割を試みる
    except Exception as e:
        print(f"⚠️ Trend fetch error: {e}")
    return "日本の景気"

import os

# API鍵の設定（環境変数から取得。ローカル用のフォールバックあり）
API_KEY = os.environ.get("TWITTER_API_KEY", "UHvEB9eE3lyWM4zPARambujIa")
API_SECRET = os.environ.get("TWITTER_API_SECRET", "VUivkTp42P0PaNoOzlglsxnfPViMFLKHQybs8I8IreFUpaSnwn")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "1924677045784838144-hrHWl35Sim0p9PW5WUUSaXYUzUW1n0")
ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET", "Vs1qPPGRMtyRU9sacMBqA59ppnMrNZLe9iWDvoiTtRpf6")

def calculate_salary_data(income):
    gross = income * 10000
    social = gross * 0.15
    if income <= 195:
        income_tax = (gross - 480000 - social) * 0.05
    elif income <= 330:
        income_tax = (gross - 480000 - social) * 0.10 - 97500
    elif income <= 695:
        income_tax = (gross - 480000 - social) * 0.20 - 427500
    elif income <= 900:
        income_tax = (gross - 480000 - social) * 0.23 - 636000
    else:
        income_tax = (gross - 480000 - social) * 0.33 - 1536000
        
    income_tax = max(income_tax, 0)
    resident_tax = max((gross - 480000 - social - 430000) * 0.10, 0)
    tedori = gross - social - income_tax - resident_tax
    rate = (tedori / gross) * 100
    
    return {
        'income': income,
        'tedori': round(tedori / 10000),
        'tax_total': round((gross - tedori) / 10000),
        'rate': round(rate, 1),
        'tedori_raw': tedori,
        'tax_raw': income_tax + resident_tax,
        'social_raw': social,
        'gross_raw': gross
    }

def get_font(size):
    font_path = "sns_content/NotoSansJP-Bold.ttf"
    if not os.path.exists(font_path):
        print("Downloading Noto Sans JP font...")
        url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Bold.otf"
        try:
            urllib.request.urlretrieve(url, font_path)
        except Exception as e:
            print(f"Failed to download font: {e}")
            # Fallback to Mac system font
            font_path = "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc"
            
    try:
        return ImageFont.truetype(font_path, size)
    except:
        return ImageFont.load_default()

def draw_pie_slice(draw, bounding_box, start_angle, end_angle, fill_color):
    """円グラフの各スライスを描画"""
    draw.pieslice(bounding_box, start_angle, end_angle, fill=fill_color)

def generate_tax_video(data):
    """Pillowとimageioを用いて、動的な円グラフを描画するショート動画（MP4）を生成する"""
    width, height = 1200, 630 # Twitter推奨サイズ
    fps = 30
    duration = 2.0 # 秒
    total_frames = int(fps * duration)
    
    frames = []
    
    # グラフデータ
    gross = data['gross_raw']
    sections = [
        {'label': '手取り', 'val': data['tedori_raw'], 'color': (16, 185, 129)},
        {'label': '税金', 'val': data['tax_raw'], 'color': (244, 63, 94)},
        {'label': '社会保険', 'val': data['social_raw'], 'color': (245, 158, 11)}
    ]
    
    title_font = get_font(64)
    sub_font = get_font(36)
    center_font = get_font(42)
    item_font = get_font(48)
    val_font = get_font(40)
    
    for f_idx in range(total_frames):
        # イージング（アニメーションの滑らかさ）
        progress = min(f_idx / (total_frames * 0.8), 1.0)
        progress = 1.0 - math.pow(1.0 - progress, 3) # Cubic ease-out
        
        img = Image.new('RGB', (width, height), color=(248, 250, 252))
        draw = ImageDraw.Draw(img)
        
        draw.text((80, 60), f"年収{data['income']}万円の「本当の」手取り", font=title_font, fill=(15, 23, 42))
        draw.text((80, 140), f"額面{data['income']}万でも、年間 {data['tax_total']}万円 が天引きされます", font=sub_font, fill=(100, 116, 139))
        
        # 円グラフの描画
        bbox = [80, 220, 80 + 340, 220 + 340]
        start_angle = -90
        for sec in sections:
            ratio = sec['val'] / gross
            sweep = ratio * 360 * progress # 進捗に応じて広がる
            if sweep > 0:
                draw_pie_slice(draw, bbox, start_angle, start_angle + sweep, sec['color'])
            start_angle += sweep
            
        # ドーナツ型にするための内側の白円
        inner_bbox = [150, 290, 150 + 200, 290 + 200]
        draw.ellipse(inner_bbox, fill=(248, 250, 252))
        
        # 中心テキスト（手取り率がカウントアップ）
        current_rate = round(data['rate'] * progress, 1)
        center_text = f"{current_rate}%"
        text_bbox = draw.textbbox((0, 0), center_text, font=center_font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        draw.text((250 - text_w/2, 390 - text_h/2), center_text, font=center_font, fill=(15, 23, 42))
        draw.text((250 - 45, 340), "手取り率", font=get_font(24), fill=(100, 116, 139))
        
        # 凡例（Legend）
        legend_x = 520
        legend_y = 250
        
        for i, sec in enumerate(sections):
            y_pos = legend_y + (i * 90)
            draw.rounded_rectangle([legend_x, y_pos, legend_x + 30, y_pos + 30], radius=8, fill=sec['color'])
            draw.text((legend_x + 50, y_pos - 10), f"{sec['label']}", font=item_font, fill=(15, 23, 42))
            
            # 数値もパラパラ変わる
            current_val = round((sec['val']/10000) * progress)
            val_str = f"約 {current_val}万円"
            draw.text((legend_x + 350, y_pos - 5), val_str, font=val_font, fill=(71, 85, 105))
            
        draw.text((width - 320, height - 50), "手取り計算.com (2026年版)", font=get_font(24), fill=(148, 163, 184))
        
        # 配列に追加
        frames.append(np.array(img))
        
    vid_path = "sns_content/tax_chart.mp4"
    imageio.mimwrite(vid_path, frames, fps=fps, codec='libx264')
    return vid_path

def generate_dynamic_tweet():
    state_file = 'sns_content/tweet_state.txt'
    
    # 状態ファイルから現在の「年収」を読み込む（デフォルト250万）
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            income = int(f.read().strip())
    except:
        income = 250
        
    # 年収が1500万円を超えたら250万円にリセットしてループ
    if income > 1500:
        income = 250

    data = calculate_salary_data(income)
    
    # バズ・テンプレートを外部JSON（スコア付きデータベース）から読み込み
    db_file = 'sns_content/templates.json'
    with open(db_file, 'r', encoding='utf-8') as f:
        templates = json.load(f)
    
    # 淘汰システム：スコア（重み）に基づいたランダム抽選
    weights = [max(float(t.get('score', 1.0)), 0.1) for t in templates]
    template = random.choices(templates, weights=weights, k=1)[0]
    
    template_id = template['id']
    main_text = template['main']
    reply_text = template.get('reply', '')
    
    # 外部トレンドキーワードの動的挿入
    trend_kw = "日本の景気"
    if '{trend_keyword}' in main_text:
        full_trend = fetch_external_trend()
        trend_kw = full_trend
        # 学習エンジンのため、外部情報に便乗したことを評価IDとして残す
        template_id = f"{template_id}::[{trend_kw}]"

    main_text = main_text.format(trend_keyword=trend_kw, **data)
    reply_text = reply_text.format(trend_keyword=trend_kw, **data)
    
    # 次の年収（+10万円）を保存
    with open(state_file, 'w', encoding='utf-8') as f:
        f.write(str(income + 10))
        
    return main_text, reply_text, data, template_id

def post_tweet(main_text, reply_text, image_path):
    """メインを画像付きで投稿し、それにぶら下げる形でリプライ（URL）を送信する"""
    
    # v1.1 API (For media upload)
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
    api_v1 = tweepy.API(auth)

    # v2 API (For tweeting)
    client = tweepy.Client(
        consumer_key=API_KEY, consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET
    )
    
    print(f"Uploading video chunked: {image_path}...")
    media_ids = None
    try:
        media = api_v1.chunked_upload(image_path, media_category="tweet_video")
        media_ids = [media.media_id]
        print("✅ Video uploaded successfully.")
        
        # Twitterのバックグラウンド動画処理を数秒待つ
        import time
        time.sleep(3)
    except Exception as e:
        print(f"⚠️ Failed to upload media: {e}. Proceeding without media.")

    print(f"Posting main tweet...")
    try:
        if media_ids:
            try:
                response = client.create_tweet(text=main_text, media_ids=media_ids)
            except Exception as e:
                print(f"⚠️ 403 Forbidden or Media attach error. Falling back to text-only: {e}")
                response = client.create_tweet(text=main_text)
        else:
            response = client.create_tweet(text=main_text)
            
        tweet_id = response.data['id']
        print(f"✅ Successfully posted main tweet ID: {tweet_id}")
        
        return tweet_id
    except Exception as e:
        print(f"❌ Error posting tweet: {e}")
        return None

if __name__ == '__main__':
    main_text, reply_text, data, template_id = generate_dynamic_tweet()
    vid_path = generate_tax_video(data)
    tweet_id = post_tweet(main_text, reply_text, vid_path)
    
    # PDCA用に履歴を保存
    if tweet_id:
        history_file = 'sns_content/tweet_history.json'
        history = []
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                try:
                    history = json.load(f)
                except:
                    pass
        history.append({
            'tweet_id': str(tweet_id),
            'template_id': template_id,
            'timestamp': time.time(),
            'income': data['income']
        })
        # 最新100件まで保持
        history = history[-100:]
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        print(f"✅ PDCA History saved (Template: {template_id})")
