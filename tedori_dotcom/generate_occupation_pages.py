import os
import json

# --- 職業データ (SEO向けに独自テキスト・FAQを大幅強化) ---
OCCUPATIONS = [
    {
        "id": "nurse", 
        "name": "看護師", 
        "avg_income": 500, 
        "description": "夜勤手当などが大きい反面、税金や社会保険料も高くなりがちな看護師のリアルな手取り額を計算します。",
        "seo_h2_1": "看護師の手取りが「額面より少なく感じる」理由",
        "seo_p_1": "看護師の給与は基本給に加えて「夜勤手当」や「超過勤務手当」などが加算されるため、額面年収は高く見えがちです。しかし、手当を含めた総支給額に対して所得税や社会保険料（健康保険・厚生年金など）が容赦なく計算されるため、結果として天引き額が膨らみ、「あんなに夜勤を頑張ったのに手元に残るのはこれだけ？」と感じるケースが非常に多いのが実情です。",
        "faq_q1": "看護師で年収500万円の場合、毎月いくら貯金するのが理想ですか？",
        "faq_a1": "年収500万の手取りは約390万円（月換算で約32万円）です。独身であれば実家暮らしなら月10万円、一人暮らしでも月5〜6万円を先取り貯蓄し、年間100万円の貯金を目指すのが理想的なラインです。",
        "faq_q2": "看護師ができる効果的な節税・税金対策はありますか？",
        "faq_a2": "もっとも手軽で効果的なのは「ふるさと納税」と「iDeCo（個人型確定拠出年金）」の併用です。とくにiDeCoは掛け金が全額所得控除になるため、高い税率がかけられている看護師にとっては非常に強力な節税対策となります。"
    },
    {
        "id": "engineer", 
        "name": "ITエンジニア", 
        "avg_income": 550, 
        "description": "年収が上がりやすいITエンジニアですが、額面が増えるほど税金の負担も急増します。エンジニアの適正な手取りと節税を解説。",
        "seo_h2_1": "ITエンジニア特有の「年収の壁」と税金トラップ",
        "seo_p_1": "ITエンジニアはスキル次第で20代・30代から年収500万円〜700万円を突破しやすい職種です。しかし、日本の税制は累進課税のため、年収が上がれば上がるほど所得税率が跳ね上がります。特に年収600万〜800万の層は「一番税金の負担増を実感しやすいゾーン」であり、昇給したのに手取りが思ったより増えないという現象（税金トラップ）に陥りがちです。",
        "faq_q1": "エンジニアがフリーランスになると手取りはどう変わりますか？",
        "faq_a1": "会社員（年収550万）とフリーランス（売上550万）では計算が全く異なります。フリーランスは社会保険料が全額自己負担（国民健康保険・国民年金）になる一方、PC代や通信費、家賃の一部を「経費」として計上できるため、経費のコントロール次第で会社員よりも可処分所得（手取り）を増やすことが可能です。",
        "faq_q2": "エンジニアにおすすめの節税対策を教えてください",
        "faq_a2": "会社員であれば「ふるさと納税」「iDeCo」「生命保険料控除」が基本です。さらに副業エンジニアとして開業届を出せば、青色申告特別控除（最大65万円）を活用し、副業の経費と本業の給与所得を損益通算するといった高度な節税テクニックも検討できます。"
    },
    {
        "id": "sales", 
        "name": "営業職", 
        "avg_income": 480, 
        "description": "インセンティブ（歩合給）で額面が変動しやすい営業職。見かけの年収と手取りのギャップをシミュレーションします。",
        "seo_h2_1": "インセンティブ（歩合給）と税金の残酷な関係",
        "seo_p_1": "営業職の魅力は成果に応じたインセンティブ（歩合給）ですが、インセンティブが支給された月は一時的に総支給額が跳ね上がるため、翌月の社会保険料や翌年の住民税に大きな影響を与えます。特に「今年は売上が良くて年収が高かったが、翌年はスランプで年収が下がった」という場合、下がった年収に対して高い住民税が請求されるため、生活が苦しくなる「住民税地獄」には注意が必要です。",
        "faq_q1": "ボーナスやインセンティブはどのくらい税金で引かれますか？",
        "faq_a1": "通常の月給と同じく、ボーナスやインセンティブからも「健康保険料」「厚生年金保険料」「雇用保険料」「所得税」が容赦なく天引きされます。目安として、総額の約20%〜25%は税金と保険料で消えると覚悟しておきましょう。",
        "faq_q2": "営業職で経費にできるものはありますか？（特定支出控除）",
        "faq_a2": "会社員でも「特定支出控除」という制度を使えば、スーツ代や接待交際費、資格取得費などを経費（給与所得控除額の半分を超えた分）として申告できる場合があります。ただし、会社の証明書が必要などハードルが高いため、現実的にはふるさと納税やiDeCoで節税する方が確実です。"
    },
    {
        "id": "civil-servant", 
        "name": "公務員", 
        "avg_income": 600, 
        "description": "安定した収入が魅力の公務員ですが、きっちり税金が引かれます。公務員ならではの手取り事情と可処分所得の現実。",
        "seo_h2_1": "公務員の「共済組合」と手取りへの影響",
        "seo_p_1": "公務員は民間企業の健康保険・厚生年金に相当する「共済組合」に加入します。共済組合の掛金率は自治体や職種によって微妙に異なりますが、基本的には民間と同水準の高い保険料が毎月天引きされます。公務員は安定している分、副業が原則禁止されているため、自力で収入を増やしたり、経費を使って節税するといった裏技が使いにくく、「与えられた手取り額の中でいかに賢くやり繰りするか」が非常に重要になります。",
        "faq_q1": "公務員でもできる節税対策はありますか？",
        "faq_a1": "副業が禁止されている公務員にとって、合法かつ確実な節税策は「ふるさと納税」と「iDeCo（個人型確定拠出年金）」の2つに絞られます。特に公務員はiDeCoの加入条件が緩和されたため、老後資金を作りながら毎月の所得税・住民税を減らす最適解となっています。",
        "faq_q2": "公務員のボーナス（期末・勤勉手当）の手取りはどう計算しますか？",
        "faq_a2": "公務員の期末・勤勉手当からも、共済掛金（短期・長期）や所得税が天引きされます。一般的に、額面ボーナス額の約80%前後が実際の手取り（口座振込額）になると計算しておくと、ボーナス払いの計画が狂いにくくなります。"
    },
    {
        "id": "pharmacist", 
        "name": "薬剤師", 
        "avg_income": 580, 
        "description": "医療職の中でも平均年収が高い薬剤師ですが、その上手取り率は何％になるのか？高所得者ならではの税金事情。",
        "seo_h2_1": "高収入な薬剤師を待ち受ける「累進課税」の壁",
        "seo_p_1": "薬剤師は初任給から比較的高水準の年収を得やすい職業ですが、日本の税制において年収500万円〜600万円台は「所得税率が10%から20%へと跳ね上がる」重要な分岐点が存在します。そのため、ドラッグストアや調剤薬局で店長・管理薬剤師となり昇給を果たしても、「税金でごっそり持っていかれて、思ったほど生活が豊かにならない」と感じる薬剤師が後を絶ちません。",
        "faq_q1": "薬剤師（年収580万）の適正な家賃はいくらですか？",
        "faq_a1": "年収580万の年間手取りは約440万円、月換算（ボーナスなしと仮定）で約36万円です。家賃の黄金比である「手取りの30%」を当てはめると、約10万〜11万円が適正な家賃の上限ラインとなります。",
        "faq_q2": "派遣薬剤師と正社員では手取り額は違いますか？",
        "faq_a2": "時給が高い派遣薬剤師は「額面収入」では正社員を上回るケースが多いですが、ボーナスが出ない点や、社会保険の加入条件（労働時間）によっては国民健康保険に自己負担で加入する必要がある点に注意が必要です。トータルの手取り・福利厚生を考慮すると、必ずしも派遣が得とは限りません。"
    }
]

