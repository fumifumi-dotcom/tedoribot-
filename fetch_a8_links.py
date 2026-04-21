import sys
import time
from playwright.sync_api import sync_playwright
import json

def fetch_links():
    results = []
    print("Starting A8.net link fetcher...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            print("Logging in...")
            page.goto("https://pub.a8.net/a8v2/asLoginAction.do")
            page.fill('input[name="login"]', "fumitaka12731")
            page.fill('input[name="passwd"]', "fumifumi0514")
            page.click('input[type="submit"]')
            page.wait_for_timeout(3000)
            
            if "loginError" in page.url or "asLoginAction" in page.url:
                print("Login failed.")
                return
            print("Login successful!")
            
            ins_ids = [
                "s00000018318002",
                "s00000018318001",
                "s00000022683007",
                "s00000016469001",
                "s00000019630001",
                "s00000023673002",
                "s00000000002006",
                "s00000011623001",
                "s00000000018015",
                "s00000005186002",
                "s00000005186001",
            ]
            print(f"Checking {len(ins_ids)} programs...")
            
            for ins_id in ins_ids:
                print(f"Fetching link for insId: {ins_id}...")
                
                # プログラム名を取得するために一度プログラム詳細に飛ぶのも良いが、直接リンク作成画面へ
                ad_url = f"https://pub.a8.net/a8v2/media/linkAction.do?insId={ins_id}&materialDesc=2&matCount=100"
                page.goto(ad_url)
                page.wait_for_timeout(1000)
                
                # ページタイトルかh2からプログラム名を取得
                prog_name = "Unknown"
                name_loc = page.locator("h2.h2, p.programTitle")
                if name_loc.count() > 0:
                    prog_name = name_loc.nth(0).inner_text().strip()
                
                # 最初のtextareaのコードを取得 (href="https://px.a8.net/svt/..." 等)
                textareas = page.locator("textarea")
                prog = {"insId": ins_id, "name": prog_name}
                
                if textareas.count() > 0:
                    html_code = textareas.nth(0).input_value()
                    url_only = ""
                    if 'href="' in html_code:
                        url_only = html_code.split('href="')[1].split('"')[0]
                    prog['html_code'] = html_code
                    prog['url'] = url_only
                else:
                    prog['html_code'] = "N/A"
                    prog['url'] = "N/A"
                
                results.append(prog)
                time.sleep(1.5)
                
            # 結果を保存
            out_file = "extracted_a8_links.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"All done! Extracted {len(results)} links to {out_file}.")
                
        except Exception as e:
            print(f"Error during fetch: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    fetch_links()
