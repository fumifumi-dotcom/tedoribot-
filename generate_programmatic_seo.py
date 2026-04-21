#!/usr/bin/env python3
import os
import math

# --- Tax & Insurance Configuration ---
HEALTH_RATE_UNDER_40 = 0.04905
HEALTH_RATE_OVER_40 = 0.05700 # Contains Kaigo Hoken
PENSION_RATE = 0.0915
EMPLOYMENT_RATE = 0.006
PENSION_MAX_MONTHLY = 650_000

BASIC_DEDUCTION_INCOME = 480_000
BASIC_DEDUCTION_RESIDENT = 430_000
SPOUSE_DEDUCTION_INCOME = 380_000
SPOUSE_DEDUCTION_RESIDENT = 330_000
CHILD_DEDUCTION_INCOME = 380_000
CHILD_DEDUCTION_RESIDENT = 330_000

RESIDENT_TAX_RATE = 0.10
RESIDENT_TAX_FIXED = 5_000
RECONSTRUCTION_TAX_RATE = 0.021

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

def calculate_tedori(annual_income, age_bracket="under40", spouse=False, children=0):
    if annual_income <= 0: return {}

    monthly_income = annual_income / 12
    health_rate = HEALTH_RATE_OVER_40 if age_bracket == "over40" else HEALTH_RATE_UNDER_40
    
    health_ins = math.floor(annual_income * health_rate)
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

    # Income tax deductions
    deduction_income = BASIC_DEDUCTION_INCOME + social_insurance
    deduction_resident = BASIC_DEDUCTION_RESIDENT + social_insurance
    
    if spouse:
        deduction_income += SPOUSE_DEDUCTION_INCOME
        deduction_resident += SPOUSE_DEDUCTION_RESIDENT
    
    deduction_income += CHILD_DEDUCTION_INCOME * children
    deduction_resident += CHILD_DEDUCTION_RESIDENT * children

    taxable_income = max(0, income_after - deduction_income)

    income_tax = 0
    for limit, rate, deduction in INCOME_TAX_TABLE:
        if taxable_income <= limit:
            income_tax = math.floor(taxable_income * rate - deduction)
            break
            
    reconstruction_tax = math.floor(income_tax * RECONSTRUCTION_TAX_RATE)
    income_tax += reconstruction_tax

    resident_taxable = max(0, income_after - deduction_resident)
    resident_tax = math.floor(resident_taxable * RESIDENT_TAX_RATE) + RESIDENT_TAX_FIXED

    total_deducted = income_tax + resident_tax + social_insurance
    tedori = max(0, annual_income - total_deducted)
    monthly_tedori = math.floor(tedori / 12)
    tedori_rate = round((tedori / annual_income) * 100, 1)

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

def get_page_info(amount_type, amount_man, age, spouse, children):
    # generate identifier and human readable titles
    annual_income = amount_man * 10000 if amount_type == "年収" else amount_man * 10000 * 12
    slug_type = "annual" if amount_type == "年収" else "monthly"
    slug_spouse = "single" if not spouse else "married"
    slug_child = f"{children}child"
    
    slug = f"case-{slug_type}-{amount_man}m-{age}-{slug_spouse}-{slug_child}"
    
    age_str = "40代以上" if age == "over40" else "20代〜30代"
    spouse_str = "配偶者あり" if spouse else "独身"
    child_str = f"子ども{children}人" if children > 0 else "子なし"
    
    status_str = f"{age_str}・{spouse_str}・{child_str}"
    
    return slug, annual_income, status_str

