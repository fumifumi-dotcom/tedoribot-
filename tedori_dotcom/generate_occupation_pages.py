import os
import json
import math

# --- 職業データ ---
OCCUPATIONS = [
    {"id": "nurse", "name": "看護師", "avg_income": 500, "description": "夜勤手当などが大きい反面、税金や社会保険料も高くなりがちな看護師のリアルな手取り額を計算します。"},
    {"id": "engineer", "name": "ITエンジニア", "avg_income": 550, "description": "年収が上がりやすいITエンジニアですが、額面が増えるほど税金の負担も急増します。エンジニアの適正な手取りと節税を解説。"},
    {"id": "sales", "name": "営業職", "avg_income": 480, "description": "インセンティブ（歩合給）で額面が変動しやすい営業職。見かけの年収と手取りのギャップをシミュレーションします。"},
    {"id": "civil-servant", "name": "公務員", "avg_income": 600, "description": "安定した収入が魅力の公務員ですが、きっちり税金が引かれます。公務員ならではの手取り事情と可処分所得の現実。"},
    {"id": "childcare", "name": "保育士", "avg_income": 390, "description": "処遇改善手当などで給与構造が複雑な保育士。実質的な手取り額と、生活費の黄金比率を計算します。"},
    {"id": "clerk", "name": "一般事務", "avg_income": 350, "description": "ボーナスや残業代が少ないことも多い一般事務。限られた額面からどれくらい引かれるのか、リアルな手取り事情を解説。"},
    {"id": "pharmacist", "name": "薬剤師", "avg_income": 580, "description": "医療職の中でも平均年収が高い薬剤師ですが、その上手取り率は何％になるのか？高所得者ならではの税金事情。"},
    {"id": "caregiver", "name": "介護福祉士", "avg_income": 380, "description": "夜勤や特殊業務手当が含まれる介護職。額面に対して手取りがいくらになるのか、リアルな生活水準を計算します。"},
    {"id": "teacher", "name": "教員", "avg_income": 650, "description": "公立・私立で差はありますが平均年収が高い教員。しかし天引きされる額も強烈です。教員のリアルな手取りシミュレーション。"},
    {"id": "driver", "name": "トラック運転手", "avg_income": 450, "description": "残業や長距離手当が大きなウエイトを占めるドライバー職。額面年収からの天引き額と手取り額を割り出します。"}
]

# --- HTML テンプレート ---
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>【{name}の平均手取り】年収{avg_income}万円だと実際いくらもらえる？ - 手取り計算.com</title>
    <meta name="description" content="{description} {name}の平均年収{avg_income}万円から、税金・社会保険料がいくら引かれ、最終的な手取り・月給がいくらになるのかを徹底解説。">
    <link rel="stylesheet" href="../css/style.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-3STMJXD6N3"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-3STMJXD6N3');
    </script>
    <!-- Google AdSense -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3012346545678100" crossorigin="anonymous"></script>
  </head>
