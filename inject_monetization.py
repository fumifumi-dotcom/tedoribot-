import os

BASE_DIR = "/Users/imamichifumitaka/Downloads/ミカタ_経理/今道_生活を豊かに/money-tools"

adsense_code = """
  <!-- Google AdSense -->
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3012346545678100" crossorigin="anonymous"></script>
"""

def inject_adsense_to_html():
    count = 0
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                if "pagead2.googlesyndication.com" not in content and "</head>" in content:
                    content = content.replace("</head>", f"{adsense_code}</head>")
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    count += 1
    print(f"✅ Injected AdSense into {count} HTML files.")

if __name__ == "__main__":
    inject_adsense_to_html()