# --- HTML テンプレート ---
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>【{name}の平均手取り】年収{avg_income}万円だと実際いくらもらえる？ - 手取り計算.com</title>
    <meta name="description" content="{description} {name}の平均年収{avg_income}万円から、税金・社会保険料がいくら引かれ、最終的な手取り・月給がいくらになるのかを徹底解説。">
    <link rel="canonical" href="https://tedori-keisan.com/articles/occupations/{id}-salary.html">
    <link rel="stylesheet" href="../../css/style.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
    <link rel="apple-touch-icon" href="/images/icon-192x192.png">
    
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-3STMJXD6N3"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-3STMJXD6N3');
    </script>
    
    <!-- JSON-LD 構造化データ -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": [
        {{
          "@type": "Question",
          "name": "{faq_q1}",
          "acceptedAnswer": {{
            "@type": "Answer",
            "text": "{faq_a1}"
          }}
        }},
        {{
          "@type": "Question",
          "name": "{faq_q2}",
          "acceptedAnswer": {{
            "@type": "Answer",
            "text": "{faq_a2}"
          }}
        }}
      ]
    }}
    </script>
</head>
<body class="bg-slate-50 text-slate-800 font-sans antialiased">
    <!-- Navbar -->
    <nav class="glass-header text-white sticky top-0 z-50">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <a href="../../" class="font-bold text-xl tracking-tight text-emerald-400">手取り計算<span class="text-white">.com</span></a>
          </div>
          <div class="hidden sm:flex items-center space-x-6 text-sm font-medium">
            <a href="../../" class="hover:text-emerald-400 transition">トップへ戻る</a>
            <a href="index.html" class="hover:text-emerald-400 transition">職業別手取り一覧</a>
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
        <div class="card p-8 mb-8 bg-white shadow-xl rounded-2xl">
            <h2 class="text-2xl font-bold border-l-4 border-emerald-500 pl-4 mb-6">{name}の平均的な「手取り額」</h2>
            <p class="text-slate-600 mb-6 font-medium leading-relaxed">
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
                    <span class="text-slate-800 font-bold text-lg">実際の手取り（年間）</span>
                    <span class="text-4xl font-black text-emerald-600">{calced_tedori}万円</span>
                </div>
            </div>
            
            <div class="bg-indigo-50 text-indigo-800 p-5 rounded-xl text-center font-bold text-lg shadow-sm">
                1ヶ月あたりの手取り月給: ボーナスなしなら約<span class="text-3xl mx-2 text-indigo-600">{monthly_tedori}</span>万円
            </div>
        </div>
        
        <!-- SEO Text Section -->
        <article class="card p-8 mb-12 bg-white shadow-xl rounded-2xl prose prose-slate max-w-none">
            <h2 class="text-2xl font-bold mb-6 text-slate-800 border-b pb-2">{seo_h2_1}</h2>
            <p class="text-slate-600 leading-relaxed mb-8">{seo_p_1}</p>
            
            <h2 class="text-2xl font-bold mb-6 text-slate-800 border-b pb-2">よくある質問（FAQ）</h2>
            <div class="space-y-6">
                <div class="bg-slate-50 p-5 rounded-xl border border-slate-100">
                    <h3 class="font-bold text-lg text-emerald-700 mb-2 flex items-center">
                        <span class="bg-emerald-100 text-emerald-700 w-8 h-8 rounded-full flex items-center justify-center mr-3 shrink-0">Q</span>
                        {faq_q1}
                    </h3>
                    <p class="text-slate-600 pl-11">{faq_a1}</p>
                </div>
                <div class="bg-slate-50 p-5 rounded-xl border border-slate-100">
                    <h3 class="font-bold text-lg text-emerald-700 mb-2 flex items-center">
                        <span class="bg-emerald-100 text-emerald-700 w-8 h-8 rounded-full flex items-center justify-center mr-3 shrink-0">Q</span>
                        {faq_q2}
                    </h3>
                    <p class="text-slate-600 pl-11">{faq_a2}</p>
                </div>
            </div>
        </article>

        <!-- Call to Action -->
        <div class="text-center bg-gradient-to-r from-slate-900 to-slate-800 p-8 rounded-2xl shadow-2xl text-white">
            <h3 class="text-2xl font-bold mb-4">もっと詳しく自分の手取りを計算する</h3>
            <p class="mb-8 text-slate-300">平均ではなく、あなたの本当の「現在の年収」を入力して、1円単位の手取りと適正家賃をシミュレーションしてみましょう。</p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
                <a href="../../" class="bg-white text-slate-900 hover:bg-slate-100 font-bold py-4 px-8 rounded-xl shadow-lg transition duration-200 flex items-center justify-center">
                    🔍 手取り計算トップへ
                </a>
                <a href="../../diagnosis.html" class="bg-emerald-500 hover:bg-emerald-400 text-white font-bold py-4 px-8 rounded-xl shadow-lg transition duration-200 flex items-center justify-center">
                    💡 お金の無料人生診断
                </a>
            </div>
        </div>
    </div>
    
    <!-- Footer -->
    <footer class="bg-slate-900 text-slate-400 py-8 mt-12">
        <div class="max-w-4xl mx-auto px-4 text-center">
            <p class="mb-4">&copy; 2026 手取り計算.com</p>
            <a href="index.html" class="text-emerald-500 hover:underline">職業別一覧へ</a>
        </div>
    </footer>
