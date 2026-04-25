#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import math
import random
import subprocess
from datetime import datetime

# ---------------------------------------------------------
# 設定
# ---------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES_DIR = os.path.join(BASE_DIR, "pages")
SITEMAP_PATH = os.path.join(BASE_DIR, "sitemap.xml")
BATCH_SIZE = 5  # 1回の実行で生成するページ数

os.makedirs(PAGES_DIR, exist_ok=True)

AFF_C = 'https://px.a8.net/svt/ejp?a8mat=4B1OTT+6P4KS2+47GS+5YRHE'
AFF_F = 'https://rpx.a8.net/svt/ejp?a8mat=4B1OTR+ACPDGY+2HOM+6C1VM&rakuten=y&a8ejpredirect=http%3A%2F%2Fhb.afl.rakuten.co.jp%2Fhgc%2F0ea62065.34400275.0ea62066.204f04c0%2Fa26041903646_4B1OTR_ACPDGY_2HOM_6C1VM%3Fpc%3Dhttp%253A%252F%252Fevent.rakuten.co.jp%252Ffurusato%252F%26m%3Dhttp%253A%252F%252Fm.rakuten.co.jp%252F'
AFF_N = 'https://px.a8.net/svt/ejp?a8mat=4B1PLP+ACPDGY+3XCC+6AZAQ'
AFF_FP = 'https://px.a8.net/svt/ejp?a8mat=FP_CONSULTATION_DUMMY'

# ---------------------------------------------------------
# 計算ロジック
# ---------------------------------------------------------
SALARY_DED = [(1625000,lambda i:550000),(1800000,lambda i:i*0.4-100000),(3600000,lambda i:i*0.3+80000),(6600000,lambda i:i*0.2+440000),(8500000,lambda i:i*0.1+1100000),(float('inf'),lambda i:1950000)]
TAX_TBL = [(1950000,0.05,0),(3300000,0.10,97500),(6950000,0.20,427500),(9000000,0.23,636000),(18000000,0.33,1536000),(40000000,0.40,2796000),(float('inf'),0.45,4796000)]

def calc(annual, spouse=False, kids=0, age=30):
    if annual <= 0: return {}
    m = annual/12
    hi = math.floor(annual*0.04905)
    if age >= 40: hi += math.floor(annual*0.008)
    pn = math.floor(min(m,650000)*0.0915*12)
    ei = math.floor(annual*0.006)
    si = hi+pn+ei
    sd = 0
    for l,c in SALARY_DED:
        if annual <= l: sd=c(annual); break
    ia = max(0, annual-sd)
    sp_ded_i = 380000 if spouse else 0
    sp_ded_r = 330000 if spouse else 0
    dep_ded_i = kids * 380000
    dep_ded_r = kids * 330000
    ti = max(0, ia-480000-si-sp_ded_i-dep_ded_i)
    it = 0
    for l,r,d in TAX_TBL:
        if ti <= l: it=math.floor(ti*r-d); break
    it += math.floor(it*0.021)
    rt_taxable = max(0, ia-430000-si-sp_ded_r-dep_ded_r)
    rt = math.floor(rt_taxable*0.10)+5000
    td = it+rt+si
    tedori = max(0, annual-td)
    return {'tedori':tedori,'monthly':math.floor(tedori/12),'rate':round(tedori/annual*100,1),
            'it':it,'rt':rt,'si':si,'hi':hi,'pn':pn,'ei':ei}

def fmt(v): return f"{int(v):,}"

