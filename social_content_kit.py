#!/usr/bin/env python3
"""
MoneyLab SNS集客コンテンツ自動生成キット

【使い方】
  python3 social_content_kit.py

これを実行すると以下が自動生成されます：
  1. X (Twitter) 用の投稿文（113パターン全て、URLとハッシュタグ付き）
  2. Note/はてなブログ用のサテライト記事テキスト
  3. 週次スケジュール例（どの曜日に何を投稿するか）

生成されたテキストをそのままSNSにコピペしてください。
"""

import os
import json
from datetime import datetime, timedelta

# 年収と推定手取りのデータ（概算）
SALARY_DATA = {}
for n in range(200, 1210, 10):
    gross = n * 10000
    # 簡易計算（概算）
    social = gross * 0.15
    if n <= 195:
        income_tax = (gross - 480000 - social) * 0.05
    elif n <= 330:
        income_tax = (gross - 480000 - social) * 0.10 - 97500
    elif n <= 695:
        income_tax = (gross - 480000 - social) * 0.20 - 427500
    elif n <= 900:
        income_tax = (gross - 480000 - social) * 0.23 - 636000
    else:
        income_tax = (gross - 480000 - social) * 0.33 - 1536000
    
    income_tax = max(income_tax, 0)
    resident_tax = max((gross - 480000 - social - 430000) * 0.10, 0)
    tedori = gross - social - income_tax - resident_tax
    rate = (tedori / gross) * 100
    
    SALARY_DATA[n] = {
        'gross': n,
        'tedori': round(tedori / 10000),
        'tax_total': round((gross - tedori) / 10000),
        'rate': round(rate, 1),
    }

def generate_all_tweets():
    """113パターン全てのX投稿文を生成（バズ特化型）"""
    tweets = []
    
    # バズ用テンプレート3種
    # Xの黄金法則に則ったバズ構文（5パターン）
    templates = [
        # パターン1: 常識破壊・警告構文（ドヤ顔系）
        "「年収{income}万だから大丈夫」と思ってる人、正直に言って全員損してます。\n実は裏で国に凄まじい額を引かれているのを知らないのは致命的。\n\n稼げば稼ぐほど「罰ゲーム」のように増える税金の実態がこれ👇\n\n【年収{income}万の真実】\n・額面：{income}万\n・手取り：{tedori}万\n・天引き：💸{tax_total}万💸\n\n自分の手取りの低さに絶望した人は、プロフのリンクで一度正確な数字を調べて対策して…\n\n#手取り計算 #税金高すぎ",
        
        # パターン2: リスト・特徴列挙構文（ブックマーク保存狙い）
        "一生手取りが増えない人の「金食い虫」リスト👇\n\n・毎月の税金を把握してない\n・ふるさと納税をやらない\n・NISAよりも貯金優先\n・そして自分の『正確な手取り水準』を知らない\n\n【年収{income}万】の場合、無対策だと国に{tax_total}万円搾取されます。\n該当してる人は今すぐプロフのURLで計算して…手遅れになる前に！\n\n#手取り計算 #新NISA #手取り",
        
        # パターン3: 対比・結論先出し構文（知的好奇心狙い）
        "年収{income}万でも『余裕がある人』と『カツカツな人』の決定的すぎる違い。\n\n結論：手取りと天引きのギャップを理解しているか。\n\n年収{income}万の場合、手取り率はわずか{rate}%。\n毎月のように計{tax_total}万円が消えている現実から目を背けないで。\n自分の本当の数字はプロフのリンクで1秒でわかります👇\n\n#金銭感覚 #手取り計算 #お金の勉強",
        
        # パターン4: 共感・代弁構文（リポスト・議論狙い）
        "「限界まで働いてるのに、手取りが全然上がらない」\nと嘆く前に、国にいくら持っていかれているか計算してほしい。\n\n【年収{income}万の絶望】\n・手取り：{tedori}万\n・天引き：{tax_total}万\n\n国はあなたを守ってくれない。自分の資産は自分で守るしかないのが現実。\nプロフのツールで現状把握から始めて👇\n\n#手取り計算 #住民税 #給与明細",
        
        # パターン5: 体験談風・主語の置き換え構文
        "経理をやってて本当に思うんだけど…\n「年収{income}万」の人たち、給与明細をちゃんと見てなくてマジで勿体ない。\n\n額面{income}万でも、実は【{tax_total}万円】も税金・保険料で引かれてるのに、対策しない人が多すぎる。\n\n何からやっていいか分からない人は、まずプロフの計算機で自分のリアルな数字を見て絶望するところから始めてほしい👇\n\n#手取り計算 #経理の裏側"
    ]
    
    for i, (income, data) in enumerate(sorted(SALARY_DATA.items())):
        template = templates[i % len(templates)]
        tweet = template.format(
            income=income,
            tedori=data['tedori'],
            tax_total=data['tax_total'],
            rate=data['rate']
        )
        tweets.append({'income': income, 'text': tweet})
    return tweets

