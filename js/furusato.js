/**
 * ふるさと納税 上限額シミュレーター - 計算エンジン & UI制御
 * 2026年度（令和8年度）の税率に基づく
 */

// ============================================================
// 税率テーブル（calculator.js と共通ロジック）
// ============================================================

const FURUSATO_TAX = {
  salaryDeduction: [
    { limit: 1_625_000, calc: () => 550_000 },
    { limit: 1_800_000, calc: (i) => i * 0.4 - 100_000 },
    { limit: 3_600_000, calc: (i) => i * 0.3 + 80_000 },
    { limit: 6_600_000, calc: (i) => i * 0.2 + 440_000 },
    { limit: 8_500_000, calc: (i) => i * 0.1 + 1_100_000 },
    { limit: Infinity, calc: () => 1_950_000 },
  ],
  incomeTaxBrackets: [
    { limit: 1_950_000, rate: 0.05 },
    { limit: 3_300_000, rate: 0.10 },
    { limit: 6_950_000, rate: 0.20 },
    { limit: 9_000_000, rate: 0.23 },
    { limit: 18_000_000, rate: 0.33 },
    { limit: 40_000_000, rate: 0.40 },
    { limit: Infinity, rate: 0.45 },
  ],
  healthRate: 0.04905,
  pensionRate: 0.0915,
  employmentRate: 0.006,
  nursingRate: 0.008,
  pensionMaxMonthly: 650_000,
  basicDeductionResident: 430_000,
  residentTaxRate: 0.10,
};

// ============================================================
// ふるさと納税上限額の計算
// ============================================================

function calculateFurusatoLimit(annualIncome, options = {}) {
  const {
    hasSpouse = false,
    dependents = 0,
    age = 'under40',
  } = options;

  if (annualIncome <= 0) {
    return { limit: 0, actualBenefit: 0, residentTaxDeduction: 0, incomeTaxDeduction: 0 };
  }

  // 社会保険料
  const monthlyIncome = annualIncome / 12;
  const healthIns = Math.floor(annualIncome * FURUSATO_TAX.healthRate);
  const nursingIns = age === '40to64' ? Math.floor(annualIncome * FURUSATO_TAX.nursingRate) : 0;
  const pensionBase = Math.min(monthlyIncome, FURUSATO_TAX.pensionMaxMonthly);
  const pension = Math.floor(pensionBase * FURUSATO_TAX.pensionRate * 12);
  const employmentIns = Math.floor(annualIncome * FURUSATO_TAX.employmentRate);
  const socialInsurance = healthIns + nursingIns + pension + employmentIns;

  // 給与所得控除
  let salaryDeduction = 0;
  for (const bracket of FURUSATO_TAX.salaryDeduction) {
    if (annualIncome <= bracket.limit) {
      salaryDeduction = bracket.calc(annualIncome);
      break;
    }
  }

  // 給与所得
  const salaryIncome = Math.max(0, annualIncome - salaryDeduction);

  // 所得控除
  const spouseDeduction = hasSpouse ? 330_000 : 0; // 住民税用の配偶者控除は33万
  const dependentDeduction = dependents * 330_000;
  const totalDeductions = FURUSATO_TAX.basicDeductionResident + socialInsurance + spouseDeduction + dependentDeduction;

  // 住民税の課税所得
  const residentTaxableIncome = Math.max(0, salaryIncome - totalDeductions);

  // 住民税所得割額
  const residentTaxIncome = Math.floor(residentTaxableIncome * FURUSATO_TAX.residentTaxRate);

  // 所得税の適用税率を特定
  // 所得税用の控除で課税所得を計算
  const basicDeductionIncome = 480_000;
  const spouseDeductionIncome = hasSpouse ? 380_000 : 0;
  const dependentDeductionIncome = dependents * 380_000;
  const incomeTaxDeductions = basicDeductionIncome + socialInsurance + spouseDeductionIncome + dependentDeductionIncome;
  const incomeTaxableIncome = Math.max(0, salaryIncome - incomeTaxDeductions);

  let incomeTaxRate = 0.05;
  for (const bracket of FURUSATO_TAX.incomeTaxBrackets) {
    if (incomeTaxableIncome <= bracket.limit) {
      incomeTaxRate = bracket.rate;
      break;
    }
  }

  // ふるさと納税の控除上限額（特例控除の上限 = 住民税所得割額の20%）
  // 上限額 = (住民税所得割額 × 20%) / (100% - 住民税率10% - 所得税率 × 102.1%) + 2,000
  const denominator = 1 - FURUSATO_TAX.residentTaxRate - incomeTaxRate * 1.021;
  let furusatoLimit = 0;
  if (denominator > 0) {
    furusatoLimit = Math.floor((residentTaxIncome * 0.20) / denominator) + 2_000;
  }

  // 自己負担額を除いた実質的な控除額
  const actualBenefit = Math.max(0, furusatoLimit - 2_000);

  // 内訳（概算）
  const incomeTaxDeduction = Math.floor(actualBenefit * incomeTaxRate * 1.021);
  const residentTaxDeduction = actualBenefit - incomeTaxDeduction;

  return {
    limit: furusatoLimit,
    actualBenefit,
    residentTaxDeduction: Math.max(0, residentTaxDeduction),
    incomeTaxDeduction: Math.max(0, incomeTaxDeduction),
    residentTaxIncome,
    incomeTaxRate,
    incomeTaxableIncome,
  };
}

