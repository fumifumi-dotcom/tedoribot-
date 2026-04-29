import os
import glob
from datetime import datetime

BASE_DIR = "/Users/imamichifumitaka/money-tools/tedori_dotcom"
BASE_URL = "https://tedori-keisan.com"

def generate_xml_sitemap():
    print("🔍 Scanning HTML files...")
    
    # 全てのHTMLを取得
    html_files = glob.glob(f"{BASE_DIR}/**/*.html", recursive=True)
    
    # 除外リスト (コンポーネント用ファイルなど)
    exclude_list = ["google", "widget", "a8_"]
    
    urls = []
    
    for file_path in html_files:
        filename = os.path.basename(file_path)
        
        # 除外チェック
        if any(ex in filename for ex in exclude_list):
            continue
            
        # 相対パスを取得
        rel_path = os.path.relpath(file_path, BASE_DIR)
        
        # Windows環境でのバックスラッシュをスラッシュに変換（念のため）
        rel_path = rel_path.replace("\\", "/")
        
        # index.html はディレクトリのルートURLにする
        if rel_path == "index.html":
            url = f"{BASE_URL}/"
            priority = "1.0"
        elif rel_path.endswith("/index.html"):
            url = f"{BASE_URL}/{rel_path.replace('index.html', '')}"
            priority = "0.8"
        else:
            url = f"{BASE_URL}/{rel_path}"
            priority = "0.6"
            
        # トップレベルの主要ページは優先度高め
        if rel_path in ["furusato.html", "retirement.html", "salary-list.html", "lifetime_tax.html", "diagnosis.html"]:
            priority = "0.9"
            
        urls.append({
            "loc": url,
            "lastmod": datetime.now().strftime("%Y-%m-%d"),
            "priority": priority
        })

    # XMLの構築
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for u in sorted(urls, key=lambda x: x["priority"], reverse=True):
        xml_content += "  <url>\n"
        xml_content += f"    <loc>{u['loc']}</loc>\n"
        xml_content += f"    <lastmod>{u['lastmod']}</lastmod>\n"
        xml_content += f"    <priority>{u['priority']}</priority>\n"
        xml_content += "  </url>\n"
        
    xml_content += "</urlset>\n"
    
    sitemap_path = os.path.join(BASE_DIR, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(xml_content)
        
    print(f"✅ Generated sitemap.xml with {len(urls)} URLs.")

if __name__ == "__main__":
    generate_xml_sitemap()
