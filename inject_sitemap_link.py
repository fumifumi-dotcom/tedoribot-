import os
import re

BASE_DIR = "/Users/imamichifumitaka/Downloads/ミカタ_経理/今道_生活を豊かに/money-tools"

def inject_sitemap_links():
    count = 0
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".html") and file != "html_sitemap.html":
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # すでにサイトマップが含まれていないかチェック
                if 'href="/html_sitemap.html"' not in content and 'href="../html_sitemap.html"' not in content and 'href="../../html_sitemap.html"' not in content:
                    # div class="footer-links" の直後にリンクを入れる
                    pattern = r'(<div\s+class=["\']footer-links["\'][^>]*>)'
                    replacement = r'\1\n        <a href="/html_sitemap.html">全記事一覧（サイトマップ）</a>'
                    
                    new_content, num_subs = re.subn(pattern, replacement, content)
                    if num_subs > 0:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        count += 1
                        
    print(f"✅ Injected Sitemap Link into {count} HTML files.")

if __name__ == "__main__":
    inject_sitemap_links()