// ============================================================
// おすすめ寄付金額のリスト生成
// ============================================================

function getSuggestedDonations(limit) {
  const suggestions = [];
  if (limit >= 5000) suggestions.push({ amount: 5000, label: '海鮮丼セット、地ビール詰め合わせ等' });
  if (limit >= 10000) suggestions.push({ amount: 10000, label: 'ブランド牛切り落とし、フルーツ盛り合わせ等' });
  if (limit >= 20000) suggestions.push({ amount: 20000, label: 'うなぎ蒲焼、カニしゃぶセット等' });
  if (limit >= 30000) suggestions.push({ amount: 30000, label: 'A5和牛ステーキ、高級フルーツ等' });
  if (limit >= 50000) suggestions.push({ amount: 50000, label: '定期便（お米12ヶ月等）、家電等' });
  if (limit >= 100000) suggestions.push({ amount: 100000, label: '旅行券、高級家電、定期便セット等' });
  return suggestions;
}

// ============================================================
// UI 制御
// ============================================================

const FDOM = {};

function initFurusatoDOM() {
  FDOM.incomeInput = document.getElementById('fIncomeInput');
  FDOM.incomeSlider = document.getElementById('fIncomeSlider');
  FDOM.incomeDisplay = document.getElementById('fIncomeDisplay');
  FDOM.spouseToggle = document.querySelectorAll('[data-fspouse]');
  FDOM.dependentsSelect = document.getElementById('fDependentsSelect');
  FDOM.ageToggle = document.querySelectorAll('[data-fage]');

  FDOM.resultLimit = document.getElementById('fResultLimit');
  FDOM.resultMonthly = document.getElementById('fResultMonthly');
  FDOM.resultBenefit = document.getElementById('fResultBenefit');
  FDOM.incomeTaxDeduction = document.getElementById('fIncomeTaxDeduction');
  FDOM.residentTaxDeduction = document.getElementById('fResidentTaxDeduction');
  FDOM.selfPayment = document.getElementById('fSelfPayment');
  FDOM.suggestionsContainer = document.getElementById('fSuggestions');
  FDOM.canvas = document.getElementById('fDonutChart');
}

function formatCurrency(value) {
  return Math.floor(value).toLocaleString('ja-JP');
}

// ============================================================
// ドーナツチャート
// ============================================================

