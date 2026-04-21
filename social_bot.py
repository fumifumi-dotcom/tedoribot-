import os
import json

def generate_tweets():
    print("--- 📱 X (Twitter) 自動配信用ツイート案の生成 ---")
    tweets = []
    
    # 300万、500万、700万、1000万の代表的なツイートを作成
    milestone_salaries = {
        500: {"tedori": 389, "tax_total": 111, "message": "これでも結婚・子育てできますか？"},
        700: {"tedori": 529, "tax_total": 171, "message": "ちょっと余裕が出たと思ったら税金が急激に襲いかかる年収帯です。"},
        1000: {"tedori": 721, "tax_total": 279, "message": "1000万プレイヤーの絶望。勝ち組かと思いきや税金で約300万持っていかれます。"}
    }

    for income, data in milestone_salaries.items():
        tweet = f"【悲報】年収{income}万円のリアルな手取り額\n\n"\
                f"額面：{income}万円\n"\
                f"手取り：わずか{data['tedori']}万円\n"\
                f"引かれる税金・保険料等：驚愕の{data['tax_total']}万円\n\n"\
                f"{data['message']}\n\n"\
                f"👇全110パターンの年収別手取り早見表\n"\
                f"https://tedori-keisan.com/salary-list.html\n\n"\
                f"#手取り #税金高すぎ #MoneyLab"
        tweets.append(tweet)

    for i, t in enumerate(tweets, 1):
        print(f"\n[ツイート案 {i}]")
        print(t)
        print("-" * 40)

def generate_note_outline():
    print("\n--- ✍️ Note/はてなブログ用 サテライト記事アウトライン ---")
    content = """
タイトル：【2026年最新】年収1000万でも手取りはたったの700万？日本の累進課税がヤバすぎる理由

（リードテキスト）
給料明細を見て「あれ？こんなに引かれてるの？」と絶望した経験はありませんか？
本記事では、日本において年収が上がれば上がるほど残酷に税金が引かれていく仕組みの真実と、代表的な年収別のリアルな「手取り額」を解説します。

（見出し1）年収500万の手取りは約389万円！社会保険料の壁
年収500万といえば一般的な平均年収ですが、実際に手元に残るのは約389万です。
健康保険、厚生年金だけで年間約74万円も引かれています。

（見出し2）年収1000万の絶望。累進課税のターゲット
年収1000万のエリートとなっても、手取りは約721万まで落ち込みます。
所得税が一気に上がり始め、約300万円もの大金が手元から消えてしまいます。

（見出し3）あなたの年収の「1円単位の正確な手取り」を知るには？
ここに乗っていない年収100万〜2000万まで、すべての手取りを完全に網羅したシミュレーター（2026年対応版）を使ってみてください。

👉 あなたの正確な手取りと、控除の内訳を無料計算する
https://tedori-keisan.com/

👉 110パターンの「年収別・手取り早見表データ」はこちら
https://tedori-keisan.com/salary-list.html
"""
    print(content)

if __name__ == "__main__":
    generate_tweets()
    generate_note_outline()
    
    print("\n✅ これらをコピーして SNS アカウントや Note に定期投稿することで、外部からの膨大なトラフィックを獲得できます。")
