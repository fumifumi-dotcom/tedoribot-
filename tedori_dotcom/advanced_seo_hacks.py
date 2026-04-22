import os
import re
from datetime import datetime

BASE_DIR = "/Users/imamichifumitaka/Downloads/ミカタ_経理/今道_生活を豊かに/money-tools"

def advanced_hacks():
    today_str = datetime.now().strftime("%Y年%m月%d日")
    date_badge = f"""
      <div style="margin-bottom: 24px; display: inline-block; background: rgba(59, 130, 246, 0.1); color: #3b82f6; padding: 4px 12px; border-radius: 9999px; font-size: 13px; font-weight: bold;">
        🕒 最終更新日: {today_str}
      </div>"""

    # パンくずリストJSON-LD
    breadcrumb_schema_base = """
  <!-- SEO HACK: Breadcrumb List -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [{
      "@type": "ListItem",
      "position": 1,
      "name": "手取り計算.com トップ",
      "item": "https://tedori-keisan.com/"
    },{
      "@type": "ListItem",
      "position": 2,
      "name": "お金の知識",
      "item": "https://tedori-keisan.com/CATEGORY_PLACEHOLDER"
    }]
  }
  </script>"""

    count_date = 0
    count_links = 0
    count_breadcrumbs = 0

    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                original_content = content
                
                # 1. 永遠の新着ハック (Inject Date Badge after </h1>)
                if "🕒 最終更新日" not in content and "</h1>" in content:
                    content = content.replace("</h1>", f"</h1>\n{date_badge}")
                    count_date += 1

                # 2. Wikipedia化ハック (Safe string replacement outside of tags)
                # "NISA" -> <a href="/articles/nisa-guide.html">NISA</a>
                # "ふるさと納税" -> <a href="/furusato.html">ふるさと納税</a>
                # 簡易的にすでに <a> の中にあるものを避けるため、正規表現ではなく一括置換後 <a><a>にならないよう調整は難しいが、
                # ここでは <p>〜</p> の中身だけをターゲットにする。
                
                def replace_wiki(match):
                    p_content = match.group(0)
                    # すでにリンクがある場合は除外
                    if "<a " in p_content:
                        return p_content
                    # NISAの文字をリンク化
                    p_content = re.sub(r'(?<!>)(新NISA|NISA)(?!<)', r'<a href="/articles/nisa-guide.html" style="color:#10b981; font-weight:bold; text-decoration:underline;">\1</a>', p_content)
                    # ふるさと納税をリンク化
                    p_content = re.sub(r'(?<!>)(ふるさと納税)(?!<)', r'<a href="/furusato.html" style="color:#3b82f6; font-weight:bold; text-decoration:underline;">\1</a>', p_content)
                    return p_content
                
                # <p>タグのみ対象にしてWikipedia化
                new_content = re.sub(r'<p[^>]*>.*?</p>', replace_wiki, content, flags=re.DOTALL)
                if new_content != content:
                    content = new_content
                    count_links += 1

                # 3. パンくずリストハック
                if "BreadcrumbList" not in content and "</head>" in content:
                    # 簡易的に現在のファイル名をカテゴリにする
                    schema = breadcrumb_schema_base.replace("CATEGORY_PLACEHOLDER", file.replace(".html", ""))
                    content = content.replace("</head>", f"{schema}\n</head>")
                    count_breadcrumbs += 1

                if content != original_content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

    print(f"✅ Injected Date Badge: {count_date} files")
    print(f"✅ Injected Wiki Links: {count_links} files")
    print(f"✅ Injected Breadcrumbs: {count_breadcrumbs} files")

if __name__ == "__main__":
    advanced_hacks()