<body class="bg-gray-50 text-slate-800 font-sans antialiased">
    <!-- Navbar -->
    <nav class="glass-header text-white sticky top-0 z-50">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <a href="../" class="font-bold text-xl tracking-tight text-emerald-400">手取り計算<span class="text-white">.com</span></a>
          </div>
          <div class="hidden sm:flex items-center space-x-6 text-sm font-medium">
            <a href="../" class="hover:text-emerald-400 transition">シミュレーター</a>
            <a href="../lifestyle.html" class="hover:text-emerald-400 transition">家賃・生活費</a>
            <a href="../furusato.html" class="hover:text-emerald-400 transition">ふるさと納税</a>
          </div>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <div class="bg-gradient-to-br from-slate-900 to-slate-800 text-white py-16">
        <div class="max-w-3xl mx-auto px-4 text-center">
            <h1 class="text-3xl md:text-5xl font-extrabold mb-6 leading-tight">
                <span class="text-emerald-400">{name}</span>の手取り事情<br>
                <span class="text-2xl md:text-3xl font-medium mt-4 block">年収{avg_income}万円のリアル</span>
            </h1>
            <p class="text-slate-300 text-lg">{description}</p>
        </div>
    </div>

    <!-- Content -->
    <div class="max-w-3xl mx-auto px-4 py-12">
        <div class="card p-8 mb-8">
            <h2 class="text-2xl font-bold border-l-4 border-emerald-500 pl-4 mb-6">{name}の平均的な「手取り額」</h2>
            <p class="text-slate-600 mb-6 font-medium">
                {name}の平均年収である<strong>約{avg_income}万円</strong>をベースに、国の最新の税率（2026年度版）で天引き額を計算してみましょう。
            </p>
            
            <div class="bg-slate-50 border border-slate-200 rounded-xl p-6 mb-6">
                <div class="flex justify-between items-center mb-4 pb-4 border-b border-slate-200">
                    <span class="text-slate-500 font-bold">額面年収</span>
                    <span class="text-2xl font-black text-slate-800">{avg_income}万円</span>
                </div>
                <div class="flex justify-between items-center text-sm text-slate-500 mb-2">
                    <span>所得税・住民税</span>
                    <span class="text-rose-500 font-bold">- 約{calced_tax}万円</span>
                </div>
                <div class="flex justify-between items-center text-sm text-slate-500 mb-4 pb-4 border-b border-slate-200">
                    <span>社会保険料等</span>
                    <span class="text-rose-500 font-bold">- 約{calced_social}万円</span>
                </div>
                <div class="flex justify-between items-center">
                    <span class="text-slate-800 font-bold">実際の手取り（年間）</span>
                    <span class="text-4xl font-black text-emerald-600">{calced_tedori}万円</span>
                </div>
            </div>
            
            <div class="bg-indigo-50 text-indigo-800 p-4 rounded-xl text-center font-bold text-lg">
                1ヶ月あたりの手取り月給: ボーナスなしなら約<span class="text-2xl">{monthly_tedori}</span>万円
            </div>
        </div>
        
        <div class="card p-8 mb-12">
            <h2 class="text-xl font-bold mb-4">{name}が知っておくべきお金のリアル</h2>
            <ul class="space-y-4 text-slate-600">
                <li class="flex items-start">
                    <svg class="w-6 h-6 text-emerald-500 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    <span><strong>天引きの多さに注意:</strong> 額面が{avg_income}万円あっても、手元に残る手取り率は約{calced_rate}%です。年間で{calced_total_tax}万円が税金や保険料として消えています。</span>
                </li>
                <li class="flex items-start">
                    <svg class="w-6 h-6 text-emerald-500 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
                    <span><strong>適正な家賃は？:</strong> 手取り{calced_tedori}万円（月換算{monthly_tedori}万円）であれば、家賃の限界ラインは約{rent}万円です。これを越えると貯金ゼロ・生活費破綻のリスクがあります。</span>
                </li>
            </ul>
        </div>

        <div class="text-center">
            <h3 class="text-2xl font-bold mb-4">もっと詳しく自分の手取りを計算する</h3>
            <p class="mb-6 text-slate-600">平均ではなく、あなたの本当の「現在の年収」を入力して、1円単位の手取りと適正家賃をシミュレーションしてみましょう。</p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
                <a href="../" class="bg-slate-900 border border-slate-800 hover:bg-slate-800 text-white font-bold py-4 px-8 rounded-xl shadow-lg transition duration-200 hover:-translate-y-1">
                    手取り計算トップへ
                </a>
                <a href="../lifestyle.html" class="bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white font-bold py-4 px-8 rounded-xl shadow-lg transition duration-200 hover:-translate-y-1 flex items-center justify-center">
                    適正家賃シミュレーターへ
                </a>
            </div>
        </div>
    </div>
    
    <!-- Footer -->
    <footer class="bg-slate-900 text-slate-400 py-8">
        <div class="max-w-4xl mx-auto px-4 text-center">
            <p class="mb-4">&copy; 2026 手取り計算.com</p>
        </div>
    </footer>
</body>
</html>
"""

def generate_pages():
    output_dir = "articles/occupations"
    os.makedirs(output_dir, exist_ok=True)
    
    for occ in OCCUPATIONS:
        income = occ["avg_income"]
        gross = income * 10000
        social = gross * 0.15
        
        if income <= 195:
            income_tax = (gross - 480000 - social) * 0.05
        elif income <= 330:
            income_tax = (gross - 480000 - social) * 0.10 - 97500
        elif income <= 695:
            income_tax = (gross - 480000 - social) * 0.20 - 427500
        elif income <= 900:
            income_tax = (gross - 480000 - social) * 0.23 - 636000
        else:
            income_tax = (gross - 480000 - social) * 0.33 - 1536000
            
        income_tax = max(income_tax, 0)
        resident_tax = max((gross - 480000 - social - 430000) * 0.10, 0)
        tedori = gross - social - income_tax - resident_tax
        rate = (tedori / gross) * 100
        
        calced_tedori = round(tedori / 10000, 1)
        calced_social = round(social / 10000, 1)
        calced_tax = round((income_tax + resident_tax) / 10000, 1)
        calced_total_tax = round(calced_social + calced_tax, 1)
        
        monthly_tedori = round((tedori_raw := tedori) / 12 / 10000, 1)
        rent = round(monthly_tedori * 0.3, 1)
        
        html = HTML_TEMPLATE.format(
            name=occ["name"],
            avg_income=occ["avg_income"],
            description=occ["description"],
            calced_tedori=calced_tedori,
            calced_social=calced_social,
            calced_tax=calced_tax,
            calced_total_tax=calced_total_tax,
            monthly_tedori=monthly_tedori,
            rent=rent,
            calced_rate=round(rate, 1)
        )
        
        filepath = os.path.join(output_dir, f"{occ['id']}-salary.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Generated: {filepath}")

if __name__ == "__main__":
    generate_pages()
