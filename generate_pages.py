#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ロングテールSEOページ自動生成スクリプト
「年収○○万円の手取り」ページを一括生成する

使い方: python3 generate_pages.py
"""

import os
import math

# ============================================================
# 税率計算ロジック（JSと同一のロジックをPythonに移植）
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


def calculate_tedori(annual_income):
    """手取り額を計算する（配偶者なし・扶養0人・39歳以下の標準ケース）"""
    if annual_income <= 0:
        return {}

    # 社会保険料
    monthly_income = annual_income / 12
    health_ins = math.floor(annual_income * HEALTH_RATE)
    pension_base = min(monthly_income, PENSION_MAX_MONTHLY)
    pension = math.floor(pension_base * PENSION_RATE * 12)
    employment_ins = math.floor(annual_income * EMPLOYMENT_RATE)
    social_insurance = health_ins + pension + employment_ins

    # 給与所得控除
    salary_deduction = 0
    for limit, calc in SALARY_DEDUCTION_TABLE:
        if annual_income <= limit:
            salary_deduction = calc(annual_income)
            break

    # 所得金額
    income_after = max(0, annual_income - salary_deduction)

    # 課税所得（所得税用）
    taxable_income = max(0, income_after - BASIC_DEDUCTION_INCOME - social_insurance)

    # 所得税
    income_tax = 0
    for limit, rate, deduction in INCOME_TAX_TABLE:
        if taxable_income <= limit:
            income_tax = math.floor(taxable_income * rate - deduction)
            break
    reconstruction_tax = math.floor(income_tax * RECONSTRUCTION_TAX_RATE)
    income_tax += reconstruction_tax

    # 住民税
    resident_taxable = max(0, income_after - BASIC_DEDUCTION_RESIDENT - social_insurance)
    resident_tax = math.floor(resident_taxable * RESIDENT_TAX_RATE) + RESIDENT_TAX_FIXED

    # 手取り
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


def fmt(value):
    """数値を日本語カンマ区切りでフォーマット"""
    return f"{int(value):,}"


# ============================================================
# ページテンプレート
# ============================================================

def generate_page_html(nenshu_man):
    """年収○○万円の個別ページHTMLを生成"""
    annual_income = nenshu_man * 10000
    r = calculate_tedori(annual_income)

    nearby = []
    for diff in [-100, -50, 50, 100]:
        n = nenshu_man + diff
        if 100 <= n <= 3000 and n != nenshu_man:
            nr = calculate_tedori(n * 10000)
            nearby.append((n, nr))

    nearby_rows = ""
    for n, nr in nearby:
        nearby_rows += f"""
          <tr>
            <td><a href="nenshu-{n}.html">{fmt(n)}万円</a></td>
            <td>¥{fmt(nr['tedori'])}</td>
            <td>¥{fmt(nr['monthly_tedori'])}</td>
            <td>{nr['tedori_rate']}%</td>
          </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>年収{fmt(nenshu_man)}万円の手取り額は？【2026年最新】税金・保険料の内訳</title>
  <meta name="description" content="年収{fmt(nenshu_man)}万円の手取りは約{fmt(r['tedori'])}円（月額約{fmt(r['monthly_tedori'])}円）です。所得税・住民税・社会保険料の内訳を2026年最新の税率で詳しく解説。">
  <meta name="keywords" content="年収{nenshu_man}万,手取り,所得税,住民税,社会保険料,2026">
  <meta property="og:title" content="年収{fmt(nenshu_man)}万円の手取り額【2026年版】">
  <meta property="og:description" content="年収{fmt(nenshu_man)}万円の手取りは約{fmt(r['tedori'])}円。税金・保険料の内訳を解説。">
  <link rel="stylesheet" href="../css/style.css">
  <style>
    .page-content {{ max-width: 800px; margin: 0 auto; padding: 40px 20px 80px; }}
    .answer-box {{ background: var(--bg-card); border: 1px solid var(--glass-border); border-radius: var(--border-radius-xl); padding: 40px; text-align: center; margin: 32px 0; }}
    .answer-label {{ font-size: 16px; color: var(--text-secondary); margin-bottom: 8px; }}
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
    .compare-table a:hover {{ text-decoration: underline; }}
    .section-title {{ font-size: 22px; font-weight: 700; margin: 40px 0 16px; letter-spacing: -0.01em; }}
    .explanation {{ color: var(--text-secondary); line-height: 1.9; font-size: 15px; margin-bottom: 24px; }}
    .back-link {{ display: inline-flex; align-items: center; gap: 8px; color: var(--accent-green); text-decoration: none; font-weight: 600; font-size: 14px; margin-bottom: 24px; }}
    .back-link:hover {{ text-decoration: underline; }}
    @media (max-width: 600px) {{
      .detail-grid {{ grid-template-columns: 1fr; }}
      .answer-value {{ font-size: 32px; }}
    }}
  </style>
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <a href="../index.html" class="logo"><div class="logo-icon">¥</div><div class="logo-text"><span>MoneyLab</span></div></a>
      <div class="header-badge">2026年度対応</div>
    </div>
  </header>

  <main class="page-content">
    <a href="../index.html" class="back-link">← 計算ツールに戻る</a>

    <h1>年収{fmt(nenshu_man)}万円の手取りはいくら？</h1>

    <div class="answer-box">
      <div class="answer-label">年収{fmt(nenshu_man)}万円の年間手取り額</div>
      <div class="answer-value">¥{fmt(r['tedori'])}</div>
      <div class="answer-detail">
        月額 <strong>¥{fmt(r['monthly_tedori'])}</strong> ｜ 手取り率 <strong>{r['tedori_rate']}%</strong>
      </div>
    </div>

    <p class="explanation">
      年収{fmt(nenshu_man)}万円（額面）の場合、所得税・住民税・社会保険料を差し引いた<strong>年間の手取り額は約{fmt(r['tedori'])}円</strong>（月額約{fmt(r['monthly_tedori'])}円）です。
      額面の約<strong>{r['tedori_rate']}%</strong>が手元に残る計算になります。
      ※2026年度の税率・社会保険料率に基づく概算です（配偶者控除なし・扶養0人・39歳以下の場合）。
    </p>

    <h2 class="section-title">💰 税金・保険料の内訳</h2>

    <div class="detail-grid">
      <div class="detail-card">
        <div class="label">所得税（復興税込）</div>
        <div class="value" style="color: #3b82f6;">¥{fmt(r['income_tax'])}</div>
        <div class="percent">年収の {round(r['income_tax']/annual_income*100, 1)}%</div>
      </div>
      <div class="detail-card">
        <div class="label">住民税</div>
        <div class="value" style="color: #6366f1;">¥{fmt(r['resident_tax'])}</div>
        <div class="percent">年収の {round(r['resident_tax']/annual_income*100, 1)}%</div>
      </div>
      <div class="detail-card">
        <div class="label">健康保険料</div>
        <div class="value" style="color: #f59e0b;">¥{fmt(r['health_insurance'])}</div>
        <div class="percent">年収の {round(r['health_insurance']/annual_income*100, 1)}%</div>
      </div>
      <div class="detail-card">
        <div class="label">厚生年金保険料</div>
        <div class="value" style="color: #ef4444;">¥{fmt(r['pension'])}</div>
        <div class="percent">年収の {round(r['pension']/annual_income*100, 1)}%</div>
      </div>
    </div>

    <h2 class="section-title">📊 近い年収との比較</h2>
    <table class="compare-table">
      <thead>
        <tr><th>年収</th><th>年間手取り</th><th>月額手取り</th><th>手取り率</th></tr>
      </thead>
      <tbody>{nearby_rows}
        <tr style="background: rgba(16,185,129,0.08);">
          <td><strong>{fmt(nenshu_man)}万円</strong></td>
          <td><strong>¥{fmt(r['tedori'])}</strong></td>
          <td><strong>¥{fmt(r['monthly_tedori'])}</strong></td>
          <td><strong>{r['tedori_rate']}%</strong></td>
        </tr>
      </tbody>
    </table>

    <h2 class="section-title">🚀 手取りを増やす方法</h2>
    <div class="explanation">
      <p>手取りを増やすには、大きく3つの方法があります。</p>
      <ol style="margin: 16px 0; padding-left: 20px;">
        <li style="margin-bottom: 12px;"><strong>年収そのものを上げる</strong> — 転職やスキルアップで額面を増やす</li>
        <li style="margin-bottom: 12px;"><strong>節税制度を活用する</strong> — ふるさと納税、iDeCo、医療費控除など</li>
        <li style="margin-bottom: 12px;"><strong>資産運用で増やす</strong> — 新NISAなら運用益が非課税</li>
      </ol>
    </div>

    <section class="cta-section" style="padding: 20px 0 40px;">
      <div class="cta-grid">
        <div class="cta-card">
          <div class="cta-icon">🚀</div>
          <h3>年収を上げる</h3>
          <p>転職サイトで無料の年収診断を受けてみましょう。</p>
          <a href="#" class="cta-button green">年収診断を受ける →</a>
        </div>
        <div class="cta-card">
          <div class="cta-icon">🏡</div>
          <h3>ふるさと納税</h3>
          <p>実質2,000円で豪華な返礼品がもらえます。</p>
          <a href="#" class="cta-button purple">上限額を計算する →</a>
        </div>
        <div class="cta-card">
          <div class="cta-icon">📈</div>
          <h3>新NISAで運用</h3>
          <p>運用益が非課税。毎月の積立で資産を増やしましょう。</p>
          <a href="#" class="cta-button orange">積立シミュレーション →</a>
        </div>
      </div>
    </section>

  </main>

  <footer class="site-footer">
    <div class="container">
      <div class="footer-links">
        <a href="../privacy.html">プライバシーポリシー</a>
        <a href="../terms.html">利用規約</a>
        <a href="../contact.html">お問い合わせ</a>
      </div>
      <p>© 2026 MoneyLab. 本ツールの計算結果は概算です。正確な金額は税理士等にご確認ください。</p>
    </div>
  </footer>