def generate_programmatic_html(amount_type, amount_man, age, spouse, children):
    slug, annual_income, status_str = get_page_info(amount_type, amount_man, age, spouse, children)
    r = calculate_tedori(annual_income, age, spouse, children)
    
    title = f"{amount_type}{fmt(amount_man)}万円の手取りは？【{status_str}】税金・保険料の徹底解説"
    description = f"{amount_type}{fmt(amount_man)}万円（{status_str}）の手取り額は約{fmt(r['tedori'])}円（月額約{fmt(r['monthly_tedori'])}円）です。所得税、住民税、介護保険等の社会保険料の内訳を詳細に計算・解説します。"
    keywords = f"{amount_type}{amount_man}万,手取り,{status_str.replace('・', ',')},税金"

    highlight_amount = r['tedori'] if amount_type == "年収" else r['monthly_tedori']
    highlight_label = "年間手取り額" if amount_type == "年収" else "月額手取り額"

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta name="keywords" content="{keywords}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:type" content="article">
  <meta name="theme-color" content="#0ea5e9">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-3STMJXD6N3"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-3STMJXD6N3');
  </script>
  <link rel="stylesheet" href="../../css/style.css">
  <style>
    .page-content {{ max-width: 800px; margin: 0 auto; padding: 40px 20px 80px; }}
    .answer-box {{ background: var(--bg-card); border: 1px solid var(--glass-border); border-radius: var(--border-radius-xl); padding: 40px; text-align: center; margin: 32px 0; }}
    .answer-label {{ font-size: 16px; color: var(--text-secondary); margin-bottom: 8px; }}
    .answer-value {{ font-size: 48px; font-weight: 800; background: var(--gradient-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
    .answer-detail {{ margin-top: 12px; color: var(--text-secondary); font-size: 15px; }}
    .detail-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 32px 0; }}
    .detail-card {{ background: var(--bg-card); border: 1px solid var(--glass-border); border-radius: var(--border-radius-lg); padding: 20px; }}
    .detail-card .label {{ font-size: 13px; color: var(--text-muted); margin-bottom: 4px; }}
    .detail-card .value {{ font-size: 22px; font-weight: 700; }}
    .detail-card .percent {{ font-size: 13px; color: var(--text-muted); margin-top: 4px; }}
    .section-title {{ font-size: 22px; font-weight: 700; margin: 40px 0 16px; }}
    .back-link {{ display: inline-flex; align-items: center; gap: 8px; color: var(--accent-green); text-decoration: none; font-weight: 600; font-size: 14px; margin-bottom: 24px; }}
    .status-badge {{ display: inline-block; padding: 4px 12px; background: rgba(14,165,233,0.1); color: var(--accent-blue); border-radius: 20px; font-size: 13px; font-weight: 600; margin-bottom: 16px; }}
    @media (max-width: 600px) {{ .detail-grid {{ grid-template-columns: 1fr; }} .answer-value {{ font-size: 32px; }} }}
  </style>
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <a href="../../index.html" class="logo"><div class="logo-icon">¥</div><div class="logo-text"><span>手取り計算.com</span></div></a>
    </div>
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3012346545678100" crossorigin="anonymous"></script>
  </header>

  <main class="page-content">
    <a href="index.html" class="back-link">← パターン別一覧に戻る</a>
    
    <div class="status-badge">{status_str}のケース</div>
    <h1>{amount_type}{fmt(amount_man)}万円の手取りはいくら？</h1>

    <div class="answer-box">
      <div class="answer-label">{amount_type}{fmt(amount_man)}万円の{highlight_label}</div>
      <div class="answer-value">¥{fmt(highlight_amount)}</div>
      <div class="answer-detail">
        年間手取り <strong>¥{fmt(r['tedori'])}</strong> ｜ 月額 <strong>¥{fmt(r['monthly_tedori'])}</strong><br>
        手取り率 <strong>{r['tedori_rate']}%</strong> (額面年収比)
      </div>
    </div>

    <p style="color: var(--text-secondary); line-height: 1.8;">
      本ページは<strong>「{amount_type}{fmt(amount_man)}万円」「{status_str}」</strong>の方に特化したシミュレーション結果です。<br>
      稼いだ額面の約<strong>{r['tedori_rate']}%</strong>しか手元に残りません。残りの金額は全て税金と社会保険料として国に天引きされます。
    </p>

    <h2 class="section-title">💰 年間天引き額の内訳（{status_str}）</h2>
    <div class="detail-grid">
      <div class="detail-card">
        <div class="label">所得税（復興税込）</div>
        <div class="value" style="color: #3b82f6;">¥{fmt(r['income_tax'])}</div>
        <div class="percent">扶養控除を加味して算出</div>
      </div>
      <div class="detail-card">
        <div class="label">住民税</div>
        <div class="value" style="color: #6366f1;">¥{fmt(r['resident_tax'])}</div>
        <div class="percent">前年の所得に対して課税</div>
      </div>
      <div class="detail-card">
        <div class="label">健康保険料{ '（介護保険含む）' if age == 'over40' else ''}</div>
        <div class="value" style="color: #f59e0b;">¥{fmt(r['health_insurance'])}</div>
        <div class="percent">{'40歳以上は介護保険料が加算' if age == 'over40' else '39歳以下の標準税率'}</div>
      </div>
      <div class="detail-card">
        <div class="label">厚生年金保険料</div>
        <div class="value" style="color: #ef4444;">¥{fmt(r['pension'])}</div>
        <div class="percent">上限額まで月額給与に比例</div>
      </div>
    </div>

    <h2 class="section-title">🚀 さらに手取りを増やすには？</h2>
    <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 24px;">
      {status_str}の方が手元に残るお金（可処分所得）を最大化するためには、「ふるさと納税」で住民税の負担を実質相殺することや、「新NISA」などの非課税制度の活用が必須です。また、これ以上税率が上がる前に適正な年収へジャンプアップ（転職等）することも有効な戦略となります。
    </p>

    <section class="cta-section" style="padding: 20px 0;">
      <div class="cta-grid" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px;">
        <div class="cta-card" style="background: var(--bg-card); border:1px solid var(--glass-border); padding: 24px; border-radius: 16px;">
          <h3>📈 非課税で増やす（新NISA）</h3>
          <p style="color: var(--text-secondary); font-size:14px; margin-bottom:16px;">手取りを投資に回して運用益を非課税化。松井証券なら手数料無料でNISAを始められます。</p>
          <a href="#" id="cta-matsui-nisa-link" class="cta-button orange" style="display:block; text-align:center;">松井証券で無料で始める →</a>
        </div>
        <div class="cta-card" style="background: var(--bg-card); border:1px solid var(--glass-border); padding: 24px; border-radius: 16px;">
          <h3>🧑‍💻 額面を大きく上げる</h3>
          <p style="color: var(--text-secondary); font-size:14px; margin-bottom:16px;">そもそも額面を変えなければ手取りの上限は見えています。今の市場価値を確認しましょう。</p>
          <a href="#" id="cta-career-link" class="cta-button purple" style="display:block; text-align:center;">無料の年代別・年収診断 →</a>
        </div>
      </div>
    </section>
  </main>
  
  <footer class="site-footer">
    <div class="container"><p>© 2026 手取り計算.com</p></div>
  </footer>
  <script src="../../js/affiliate.js"></script>
</body>
</html>"""
    return html, slug

def main():
    import json
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CASES_DIR = os.path.join(BASE_DIR, 'cases')
    os.makedirs(CASES_DIR, exist_ok=True)
    
    amount_monthly = list(range(15, 81)) # 15万〜80万
    amount_annual = list(range(200, 1510, 10)) # 200万〜1500万(10万刻み)
    
    ages = ['under40', 'over40']
    
    # spouses, children
    families = [
        (False, 0), # 独身
        (True, 0),  # 配偶者専業
        (True, 1),  # 配偶者+子1
        (True, 2)   # 配偶者+子2
    ]
    
    all_pages = []
    
    # Monthly Generation
    print("Generating monthly variants...")
    for am in amount_monthly:
        for age in ages:
            for s, c in families:
                html, slug = generate_programmatic_html("月収", am, age, s, c)
                all_pages.append({'slug': slug, 'title': f"月収{am}万円の手取り", 'type': 'monthly'})
                with open(os.path.join(CASES_DIR, f"{slug}.html"), 'w', encoding='utf-8') as f:
                    f.write(html)
                    
    # Annual Generation
    print("Generating annual variants...")
    for am in amount_annual:
        for age in ages:
            for s, c in families:
                html, slug = generate_programmatic_html("年収", am, age, s, c)
                all_pages.append({'slug': slug, 'title': f"年収{am}万円の手取り", 'type': 'annual'})
                with open(os.path.join(CASES_DIR, f"{slug}.html"), 'w', encoding='utf-8') as f:
                    f.write(html)
                    
    print(f"✅ Generated {len(all_pages)} deep long-tail pages in cases/")
    
    # Generate Hub Index Page
    # (チャンクごとに目次を作る)
    print("Generating Hub Index...")
    index_html = """<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>個別シミュレーション事例一覧（プログラマティックSEO）</title>
  <link rel="stylesheet" href="../css/style.css">
  <style>.cases-grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap:12px; } .cases-grid a { display:block; padding: 12px; background:var(--bg-card); border:1px solid var(--glass-border); text-decoration:none; color:var(--text-primary); border-radius:8px;} .cases-grid a:hover { border-color:var(--accent-blue); } </style>
