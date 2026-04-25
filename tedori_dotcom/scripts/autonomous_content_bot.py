#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import random
import datetime
import subprocess
from google import genai
from google.genai import types

# ---------------------------------------------------------
# 設定
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")
SITEMAP_PATH = os.path.join(BASE_DIR, "sitemap.xml")

# APIキーの取得（環境変数から）
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set.")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)

# A8.net 提携済みリンク
AFF_LINKS = {
    "career": "https://px.a8.net/svt/ejp?a8mat=4B1OTT+6P4KS2+47GS+5YRHE",
    "furusato": "https://rpx.a8.net/svt/ejp?a8mat=4B1OTR+ACPDGY+2HOM+6C1VM&rakuten=y&a8ejpredirect=http%3A%2F%2Fhb.afl.rakuten.co.jp%2Fhgc%2F0ea62065.34400275.0ea62066.204f04c0%2Fa26041903646_4B1OTR_ACPDGY_2HOM_6C1VM%3Fpc%3Dhttp%253A%252F%252Fevent.rakuten.co.jp%252Ffurusato%252F%26m%3Dhttp%253A%252F%252Fm.rakuten.co.jp%252F",
    "nisa": "https://px.a8.net/svt/ejp?a8mat=4B1PLP+ACPDGY+3XCC+6AZAQ"
}

# 記事のトピック候補（まだ書かれていないロングテールキーワード）
TOPICS = [
    {"keyword": "年収400万 実家暮らし 貯金", "slug": "income-400-living-with-parents"},
    {"keyword": "手取り15万 一人暮らし きつい", "slug": "tedori-15-single-hard"},
    {"keyword": "年収500万 住宅ローン いくらまで", "slug": "income-500-mortgage-limit"},
    {"keyword": "手取り20万 投資 割合", "slug": "tedori-20-investment-ratio"},
    {"keyword": "ボーナスなし 年収300万 手取り", "slug": "no-bonus-income-300-tedori"},
    {"keyword": "年収600万 子育て 限界", "slug": "income-600-parenting-limit"},
    {"keyword": "手取り25万 車 維持費", "slug": "tedori-25-car-maintenance"},
    {"keyword": "年収800万 専業主婦 きつい", "slug": "income-800-housewife-hard"},
    {"keyword": "手取り30万 家賃 目安", "slug": "tedori-30-rent-guide"},
    {"keyword": "20代 手取り 絶望", "slug": "20s-tedori-despair"},
    {"keyword": "30代 手取り 中央値 リアル", "slug": "30s-tedori-median-real"},
    {"keyword": "手取りが増えない 理由", "slug": "why-tedori-not-increasing"},
    {"keyword": "社会保険料 高すぎ おかしい", "slug": "social-insurance-too-high"},
    {"keyword": "ふるさと納税 年収400万 やらないと損", "slug": "furusato-income-400-loss"},
    {"keyword": "新NISA 手取り20万 いくら", "slug": "nisa-tedori-20-how-much"}
]

# ---------------------------------------------------------
# メイン処理
# ---------------------------------------------------------
def main():
    # 既存の記事スラッグを取得して重複を避ける
    existing_files = os.listdir(ARTICLES_DIR) if os.path.exists(ARTICLES_DIR) else []
    existing_slugs = [f.replace('.html', '') for f in existing_files if f.endswith('.html')]

    available_topics = [t for t in TOPICS if t['slug'] not in existing_slugs]
    if not available_topics:
        print("No new topics available. Please add more to TOPICS list.")
        sys.exit(0)

    # ランダムに1つ選ぶ
    target_topic = random.choice(available_topics)
    keyword = target_topic["keyword"]
    slug = target_topic["slug"]

    print(f"Generating article for keyword: {keyword} (slug: {slug})")

    html_content = generate_article(keyword, slug)
    if not html_content:
        print("Failed to generate content.")
        sys.exit(1)

    # HTMLファイルとして保存
    file_path = os.path.join(ARTICLES_DIR, f"{slug}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Saved: {file_path}")

    # sitemap.xml の更新
    update_sitemap()

    # Git Commit & Push
    git_commit_and_push(slug)