function drawFurusatoChart(canvas, data) {
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const size = 200;

  canvas.width = size * dpr;
  canvas.height = size * dpr;
  canvas.style.width = size + 'px';
  canvas.style.height = size + 'px';
  ctx.scale(dpr, dpr);

  const cx = size / 2;
  const cy = size / 2;
  const outerRadius = 85;
  const innerRadius = 58;

  ctx.clearRect(0, 0, size, size);

  const total = data.reduce((sum, d) => sum + d.value, 0);
  if (total <= 0) return;

  let startAngle = -Math.PI / 2;

  data.forEach((item) => {
    const sliceAngle = (item.value / total) * Math.PI * 2;
    const endAngle = startAngle + sliceAngle;

    ctx.beginPath();
    ctx.arc(cx, cy, outerRadius, startAngle, endAngle);
    ctx.arc(cx, cy, innerRadius, endAngle, startAngle, true);
    ctx.closePath();
    ctx.fillStyle = item.color;
    ctx.fill();

    startAngle = endAngle;
  });

  ctx.fillStyle = '#f1f5f9';
  ctx.font = '700 12px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('控除内訳', cx, cy - 8);

  ctx.font = '600 11px Inter, sans-serif';
  ctx.fillStyle = '#94a3b8';
  ctx.fillText('自己負担 ¥2,000', cx, cy + 12);
}

// ============================================================
// メイン更新
// ============================================================

function getFurusatoOptions() {
  let hasSpouse = false;
  FDOM.spouseToggle.forEach(btn => {
    if (btn.classList.contains('active')) {
      hasSpouse = btn.dataset.fspouse === 'yes';
    }
  });
  const dependents = parseInt(FDOM.dependentsSelect.value) || 0;
  let age = 'under40';
  FDOM.ageToggle.forEach(btn => {
    if (btn.classList.contains('active')) {
      age = btn.dataset.fage;
    }
  });
  return { hasSpouse, dependents, age };
}

function updateFurusato() {
  const income = parseInt(FDOM.incomeInput.value) || 0;
  const annualIncome = income * 10000;
  const options = getFurusatoOptions();
  const result = calculateFurusatoLimit(annualIncome, options);

  FDOM.incomeSlider.value = income;
  FDOM.incomeDisplay.textContent = formatCurrency(income);

  FDOM.resultLimit.textContent = '¥' + formatCurrency(result.limit);
  FDOM.resultMonthly.textContent = formatCurrency(Math.floor(result.limit / 12));
  FDOM.resultBenefit.textContent = '¥' + formatCurrency(result.actualBenefit);
  FDOM.incomeTaxDeduction.textContent = '¥' + formatCurrency(result.incomeTaxDeduction);
  FDOM.residentTaxDeduction.textContent = '¥' + formatCurrency(result.residentTaxDeduction);
  FDOM.selfPayment.textContent = '¥2,000';

  // Chart
  const chartData = [
    { label: '所得税からの控除', value: result.incomeTaxDeduction, color: '#3b82f6' },
    { label: '住民税からの控除', value: result.residentTaxDeduction, color: '#6366f1' },
    { label: '自己負担', value: 2000, color: '#64748b' },
  ];
  drawFurusatoChart(FDOM.canvas, chartData);

  // Suggestions
  const suggestions = getSuggestedDonations(result.limit);
  let suggestionsHtml = '';
  suggestions.forEach(s => {
    suggestionsHtml += `
      <div class="suggestion-item">
        <div class="suggestion-amount">¥${formatCurrency(s.amount)}</div>
        <div class="suggestion-desc">${s.label}</div>
      </div>`;
  });
  FDOM.suggestionsContainer.innerHTML = suggestionsHtml;
}

// ============================================================
// イベントバインド
// ============================================================

function bindFurusatoEvents() {
  FDOM.incomeInput.addEventListener('input', updateFurusato);

  FDOM.incomeSlider.addEventListener('input', (e) => {
    FDOM.incomeInput.value = e.target.value;
    updateFurusato();
  });

  FDOM.spouseToggle.forEach(btn => {
    btn.addEventListener('click', () => {
      FDOM.spouseToggle.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      updateFurusato();
    });
  });

  FDOM.ageToggle.forEach(btn => {
    btn.addEventListener('click', () => {
      FDOM.ageToggle.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      updateFurusato();
    });
  });

  FDOM.dependentsSelect.addEventListener('change', updateFurusato);
}

// ============================================================
// 初期化
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
  initFurusatoDOM();
  bindFurusatoEvents();
  updateFurusato();
});