</head>
<body>
  <header class="site-header"><div class="container header-inner"><a href="../index.html" class="logo">手取り計算.com</a></div></header>
  <main class="container" style="padding:40px 20px;">
    <h1>すべての個別ケース（手取り・税金早見表）</h1>
    <p>あなたの年齢・家族構成に完全一致するシミュレーションを選択してください。</p>
    
    <h2 style="margin-top:40px; margin-bottom:20px;">【月収別】手取り額と税金</h2>
    <div class="cases-grid">
"""
    # Simply list every 50th for index brevity if too large? 1700 is slightly big but okay for a sitemap-hub.
    # Actually, grouping by single/married and age is better, but let's just dump them since this is an SEO crawler hub.
    for p in all_pages:
        if p['type'] == 'monthly':
            index_html += f"      <a href=\"{p['slug']}.html\">{p['title']}</a>\n"
            
    index_html += """
    </div>
    <h2 style="margin-top:40px; margin-bottom:20px;">【年収別】手取り額と税金</h2>
    <div class="cases-grid">
"""
    for p in all_pages:
        if p['type'] == 'annual':
            index_html += f"      <a href=\"{p['slug']}.html\">{p['title']}</a>\n"
            
    index_html += """
    </div>
  </main>
</body>
</html>
"""
    with open(os.path.join(CASES_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)

    # XML Sitemap specifically for the cases
    print("Generating sitemap_cases.xml...")
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for p in all_pages:
        sitemap += f"  <url><loc>https://tedori-keisan.com/cases/{p['slug']}.html</loc><priority>0.5</priority></url>\n"
    sitemap += '</urlset>'
    
    with open(os.path.join(BASE_DIR, 'sitemap_cases.xml'), 'w', encoding='utf-8') as f:
        f.write(sitemap)
        
    print(f"✅ sitemap_cases.xml created with {len(all_pages)} entries.")
    
if __name__ == '__main__':
    main()
