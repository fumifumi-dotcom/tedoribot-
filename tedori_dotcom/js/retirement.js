/**
 * 退職金の手取り計算ロジック
 */

const DOM = {};

function initDOM() {
  DOM.retSlider = document.getElementById('retirementSlider');
  DOM.retInput = document.getElementById('retirementInput');
  DOM.yearsInput = document.getElementById('yearsInput');
  DOM.reasonSelect = document.getElementById('reasonSelect');

  DOM.resTedori = document.getElementById('resultTedori');
  DOM.resRate = document.getElementById('resultRate');
  DOM.breakGross = document.getElementById('breakdownGross');
  DOM.breakDeduction = document.getElementById('breakdownDeduction');
  DOM.breakTaxable = document.getElementById('breakdownTaxable');
  DOM.breakIncomeTax = document.getElementById('breakdownIncomeTax');
  DOM.breakResidentTax = document.getElementById('breakdownResidentTax');
  DOM.dynamicCta = document.getElementById('dynamic-recommendation');
}

function format(num) {
  return Math.floor(num).toLocaleString('ja-JP');
}

// 所得税率テーブル
const INCOME_TAX_BRACKETS = [
  { limit: 1_950_000, rate: 0.05, deduction: 0 },
  { limit: 3_300_000, rate: 0.10, deduction: 97_500 },
  { limit: 6_950_000, rate: 0.20, deduction: 427_500 },
  { limit: 9_000_000, rate: 0.23, deduction: 636_000 },
  { limit: 18_000_000, rate: 0.33, deduction: 1_536_000 },
  { limit: 40_000_000, rate: 0.40, deduction: 2_796_000 },
  { limit: Infinity, rate: 0.45, deduction: 4_796_000 },
];

function calculateRetirementTax() {
  const grossIncome = (parseInt(DOM.retInput.value) || 0) * 10000;
  let years = parseInt(DOM.yearsInput.value) || 1;
  const reason = DOM.reasonSelect.value;
  
  if (grossIncome <= 0 || years <= 0) {
    return { gross: 0, deduction: 0, taxable: 0, incomeTax: 0, residentTax: 0, tedori: 0, rate: 0 };
  }

  // 1. 退職所得控除の計算
  let deduction = 0;
  if (years <= 20) {
    deduction = 400_000 * years;
    if (deduction < 800_000) deduction = 800_000; // 最低80万
  } else {
    deduction = 8_000_000 + 700_000 * (years - 20);
  }

  // 2. 課税退職所得金額
  let taxable = 0;
  if (grossIncome > deduction) {
    const remaining = grossIncome - deduction;
    
    // 特定役員退職手当等（勤続5年以下の役員等）の場合は 1/2 しない
    if (reason === 'executive' && years <= 5) {
      taxable = remaining;
    } else {
      // 原則として 1/2 (令和4年改正により勤続5年以下の一般退職金で300万を超える部分は1/2しない例外があるがここでは簡易化のため原則適用)
      taxable = Math.floor(remaining / 2);
    }
  }
  
  // 1,000円未満切り捨て
  taxable = Math.floor(taxable / 1000) * 1000;

  // 3. 所得税（復興特別所得税含む）
  let incomeTaxBase = 0;
  for (const bracket of INCOME_TAX_BRACKETS) {
    if (taxable <= bracket.limit) {
      incomeTaxBase = Math.floor(taxable * bracket.rate - bracket.deduction);
      break;
    }
  }
  const incomeTaxWithRecon = Math.floor(incomeTaxBase * 1.021);

  // 4. 住民税
  // 住民税は課税退職所得金額の10%
  const residentTax = Math.floor(taxable * 0.1);

  // 5. 手取り計算
  const totalTax = incomeTaxWithRecon + residentTax;
  const tedori = grossIncome - totalTax;
  const rate = (tedori / grossIncome) * 100;

  return {
    gross: grossIncome,
    deduction,
    taxable,
    incomeTax: incomeTaxWithRecon,
    residentTax,
    tedori,
    rate
  };
}

function renderCTA(tedori) {
  if (!DOM.dynamicCta) return;
  
  // 退職金専用のパーソナライズCTA
  let html = `
    <div class="dynamic-cta-card" style="background: linear-gradient(135deg, rgba(59,130,246,0.1) 0%, rgba(139,92,246,0.1) 100%); border: 1px solid var(--accent-blue); border-radius: var(--border-radius-lg); padding: 24px; text-align: left; animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);">
      <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
        <span style="font-size: 24px;">👴</span>
        <h3 style="color: var(--accent-blue); margin: 0; font-size: 18px;">退職金の「枯渇」を防ぐ資産運用</h3>
      </div>
      <p style="color: var(--text-secondary); font-size: 14px; line-height: 1.6; margin-bottom: 20px;">
        まとまった退職金を手に入れて安心していませんか？ 昨今のインフレ（物価高）により、銀行にただ預けているだけでは資金の価値は目減りしていきます。<br>
        老後資金を長持ちさせるための「新NISA」や堅実なインデックス投資、不動産投資への分散など、専門のプライベートFP（ファイナンシャルプランナー）に無料で相談してみましょう。
      </p>
      <div style="display: flex; gap: 12px; flex-wrap: wrap;">
        <a href="#" class="cta-button blue" style="flex: 1; text-align: center; font-size: 15px; min-width: 200px;" target="_blank" rel="noopener">【無料】優良FPに老後のマネープランを相談 →</a>
      </div>
    </div>
  `;
  
  DOM.dynamicCta.innerHTML = html;
  DOM.dynamicCta.style.display = 'block';
}

function update() {
  const result = calculateRetirementTax();
  
  DOM.retSlider.value = parseInt(DOM.retInput.value);
  
  DOM.resTedori.textContent = '¥' + format(result.tedori);
  DOM.resRate.textContent = result.rate.toFixed(1);
  
  DOM.breakGross.textContent = '¥' + format(result.gross);
  DOM.breakDeduction.textContent = '¥' + format(result.deduction);
  DOM.breakTaxable.textContent = '¥' + format(result.taxable);
  DOM.breakIncomeTax.textContent = '¥' + format(result.incomeTax);
  DOM.breakResidentTax.textContent = '¥' + format(result.residentTax);
  
  // CTAの表示
  if (result.gross > 0) {
    renderCTA(result.tedori);
  } else {
    DOM.dynamicCta.style.display = 'none';
  }
}

function bindEvents() {
  DOM.retInput.addEventListener('input', update);
  DOM.yearsInput.addEventListener('input', update);
  DOM.reasonSelect.addEventListener('change', update);
  
  DOM.retSlider.addEventListener('input', (e) => {
    DOM.retInput.value = e.target.value;
    update();
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initDOM();
  bindEvents();
  update();
});
