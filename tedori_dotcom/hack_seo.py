import os
import re
from datetime import datetime

BASE_DIR = "/Users/imamichifumitaka/Downloads/ミカタ_経理/今道_生活を豊かに/money-tools"
SITEMAP_XML = os.path.join(BASE_DIR, "sitemap.xml")

FAQ_SCHEMA = """
  <!-- SEO HACK: FAQ Schema for maximum SERP real estate -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [{
      "@type": "Question",
      "name": "手取りは額面の何割ですか？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "一般的に手取りは額面給与の約75%〜85%となります。正確な金額は所得税、住民税、社会保険料の控除額によって変動します。当サイトのシミュレーターで1円単位の正確な金額を計算できます。"
      }
    }, {
      "@type": "Question",
      "name": "NISAやふるさと納税で手取りは増えますか？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "ふるさと納税を活用することで翌年の住民税が控除され、実質的な手元に残る価値（返礼品＋税金控除）を最大化できます。また新NISAを活用すれば投資の運用益が非課税になるため、将来の資産を爆発的に増やせます。まずは証券口座の手数料が安い松井証券などのネット証券で始めるのが鉄則です。"
      }
    }]
  }
  </script>"""

FAVICON_TAGS = """
  <!-- Favicon -->
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/favicon.svg">
"""

def inject_html_hacks():
    count = 0
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                modified = False
                
                # Insert Favicon if missing
                if "favicon.svg" not in content and "</head>" in content:
                    content = content.replace("</head>", f"{FAVICON_TAGS}</head>")
                    modified = True
                    
                # Insert FAQ Schema if missing
                if "SEO HACK: FAQ Schema" not in content and "</head>" in content:
                     content = content.replace("</head>", f"{FAQ_SCHEMA}\n</head>")
                     modified = True
                     
                if modified:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    count += 1
    print(f"✅ Injected Favicon and FAQ Schema into {count} HTML files.")

def update_sitemap_lastmod():
    if not os.path.exists(SITEMAP_XML):
        print("❌ sitemap.xml not found")
        return
        
    with open(SITEMAP_XML, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 現在の時刻をISO8601フォーマットで生成
    now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+09:00")
    
    # <lastmod>2026-04-18</lastmod> みたいなものを全て現在の秒単位まで上書きする
    new_content = re.sub(r"<lastmod>.*?</lastmod>", f"<lastmod>{now_iso}</lastmod>", content)
    
    with open(SITEMAP_XML, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    print(f"✅ Modified all <lastmod> timestamps in sitemap.xml to {now_iso} to force emergency recrawl.")

if __name__ == "__main__":
    inject_html_hacks()
    update_sitemap_lastmod()
