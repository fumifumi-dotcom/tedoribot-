import os
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, concatenate_videoclips
import math

# --- 手取り計算ロジック（簡易版） ---
def calculate_tedori_simple(annual_income_man):
    income = annual_income_man * 10_000
    # ざっくりとした手取り計算（約75〜80%）
    if annual_income_man <= 300:
        rate = 0.80
    elif annual_income_man <= 600:
        rate = 0.77
    elif annual_income_man <= 1000:
        rate = 0.73
    else:
        rate = 0.65
        
    tedori = math.floor(income * rate)
    tax = income - tedori
    return tedori, tax

def create_text_image(text, width=1080, height=1920, bg_color="#0f172a", text_color="#ffffff", font_size=80):
    """ 指定したテキストが中央に配置された画像を生成する """
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # macOS標準のヒラギノフォントを使用
    font_path = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Font not found: {font_path}, using default.")
        font = ImageFont.load_default()

    # テキストを改行で分割
    lines = text.split('\n')
    
    # 全体の高さを計算
    total_height = sum(draw.textbbox((0,0), line, font=font)[3] - draw.textbbox((0,0), line, font=font)[1] for line in lines) + (len(lines)-1)*20
    
    current_y = (height - total_height) / 2
    
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (width - text_w) / 2
        
        # 影を描画
        draw.text((x+4, current_y+4), line, font=font, fill="#000000")
        # メインテキスト
        draw.text((x, current_y), line, font=font, fill=text_color)
        current_y += text_h + 20
        
    return img

def generate_short_video(annual_income_man, output_dir):
    """ 年収ごとのショート動画を生成する """
    tedori, tax = calculate_tedori_simple(annual_income_man)
    
    tedori_man = tedori // 10000
    tax_man = tax // 10000
    
    # シーン構成
    scenes = [
        {"text": f"年収{annual_income_man}万円の\n絶望的な手取り\n知ってる？", "duration": 2.0, "color": "#0ea5e9"},
        {"text": "税金と社会保険料で...", "duration": 1.5, "color": "#ffffff"},
        {"text": f"ドカン！と約{tax_man}万円\n引かれて...", "duration": 2.0, "color": "#ef4444"},
        {"text": f"結論：\n手取りは {tedori_man}万円", "duration": 2.5, "color": "#10b981"},
        {"text": "プロフのリンクで\n自分の正確な手取りを\n計算してみよう！\n\n🔍 手取り計算.com", "duration": 3.0, "color": "#f59e0b"}
    ]
    
    clips = []
    
    # 一時画像の保存先
    temp_dir = os.path.join(output_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    for i, scene in enumerate(scenes):
        img = create_text_image(scene["text"], text_color=scene["color"])
        img_path = os.path.join(temp_dir, f"scene_{i}.png")
        img.save(img_path)
        
        # ImageClip作成 (moviepy v2ではwith_durationを使用)
        clip = ImageClip(img_path).with_duration(scene["duration"])
        clips.append(clip)
        
    # 動画を結合
    final_video = concatenate_videoclips(clips, method="compose")
    
    # 出力ファイル名
    output_filename = os.path.join(output_dir, f"shorts_{annual_income_man}man.mp4")
    
    # 書き出し (24fps)
    print(f"🎬 Exporting video for {annual_income_man}万円...")
    final_video.write_videofile(output_filename, fps=24, codec="libx264", audio=False, logger=None)
    
    print(f"✅ Created: {output_filename}")
    
def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OUTPUT_DIR = os.path.join(BASE_DIR, "sns_content", "videos")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # テストとして年収400万、500万、600万、1000万の動画を生成
    test_incomes = [400, 500, 600, 1000]
    
    for income in test_incomes:
        generate_short_video(income, OUTPUT_DIR)
        
    print("🎉 All short videos generated successfully!")

if __name__ == "__main__":
    main()