# ---------------------------------------------------------
# テンプレート生成
# ---------------------------------------------------------
def page_html(title, desc, canonical, h1, answer_label, r, annual, body_extra=""):
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<link rel="stylesheet" href="../css/style.css">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-3STMJXD6N3"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-3STMJXD6N3');</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3012346545678100" crossorigin="anonymous"></script>
<style>
.page-content{{max-width:800px;margin:0 auto;padding:40px 20px 80px}}
.answer-box{{background:var(--bg-card);border:1px solid var(--glass-border);border-radius:var(--border-radius-xl);padding:40px;text-align:center;margin:32px 0}}
.answer-value{{font-size:48px;font-weight:800;background:var(--gradient-primary);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
.answer-detail{{margin-top:12px;color:var(--text-secondary);font-size:15px}}
.answer-detail strong{{color:var(--text-primary)}}
.detail-grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:32px 0}}
.detail-card{{background:var(--bg-card);border:1px solid var(--glass-border);border-radius:var(--border-radius-lg);padding:20px}}
.detail-card .label{{font-size:13px;color:var(--text-muted);margin-bottom:4px}}
.detail-card .value{{font-size:22px;font-weight:700}}
.section-title{{font-size:22px;font-weight:700;margin:40px 0 16px}}
.explanation{{color:var(--text-secondary);line-height:1.9;font-size:15px;margin-bottom:24px}}
.back-link{{display:inline-flex;align-items:center;gap:8px;color:var(--accent-green);text-decoration:none;font-weight:600;font-size:14px;margin-bottom:24px}}
@media(max-width:600px){{.detail-grid{{grid-template-columns:1fr}}.answer-value{{font-size:32px}}}}
</style>
</head>
<body>
<header class="site-header"><div class="container header-inner">
<a href="../index.html" class="logo"><div class="logo-icon">¥</div><div class="logo-text"><span>手取り計算.com</span></div></a>
<nav class="header-nav" style="display:flex;gap:20px;align-items:center;">
<a href="../index.html" style="color:var(--text-secondary);font-size:13px;text-decoration:none;font-weight:500;">手取り計算</a>
<a href="../furusato.html" style="color:var(--text-secondary);font-size:13px;text-decoration:none;font-weight:500;">ふるさと納税</a>
<a href="../diagnosis.html" style="color:#8b5cf6;font-size:13px;text-decoration:none;font-weight:700;">🔮 人生診断</a>
</nav></div></header>
<main class="page-content">
<a href="../index.html" class="back-link">← 計算ツールに戻る</a>
<h1>{h1}</h1>
<div class="answer-box">
<div style="font-size:16px;color:var(--text-secondary);margin-bottom:8px;">{answer_label}</div>
<div class="answer-value">¥{fmt(r['tedori'])}</div>
<div class="answer-detail">月額 <strong>¥{fmt(r['monthly'])}</strong> ｜ 手取り率 <strong>{r['rate']}%</strong></div>
</div>
<h2 class="section-title">💰 内訳</h2>
<div class="detail-grid">
<div class="detail-card"><div class="label">所得税</div><div class="value" style="color:#3b82f6">¥{fmt(r['it'])}</div></div>
<div class="detail-card"><div class="label">住民税</div><div class="value" style="color:#6366f1">¥{fmt(r['rt'])}</div></div>
<div class="detail-card"><div class="label">健康保険</div><div class="value" style="color:#f59e0b">¥{fmt(r['hi'])}</div></div>
<div class="detail-card"><div class="label">厚生年金</div><div class="value" style="color:#ef4444">¥{fmt(r['pn'])}</div></div>
</div>
{body_extra}
<div style="background:#111827;border:2px solid #ef4444;border-radius:12px;padding:24px;text-align:center;margin:32px 0;box-shadow:0 10px 25px -5px rgba(239,68,68,0.3);position:relative;overflow:hidden;">
<div style="position:absolute;top:0;left:0;right:0;background:#ef4444;color:white;font-weight:900;font-size:14px;padding:4px 0;letter-spacing:2px;">⚠️ 絶望メーター ⚠️</div>
<h3 style="font-size:20px;font-weight:800;color:white;margin:28px 0 12px;">国に搾取されている年間金額</h3>
<div style="font-size:32px;font-weight:900;color:white;font-family:monospace;margin-bottom:8px;">¥{fmt(r['it']+r['rt']+r['si'])}</div>
<p style="color:#d1d5db;font-size:14px;line-height:1.6;margin-bottom:20px;">毎年これだけのお金があなたの給料から強制的に奪われています。<br>このまま放置すると、老後破産の確率は極めて高くなります。</p>
<div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:8px;padding:16px;margin-bottom:20px;text-align:left;">
<p style="margin:0 0 8px;font-size:13px;color:#f87171;font-weight:bold;">🚨 【警告】絶望的な状況を「無料」で回避する唯一の手段</p>
<p style="margin:0;font-size:13px;color:#d1d5db;">プロのFPに無料で家計相談し、保険や固定費のムダを排除してもらってください。</p>
</div>
<a href="{AFF_FP}" style="display:block;width:100%;background:linear-gradient(135deg,#10b981 0%,#059669 100%);color:white;text-decoration:none;padding:16px;border-radius:12px;font-weight:900;font-size:16px;box-sizing:border-box;">👨‍🏫 プロのFPに無料で家計改善を依頼する</a>
<a href="../diagnosis.html" style="display:block;margin-top:16px;color:#9ca3af;font-size:13px;text-decoration:underline;">自分の「生涯賃金のショート額」を診断する（無料）</a>
</div>
</main>
<footer class="site-footer"><div class="container"><p>© 2026 手取り計算.com</p></div></footer>
</body></html>"""

# ---------------------------------------------------------
# パターン生成
# ---------------------------------------------------------
def get_all_possible_patterns():
    patterns = []
    
    # 1. 時給パターン (時給900円〜2500円、週40時間想定)
    for hourly in range(900, 3001, 100):
        annual = hourly * 8 * 20 * 12
        patterns.append({
            "type": "hourly",
            "val": hourly,
            "annual": annual,
            "slug": f"jikyu-{hourly}",
            "title": f"時給{hourly}円の手取り額はいくら？月収・年収換算【2026年最新】",
            "desc": f"時給{hourly}円（フルタイム）の手取り額や所得税、社会保険料を計算。月収や年収換算も。",
            "h1": f"時給{hourly}円（フルタイム）の手取り額",
            "label": f"時給{hourly}円（年収約{fmt(annual/10000)}万円）の手取り"
        })
        
    # 2. 日給パターン (日給8000円〜25000円、月20日想定)
    for daily in range(8000, 26000, 1000):
        annual = daily * 20 * 12
        patterns.append({
            "type": "daily",
            "val": daily,
            "annual": annual,
            "slug": f"nikkyu-{daily}",
            "title": f"日給{daily}円の手取り額はいくら？月収・年収換算【2026年最新】",
            "desc": f"日給{daily}円で20日働いた場合の手取り額や各種税金を計算。月収・年収換算も。",
            "h1": f"日給{daily}円の手取り額",
            "label": f"日給{daily}円（年収約{fmt(annual/10000)}万円）の手取り"
        })

    # 3. ボーナス有無パターン (月収20万〜60万、ボーナス2ヶ月/なし等)
    for monthly_k in range(20, 61, 5):
        monthly = monthly_k * 10000
        # ボーナスなし
        patterns.append({
            "type": "bonus",
            "annual": monthly * 12,
            "slug": f"gesshu-{monthly_k}-nobonus",
            "title": f"月収{monthly_k}万（ボーナスなし）の手取り額と税金【2026年最新】",
            "desc": f"月収{monthly_k}万円でボーナスがない場合の年収と手取り額、引かれる税金・保険料を計算。",
            "h1": f"月収{monthly_k}万（ボーナスなし）の手取り額",
            "label": f"月収{monthly_k}万（ボーナスなし・年収{fmt(monthly*12/10000)}万円）の手取り"
        })
        # ボーナス2ヶ月分
        patterns.append({
            "type": "bonus",
            "annual": monthly * 14,
            "slug": f"gesshu-{monthly_k}-bonus2m",
            "title": f"月収{monthly_k}万（ボーナス2ヶ月分）の手取り額と税金【2026年最新】",
            "desc": f"月収{monthly_k}万円で年間ボーナス2ヶ月分がある場合の年収と手取り額、各種税金を計算。",
            "h1": f"月収{monthly_k}万（ボーナス2ヶ月分）の手取り額",
            "label": f"月収{monthly_k}万（ボーナス2ヶ月分・年収{fmt(monthly*14/10000)}万円）の手取り"
        })

    return patterns

def main():
    existing_files = os.listdir(PAGES_DIR)
    existing_slugs = [f.replace('.html', '') for f in existing_files if f.endswith('.html')]

    all_patterns = get_all_possible_patterns()
    # シャッフルしてランダム性を出す
    random.shuffle(all_patterns)

    generated_count = 0
    generated_slugs = []

    for pat in all_patterns:
        if generated_count >= BATCH_SIZE:
            break
        if pat["slug"] in existing_slugs:
            continue

        annual = pat["annual"]
        r = calc(annual)
        
        # エキストラコンテンツの生成
        extra = ""
        if pat["type"] == "hourly":
            extra = f"""<h2 class="section-title">🕒 勤務条件の前提</h2>
