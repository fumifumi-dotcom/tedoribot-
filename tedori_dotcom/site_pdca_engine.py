import os
import re
import requests
import json
import subprocess
from datetime import datetime, timedelta

API_TOKEN = os.environ.get("CF_API_TOKEN", "")
ACCOUNT_ID = "90d5062a2063f8319a48d6f48908abe6"
BASE_DIR = "/Users/imamichifumitaka/Downloads/ミカタ_経理/今道_生活を豊かに/money-tools"

def fetch_top_pages():
    url = "https://api.cloudflare.com/client/v4/graphql"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    start_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%dT00:00:00Z")
    query = """
    query {
      viewer {
        accounts(filter: {accountTag: "%s"}) {
          rumPageloadEventsAdaptiveGroups(
            limit: 50,
            filter: {datetime_geq: "%s"}
            orderBy: [count_DESC]
          ) {
            count
            dimensions {
              requestPath
            }
          }
        }
      }
    }
    """ % (ACCOUNT_ID, start_date)

    response = requests.post(url, headers=headers, json={"query": query})
    data = response.json()
    
    try:
        events = data['data']['viewer']['accounts'][0]['rumPageloadEventsAdaptiveGroups']
    except (KeyError, IndexError):
        return []

    top_paths = []
    # 除外リスト: トップページや機能ページ、ディレクトリなど
    exclude_paths = ['/', '/index.html', '/articles/index.html', '/articles/']
    
    for event in events:
        path = event['dimensions']['requestPath']
        if path in exclude_paths or not path.endswith('.html'):
            continue
        top_paths.append((path, event['count']))
        if len(top_paths) >= 3:
            break
            
    return top_paths

def extract_metadata(path):
    local_path = os.path.join(BASE_DIR, path.lstrip('/'))
    if not os.path.exists(local_path):
        return None, None
        
    with open(local_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
    desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE)
    
    title = title_match.group(1).replace(' - 手取り計算.com', '') if title_match else "人気記事"
    desc = desc_match.group(1) if desc_match else "多くのユーザーに読まれている注目の記事です。"
    
    # Descriptionを少し短くする
    if len(desc) > 60:
        desc = desc[:60] + "..."
        
    return title, desc

def update_index_html(top_pages):
    index_path = os.path.join(BASE_DIR, 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    html_blocks = ['<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; max-width: 900px; margin: 0 auto;">']
    
    colors = ['#f43f5e', '#3b82f6', '#10b981'] # Red, Blue, Green
    
    for i, (path, count) in enumerate(top_pages[:3]):
        title, desc = extract_metadata(path)
        if not title:
            continue
            
        color = colors[i % len(colors)]
        rank = i + 1
        
        # 相対パスへの変換（index.htmlから見たパス）
        href = path.lstrip('/')
        
        card = f"""
        <a href="{href}" style="display: block; border: 1px solid var(--glass-border); border-radius: var(--border-radius-md); overflow: hidden; text-decoration: none; background: var(--bg-secondary); transition: transform 0.2s; position: relative;" onmouseover="this.style.transform='translateY(-4px)';" onmouseout="this.style.transform='none';">
          <div style="position: absolute; top: 0; right: 0; background: {color}; color: white; font-weight: bold; padding: 4px 12px; border-bottom-left-radius: 8px; font-size: 14px;">NO.{rank}</div>
          <div style="background: {color}20; height: 8px;"></div>
          <div style="padding: 24px;">
            <span style="color: {color}; font-size: 12px; font-weight: bold;">🔥 急上昇ランキング</span>
            <h3 style="color: var(--text-primary); margin-top: 12px; margin-bottom: 8px; font-size: 18px;">{title}</h3>
            <p style="color: var(--text-secondary); font-size: 14px; line-height: 1.6;">{desc}</p>
          </div>
        </a>"""
        html_blocks.append(card)
        
    html_blocks.append('</div>')
    
    new_block = "\n".join(html_blocks)
    
    # プレースホルダーの置き換え
    pattern = r'<!-- PDCA_TRENDING_START -->.*?<!-- PDCA_TRENDING_END -->'
    new_content = re.sub(pattern, f'<!-- PDCA_TRENDING_START -->\n{new_block}\n      <!-- PDCA_TRENDING_END -->', content, flags=re.DOTALL)
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"✅ index.html updated with top {len(top_pages)} trending pages!")

def deploy_to_cloudflare():
    print("🚀 Deploying updated site to Cloudflare Pages...")
    env = os.environ.copy()
    env['PATH'] = f"/Users/imamichifumitaka/Downloads/ミカタ_経理/今道_生活を豊かに/node-v20.18.3-darwin-arm64/bin:{env.get('PATH', '')}"
    
    result = subprocess.run(
        ["npx", "wrangler", "pages", "deploy", ".", "--project-name=tedori-keisan", "--commit-dirty=true"],
        cwd=BASE_DIR,
        env=env,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Deploy successful!")
    else:
        print("❌ Deploy failed:")
        print(result.stderr)

if __name__ == "__main__":
    print(f"--- [Site PDCA Engine] Started at {datetime.now()} ---")
    top_pages = fetch_top_pages()
    if top_pages:
        for p, c in top_pages:
            print(f"- {p} ({c} views)")
        update_index_html(top_pages)
        deploy_to_cloudflare()
    else:
        print("⚠️ No top pages found to update.")
    print("--- [Site PDCA Engine] Finished ---")