def generate_thread_tweets():
    """バズりやすい「スレッド形式」のツイートを生成"""
    threads = []

    # スレッド1: 年収帯別の残酷ランキング
    thread1 = [
        """🧵【保存版】年収別・手取り額の残酷な真実ランキング

日本の税金がいかにエグいか、年収帯ごとに暴いていくスレッドです。

これを知らずに生きている人が多すぎます。""",
        f"""① 年収300万 → 手取り{SALARY_DATA[300]['tedori']}万
② 年収500万 → 手取り{SALARY_DATA[500]['tedori']}万
③ 年収700万 → 手取り{SALARY_DATA[700]['tedori']}万
④ 年収1000万 → 手取り{SALARY_DATA[1000]['tedori']}万

年収700万以上になると急に税率がバグります。""",
        f"""特にエグいのは年収1000万。

額面1000万に対して天引きされる額はなんと{SALARY_DATA[1000]['tax_total']}万円。

1000万プレイヤーの現実は、手取りでみると「普通の暮らし」です。""",
        """結論：節税はもちろん大事だが、手取りを根本的に増やすには「額面を上げる」しかない。

全110パターンの年収別手取り早見表はこちら👇
https://tedori-keisan.com/salary-list.html

#手取り計算 #MoneyLab"""
    ]
    threads.append(thread1)

    # スレッド2: ふるさと納税
    thread2 = [
        """🧵【やらないと毎年損してる】ふるさと納税、まだやってない人多すぎ問題

「面倒だから」で放置してる人に言いたい。
あなたは毎年、数万円分のお肉を国に「無料で」あげています。""",
        """ふるさと納税の仕組みを一言で：

「来年払う住民税を今年別の自治体に前払い」
→ 実質2,000円で豪華な返礼品がもらえる

確定申告も不要（5自治体以内ならワンストップで紙1枚）""",
        """上限額を超えると「ただの寄付」になるので、
まず自分の上限額だけは絶対に知っておこう。

年収を入れるだけで1秒で計算できるツール👇
https://tedori-keisan.com/furusato.html

#ふるさと納税 #MoneyLab"""
    ]
    threads.append(thread2)

    return threads

def generate_note_articles():
    """Note用の完成記事テキスト（3本）"""
    articles = []

    articles.append({
        'title': '【2026年最新】全110パターン！年収別の手取り額と税金を完全まとめ',
        'body': f"""毎月の給料明細を見て「あれ、こんなもん？」と思ったことはありませんか。

日本の税制は非常に複雑で、年収が上がれば上がるほど、税金や社会保険料が指数関数的に増えていきます。

## 代表的な年収の手取り一覧

| 年収（額面） | 手取り | 天引き合計 | 手取り率 |
|---|---|---|---|
| 300万円 | {SALARY_DATA[300]['tedori']}万円 | {SALARY_DATA[300]['tax_total']}万円 | {SALARY_DATA[300]['rate']}% |
| 400万円 | {SALARY_DATA[400]['tedori']}万円 | {SALARY_DATA[400]['tax_total']}万円 | {SALARY_DATA[400]['rate']}% |
| 500万円 | {SALARY_DATA[500]['tedori']}万円 | {SALARY_DATA[500]['tax_total']}万円 | {SALARY_DATA[500]['rate']}% |
| 600万円 | {SALARY_DATA[600]['tedori']}万円 | {SALARY_DATA[600]['tax_total']}万円 | {SALARY_DATA[600]['rate']}% |
| 700万円 | {SALARY_DATA[700]['tedori']}万円 | {SALARY_DATA[700]['tax_total']}万円 | {SALARY_DATA[700]['rate']}% |
| 800万円 | {SALARY_DATA[800]['tedori']}万円 | {SALARY_DATA[800]['tax_total']}万円 | {SALARY_DATA[800]['rate']}% |
| 1000万円 | {SALARY_DATA[1000]['tedori']}万円 | {SALARY_DATA[1000]['tax_total']}万円 | {SALARY_DATA[1000]['rate']}% |

年収が上がるほど手取り率が下がっていくのが一目瞭然です。

## あなたの年収の手取りをもっと正確に知りたいなら

以下のサイトでは、年収100万円から2000万円まで、10万円刻みで110パターンすべての手取り額を完全に網羅しています。

👉 **年収別 手取り早見表（全110パターン）**
https://tedori-keisan.com/salary-list.html

👉 **あなたの年収から正確な手取りを1秒で計算する**
https://tedori-keisan.com/

## なぜ年収が上がっても手取りが増えないのか

答えは「累進課税」です。所得税は稼げば稼ぐほど税率が上がる仕組みになっており、年収700万を超えると…詳しくは以下のコラムをご覧ください。

👉 なぜ日本の税金は高いのか？累進課税の罠と対策
https://tedori-keisan.com/articles/why-tax-high.html
"""
    })

    return articles

