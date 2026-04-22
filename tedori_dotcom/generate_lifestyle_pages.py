#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ロングテールSEOページ自動生成スクリプト（家賃・生活費編）
「手取り○○万円の家賃・生活費」ページを一括生成する
"""

import os
import math

RATIOS = [
    {'id': 'rent', 'label': '家賃・住居費', 'percent': 30, 'color': '#10b981'},
    {'id': 'food', 'label': '食費', 'percent': 15, 'color': '#f59e0b'},
    {'id': 'savings', 'label': '貯金・投資', 'percent': 15, 'color': '#3b82f6'},
    {'id': 'utilities', 'label': '水道光熱・通信', 'percent': 10, 'color': '#8b5cf6'},
    {'id': 'hobby', 'label': '交際費・趣味美容', 'percent': 20, 'color': '#ec4899'},
    {'id': 'others', 'label': '日用品・その他', 'percent': 10, 'color': '#64748b'}
]

def fmt(value):
    return f"{int(value):,}"

def generate_lifestyle_html(net_income_man):
    net_income_yen = net_income_man * 10000
    
    # 計算
    rent = net_income_yen * 0.30
    food = net_income_yen * 0.15
    savings = net_income_yen * 0.15
    
    # 比較用（近い手取り額）
    nearby = []
    for diff in [-2, -1, 1, 2]:
        n = net_income_man + diff
        if 10 <= n <= 100 and n != net_income_man:
            nr = n * 10000
            nearby.append((n, nr * 0.30, nr * 0.15))
            
    nearby_rows = ""
    for n, n_rent, n_sav in nearby:
        nearby_rows += f"""
          <tr>
            <td><a href="net-{n}.html">{n}万円</a></td>
            <td>¥{fmt(n_rent)}</td>
            <td>¥{fmt(n_sav)}</td>
          </tr>"""

    breakdown_list = ""
    for r in RATIOS:
        val = net_income_yen * (r['percent'] / 100)
        breakdown_list += f"""
        <li class="breakdown-item" style="display:flex; justify-content:space-between; align-items:center; padding: 12px 0; border-bottom: 1px solid var(--glass-border);">
          <div class="breakdown-left" style="display:flex; align-items:center;">
            <span class="breakdown-dot" style="width:12px; height:12px; border-radius:50%; background:{r['color']}; margin-right:12px;"></span>
            <span class="breakdown-name" style="font-weight:600; color:var(--text-primary); font-size: 15px;">{r['label']}</span>
          </div>
          <div class="breakdown-right" style="text-align:right;">
            <div class="breakdown-amount" style="font-size: 16px; font-weight:700;">¥{fmt(val)}</div>
            <div class="breakdown-percent" style="font-size: 12px; color:var(--text-muted);">{r['percent']}%</div>
          </div>
        </li>
        """

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>手取り{net_income_man}万円の家賃・生活費レベルは？【一人暮らしの貯金額目安】</title>
  <meta name="description" content="毎月の手取りが{net_income_man}万円の場合、適正な家賃目安は約{fmt(rent)}円、理想の貯金額は約{fmt(savings)}円です。後悔しない生活費の内訳と黄金比を解説します。">
  <meta name="keywords" content="手取り{net_income_man}万,家賃,生活費,貯金,一人暮らし,目安">
  <meta property="og:title" content="手取り{net_income_man}万円の家賃と生活費内訳">
  <meta property="og:description" content="手取り{net_income_man}万円なら家賃はいくらが限界？生活費の黄金比シミュレーション。">
  <meta property="og:type" content="article">
  <meta property="og:image" content="https://tedori-keisan.pages.dev/images/ogp.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#0ea5e9">
  <link rel="manifest" href="../manifest.json">
  <link rel="stylesheet" href="../css/style.css">
  <style>
    .page-content {{ max-width: 800px; margin: 0 auto; padding: 40px 20px 80px; }}
    .compare-table {{ width: 100%; border-collapse: collapse; margin: 24px 0; }}
    .compare-table th {{ background: var(--bg-tertiary); padding: 12px 16px; text-align: left; font-size: 13px; color: var(--text-secondary); font-weight: 600; }}
    .compare-table td {{ padding: 12px 16px; border-bottom: 1px solid var(--glass-border); font-size: 14px; }}
    .compare-table a {{ color: var(--accent-green); text-decoration: none; }}
    .compare-table a:hover {{ text-decoration: underline; }}
    .back-link {{ display: inline-flex; align-items: center; gap: 8px; color: var(--accent-green); text-decoration: none; font-weight: 600; font-size: 14px; margin-bottom: 24px; }}
    .back-link:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <a href="../index.html" class="logo"><div class="logo-icon">¥</div><div class="logo-text"><span>手取り計算.com</span></div></a>
      <div class="header-badge" style="background: rgba(16, 185, 129, 0.1); color: var(--accent-green);">生活費ガイド</div>
    </div>
  </header>

  <main class="page-content">
    <a href="../lifestyle.html" class="back-link">← シミュレーターに戻る</a>

    <h1>手取り{net_income_man}万円の家賃・生活費レベル</h1>

    <div class="glass-card" style="margin: 32px 0;">
      <div class="card-header">
        <div class="card-icon blue" style="background: rgba(59, 130, 246, 0.1); color: #3b82f6;">💰</div>
        <div class="card-title">毎月の生活費 黄金比</div>
      </div>
      
      <div class="result-hero" style="background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2);">
        <div class="result-label" style="color: var(--accent-green); font-weight: bold;">適正な家賃の目安（手取りの30%）</div>
        <div class="result-value" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">¥{fmt(rent)}</div>
        <div class="result-sub">毎月 <strong>¥{fmt(savings)}</strong> の貯金ペース</div>
      </div>

      <ul style="margin-top: 32px; list-style: none; padding: 0;">
        {breakdown_list}
      </ul>
    </div>

    <p style="color: var(--text-secondary); line-height: 1.8; margin-bottom: 32px;">
      手取りが毎月<strong>{net_income_man}万円</strong>の場合、生活を圧迫しない無理のない家賃の上限は<strong>約{fmt(rent)}円</strong>です。
      これをオーバーすると、食費を削るか貯金ができなくなる「生活費破産」のリスクが高まります。
    </p>

    <h2 style="margin-top:40px; font-size:22px;">📊 近い手取りとの比較</h2>
    <table class="compare-table">
      <thead>
        <tr><th>手取り</th><th>家賃目安</th><th>理想の貯金額</th></tr>
      </thead>
      <tbody>{nearby_rows}
        <tr style="background: rgba(16,185,129,0.08);">
          <td><strong>{net_income_man}万円</strong></td>
          <td><strong>¥{fmt(rent)}</strong></td>
          <td><strong>¥{fmt(savings)}</strong></td>
        </tr>
      </tbody>
    </table>

    <section class="cta-section" style="margin-top:48px;">
      <h2 style="text-align: center; margin-bottom: 24px;">家賃が高くてキツイ、貯金できないなら👇</h2>
      <div class="cta-grid">
        <div class="cta-card">
          <div class="cta-icon">🚀</div>
          <h3>稼いで手取りを増やす</h3>
          <p>そもそもの「給料」が少なければ節約には限界があります。あなたの適正年収を調べてみましょう。</p>
          <a href="#" class="cta-button green" id="cta-career-link">無料の市場価値診断 →</a>
        </div>
        <div class="cta-card">
          <div class="cta-icon">🏡</div>
          <h3>税金を減らして手取りを増やす</h3>
          <p>会社員ができる最強の現金防衛術「ふるさと納税」。まだやっていない人は今すぐチェック。</p>
          <a href="../furusato.html" class="cta-button purple">ふるさと納税シミュレーター →</a>
        </div>
      </div>
    </section>

  </main>

  <footer class="site-footer">
    <div class="container">
      <p>© 2026 手取り計算.com</p>
    </div>
  </footer>
  <script src="../js/affiliate.js"></script>
</body>
</html>"""
    return html

def main():
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lifestyle_pages')
    os.makedirs(output_dir, exist_ok=True)

    # 手取り10万〜100万（1万円刻み：10〜50万、5万刻み：50〜100万）
    targets = list(range(10, 51, 1)) + list(range(55, 105, 5))

    print(f"⏳ {len(targets)}ページを生成します...")

    for n in targets:
        filepath = os.path.join(output_dir, f"net-{n}.html")
        html = generate_lifestyle_html(n)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

    print(f"✅ 完了！{len(targets)}ページを {output_dir} に生成しました。")

if __name__ == '__main__':
    main()