</body>
</html>
"""

# --- Hub (Index) ページテンプレート ---
HUB_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>職業別・平均手取りシミュレーション一覧 - 手取り計算.com</title>
    <meta name="description" content="さまざまな職業の平均年収と、そこから引かれる税金・社会保険料、最終的な「手取り額」をまとめた一覧ページです。">
    <link rel="stylesheet" href="../../css/style.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+JP:wght@400;500;700;900&display=swap" rel="stylesheet">
    <link rel="icon" href="/favicon.svg" type="image/svg+xml">
</head>
<body class="bg-slate-50 text-slate-800 font-sans antialiased">
    <nav class="glass-header text-white sticky top-0 z-50 bg-slate-900">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <a href="../../" class="font-bold text-xl tracking-tight text-emerald-400">手取り計算<span class="text-white">.com</span></a>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-4xl mx-auto px-4 py-16">
        <h1 class="text-3xl font-extrabold mb-8 text-center border-b pb-4">職業別・平均手取り一覧</h1>
        <p class="text-center text-slate-600 mb-12">各職業の平均年収から、リアルな手取り額と税金の裏側を徹底解説します。</p>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            {links}
        </div>
    </div>
</body>
</html>
"""

def generate_hub_page(output_dir):
    links_html = ""
    for occ in OCCUPATIONS:
        links_html += f"""
        <a href="{occ['id']}-salary.html" class="block p-6 bg-white rounded-xl shadow hover:shadow-md transition border border-slate-100 hover:border-emerald-300">
            <h2 class="text-xl font-bold text-emerald-700 mb-2">{occ['name']} の手取り</h2>
            <p class="text-slate-500 text-sm">平均年収: {occ['avg_income']}万円</p>
        </a>
        """
    
    filepath = os.path.join(output_dir, "index.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(HUB_TEMPLATE.format(links=links_html))
    print(f"Generated Hub Page: {filepath}")


def generate_pages():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "articles/occupations")
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
        
        monthly_tedori = round(tedori / 12 / 10000, 1)
        rent = round(monthly_tedori * 0.3, 1)
        
        html = HTML_TEMPLATE.format(
            id=occ["id"],
            name=occ["name"],
            avg_income=occ["avg_income"],
            description=occ["description"],
            seo_h2_1=occ["seo_h2_1"],
            seo_p_1=occ["seo_p_1"],
            faq_q1=occ["faq_q1"],
            faq_a1=occ["faq_a1"],
            faq_q2=occ["faq_q2"],
            faq_a2=occ["faq_a2"],
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
        
    # ハブページの生成
    generate_hub_page(output_dir)

if __name__ == "__main__":
    generate_pages()
