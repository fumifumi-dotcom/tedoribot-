#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
月収ベース＋家族構成ベースのSEOページ生成
"""
import os, math

# 計算ロジック
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
    # 配偶者控除（所得税38万、住民税33万）
    sp_ded_i = 380000 if spouse else 0
    sp_ded_r = 330000 if spouse else 0
    # 扶養控除（16歳以上の子のみ。ここでは簡易的に1人38万）
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

AFF_C = 'https://px.a8.net/svt/ejp?a8mat=4B1OTT+6P4KS2+47GS+5YRHE'
AFF_F = 'https://rpx.a8.net/svt/ejp?a8mat=4B1OTR+ACPDGY+2HOM+6C1VM&rakuten=y&a8ejpredirect=http%3A%2F%2Fhb.afl.rakuten.co.jp%2Fhgc%2F0ea62065.34400275.0ea62066.204f04c0%2Fa26041903646_4B1OTR_ACPDGY_2HOM_6C1VM%3Fpc%3Dhttp%253A%252F%252Fevent.rakuten.co.jp%252Ffurusato%252F%26m%3Dhttp%253A%252F%252Fm.rakuten.co.jp%252F'
AFF_N = 'https://px.a8.net/svt/ejp?a8mat=4B1PLP+ACPDGY+3XCC+6AZAQ'

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
<section class="cta-section" style="padding:20px 0 40px;"><div class="cta-grid">
<div class="cta-card"><div class="cta-icon">🚀</div><h3>年収を上げる</h3><p>無料で市場価値を診断</p><a href="{AFF_C}" class="cta-button green" target="_blank" rel="noopener sponsored">年収診断 →</a></div>
<div class="cta-card"><div class="cta-icon">🏡</div><h3>ふるさと納税</h3><p>実質2,000円で返礼品</p><a href="{AFF_F}" class="cta-button purple" target="_blank" rel="noopener sponsored">返礼品を探す →</a></div>
<div class="cta-card"><div class="cta-icon">📈</div><h3>NISA</h3><p>非課税で資産運用</p><a href="{AFF_N}" class="cta-button orange" target="_blank" rel="noopener sponsored">口座開設 →</a></div>
</div></section>
<div style="background:linear-gradient(135deg,rgba(139,92,246,0.08),rgba(59,130,246,0.08));border:1px solid rgba(139,92,246,0.2);border-radius:var(--border-radius-lg);padding:28px;text-align:center;margin:32px 0;">
<div style="font-size:32px;margin-bottom:8px;">🔮</div>
<h3 style="font-size:18px;font-weight:700;margin-bottom:8px;">この手取りで人生は満足？</h3>
<a href="../diagnosis.html" style="display:inline-flex;align-items:center;background:linear-gradient(135deg,#8b5cf6,#6366f1);color:#fff;padding:12px 28px;border-radius:9999px;font-weight:700;font-size:15px;text-decoration:none;">無料で診断する →</a>
</div>
</main>
<footer class="site-footer"><div class="container"><p>© 2026 手取り計算.com</p></div></footer>
</body></html>"""

