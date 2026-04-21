import sys
import time
from playwright.sync_api import sync_playwright

def main():
    print("Starting A8.net login process...")
    with sync_playwright() as p:
        # 完全に独立した隔離環境（ヘッドレス）で起動
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            print("Navigating to login page...")
            page.goto("https://pub.a8.net/a8v2/asLoginAction.do")
            
            # Form fill
            print("Entering credentials...")
            page.fill('input[name="login"]', "fumitaka12731")
            page.fill('input[name="passwd"]', "fumifumi0514")
            
            print("Clicking login button...")
            page.click('input[type="submit"]')
            
            # Wait for either success page or CAPTCHA/Error
            page.wait_for_timeout(3000)
            
            # Taking screenshot to verify
            screenshot_path = "a8_login_result.png"
            page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")
            
            # Check current URL
            current_url = page.url
            print(f"Current URL after login attempt: {current_url}")
            
            if "loginError" in current_url or "asLoginAction.do" in current_url:
                print("FAILED: Did not navigate to dashboard. Either CAPTCHA or incorrect credentials.")
                # We save HTML to check what error it is
                with open("a8_error.html", "w") as f:
                    f.write(page.content())
            else:
                print("SUCCESS: Logged in!")
                print("Navigating to programs list...")
                page.goto("https://pub.a8.net/a8v2/media/partnerProgramListAction.do?act=search&viewPage=new")
                
                # 取引先プログラムリストのHTMLを保存
                html_path = "a8_programs.html"
                with open(html_path, "w") as f:
                    f.write(page.content())
                print(f"Programs HTML saved to {html_path}")
                
        except Exception as e:
            print(f"Error during runtime: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
