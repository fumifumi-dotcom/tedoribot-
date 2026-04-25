import os
import json
import tweepy
import random
import sys
import time
import datetime
import urllib.request
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
import math
import imageio
import numpy as np
import google.generativeai as genai

def fetch_external_trend():
    """Yahoo Business RSSから最新の外部トレンドを取得（バリエーション強化版）"""
    try:
        url = 'https://news.yahoo.co.jp/rss/topics/business.xml'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            root = ET.fromstring(response.read())
        
        items = root.findall('.//item/title')
        if items:
            # 最新15件からランダムに選び、毎回違う話題にする
            recent_items = items[:15]
            random_item = random.choice(recent_items)
            
            # 全角・半角スペースで分割して主要キーワードを取得
            keyword = random_item.text.split()[0]
            
            # 「日経平均」などの頻出すぎて面白くないワードを除外
            boring_words = ["日経平均", "NYダウ", "東証", "反発", "続落", "終値", "円相場"]
            if not any(bw in keyword for bw in boring_words):
                return keyword
                
    except Exception as e:
        print(f"⚠️ Trend fetch error: {e}")
        
    # RSSから取得できなかった場合や、退屈なワードだった場合の魅力的なフォールバック
    fallbacks = [
        "止まらない物価高", 
        "円安による値上げラッシュ", 
        "爆買いインバウンド", 
        "実質賃金の低下", 
        "社会保険料の負担増", 
        "見えないステルス増税"
    ]
    return random.choice(fallbacks)

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
    
    # グラフデータとカラーテーマの分岐
    gross = data['gross_raw']
    current_hour = datetime.datetime.now().hour
    if 5 <= current_hour < 11:
        bg_color = (240, 248, 255)
        text_color = (15, 23, 42)
        subtext_color = (100, 116, 139)
        color_tedori = (59, 130, 246)
        color_tax = (239, 68, 68)
        color_social = (14, 165, 233)
    elif 11 <= current_hour < 17:
        bg_color = (255, 250, 240)
        text_color = (15, 23, 42)
        subtext_color = (100, 116, 139)
        color_tedori = (245, 158, 11)
        color_tax = (220, 38, 38)
        color_social = (251, 146, 60)
    else:
        bg_color = (15, 23, 42)
        text_color = (248, 250, 252)
        subtext_color = (148, 163, 184)
        color_tedori = (16, 185, 129)
        color_tax = (225, 29, 72)
        color_social = (139, 92, 246)

    sections = [
        {'label': '手取り', 'val': data['tedori_raw'], 'color': color_tedori},
        {'label': '税金', 'val': data['tax_raw'], 'color': color_tax},
        {'label': '社会保険', 'val': data['social_raw'], 'color': color_social}
    ]
    
    title_font = get_font(72)
    sub_font = get_font(40)
    center_font = get_font(48)
    item_font = get_font(52)
    val_font = get_font(48)
    
    for f_idx in range(total_frames):
        # イージング（アニメーションの滑らかさ）
        progress = min(f_idx / (total_frames * 0.8), 1.0)
        progress = 1.0 - math.pow(1.0 - progress, 3) # Cubic ease-out
        
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        draw.text((80, 60), f"年収{data['income']}万円の「本当の」手取り", font=title_font, fill=text_color)
        draw.text((80, 140), f"額面{data['income']}万でも、年間 {data['tax_total']}万円 が天引きされます", font=sub_font, fill=subtext_color)
        
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
        draw.ellipse(inner_bbox, fill=bg_color)
        
        # 中心テキスト（手取り率がカウントアップ）
        current_rate = round(data['rate'] * progress, 1)
        center_text = f"{current_rate}%"
        text_bbox = draw.textbbox((0, 0), center_text, font=center_font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        draw.text((250 - text_w/2, 390 - text_h/2), center_text, font=center_font, fill=text_color)
        draw.text((250 - 45, 340), "手取り率", font=get_font(24), fill=subtext_color)
        
        # 凡例（Legend）
        legend_x = 520
        legend_y = 250
        
        for i, sec in enumerate(sections):
            y_pos = legend_y + (i * 90)
            draw.rounded_rectangle([legend_x, y_pos, legend_x + 30, y_pos + 30], radius=8, fill=sec['color'])
            draw.text((legend_x + 50, y_pos - 10), f"{sec['label']}", font=item_font, fill=text_color)
            
            # 数値もパラパラ変わる
            current_val = round((sec['val']/10000) * progress)
            val_str = f"約 {current_val}万円"
            draw.text((legend_x + 350, y_pos - 5), val_str, font=val_font, fill=text_color)
            
        draw.text((width - 320, height - 50), "手取り計算.com (2026年版)", font=get_font(24), fill=subtext_color)
        
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
        
    if income > 1500:
        income = 250

    data = calculate_salary_data(income)
    
    # 外部トレンドキーワードの取得（インバウンド情報）
    trend_kw = fetch_external_trend()
    
    # 過去の成功データ（PDCA結果）を読み込む
    best_trend_info = ""
    try:
        best_trend_file = 'sns_content/best_trend.json'
        if os.path.exists(best_trend_file):
            with open(best_trend_file, 'r', encoding='utf-8') as f:
                bt = json.load(f)
                best_trend_info = f"\n【過去の成功データ】: 前回は『{bt.get('best_trend', '')}』の文脈で大きな反響がありました。この成功パターン（読者の感情を抉る構成）を踏襲、またはさらに超える内容にしてください。"
    except Exception as e:
        print(f"⚠️ Could not load best trend: {e}")

    # 時間帯別コンテキスト（テンプレ化を避けるため緩やかな指示に変更）
    current_hour = datetime.datetime.now().hour
    if 5 <= current_hour < 11:
        time_context = "今は朝の通勤時間帯。出勤する人たちの気怠さや、これから1日働くことへの徒労感に寄り添うトーン。"
    elif 11 <= current_hour < 17:
        time_context = "今日のお昼時・日中の時間帯。ランチ代や日々の節約など、日常の身近なお金の話と絡めると自然なトーン。"
    else:
        time_context = "今は夜のリラックスタイム。ふと将来を考えた時の漠然とした不安や、「このままでいいのか」という焦燥感を刺激するトーン。"

    # 人間味とバリエーションを出すためのスタイル
    writing_styles = [
        "居酒屋で友人に愚痴るような、少しくだけたリアルな口調（適度なタメ口交じり）",
        "ふとスマホのニュースを見て気づいてしまった、素朴な疑問と焦りを表現する呟き",
        "「〜ってマ？」のようなネットスラングを少しだけ混ぜた、現代のリアルな社会人風",
        "あえて感情を抑え、エクセルを見つめるように冷静に数字のヤバさを語るスタイル",
        "「これ知ってた？」とフォロワーに軽く問いかけるような親しみやすいスタイル"
    ]
    selected_style = random.choice(writing_styles)

    # 構成のバリエーション
    structure_styles = [
        "箇条書きを一切使わず、短い数行のポエムや呟きのように書く",
        "冒頭でトレンドワードに自然に触れ、中盤で【年収〇〇万】の箇条書きで数字を叩きつける",
        "「やばい」などの一言から始まり、最後に向かって静かに絶望していく構成"
    ]
    selected_structure = random.choice(structure_styles)

    # CTA（プロフィールへの誘導）のランダム化（約30%の確率で誘導する）
    use_cta = random.random() < 0.3
    cta_instruction = "・最後は必ず「プロフ見て」「プロフのツールで計算してみて」などの軽い言葉でプロフィール欄へ誘導して終わってください。" if use_cta else "・プロフィールへの誘導やリンクの案内は【一切書かないで】ください。純粋な呟きや問題提起で終わらせてください。"

    API_KEY_GEMINI = os.environ.get("GEMINI_API_KEY", "")
    
    main_text = ""
    # Gemini APIキーが設定されている場合はAIで完全動的生成
    if API_KEY_GEMINI:
        try:
            genai.configure(api_key=API_KEY_GEMINI)
            model = genai.GenerativeModel('gemini-1.5-flash') # 高速・無料枠対応モデル
            
            prompt = f"""
あなたはX（Twitter）の一般ユーザーとして、人間味あふれるリアルな投稿を作成してください。AIが書いたような「綺麗すぎる文章」「テンプレ感」「大げさな表現（例：残酷な現実、〜の真実など）」は絶対に避けてください。

【今回の投稿設定】
・今日の話題（自然に混ぜる）: {trend_kw}
・対象年収: {data['income']}万円
・手取り額: 約{data['tedori']}万円
・天引きされる税金等: 年間約{data['tax_total']}万円{best_trend_info}
・時間帯の文脈: {time_context}
・文体の指定: {selected_style}
・文章構成の指定: {selected_structure}

【厳守事項】
・いかにもAIが作ったような「〜をご存知ですか？」「〜をご紹介します」といった定型文は禁止。
・すべての数字（年収や税金）を使う必要はありません。必要な数字だけをピックアップし、人間らしい「生々しさ」「弱音」「皮肉」などを交えて表現してください。
・文字が詰まったブロック状の文章は避け、適度に改行を入れてスマホで読みやすくしてください。
・ハッシュタグは一切不要です。
{cta_instruction}
"""
            response = model.generate_content(prompt)
            main_text = response.text.strip()
            
            # AIが「」などをつけて返した場合は除去
            main_text = main_text.replace("「", "").replace("」", "")
            if main_text.startswith('"') and main_text.endswith('"'):
                main_text = main_text[1:-1]
        except Exception as e:
            print(f"⚠️ Gemini API Error: {e}")
            
    # Geminiがエラーだった場合やAPIキーがない場合のフォールバック（緊急用）
    if not main_text:
        main_text = f"いま世間は『{trend_kw}』の話題で持ちきりですが…\n\nそれよりヤバいのが「あなたの税金」です。\n\n【年収{data['income']}万円の残酷な現実】\n・額面：{data['income']}万円\n・手取り：たった{data['tedori']}万円\n・国に奪われる額：年間{data['tax_total']}万円\n\n現実に絶望したい人はプロフ見て。"

    # 学習エンジン用ID
    template_id = f"gemini_LLM::[{trend_kw}]"
    reply_text = "" # リンクはプロフィール誘導に絞るため今回は不要
    
    # 次の年収（+10万円）を保存
    with open(state_file, 'w', encoding='utf-8') as f:
        f.write(str(income + 10))
        
    return main_text, reply_text, data, template_id

def post_tweet(main_text, reply_text, media_path=None, is_video=False):
    """メインを画像/動画付きで投稿し、それにぶら下げる形でリプライ（URL）を送信する"""
    
    # v1.1 API (For media upload)
    auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
    api_v1 = tweepy.API(auth)

    # v2 API (For tweeting)
    client = tweepy.Client(
        consumer_key=API_KEY, consumer_secret=API_SECRET,
        access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET
    )
    
    media_ids = None
    if media_path:
        print(f"Uploading media: {media_path}...")
        try:
            if is_video:
                media = api_v1.chunked_upload(media_path, media_category="tweet_video")
            else:
                media = api_v1.media_upload(media_path)
            media_ids = [media.media_id]
            print("✅ Media uploaded successfully.")
            
            # Twitterのバックグラウンド動画処理を待つ
            if is_video:
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
                print(f"⚠️ 403/401 Forbidden or Media attach error. Falling back to text-only: {e}")
                response = client.create_tweet(text=main_text)
        else:
            response = client.create_tweet(text=main_text)
            
        tweet_id = response.data['id']
        print(f"✅ Successfully posted main tweet ID: {tweet_id}")
        
        return tweet_id
    except Exception as e:
        print(f"❌ Error posting tweet: {e}")
        return None

def generate_tax_image(data):
    """Pillowを用いて、静止画の円グラフを描画する"""
    width, height = 1200, 630 # Twitter推奨サイズ
    
    gross = data['gross_raw']
    bg_color = (15, 23, 42)
    text_color = (248, 250, 252)
    subtext_color = (148, 163, 184)
    color_tedori = (16, 185, 129)
    color_tax = (225, 29, 72)
    color_social = (139, 92, 246)

    sections = [
        {'label': '手取り', 'val': data['tedori_raw'], 'color': color_tedori},
        {'label': '税金', 'val': data['tax_raw'], 'color': color_tax},
        {'label': '社会保険', 'val': data['social_raw'], 'color': color_social}
    ]
    
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    draw.text((80, 60), f"年収{data['income']}万円の「本当の」手取り", font=get_font(72), fill=text_color)
    draw.text((80, 140), f"額面{data['income']}万でも、年間 {data['tax_total']}万円 が天引きされます", font=get_font(40), fill=subtext_color)
    
    bbox = [80, 220, 80 + 340, 220 + 340]
    start_angle = -90
    for sec in sections:
        ratio = sec['val'] / gross
        sweep = ratio * 360
        if sweep > 0:
            draw_pie_slice(draw, bbox, start_angle, start_angle + sweep, sec['color'])
        start_angle += sweep
        
    inner_bbox = [150, 290, 150 + 200, 290 + 200]
    draw.ellipse(inner_bbox, fill=bg_color)
    
    center_text = f"{data['rate']}%"
    text_bbox = draw.textbbox((0, 0), center_text, font=get_font(48))
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]
    draw.text((250 - text_w/2, 390 - text_h/2), center_text, font=get_font(48), fill=text_color)
    draw.text((250 - 45, 340), "手取り率", font=get_font(24), fill=subtext_color)
    
    legend_x = 520
    legend_y = 250
    for i, sec in enumerate(sections):
        y_pos = legend_y + (i * 90)
        draw.rounded_rectangle([legend_x, y_pos, legend_x + 30, y_pos + 30], radius=8, fill=sec['color'])
        draw.text((legend_x + 50, y_pos - 10), f"{sec['label']}", font=get_font(52), fill=text_color)
        val_str = f"約 {round(sec['val']/10000)}万円"
        draw.text((legend_x + 350, y_pos - 5), val_str, font=get_font(48), fill=text_color)
        
    draw.text((width - 320, height - 50), "手取り計算.com (2026年版)", font=get_font(24), fill=subtext_color)
    
    img_path = "sns_content/tax_chart.png"
    img.save(img_path)
    return img_path

if __name__ == '__main__':
    main_text, reply_text, data, template_id = generate_dynamic_tweet()
    
    # 添付メディアのランダム化（動画20%、静止画30%、テキストのみ50%）
    rnd = random.random()
    media_path = None
    is_video = False
    
    if rnd < 0.20:
        media_path = generate_tax_video(data)
        is_video = True
    elif rnd < 0.50:
        media_path = generate_tax_image(data)
        is_video = False
        
    tweet_id = post_tweet(main_text, reply_text, media_path=media_path, is_video=is_video)
    
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
