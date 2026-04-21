import requests

SITEMAP_URL = "https://tedori-keisan.com/sitemap.xml"

def ping_search_engines():
    engines = {
        "Google": f"http://www.google.com/ping?sitemap={SITEMAP_URL}",
        "Bing": f"http://www.bing.com/ping?sitemap={SITEMAP_URL}"
    }

    print(f"📡 Sending Ping notifications for {SITEMAP_URL} ...")
    
    for name, url in engines.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: Successfully pinged! (Status: 200)")
            else:
                print(f"⚠️ {name}: Ping returned status code {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Failed to ping. Error: {str(e)}")

if __name__ == "__main__":
    ping_search_engines()
