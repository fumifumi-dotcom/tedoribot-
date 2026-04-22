#!/usr/bin/env python3
"""
Cloudflare Pages カスタムドメイン設定スクリプト
tedori-keisan.com を Cloudflare Pages に紐付ける
"""
import json
import subprocess
import sys

# Wrangler の OAuth トークンを取得
import re
config_paths = [
    "/Users/imamichifumitaka/.wrangler/config/default.toml",
    "/Users/imamichifumitaka/Library/Preferences/.wrangler/config/default.toml",
]
token = None
for p in config_paths:
    try:
        with open(p, "r") as f:
            content = f.read()
            m = re.search(r'oauth_token\s*=\s*"([^"]+)"', content)
            if m:
                token = m.group(1)
                break
    except (FileNotFoundError, Exception):
        continue

if not token:
    print("❌ Wrangler の OAuth トークンが見つかりません")
    sys.exit(1)

print(f"✅ OAuth トークン取得完了")

ACCOUNT_ID = "90d5062a2063f8319a48d6f48908abe6"
PROJECT_NAME = "tedori-keisan"
DOMAIN = "tedori-keisan.com"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

def api_call(method, url, data=None):
    """Cloudflare API を curl で呼び出す"""
    cmd = ["curl", "-s", "-X", method, url]
    for k, v in headers.items():
        cmd.extend(["-H", f"{k}: {v}"])
    if data:
        cmd.extend(["-d", json.dumps(data)])
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"Response: {result.stdout[:500]}")
        return None

# Step 1: ドメインをCloudflareに追加（ゾーンとして）
print(f"\n📡 Step 1: {DOMAIN} をCloudflareに追加中...")
resp = api_call("POST", f"https://api.cloudflare.com/client/v4/zones", {
    "name": DOMAIN,
    "account": {"id": ACCOUNT_ID},
    "type": "full",
})

if resp and resp.get("success"):
    zone = resp["result"]
    zone_id = zone["id"]
    nameservers = zone.get("name_servers", [])
    print(f"✅ ゾーン作成成功！ Zone ID: {zone_id}")
    print(f"📋 ネームサーバー:")
    for ns in nameservers:
        print(f"   • {ns}")
elif resp and not resp.get("success"):
    errors = resp.get("errors", [])
    # すでに存在する場合
    if any("already exists" in str(e) for e in errors):
        print("ℹ️  ゾーンは既に存在します。既存のゾーンを使用します。")
        # 既存ゾーンを取得
        resp2 = api_call("GET", f"https://api.cloudflare.com/client/v4/zones?name={DOMAIN}&account.id={ACCOUNT_ID}")
        if resp2 and resp2.get("result"):
            zone = resp2["result"][0]
            zone_id = zone["id"]
            nameservers = zone.get("name_servers", [])
            print(f"✅ Zone ID: {zone_id}")
            print(f"📋 ネームサーバー:")
            for ns in nameservers:
                print(f"   • {ns}")
        else:
            print(f"❌ ゾーン取得失敗: {resp2}")
            sys.exit(1)
    else:
        print(f"❌ ゾーン作成失敗: {errors}")
        sys.exit(1)

# Step 2: Pages プロジェクトにカスタムドメインを追加
print(f"\n🔗 Step 2: カスタムドメイン {DOMAIN} を Pages に紐付け中...")
resp = api_call("POST", 
    f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/pages/projects/{PROJECT_NAME}/domains",
    {"name": DOMAIN}
)

if resp and resp.get("success"):
    print(f"✅ カスタムドメイン設定成功！")
elif resp:
    errors = resp.get("errors", [])
    if any("already" in str(e).lower() for e in errors):
        print("ℹ️  カスタムドメインは既に設定済みです。")
    else:
        print(f"⚠️  結果: {json.dumps(resp, indent=2, ensure_ascii=False)}")

# www サブドメインも追加
print(f"\n🔗 Step 3: www.{DOMAIN} も追加中...")
resp = api_call("POST",
    f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/pages/projects/{PROJECT_NAME}/domains",
    {"name": f"www.{DOMAIN}"}
)
if resp and resp.get("success"):
    print(f"✅ www.{DOMAIN} 設定成功！")
elif resp:
    errors = resp.get("errors", [])
    if any("already" in str(e).lower() for e in errors):
        print("ℹ️  www は既に設定済みです。")
    else:
        print(f"⚠️  結果: {json.dumps(resp, indent=2, ensure_ascii=False)}")

print("\n" + "="*60)
print("🎉 設定完了！")
print("="*60)
print(f"\n以下のネームサーバーをお名前.comに設定してください:")
for ns in nameservers:
    print(f"  ▸ {ns}")
print(f"\nネームサーバー変更後、{DOMAIN} でサイトにアクセスできるようになります。")
print("（DNS反映に最大24時間かかる場合がありますが、通常は数分〜1時間で完了します）")