def main():
    base = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(base, 'pages')
    os.makedirs(out, exist_ok=True)
    count = 0

    # ===== 月収ベースページ =====
    for geshu in range(15, 101, 5):  # 月収15万〜100万（5万刻み）
        annual = geshu * 12 * 10000
        r = calc(annual)
        slug = f"gesshu-{geshu}"
        # 近い月収の比較テーブル
        comp = ""
        for d in [-10, -5, 5, 10]:
            g2 = geshu + d
            if 10 <= g2 <= 150 and g2 != geshu:
                r2 = calc(g2*12*10000)
                comp += f'<tr><td><a href="gesshu-{g2}.html">月収{g2}万円</a></td><td>¥{fmt(r2["tedori"])}</td><td>¥{fmt(r2["monthly"])}</td></tr>\n'
        extra = f"""<h2 class="section-title">📊 近い月収との比較</h2>
<table style="width:100%;border-collapse:collapse;margin:24px 0">
<thead><tr><th style="background:var(--bg-tertiary);padding:12px;text-align:left;font-size:13px">月収</th><th style="background:var(--bg-tertiary);padding:12px;text-align:left;font-size:13px">年間手取り</th><th style="background:var(--bg-tertiary);padding:12px;text-align:left;font-size:13px">月額手取り</th></tr></thead>
<tbody><tr style="background:rgba(16,185,129,0.08)"><td><strong>月収{geshu}万円</strong></td><td><strong>¥{fmt(r['tedori'])}</strong></td><td><strong>¥{fmt(r['monthly'])}</strong></td></tr>
{comp}</tbody></table>
<p class="explanation">月収{geshu}万円は年収に換算すると<strong>{fmt(geshu*12)}万円</strong>です。ボーナスがある場合は実際の年収はこれより高くなるため、手取りも変わります。<a href="nenshu-{geshu*12}.html" style="color:var(--accent-green)">年収{geshu*12}万円の手取りはこちら</a></p>"""
        html = page_html(
            f"月収{geshu}万円の手取りは？【2026年最新】",
            f"月収{geshu}万円の手取りは月額約{fmt(r['monthly'])}円。所得税・住民税・社会保険料の内訳を2026年最新税率で計算。",
            f"https://tedori-keisan.com/pages/{slug}.html",
            f"月収{geshu}万円の手取りはいくら？",
            f"月収{geshu}万円（年収{geshu*12}万円）の手取り",
            r, annual, extra)
        with open(os.path.join(out, f"{slug}.html"), 'w', encoding='utf-8') as f:
            f.write(html)
        count += 1

    # ===== 家族構成別ページ =====
    family_patterns = [
        ("spouse", True, 0, "配偶者あり（扶養内）"),
        ("kids1", False, 1, "子供1人（16歳以上）"),
        ("kids2", False, 2, "子供2人（16歳以上）"),
        ("family3", True, 1, "配偶者＋子供1人"),
        ("family4", True, 2, "配偶者＋子供2人"),
    ]
    incomes = list(range(300, 810, 50)) + [250, 900, 1000, 1200]
    incomes = sorted(set(incomes))

    for nenshu in incomes:
        annual = nenshu * 10000
        for key, sp, kids, label in family_patterns:
            r = calc(annual, spouse=sp, kids=kids)
            r_single = calc(annual)
            diff = r['tedori'] - r_single['tedori']
            slug = f"nenshu-{nenshu}-{key}"
            extra = f"""<h2 class="section-title">💡 独身との手取り差</h2>
<p class="explanation">{label}の場合、独身と比べて年間の手取りが<strong style="color:var(--accent-green)">約{fmt(abs(diff))}円{"多く" if diff > 0 else "少なく"}</strong>なります。{"配偶者控除や扶養控除が適用されるため、税金が軽減されます。" if diff > 0 else ""}</p>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:24px 0">
<div class="detail-card"><div class="label">独身の場合</div><div class="value">¥{fmt(r_single['tedori'])}</div></div>
<div class="detail-card"><div class="label">{label}の場合</div><div class="value" style="color:var(--accent-green)">¥{fmt(r['tedori'])}</div></div>
</div>"""
            html = page_html(
                f"年収{nenshu}万円・{label}の手取り額【2026年最新】",
                f"年収{nenshu}万円で{label}の手取りは約{fmt(r['tedori'])}円。配偶者控除・扶養控除適用後の手取りを2026年税率で計算。",
                f"https://tedori-keisan.com/pages/{slug}.html",
                f"年収{nenshu}万円・{label}の手取り",
                f"年収{nenshu}万円・{label}の年間手取り",
                r, annual, extra)
            with open(os.path.join(out, f"{slug}.html"), 'w', encoding='utf-8') as f:
                f.write(html)
            count += 1

    print(f"✅ {count}ページを追加生成しました。")

    # sitemap再生成
    sitemap_path = os.path.join(base, 'sitemap.xml')
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for p in ['','furusato.html','compound.html','lifetime_tax.html','retirement.html','salary-list.html','diagnosis.html']:
            pr = '1.0' if p in ['','furusato.html','diagnosis.html'] else '0.9'
            f.write(f'  <url><loc>https://tedori-keisan.com/{p}</loc><priority>{pr}</priority></url>\n')
        for fn in sorted(os.listdir(out)):
            if fn.endswith('.html'):
                f.write(f'  <url><loc>https://tedori-keisan.com/pages/{fn}</loc><priority>0.7</priority></url>\n')
        articles_dir = os.path.join(base, 'articles')
        if os.path.exists(articles_dir):
            for fn in sorted(os.listdir(articles_dir)):
                if fn.endswith('.html'):
                    f.write(f'  <url><loc>https://tedori-keisan.com/articles/{fn}</loc><priority>0.8</priority></url>\n')
        f.write('</urlset>\n')
    print("✅ sitemap.xml を更新しました。")

if __name__ == '__main__':
    main()
