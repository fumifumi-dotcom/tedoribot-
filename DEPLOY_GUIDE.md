# MoneyLab デプロイ＆収益化セットアップ手順書

このドキュメントは、構築済みの「手取り計算シミュレーター」サイトをインターネットに公開し、
アフィリエイト＋AdSenseで収益化するための全手順を、順序どおりに記載したものです。

---

## 現在の構築済みファイル一覧

```
money-tools/
├── index.html          ← メイン計算ツール
├── css/style.css       ← デザイン
├── js/calculator.js    ← 計算エンジン
├── pages/              ← SEOロングテールページ（113ページ）
│   ├── nenshu-200.html
│   ├── nenshu-250.html
│   ├── ...
│   └── nenshu-2000.html
├── privacy.html        ← プライバシーポリシー
├── terms.html          ← 利用規約
├── contact.html        ← お問い合わせ
├── sitemap.xml         ← サイトマップ
└── generate_pages.py   ← ページ生成スクリプト
```

---

## STEP 1：ドメインを取得する（5分・約1,500円/年）

好みのドメイン名を取得してください。おすすめのドメイン候補：
- `moneylab.jp`
- `tedori-keisan.com`
- `nenkin-calc.jp`

### 取得先（安い順）
1. **Cloudflare Registrar**（https://www.cloudflare.com/products/registrar/）
   - 原価提供（最安）。`.com` で年約1,200円前後
2. **お名前.com**（https://www.onamae.com/）
   - 日本語対応で安心。初年度割引あり
3. **Google Domains → Squarespace**（https://domains.squarespace.com/）

### やること
1. 上記いずれかのサイトにアクセス
2. 希望のドメインを検索
3. 購入手続き（クレジットカード登録）

---

## STEP 2：GitHubにリポジトリを作成する（5分・無料）

### やること
1. https://github.com にアクセス（アカウントがなければ無料作成）
2. 「New repository」をクリック
3. リポジトリ名: `moneylab`（任意）
4. Public を選択
5. 「Create repository」をクリック

### ローカルからプッシュするコマンド（今道さんのPCで実行）
```bash
cd /Users/imamichifumitaka/Downloads/ミカタ_経理/今道_生活を豊かに/money-tools
git init
git add .
git commit -m "初回デプロイ: 手取り計算シミュレーター"
git branch -M main
git remote add origin https://github.com/[あなたのユーザー名]/moneylab.git
git push -u origin main
```
※ `[あなたのユーザー名]` は GitHubのユーザー名に置き換えてください。

---

## STEP 3：Cloudflare Pages にデプロイする（10分・無料）

Cloudflare Pagesは無料で商用利用OKのホスティングサービスです。

### やること
1. https://dash.cloudflare.com にアクセス（アカウントがなければ無料作成）
2. 左メニュー「Pages」をクリック
3. 「Create a project」→「Connect to Git」
4. GitHubアカウントを連携し、先ほど作成した `moneylab` リポジトリを選択
5. ビルド設定:
   - **Production branch:** `main`
   - **Build command:** （空欄のまま）
   - **Build output directory:** `/`（ルート）
6. 「Save and Deploy」をクリック

### カスタムドメインの設定
1. Cloudflare Pages の設定画面で「Custom domains」
2. STEP 1で取得したドメインを入力
3. DNSレコードが自動設定される（Cloudflareでドメインを取得した場合は即反映）

---

## STEP 4：ASP（アフィリエイトサービス）に登録する（15分・無料）

サイトが公開されたら、アフィリエイトASPに登録しサイト審査を受けます。

### 登録すべきASP
| ASP名 | URL | 特徴 |
| :--- | :--- | :--- |
| **A8.net** | https://www.a8.net/ | 最大手。転職・金融案件が豊富 |
| **もしもアフィリエイト** | https://af.moshimo.com/ | Amazon・楽天との連携が簡単 |
| **バリューコマース** | https://www.valuecommerce.ne.jp/ | Yahoo!系・金融系に強い |
| **アクセストレード** | https://www.accesstrade.ne.jp/ | 金融・証券に特化 |

### 狙うべきアフィリエイト案件（高単価）
| 案件ジャンル | 紹介先の例 | 1件あたりの報酬目安 |
| :--- | :--- | :--- |
| **転職サイト** | doda, リクルートエージェント, ビズリーチ | 5,000〜15,000円 |
| **ふるさと納税** | さとふる, ふるなび, 楽天ふるさと納税 | 新規利用で1,000〜5,000円 |
| **証券口座開設** | SBI証券, 楽天証券, マネックス証券 | 3,000〜10,000円 |
| **iDeCo** | SBI証券iDeCo, 楽天証券iDeCo | 5,000〜8,000円 |
| **クレジットカード** | 三井住友カード, 楽天カード | 3,000〜10,000円 |

### やること
1. 上記ASPに会員登録（全て無料）
2. サイトURL（カスタムドメイン）を登録してサイト審査を受ける
3. 審査通過後、各案件に提携申請
4. 提携承認後、取得したアフィリエイトリンクを `index.html` と各 `nenshu-*.html` のCTAボタンに設定

---

## STEP 5：Google AdSenseに申請する（10分・無料）

サイトが安定して運営されている状態（公開後1〜2週間程度）で申請します。

### 申請条件（すべて構築済み ✅）
- [x] オリジナルコンテンツ（計算ツール + 113ページのSEOコンテンツ）
- [x] プライバシーポリシー
- [x] 利用規約
- [x] お問い合わせページ
- [x] モバイル対応
- [x] HTTPS対応（Cloudflare Pages で自動）

### やること
1. https://adsense.google.com にアクセス
2. Googleアカウントでログイン
3. サイトURLを入力して申請
4. 審査用のHTMLコードをサイトの `<head>` に貼り付け（私が代行可能）
5. 承認を待つ（通常1〜14日）

---

## STEP 6：Google Search Consoleに登録する（5分・無料）

検索エンジンにサイトを認識させ、インデックスを促進します。

### やること
1. https://search.google.com/search-console にアクセス
2. 「プロパティを追加」→ ドメインを入力
3. DNS認証（Cloudflareの場合、TXTレコードを追加）
4. サイトマップとして `sitemap.xml` のURLを送信

---

## まとめ：全ステップの所要時間

| ステップ | 所要時間 | コスト |
| :--- | :--- | :--- |
| STEP 1: ドメイン取得 | 5分 | 約1,500円/年 |
| STEP 2: GitHub | 5分 | 無料 |
| STEP 3: Cloudflare Pages デプロイ | 10分 | 無料 |
| STEP 4: ASP登録 | 15分 | 無料 |
| STEP 5: AdSense申請 | 10分 | 無料 |
| STEP 6: Search Console登録 | 5分 | 無料 |
| **合計** | **約50分** | **約1,500円/年** |