<p class="explanation">時給{pat["val"]}円で、1日8時間、月20日（週5日）フルタイムで働いた場合を想定して計算しています。<br>・月収換算：約{fmt(pat["val"]*8*20)}円<br>・年収換算：約{fmt(annual)}円</p>"""
        elif pat["type"] == "daily":
            extra = f"""<h2 class="section-title">📅 勤務条件の前提</h2>
<p class="explanation">日給{pat["val"]}円で、月20日稼働した場合を想定して計算しています。<br>・月収換算：約{fmt(pat["val"]*20)}円<br>・年収換算：約{fmt(annual)}円</p>"""
        elif pat["type"] == "bonus":
            extra = f"""<h2 class="section-title">💼 年収とボーナスの関係</h2>
<p class="explanation">毎月の基本給とボーナスを合わせた「総支給額（年収）」に対して税金や社会保険料がかかるため、同じ月収でもボーナスの有無で年間の手取りは大きく変わります。このページでは年収{fmt(annual)}円として計算しています。</p>"""

        html = page_html(pat["title"], pat["desc"], f"https://tedori-keisan.com/pages/{pat['slug']}.html", pat["h1"], pat["label"], r, annual, extra)
        
        file_path = os.path.join(PAGES_DIR, f"{pat['slug']}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        generated_slugs.append(pat["slug"])
        generated_count += 1

    if generated_count == 0:
        print("No new patterns to generate.")
        return

    print(f"Generated {generated_count} pages: {', '.join(generated_slugs)}")

    # Sitemap更新
    update_sitemap()
    
    # Gitコミット＆プッシュ
    git_commit_and_push(f"{generated_count} programmatic pages")


def update_sitemap():
    print("Updating sitemap.xml...")
    with open(SITEMAP_PATH, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for p in ['','furusato.html','compound.html','lifetime_tax.html','retirement.html','salary-list.html','diagnosis.html']:
            pr = '1.0' if p in ['','furusato.html','diagnosis.html'] else '0.9'
            f.write(f'  <url><loc>https://tedori-keisan.com/{p}</loc><priority>{pr}</priority></url>\n')
        
        if os.path.exists(PAGES_DIR):
            for fn in sorted(os.listdir(PAGES_DIR)):
                if fn.endswith('.html'):
                    f.write(f'  <url><loc>https://tedori-keisan.com/pages/{fn}</loc><priority>0.7</priority></url>\n')
        
        articles_dir = os.path.join(BASE_DIR, 'articles')
        if os.path.exists(articles_dir):
            for fn in sorted(os.listdir(articles_dir)):
                if fn.endswith('.html'):
                    f.write(f'  <url><loc>https://tedori-keisan.com/articles/{fn}</loc><priority>0.8</priority></url>\n')
                    
        f.write('</urlset>\n')

def git_commit_and_push(msg):
    print("Deploying to GitHub / Cloudflare Pages...")
    try:
        subprocess.run(["git", "-C", BASE_DIR, "add", "pages/", "sitemap.xml"], check=True)
        subprocess.run(["git", "-C", BASE_DIR, "commit", "-m", f"auto-content: add {msg}"], check=True)
        subprocess.run(["git", "-C", BASE_DIR, "push", "origin", "main"], check=True)
        print("✅ Successfully deployed!")
    except subprocess.CalledProcessError as e:
        print(f"Git execution failed: {e}")

if __name__ == "__main__":
    main()
