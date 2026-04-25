#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ロングテールSEOページ拡張生成スクリプト
年収×年齢のパターンで大量のページを自動生成する

使い方: python3 generate_longtail.py
"""

import os
import math

# ============================================================
# 税率計算ロジック（generate_pages.pyと同一）
# ============================================================
SALARY_DEDUCTION_TABLE = [
    (1_625_000, lambda income: 550_000),
    (1_800_000, lambda income: income * 0.4 - 100_000),
    (3_600_000, lambda income: income * 0.3 + 80_000),
    (6_600_000, lambda income: income * 0.2 + 440_000),
    (8_500_000, lambda income: income * 0.1 + 1_100_000),
    (float('inf'), lambda income: 1_950_000),
]

INCOME_TAX_TABLE = [
    (1_950_000, 0.05, 0),
    (3_300_000, 0.10, 97_500),
    (6_950_000, 0.20, 427_500),
    (9_000_000, 0.23, 636_000),
    (18_000_000, 0.33, 1_536_000),
    (40_000_000, 0.40, 2_796_000),
    (float('inf'), 0.45, 4_796_000),
]

HEALTH_RATE = 0.04905
PENSION_RATE = 0.0915
EMPLOYMENT_RATE = 0.006
PENSION_MAX_MONTHLY = 650_000
BASIC_DEDUCTION_INCOME = 480_000
BASIC_DEDUCTION_RESIDENT = 430_000
RESIDENT_TAX_RATE = 0.10
RESIDENT_TAX_FIXED = 5_000
RECONSTRUCTION_TAX_RATE = 0.021

# 介護保険料率（40歳以上）
KAIGO_RATE = 0.008

def calculate_tedori(annual_income, age=30):
    if annual_income <= 0:
        return {}
    monthly_income = annual_income / 12
    health_ins = math.floor(annual_income * HEALTH_RATE)
    if age >= 40:
        health_ins += math.floor(annual_income * KAIGO_RATE)
    pension_base = min(monthly_income, PENSION_MAX_MONTHLY)
    pension = math.floor(pension_base * PENSION_RATE * 12)
    employment_ins = math.floor(annual_income * EMPLOYMENT_RATE)
    social_insurance = health_ins + pension + employment_ins

    salary_deduction = 0
    for limit, calc in SALARY_DEDUCTION_TABLE:
        if annual_income <= limit:
            salary_deduction = calc(annual_income)
            break
    income_after = max(0, annual_income - salary_deduction)
    taxable_income = max(0, income_after - BASIC_DEDUCTION_INCOME - social_insurance)
    income_tax = 0
    for limit, rate, deduction in INCOME_TAX_TABLE:
        if taxable_income <= limit:
            income_tax = math.floor(taxable_income * rate - deduction)
            break
    income_tax += math.floor(income_tax * RECONSTRUCTION_TAX_RATE)
    resident_taxable = max(0, income_after - BASIC_DEDUCTION_RESIDENT - social_insurance)
    resident_tax = math.floor(resident_taxable * RESIDENT_TAX_RATE) + RESIDENT_TAX_FIXED
    total_deducted = income_tax + resident_tax + social_insurance
    tedori = max(0, annual_income - total_deducted)
    monthly_tedori = math.floor(tedori / 12)
    tedori_rate = round(tedori / annual_income * 100, 1)

    return {
        'annual_income': annual_income,
        'tedori': tedori,
        'monthly_tedori': monthly_tedori,
        'income_tax': income_tax,
        'resident_tax': resident_tax,
        'social_insurance': social_insurance,
        'health_insurance': health_ins,
        'pension': pension,
        'employment_insurance': employment_ins,
        'tedori_rate': tedori_rate,
    }

def fmt(v): return f"{int(v):,}"

# アフィリエイトリンク（A8提携済み）
AFF_CAREER = 'https://px.a8.net/svt/ejp?a8mat=4B1OTT+6P4KS2+47GS+5YRHE'
AFF_FURUSATO = 'https://rpx.a8.net/svt/ejp?a8mat=4B1OTR+ACPDGY+2HOM+6C1VM&rakuten=y&a8ejpredirect=http%3A%2F%2Fhb.afl.rakuten.co.jp%2Fhgc%2F0ea62065.34400275.0ea62066.204f04c0%2Fa26041903646_4B1OTR_ACPDGY_2HOM_6C1VM%3Fpc%3Dhttp%253A%252F%252Fevent.rakuten.co.jp%252Ffurusato%252F%26m%3Dhttp%253A%252F%252Fm.rakuten.co.jp%252F'
AFF_NISA = 'https://px.a8.net/svt/ejp?a8mat=4B1PLP+ACPDGY+3XCC+6AZAQ'

def age_advice(nenshu, age):
    """年齢×年収に応じたアドバイステキスト"""
    if age <= 25:
        return f"20代前半で年収{nenshu}万円は、これからキャリアを築いていく重要な時期です。<strong>スキルアップへの投資</strong>と<strong>少額からの積立投資（NISA）</strong>を今すぐ始めることで、30代以降に大きな差がつきます。"
    elif age <= 30:
        return f"20代後半〜30歳で年収{nenshu}万円の方は、転職市場での価値が最も高い時期。<strong>適正年収の診断</strong>を受けて、自分の市場価値を知っておくことが手取りアップの第一歩です。"
    elif age <= 35:
        return f"30代前半で年収{nenshu}万円の場合、結婚・住宅購入などライフイベントが増える時期。<strong>ふるさと納税</strong>と<strong>iDeCo</strong>で節税を最大化し、実質的な手取りを増やしましょう。"
    elif age <= 40:
        return f"30代後半で年収{nenshu}万円は、キャリアの中盤戦。管理職へのステップアップや専門性の深化で<strong>年収100万円以上のアップ</strong>も現実的です。まずは市場価値を確認しましょう。"
    elif age <= 45:
        return f"40代で年収{nenshu}万円の場合、<strong>介護保険料が加算</strong>されるため手取り率が下がります。ふるさと納税・iDeCoなどの節税対策が特に重要な年代です。"
    elif age <= 50:
        return f"40代後半で年収{nenshu}万円の方は、子どもの教育費がピークを迎える時期。<strong>税金の最適化</strong>と<strong>老後資金の準備</strong>を並行して進めることが重要です。"
    else:
        return f"50代で年収{nenshu}万円の場合、退職金や年金を見据えた<strong>出口戦略</strong>が重要です。NISAでの非課税運用とiDeCoの受取方法の最適化を検討しましょう。"

def generate_age_page(nenshu, age):
    annual = nenshu * 10000
    r = calculate_tedori(annual, age)
    kaigo_text = "（介護保険料込み）" if age >= 40 else ""
    slug = f"nenshu-{nenshu}-age-{age}"

    # 関連ページリンク
    related = ""
    ages = [25, 30, 35, 40, 45, 50]
    for a in ages:
        if a != age:
            ra = calculate_tedori(annual, a)
            related += f'<tr><td><a href="{slug.replace(f"age-{age}", f"age-{a}")}.html">{a}歳</a></td><td>¥{fmt(ra["tedori"])}</td><td>¥{fmt(ra["monthly_tedori"])}</td><td>{ra["tedori_rate"]}%</td></tr>\n'

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>年収{nenshu}万円・{age}歳の手取り額は？【2026年最新】</title>
  <meta name="description" content="年収{nenshu}万円・{age}歳の手取りは約{fmt(r['tedori'])}円（月額約{fmt(r['monthly_tedori'])}円）。{age}歳の税金・社会保険料{kaigo_text}を2026年最新税率で計算。">
  <meta property="og:title" content="年収{nenshu}万円・{age}歳の手取り額【2026年版】">
  <meta property="og:description" content="年収{nenshu}万円・{age}歳の手取りは約{fmt(r['tedori'])}円。">
  <link rel="canonical" href="https://tedori-keisan.com/pages/{slug}.html">
  <link rel="stylesheet" href="../css/style.css">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-3STMJXD6N3"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-3STMJXD6N3');</script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3012346545678100" crossorigin="anonymous"></script>
  <style>
    .page-content {{ max-width: 800px; margin: 0 auto; padding: 40px 20px 80px; }}
    .answer-box {{ background: var(--bg-card); border: 1px solid var(--glass-border); border-radius: var(--border-radius-xl); padding: 40px; text-align: center; margin: 32px 0; }}
    .answer-value {{ font-size: 48px; font-weight: 800; background: var(--gradient-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
    .answer-detail {{ margin-top: 12px; color: var(--text-secondary); font-size: 15px; }}
    .answer-detail strong {{ color: var(--text-primary); }}
    .detail-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 32px 0; }}
    .detail-card {{ background: var(--bg-card); border: 1px solid var(--glass-border); border-radius: var(--border-radius-lg); padding: 20px; }}
    .detail-card .label {{ font-size: 13px; color: var(--text-muted); margin-bottom: 4px; }}
    .detail-card .value {{ font-size: 22px; font-weight: 700; }}
    .detail-card .percent {{ font-size: 13px; color: var(--text-muted); margin-top: 4px; }}
    .compare-table {{ width: 100%; border-collapse: collapse; margin: 24px 0; }}
    .compare-table th {{ background: var(--bg-tertiary); padding: 12px 16px; text-align: left; font-size: 13px; color: var(--text-secondary); font-weight: 600; }}
    .compare-table td {{ padding: 12px 16px; border-bottom: 1px solid var(--glass-border); font-size: 14px; }}
    .compare-table a {{ color: var(--accent-green); text-decoration: none; }}
    .section-title {{ font-size: 22px; font-weight: 700; margin: 40px 0 16px; }}
    .explanation {{ color: var(--text-secondary); line-height: 1.9; font-size: 15px; margin-bottom: 24px; }}
    .back-link {{ display: inline-flex; align-items: center; gap: 8px; color: var(--accent-green); text-decoration: none; font-weight: 600; font-size: 14px; margin-bottom: 24px; }}
    @media (max-width: 600px) {{ .detail-grid {{ grid-template-columns: 1fr; }} .answer-value {{ font-size: 32px; }} }}
  </style>
</head>
<body>
  <header class="site-header"><div class="container header-inner">
    <a href="../index.html" class="logo"><div class="logo-icon">¥</div><div class="logo-text"><span>手取り計算.com</span></div></a>
    <nav class="header-nav" style="display:flex;gap:20px;align-items:center;">
      <a href="../index.html" style="color:var(--text-secondary);font-size:13px;text-decoration:none;font-weight:500;">手取り計算</a>
      <a href="../furusato.html" style="color:var(--text-secondary);font-size:13px;text-decoration:none;font-weight:500;">ふるさと納税</a>
      <a href="../diagnosis.html" style="color:#8b5cf6;font-size:13px;text-decoration:none;font-weight:700;">🔮 人生診断</a>
    </nav>
  </div></header>

  <main class="page-content">
    <a href="../index.html" class="back-link">← 計算ツールに戻る</a>
    <h1>年収{nenshu}万円・{age}歳の手取りはいくら？</h1>

    <div class="answer-box">
      <div style="font-size:16px;color:var(--text-secondary);margin-bottom:8px;">年収{nenshu}万円・{age}歳の年間手取り額</div>
      <div class="answer-value">¥{fmt(r['tedori'])}</div>
      <div class="answer-detail">月額 <strong>¥{fmt(r['monthly_tedori'])}</strong> ｜ 手取り率 <strong>{r['tedori_rate']}%</strong></div>
    </div>

    <p class="explanation">年収{nenshu}万円（額面）・{age}歳の場合、税金・社会保険料{kaigo_text}を差し引いた<strong>年間の手取りは約{fmt(r['tedori'])}円</strong>（月額約{fmt(r['monthly_tedori'])}円）です。額面の約<strong>{r['tedori_rate']}%</strong>が手元に残ります。</p>

    <h2 class="section-title">💰 税金・保険料の内訳</h2>
    <div class="detail-grid">
      <div class="detail-card"><div class="label">所得税（復興税込）</div><div class="value" style="color:#3b82f6;">¥{fmt(r['income_tax'])}</div><div class="percent">年収の{round(r['income_tax']/annual*100,1)}%</div></div>
      <div class="detail-card"><div class="label">住民税</div><div class="value" style="color:#6366f1;">¥{fmt(r['resident_tax'])}</div><div class="percent">年収の{round(r['resident_tax']/annual*100,1)}%</div></div>
      <div class="detail-card"><div class="label">健康保険料{kaigo_text}</div><div class="value" style="color:#f59e0b;">¥{fmt(r['health_insurance'])}</div><div class="percent">年収の{round(r['health_insurance']/annual*100,1)}%</div></div>
      <div class="detail-card"><div class="label">厚生年金保険料</div><div class="value" style="color:#ef4444;">¥{fmt(r['pension'])}</div><div class="percent">年収の{round(r['pension']/annual*100,1)}%</div></div>
    </div>

    <h2 class="section-title">💡 {age}歳・年収{nenshu}万円のあなたへ</h2>
    <p class="explanation">{age_advice(nenshu, age)}</p>

    <section class="cta-section" style="padding:20px 0 40px;">
      <div class="cta-grid">
        <div class="cta-card"><div class="cta-icon">🚀</div><h3>年収を上げる</h3><p>無料の市場価値診断で適正年収を確認</p><a href="{AFF_CAREER}" class="cta-button green" target="_blank" rel="noopener sponsored">年収診断を受ける →</a></div>
        <div class="cta-card"><div class="cta-icon">🏡</div><h3>ふるさと納税</h3><p>実質2,000円で返礼品がもらえます</p><a href="{AFF_FURUSATO}" class="cta-button purple" target="_blank" rel="noopener sponsored">返礼品を探す →</a></div>
        <div class="cta-card"><div class="cta-icon">📈</div><h3>NISA口座開設</h3><p>運用益が非課税。手数料無料</p><a href="{AFF_NISA}" class="cta-button orange" target="_blank" rel="noopener sponsored">口座を開設する →</a></div>
      </div>
    </section>

    <!-- 診断CTA -->
    <div style="background:linear-gradient(135deg,rgba(139,92,246,0.08),rgba(59,130,246,0.08));border:1px solid rgba(139,92,246,0.2);border-radius:var(--border-radius-lg);padding:28px;text-align:center;margin:32px 0;">
      <div style="font-size:32px;margin-bottom:8px;">🔮</div>
      <h3 style="font-size:18px;font-weight:700;margin-bottom:8px;">この手取りで人生は満足？</h3>
      <p style="font-size:14px;color:var(--text-secondary);margin-bottom:16px;">AIが3問で人生満足度を無料診断</p>
      <a href="../diagnosis.html" style="display:inline-flex;align-items:center;background:linear-gradient(135deg,#8b5cf6,#6366f1);color:#fff;padding:12px 28px;border-radius:9999px;font-weight:700;font-size:15px;text-decoration:none;box-shadow:0 8px 24px rgba(139,92,246,0.3);">無料で診断する（60秒）</a>
    </div>

    <h2 class="section-title">📊 年齢別の手取り比較（年収{nenshu}万円）</h2>
    <table class="compare-table">
      <thead><tr><th>年齢</th><th>年間手取り</th><th>月額手取り</th><th>手取り率</th></tr></thead>
      <tbody>
        <tr style="background:rgba(16,185,129,0.08);"><td><strong>{age}歳（あなた）</strong></td><td><strong>¥{fmt(r['tedori'])}</strong></td><td><strong>¥{fmt(r['monthly_tedori'])}</strong></td><td><strong>{r['tedori_rate']}%</strong></td></tr>
        {related}
      </tbody>
    </table>
  </main>

  <footer class="site-footer"><div class="container">
    <div class="footer-links"><a href="../html_sitemap.html">全記事一覧</a><a href="../privacy.html">プライバシーポリシー</a></div>
    <p>© 2026 手取り計算.com</p>
  </div></footer>
</body>
</html>"""


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base, 'pages')
    os.makedirs(output_dir, exist_ok=True)

    # 年収パターン: 200〜1200万を50万刻み + 300〜800万を10万刻み
    incomes = sorted(set(
        list(range(200, 1250, 50)) + list(range(300, 810, 10))
    ))
    ages = [25, 30, 35, 40, 45, 50]

    generated = []
    for nenshu in incomes:
        for age in ages:
            slug = f"nenshu-{nenshu}-age-{age}"
            filepath = os.path.join(output_dir, f"{slug}.html")
            html = generate_age_page(nenshu, age)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            generated.append(slug)

    print(f"✅ {len(generated)}ページを生成しました。")

    # sitemap.xmlを更新
    sitemap_path = os.path.join(base, 'sitemap.xml')
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        # トップページ群
        for page in ['', 'furusato.html', 'compound.html', 'lifetime_tax.html',
                      'retirement.html', 'salary-list.html', 'diagnosis.html']:
            p = '1.0' if page in ['', 'furusato.html', 'diagnosis.html'] else '0.9'
            f.write(f'  <url><loc>https://tedori-keisan.com/{page}</loc><priority>{p}</priority></url>\n')
        # 既存の年収ページ
        existing_pages = os.path.join(base, 'pages')
        for fn in sorted(os.listdir(existing_pages)):
            if fn.endswith('.html'):
                f.write(f'  <url><loc>https://tedori-keisan.com/pages/{fn}</loc><priority>0.7</priority></url>\n')
        # articles
        articles_dir = os.path.join(base, 'articles')
        if os.path.exists(articles_dir):
            for fn in sorted(os.listdir(articles_dir)):
                if fn.endswith('.html'):
                    f.write(f'  <url><loc>https://tedori-keisan.com/articles/{fn}</loc><priority>0.8</priority></url>\n')
        f.write('</urlset>\n')
    print("✅ sitemap.xml を更新しました。")

if __name__ == '__main__':
    main()
