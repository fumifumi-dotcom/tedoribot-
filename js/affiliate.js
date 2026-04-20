/**
 * アフィリエイトリンク管理（収益確定案件のみ）
 * ================================
 * 全ページのCTAボタンのリンクを一元管理します。
 * 
 * 【重要】このファイルには、A8.netで提携済み＝確実に報酬が発生するリンクのみを記載。
 * 提携申請中の案件は、承認後にここに追加してください。
 * 
 * 【追加手順】
 * 1. A8.netにログイン → 「参加中プログラム」→ 広告リンク作成
 * 2. 「テキスト」タイプのリンクURLをコピー
 * 3. 下記の該当URLを差し替え
 * 4. サイトを再デプロイ（wrangler pages deploy .）
 */

const AFFILIATE_LINKS = {
  // =============================
  // ✅ 提携済み・収益確定の案件のみ
  // =============================

  // 転職・年収診断（dodaチャレンジ - A8.net提携済み）
  // 成果報酬：登録完了時
  career: {
    url: 'https://px.a8.net/svt/ejp?a8mat=4B1OTT+6P4KS2+47GS+5YRHE',
    label: '無料の年収診断を受ける →',
  },

  // 楽天ふるさと納税（A8.net提携済み）
  // 成果報酬：購入金額の一定%
  rakutenFurusato: {
    url: 'https://rpx.a8.net/svt/ejp?a8mat=4B1OTR+ACPDGY+2HOM+6C1VM&rakuten=y&a8ejpredirect=http%3A%2F%2Fhb.afl.rakuten.co.jp%2Fhgc%2F0ea62065.34400275.0ea62066.204f04c0%2Fa26041903646_4B1OTR_ACPDGY_2HOM_6C1VM%3Fpc%3Dhttp%253A%252F%252Fevent.rakuten.co.jp%252Ffurusato%252F%26m%3Dhttp%253A%252F%252Fm.rakuten.co.jp%252F',
    label: '楽天ふるさと納税で探す →',
  },

  // =============================
  // ⏳ 申請中（承認後にURLを差し替え）
  // =============================
  // satofuru: { url: '承認後に差し替え', label: 'さとふるで探す →' },
  // sbi: { url: '承認後に差し替え', label: 'SBI証券で口座開設 →' },
};

/**
 * CTAボタンのIDとアフィリエイトキーのマッピング
 * 
 * ページ内のボタンに id="cta-career-link" 等を振っておけば、
 * 自動的に上記の提携済みURLが適用されます。
 */
const CTA_MAPPING = {
  // 転職系CTA（全ページ共通）
  'cta-career-link': 'career',
  'cta-career-link-salary-list': 'career',
  'cta-career': 'career',           // index.html用
  
  // ふるさと納税系CTA
  'cta-rakuten-link': 'rakutenFurusato',
  'cta-rakuten': 'rakutenFurusato',     // furusato.html用
  'cta-satofuru-link': 'rakutenFurusato',
  'cta-satofuru': 'rakutenFurusato',    // furusato.html用
  'cta-furunavi-link': 'rakutenFurusato',
  'cta-furunavi': 'rakutenFurusato',    // furusato.html用
  'cta-furusato-link': 'rakutenFurusato',
  'cta-furusato': 'rakutenFurusato',    // index.html用
  
  // 投資系CTA → 提携済みのdodaに転送（松井証券承認後に差替）
  'cta-invest-link': 'career',
  'cta-invest': 'career',              // index.html用
};

/**
 * アフィリエイトリンクを適用
 */
function applyAffiliateLinks() {
  Object.entries(CTA_MAPPING).forEach(([elementId, key]) => {
    const el = document.getElementById(elementId);
    const config = AFFILIATE_LINKS[key];
    if (el && config) {
      el.href = config.url;
      el.target = '_blank';
      el.rel = 'noopener noreferrer sponsored';
      if (config.label) {
        el.textContent = config.label;
      }
    }
  });
}

// DOM読み込み完了後に適用
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', applyAffiliateLinks);
} else {
  applyAffiliateLinks();
}