def generate_weekly_schedule():
    """1週間の投稿スケジュール例"""
    today = datetime.now()
    schedule = []
    
    patterns = [
        ('月', '単発ツイート（300万〜500万台の年収帯・共感狙い）'),
        ('火', 'コラム記事のシェア（「なぜ税金は高いのか」等）'),  
        ('水', '単発ツイート（700万〜1000万台の年収帯・衝撃狙い）'),
        ('木', 'スレッド形式の連投（年収別ランキング等）'),
        ('金', 'ふるさと納税 or 新NISAの啓蒙ツイート'),
        ('土', 'Note記事の公開・シェア'),
        ('日', '前週のベストツイートのリポスト'),
    ]
    
    return patterns

def main():
    print("=" * 60)
    print("  MoneyLab SNS集客コンテンツキット")
    print("=" * 60)
    
    # --- 1. 全ツイート生成 ---
    tweets = generate_all_tweets()
    
    output_dir = 'sns_content'
    os.makedirs(output_dir, exist_ok=True)
    
    with open(f'{output_dir}/all_tweets.txt', 'w', encoding='utf-8') as f:
        for t in tweets:
            f.write(f"--- 年収{t['income']}万円 ---\n")
            f.write(t['text'])
            f.write('\n\n')
    
    print(f"\n✅ 単発ツイート {len(tweets)}本 → {output_dir}/all_tweets.txt")
    
    # --- 2. スレッド形式ツイート ---
    threads = generate_thread_tweets()
    with open(f'{output_dir}/thread_tweets.txt', 'w', encoding='utf-8') as f:
        for i, thread in enumerate(threads, 1):
            f.write(f"======= スレッド {i} =======\n\n")
            for j, tweet in enumerate(thread, 1):
                f.write(f"[{j}/{len(thread)}]\n{tweet}\n\n")
            f.write('\n')
    
    print(f"✅ スレッドツイート {len(threads)}セット → {output_dir}/thread_tweets.txt")
    
    # --- 3. Note記事 ---
    articles = generate_note_articles()
    with open(f'{output_dir}/note_articles.md', 'w', encoding='utf-8') as f:
        for art in articles:
            f.write(f"# {art['title']}\n\n")
            f.write(art['body'])
            f.write('\n\n---\n\n')
    
    print(f"✅ Note用記事 {len(articles)}本 → {output_dir}/note_articles.md")
    
    # --- 4. 週次スケジュール ---
    schedule = generate_weekly_schedule()
    with open(f'{output_dir}/weekly_schedule.txt', 'w', encoding='utf-8') as f:
        f.write("=== MoneyLab 週次SNS投稿スケジュール ===\n\n")
        for day, task in schedule:
            f.write(f"  {day}曜日：{task}\n")
        f.write(f"\n※ 投稿のベストタイム：7:00〜8:00（通勤時間帯）、12:00〜13:00（昼休み）、21:00〜22:00（帰宅後）\n")
    
    print(f"✅ 週次スケジュール → {output_dir}/weekly_schedule.txt")
    
    # --- サマリー表示 ---
    print(f"\n{'=' * 60}")
    print(f"  生成完了！ {output_dir}/ フォルダに全ファイル出力しました")
    print(f"{'=' * 60}")
    print(f"\n  📱 all_tweets.txt    → Xにそのままコピペ投稿（{len(tweets)}本）")
    print(f"  📱 thread_tweets.txt → バズりやすいスレッド形式（{len(threads)}セット）")
    print(f"  ✍️  note_articles.md  → Noteに貼り付けて公開")
    print(f"  📅 weekly_schedule.txt → 投稿スケジュール表\n")

if __name__ == "__main__":
    main()
