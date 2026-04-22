import os
import json
import time
import tweepy
from collections import defaultdict

# API鍵（環境変数から取得。ローカル用のフォールバックあり）
API_KEY = os.environ.get("TWITTER_API_KEY", "UHvEB9eE3lyWM4zPARambujIa")
API_SECRET = os.environ.get("TWITTER_API_SECRET", "VUivkTp42P0PaNoOzlglsxnfPViMFLKHQybs8I8IreFUpaSnwn")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "1924677045784838144-hrHWl35Sim0p9PW5WUUSaXYUzUW1n0")
ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET", "Vs1qPPGRMtyRU9sacMBqA59ppnMrNZLe9iWDvoiTtRpf6")

BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN", "AAAAAAAAAAAAAAAAAAAAAC0S8QEAAAAAhad%2B7SrSIQC4JI5YdguDnOExFeo%3DqORLHE8Pt6MydU3m1HIAQ69t4dSiiI0eCrX9z9bAdZbi00qlLt")

# クラウドでも動作する相対パス
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sns_content")
HISTORY_FILE = os.path.join(DIR, 'tweet_history.json')
TEMPLATES_FILE = os.path.join(DIR, 'templates.json')

def load_data():
    if not os.path.exists(HISTORY_FILE) or not os.path.exists(TEMPLATES_FILE):
        return None, None
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        try:
            history = json.load(f)
        except:
            return None, None
    with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
        try:
            templates = json.load(f)
        except:
            return None, None
    return history, templates

def evaluate_and_update_scores():
    print("--- [SNS PDCA Evaluator] Started ---")
    history, templates = load_data()
    if not history or not templates:
        print("⚠️ No history or templates found. Bot hasn't tweeted enough.")
        return

    # 1. 過去のツイートIDをリスト化（直近50件）
    recent_history = history[-50:]
    tweet_ids = [str(item['tweet_id']) for item in recent_history]
    if not tweet_ids:
        print("⚠️ No tweet IDs in history.")
        return

    client = tweepy.Client(bearer_token=BEARER_TOKEN)

    print(f"📡 Fetching metrics for {len(tweet_ids)} recent tweets...")
    
    # 100件まで一括取得可能
    try:
        response = client.get_tweets(ids=tweet_ids, tweet_fields=["public_metrics"])
    except Exception as e:
        print(f"❌ API Error fetching metrics: {e}")
        return

    if not response or not response.data:
        print("⚠️ Could not fetch data from X API.")
        return

    # 2. テンプレートごとの「エンゲージメント（特にブックマーク）」を集計
    # アルゴリズム2026: ブックマーク(x10), リプライ(x5), リツイート(x3), いいね(x1)
    tpl_scores = defaultdict(list)
    trend_scores = defaultdict(list)

    # 辞書化してIDからTemplate IDを引けるようにする
    history_map = {str(item['tweet_id']): item['template_id'] for item in recent_history}

    for tweet in response.data:
        tid = str(tweet.id)
        metrics = tweet.public_metrics
        raw_tpl_id = history_map.get(tid)
        
        if not raw_tpl_id: continue
        
        b = metrics.get('bookmark_count', 0)
        r = metrics.get('reply_count', 0)
        rt = metrics.get('retweet_count', 0)
        l = metrics.get('like_count', 0)
        imp = metrics.get('impression_count', 0)

        # 独自のバズ戦闘力算出（Xの2024アルゴリズム特化：ブックマークとリプライを異常なほど優遇）
        strength = (b * 20) + (r * 10) + (rt * 2) + l
        # インプレッションに対しても加点
        strength += (imp * 0.02)

        # 外部トレンドID (`tpl_001::[日銀利上げ]`) の場合、ベースIDを抽出
        base_tpl_id = raw_tpl_id.split('::')[0]
        tpl_scores[base_tpl_id].append(strength)

        # トレンドキーワードが使われていれば、その市場ワード自身の「稼げるポテンシャル」を集計
        if '::' in raw_tpl_id:
            trend_kw = raw_tpl_id.split('::')[1]
            trend_scores[trend_kw].append(strength)

    if not tpl_scores:
        print("⚠️ No scores could be calculated.")
        return

    # 3. 各テンプレート及びトレンド市場の平均戦闘力を算出
    print("\n--- 📊 テンプレート戦闘力 レポート ---")
    avg_scores = {}
    for base_tpl_id, strengths in tpl_scores.items():
        avg = sum(strengths) / len(strengths)
        avg_scores[base_tpl_id] = avg
        print(f"Template {base_tpl_id}: {avg:.1f} pts (from {len(strengths)} tweets)")

    BEST_TREND_FILE = os.path.join(DIR, 'best_trend.json')
    best_trend_kw = None
    best_trend_score = 0.0

    if trend_scores:
        print("\n--- 🌍 市場トレンド戦闘力 レポート (アウトバウンド便乗効果) ---")
        for kw, strengths in trend_scores.items():
            avg = sum(strengths) / len(strengths)
            print(f"Market Trend {kw}: {avg:.1f} pts (from {len(strengths)} usages)")
            if avg > best_trend_score:
                best_trend_score = avg
                best_trend_kw = kw

        if best_trend_kw:
            with open(BEST_TREND_FILE, 'w', encoding='utf-8') as f:
                json.dump({'best_trend': best_trend_kw, 'score': best_trend_score}, f, ensure_ascii=False)
            print(f"🌟 Best Trend Saved: {best_trend_kw} ({best_trend_score:.1f} pts)")

    # 基準となる全体平均
    global_avg = sum(avg_scores.values()) / len(avg_scores) if avg_scores else 1.0
    if global_avg == 0: global_avg = 1.0

    # 4. テンプレートのScoreを上書きして「淘汰と生存」を行う
    updated_count = 0
    for t in templates:
        tpl_id = t['id']
        if tpl_id in avg_scores:
            # 現在のスコアに、平均の変動幅をマイルドに反映する（指数移動平均のような形）
            # 新スコア = (旧スコア * 0.5) + ( (対象の平均戦闘力 / 全体平均) * 自己基準(10.0) * 0.5 )
            ratio = avg_scores[tpl_id] / global_avg
            # スコアの上下限の決定
            raw_new_score = (t.get('score', 10.0) * 0.5) + (ratio * 10.0 * 0.5)
            # 最低でも1.0、上限を50.0としてクリップ
            new_score = max(1.0, min(50.0, raw_new_score))
            
            print(f"[{tpl_id}] Score update: {t.get('score', 10.0):.1f} ➡️ {new_score:.1f}")
            t['score'] = round(new_score, 1)
            updated_count += 1
        else:
            # まだツイートされていない新テンプレートには初期スコアボーナス
            t['score'] = 15.0

    # JSON保存
    with open(TEMPLATES_FILE, 'w', encoding='utf-8') as f:
        json.dump(templates, f, indent=2, ensure_ascii=False)

    print(f"\n✅ {updated_count} templates updated. Machine learning cycle complete.")
    print("--- [SNS PDCA Evaluator] Finished ---")

if __name__ == "__main__":
    evaluate_and_update_scores()