// --- 動的パーソナライズCTAのレンダリング関数 ---
window.renderDynamicRecommendation = function(grossIncome) {
  const container = document.getElementById('dynamic-recommendation');
  if (!container) return;
  
  let html = '';
  
  if (grossIncome < 5000000) {
    // 500万未満は転職を強めにプッシュ（doda = 提携済み✅）
    html = `
      <div class="dynamic-cta-card" style="background: linear-gradient(135deg, rgba(16,185,129,0.1) 0%, rgba(59,130,246,0.1) 100%); border: 1px solid var(--accent-green); border-radius: var(--border-radius-lg); padding: 24px; text-align: left; margin-top: 32px; animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
          <span style="font-size: 24px;">💡</span>
          <h3 style="color: var(--accent-green); margin: 0; font-size: 18px;">手取りを増やすなら、まずは市場価値診断</h3>
        </div>
        <p style="color: var(--text-secondary); font-size: 14px; line-height: 1.6; margin-bottom: 20px;">
          手取り額を増やす最も手っ取り早く確実な方法は、額面年収自体を上げることです。今のあなたの経験やスキルなら、<strong>本来もっと高い年収</strong>をもらえる可能性があります。<br>
          完全無料で利用できる「年収・市場価値診断」で、まずはあなたの適正年収をチェックしてみませんか？
        </p>
        <a href="${AFFILIATE_LINKS.career.url}" class="cta-button green" style="width: 100%; text-align: center; display: block; font-size: 16px;" target="_blank" rel="noopener sponsored">無料の年収・市場価値診断を受ける →</a>
      </div>
    `;
  } else if (grossIncome < 7000000) {
    // 500万〜700万未満は楽天ふるさと納税（提携済み✅）＋転職（提携済み✅）
    html = `
      <div class="dynamic-cta-card" style="background: linear-gradient(135deg, rgba(139,92,246,0.1) 0%, rgba(245,158,11,0.1) 100%); border: 1px solid var(--accent-purple); border-radius: var(--border-radius-lg); padding: 24px; text-align: left; margin-top: 32px; animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
          <span style="font-size: 24px;">🛡️</span>
          <h3 style="color: var(--accent-purple); margin: 0; font-size: 18px;">税金で損していませんか？ 最強の節税対策</h3>
        </div>
        <p style="color: var(--text-secondary); font-size: 14px; line-height: 1.6; margin-bottom: 20px;">
          年収500万円を超えると、税金と社会保険料の「壁」が高くなり負担が急増します。手取りを最大化するためには「正しい節税」が必須です。<br>
          まずは自己負担実質2,000円で豪華な返礼品がもらえる<strong>ふるさと納税</strong>から始めましょう。
        </p>
        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
          <a href="${AFFILIATE_LINKS.rakutenFurusato.url}" class="cta-button purple" style="flex: 1; text-align: center; font-size: 15px; min-width: 200px;" target="_blank" rel="noopener sponsored">楽天ふるさと納税で探す →</a>
          <a href="${AFFILIATE_LINKS.career.url}" class="cta-button green" style="flex: 1; text-align: center; font-size: 15px; min-width: 200px;" target="_blank" rel="noopener sponsored">年収を上げる市場価値診断 →</a>
        </div>
      </div>
    `;
  } else {
    // 700万以上は転職（高年収帯のdoda = 提携済み✅）に集中
    html = `
      <div class="dynamic-cta-card" style="background: linear-gradient(135deg, rgba(239,68,68,0.05) 0%, rgba(245,158,11,0.1) 100%); border: 1px solid #ef4444; border-radius: var(--border-radius-lg); padding: 24px; text-align: left; margin-top: 32px; animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
          <span style="font-size: 24px;">💎</span>
          <h3 style="color: #ef4444; margin: 0; font-size: 18px;">高所得者こそ「適正年収」を知るべき</h3>
        </div>
        <p style="color: var(--text-secondary); font-size: 14px; line-height: 1.6; margin-bottom: 20px;">
          年収700万円以上の方は、税率33%以上の累進課税ゾーンに突入しています。<strong>節税には限界があり、手取りを劇的に増やすには「さらに上のステージ」への転職</strong>が最も効果的です。<br>
          エグゼクティブ転職の市場では、同スキルでも年収100〜300万円のギャップがあるケースが日常的です。
        </p>
        <a href="${AFFILIATE_LINKS.career.url}" class="cta-button" style="background: #ef4444; color: white; width: 100%; text-align: center; display: block; font-size: 16px;" target="_blank" rel="noopener sponsored">【無料】高年収向け市場価値診断 →</a>
      </div>
    `;
  }
  
  container.innerHTML = html;
  container.style.display = 'block';
};

// --- GA4 クリックイベントのトラッキング ---
document.addEventListener('click', function(e) {
  const target = e.target.closest('a.cta-button');
  if (!target) return;
  
  const linkUrl = target.getAttribute('href') || '';
  const labelText = target.textContent || '';
  
  let campaign = 'other';
  if (linkUrl.includes('a8.net')) {
    if (linkUrl.includes('4B1OTT')) campaign = 'doda_career';
    if (linkUrl.includes('rakuten')) campaign = 'rakuten_furusato';
  }

  const incomeInput = document.getElementById('incomeInput');
  const retInput = document.getElementById('retirementInput');
  let currentIncome = 'unknown';
  if (incomeInput && incomeInput.value) currentIncome = incomeInput.value + '万';
  if (retInput && retInput.value) currentIncome = retInput.value + '万(退職)';

  if (typeof gtag === 'function') {
    gtag('event', 'cta_click', {
      'event_category': 'affiliate',
      'event_label': campaign,
      'user_income_range': currentIncome,
      'link_text': labelText.trim()
    });
  }
});