</body>
</html>"""
    return html


# ============================================================
# メイン実行
# ============================================================

def main():
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pages')
    os.makedirs(output_dir, exist_ok=True)

    # 年収200万〜2000万まで、50万円刻み（主要ページ）
    # + 10万円刻みの追加ページ（年収300〜1000万の高需要帯）
    targets = set()

    # 50万円刻み（200〜2000万）
    for n in range(200, 2050, 50):
        targets.add(n)

    # 10万円刻み（高需要帯: 250〜1200万）
    for n in range(250, 1210, 10):
        targets.add(n)

    targets = sorted(targets)

    print(f"⏳ {len(targets)}ページを生成します...")

    for nenshu in targets:
        filename = f"nenshu-{nenshu}.html"
        filepath = os.path.join(output_dir, filename)
        html = generate_page_html(nenshu)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

    print(f"✅ 完了！{len(targets)}ページを {output_dir} に生成しました。")

    # サイトマップ生成
    sitemap_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sitemap.xml')
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        f.write('  <url><loc>https://example.com/</loc><priority>1.0</priority></url>\n')
        for nenshu in targets:
            f.write(f'  <url><loc>https://example.com/pages/nenshu-{nenshu}.html</loc><priority>0.8</priority></url>\n')
        f.write('</urlset>\n')
    print(f"✅ sitemap.xml を生成しました。")


if __name__ == '__main__':
    main()