# ---------------------------------------------------------
# AIによる記事生成
# ---------------------------------------------------------
def generate_article(keyword, slug):
    prompt = f"""
あなたはFP（ファイナンシャルプランナー）資格を持つ、給与計算と税制のプロフェッショナルWebライターです。
ターゲットキーワード「{keyword}」で検索するユーザーの悩みを解決するSEO記事のHTMLコンテンツ（<body>の中身のみ、<main>タグで囲むこと）を生成してください。

【厳守するルール】
1. **PREP法**（結論→理由→具体例→結論）を用いて、論理的で読みやすい構成にすること。
2. 文字数は約2,000〜3,000文字程度を想定したボリューム感にすること。
3. HTMLタグ（<h2>, <h3>, <p>, <ul>, <li>, <strong>, <table>など）を適切に使用して構造化すること。
4. クラス名は以下を使用可能：
   - 記事コンテナ: `<article style="background:var(--bg-secondary); padding:40px; border-radius:var(--border-radius-lg); border:1px solid var(--glass-border);">`
   - H1タイトル: `<h1 style="font-size:28px; color:var(--text-primary); margin-bottom:24px;">`
   - H2見出し: `<h2 style="font-size:22px; color:var(--accent-blue); margin-top:40px; border-bottom:2px solid var(--glass-border);">`
   - テキスト: `<p style="color:var(--text-secondary); line-height:1.8; margin-bottom:24px;">`
5. 記事の冒頭に、以下のような「更新日バッジ」を入れること。
   `<div style="margin-bottom: 24px; display: inline-block; background: rgba(59, 130, 246, 0.1); color: #3b82f6; padding: 4px 12px; border-radius: 9999px; font-size: 13px; font-weight: bold;">🕒 最終更新日: {datetime.date.today().strftime('%Y年%m月%d日')}</div>`
6. **必ず以下の3つのアフィリエイトリンクへの誘導を、文脈に合わせて自然に（解決策として）配置すること**。ボタンデザインは以下を使用。
   - 転職・年収診断: `<div style="text-align:center; margin:32px 0;"><a href="{AFF_LINKS['career']}" class="cta-button green" style="display:inline-block; padding:16px 32px; font-size:16px;" target="_blank" rel="noopener sponsored">自分の適正年収を無料診断する →</a></div>`
   - ふるさと納税: `<div style="text-align:center; margin:32px 0;"><a href="{AFF_LINKS['furusato']}" class="cta-button purple" style="display:inline-block; padding:16px 32px; font-size:16px;" target="_blank" rel="noopener sponsored">楽天ふるさと納税で節税する →</a></div>`
   - NISA口座: `<div style="text-align:center; margin:32px 0;"><a href="{AFF_LINKS['nisa']}" class="cta-button orange" style="display:inline-block; padding:16px 32px; font-size:16px;" target="_blank" rel="noopener sponsored">松井証券でNISAを始める →</a></div>`
7. アウトプットは **HTMLコードのみ**（```html などのマークダウンブロックは不要、直接HTMLから開始すること）。<html>や<head>は不要。<main class="container" style="max-width: 800px; margin: 40px auto;"> から開始すること。

では、「{keyword}」に関する最高品質の記事を生成してください。タイトルはH1タグで魅力的に設定してください。
"""
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        content = response.text.strip()
        # 万が一マークダウンブロックがついていたら削除
        if content.startswith("```html"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        
        # テンプレートに埋め込み
        full_html = build_full_html(keyword, slug, content.strip())
        return full_html
    except Exception as e:
        print(f"API Error: {e}")
        return None

def build_full_html(keyword, slug, main_content):
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{keyword}のリアルと解決策【2026年最新】</title>
  <meta name="description" content="{keyword}に関する悩みを給与計算のプロが徹底解説。原因と具体的な解決策（節税・転職・投資）をまとめました。">
  <link rel="canonical" href="https://tedori-keisan.com/articles/{slug}.html">
  <link rel="stylesheet" href="../css/style.css">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-3STMJXD6N3"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-3STMJXD6N3');</script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3012346545678100" crossorigin="anonymous"></script>
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <a href="../index.html" class="logo"><div class="logo-icon">¥</div><div class="logo-text"><span>手取り計算.com</span></div></a>
      <nav class="header-nav" style="display:flex;gap:20px;align-items:center;">
        <a href="../index.html" style="color:var(--text-secondary);font-size:13px;text-decoration:none;font-weight:500;">手取り計算</a>
        <a href="../furusato.html" style="color:var(--text-secondary);font-size:13px;text-decoration:none;font-weight:500;">ふるさと納税</a>
        <a href="../diagnosis.html" style="color:#8b5cf6;font-size:13px;text-decoration:none;font-weight:700;">🔮 人生診断</a>
      </nav>
    </div>
  </header>

  {main_content}

  <footer class="site-footer"><div class="container">
    <div class="footer-links"><a href="../html_sitemap.html">全記事一覧</a><a href="../privacy.html">プライバシーポリシー</a></div>
    <p>© 2026 手取り計算.com</p>
  </div></footer>
</body>
</html>"""

# ---------------------------------------------------------
# Sitemap 更新
# ---------------------------------------------------------
def update_sitemap():
    print("Updating sitemap.xml...")
    # 既存の sitemap.xml をパースするより、シンプルに再構築する
    with open(SITEMAP_PATH, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        # Core pages
        for p in ['','furusato.html','compound.html','lifetime_tax.html','retirement.html','salary-list.html','diagnosis.html']:
            pr = '1.0' if p in ['','furusato.html','diagnosis.html'] else '0.9'
            f.write(f'  <url><loc>https://tedori-keisan.com/{p}</loc><priority>{pr}</priority></url>\n')
        
        # /pages/ (Generated patterns)
        pages_dir = os.path.join(BASE_DIR, 'pages')
        if os.path.exists(pages_dir):
            for fn in sorted(os.listdir(pages_dir)):
                if fn.endswith('.html'):
                    f.write(f'  <url><loc>https://tedori-keisan.com/pages/{fn}</loc><priority>0.7</priority></url>\n')
        
        # /articles/ (Including auto-generated ones)
        if os.path.exists(ARTICLES_DIR):
            for fn in sorted(os.listdir(ARTICLES_DIR)):
                if fn.endswith('.html'):
                    f.write(f'  <url><loc>https://tedori-keisan.com/articles/{fn}</loc><priority>0.8</priority></url>\n')
                    
        f.write('</urlset>\n')
    print("Sitemap updated.")

# ---------------------------------------------------------
# Git コミット＆プッシュ
# ---------------------------------------------------------
def git_commit_and_push(slug):
    print("Deploying to GitHub / Cloudflare Pages...")
    try:
        subprocess.run(["git", "-C", BASE_DIR, "add", "articles/", "sitemap.xml"], check=True)
        subprocess.run(["git", "-C", BASE_DIR, "commit", "-m", f"auto-content: add article {slug}"], check=True)
        subprocess.run(["git", "-C", BASE_DIR, "push", "origin", "main"], check=True)
        print("✅ Successfully deployed!")
    except subprocess.CalledProcessError as e:
        print(f"Git execution failed: {e}")

if __name__ == "__main__":
    main()
