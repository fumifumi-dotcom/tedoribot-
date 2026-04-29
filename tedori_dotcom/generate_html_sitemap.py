import os
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SITEMAP_XML = os.path.join(BASE_DIR, "sitemap.xml")
HTML_SITEMAP = os.path.join(BASE_DIR, "html_sitemap.html")

def generate_html_sitemap():
    if not os.path.exists(SITEMAP_XML):
        print("❌ sitemap.xml not found!")
        return

    # Parse XML
    tree = ET.parse(SITEMAP_XML)
    root = tree.getroot()
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    
    urls = []
    for url_tag in root.findall('ns:url', namespace):
        loc = url_tag.find('ns:loc', namespace)
        if loc is not None and loc.text:
            url_str = loc.text
            # ローカルのパスを取得してタイトルを抽出する
            local_path = url_str.replace("https://tedori-keisan.com/", "")
            if local_path == "":
                local_path = "index.html"
                
            full_path = os.path.join(BASE_DIR, local_path)
            title = url_str
            if os.path.exists(full_path):
                import re
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        c = f.read()
                        m = re.search(r'<title>(.*?)</title>', c, re.IGNORECASE)
                        if m:
                            title = m.group(1).replace(" - 手取り計算.com", "").replace(" | 手取り計算.com", "")
                except Exception:
                    pass
            
            urls.append((url_str, title))

    # HTML生成
    html_content = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>サイトマップ（全記事一覧） | 手取り計算.com</title>
  <meta name="description" content="手取り計算.comのすべての記事・ページの一覧です。">
  <link rel="stylesheet" href="css/style.css">
  <link rel="canonical" href="https://tedori-keisan.com/html_sitemap.html">
  <!-- Google AdSense -->
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3012346545678100" crossorigin="anonymous"></script>
  <!-- Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-3STMJXD6N3"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-3STMJXD6N3');
  </script>
</head>
<body class="bg-gray-50 text-slate-800">
  <header class="site-header">
    <div class="container header-inner">
      <a href="index.html" class="logo"><div class="logo-icon">¥</div><div class="logo-text"><span>手取り計算.com</span></div></a>
    </div>
  </header>

  <main class="container" style="max-width: 900px; margin: 60px auto; padding: 0 20px;">
    <h1 style="font-size: 28px; margin-bottom: 32px; color: var(--text-primary);">🗺️ サイトマップ（全記事一覧）</h1>
    <div style="background: var(--bg-card); border: 1px solid var(--glass-border); border-radius: 12px; padding: 32px;">
      <ul style="list-style: none; padding: 0; display: grid; gap: 16px;">
"""
    for full_url, title in urls:
        html_content += f'        <li style="border-bottom: 1px solid var(--glass-border); padding-bottom: 8px;"><a href="{full_url}" style="color: #3b82f6; text-decoration: none; font-weight: 500;">{title}</a></li>\n'
        
    html_content += """
      </ul>
    </div>
  </main>

  <footer class="site-footer">
    <div class="container">
      <div class="footer-links">
        <a href="/index.html">ホームへ戻る</a>
        <a href="/html_sitemap.html">サイトマップ</a>
      </div>
      <p>© 2026 手取り計算.com</p>
    </div>
  </footer>
</body>
</html>
"""

    with open(HTML_SITEMAP, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"✅ HTML Sitemap generated with {len(urls)} links at: html_sitemap.html")

if __name__ == "__main__":
    generate_html_sitemap()
