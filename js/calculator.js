/**
 * 手取り計算シミュレーター - 計算エンジン & UI制御
 * 2026年度（令和8年度）の税率・社会保険料率に基づく
 */

// ============================================================
// 税率・料率テーブル（更新しやすいように分離）
// ============================================================

const TAX_RATES = {
  // 給与所得控除（2026年度）
  salaryDeduction: [
    { limit: 1_625_000, calc: () => 550_000 },
    { limit: 1_800_000, calc: (income) => income * 0.4 - 100_000 },
    { limit: 3_600_000, calc: (income) => income * 0.3 + 80_000 },
    { limit: 6_600_000, calc: (income) => income * 0.2 + 440_000 },
    { limit: 8_500_000, calc: (income) => income * 0.1 + 1_100_000 },
    { limit: Infinity, calc: () => 1_950_000 },
  ],

  // 所得税率（累進課税）
  incomeTax: [
    { limit: 1_950_000, rate: 0.05, deduction: 0 },
    { limit: 3_300_000, rate: 0.10, deduction: 97_500 },
    { limit: 6_950_000, rate: 0.20, deduction: 427_500 },
    { limit: 9_000_000, rate: 0.23, deduction: 636_000 },
    { limit: 18_000_000, rate: 0.33, deduction: 1_536_000 },
    { limit: 40_000_000, rate: 0.40, deduction: 2_796_000 },
    { limit: Infinity, rate: 0.45, deduction: 4_796_000 },
  ],

  // 基礎控除（所得税用）
  basicDeductionIncomeTax: 480_000,
  // 基礎控除（住民税用）
  basicDeductionResidentTax: 430_000,

  // 住民税率
  residentTaxRate: 0.10,
  // 住民税 均等割
  residentTaxFixed: 5_000,

  // 復興特別所得税率
  reconstructionTaxRate: 0.021,

  // 社会保険料率（従業員負担分）
  healthInsuranceRate: 0.04905, // 健康保険料率（東京都・協会けんぽ 2026年度想定）
  nursingInsuranceRate: 0.008,  // 介護保険料率（40歳以上）
  pensionRate: 0.0915,          // 厚生年金保険料率
  employmentInsuranceRate: 0.006, // 雇用保険料率

  // 厚生年金の標準報酬月額上限
  pensionMaxMonthly: 650_000,
};

// ============================================================
// 計算ロジック
// ============================================================

function calculateTedori(annualIncome, options = {}) {
  const {
    hasSpouse = false,
    dependents = 0,
    age = 'under40', // 'under40', '40to64', '65plus'
  } = options;

  if (annualIncome <= 0) {
    return {
      annualIncome: 0, tedori: 0, monthlyTedori: 0,
      incomeTax: 0, residentTax: 0, socialInsurance: 0,
      healthInsurance: 0, pension: 0, employmentInsurance: 0, nursingInsurance: 0,
      tedoriRate: 0,
    };
  }

  // 1. 社会保険料の計算
  const monthlyIncome = annualIncome / 12;

  // 健康保険料
  const healthInsurance = Math.floor(annualIncome * TAX_RATES.healthInsuranceRate);

  // 介護保険料（40歳以上のみ）
  const nursingInsurance = age === '40to64'
    ? Math.floor(annualIncome * TAX_RATES.nursingInsuranceRate)
    : 0;

  // 厚生年金保険料（上限あり）
  const pensionBase = Math.min(monthlyIncome, TAX_RATES.pensionMaxMonthly);
  const pension = Math.floor(pensionBase * TAX_RATES.pensionRate * 12);

  // 雇用保険料
  const employmentInsurance = Math.floor(annualIncome * TAX_RATES.employmentInsuranceRate);

  const socialInsurance = healthInsurance + nursingInsurance + pension + employmentInsurance;

  // 2. 給与所得控除
  let salaryDeduction = 0;
  for (const bracket of TAX_RATES.salaryDeduction) {
    if (annualIncome <= bracket.limit) {
      salaryDeduction = bracket.calc(annualIncome);
      break;
    }
  }

  // 3. 所得金額
  const incomeAfterSalaryDeduction = Math.max(0, annualIncome - salaryDeduction);

  // 4. 所得控除の合計
  const deductions = TAX_RATES.basicDeductionIncomeTax + socialInsurance;
  // 配偶者控除（簡易: 38万円）
  const spouseDeduction = hasSpouse ? 380_000 : 0;
  // 扶養控除（簡易: 1人あたり38万円）
  const dependentDeduction = dependents * 380_000;

  const totalDeductions = deductions + spouseDeduction + dependentDeduction;

  // 5. 課税所得（所得税用）
  const taxableIncome = Math.max(0, incomeAfterSalaryDeduction - totalDeductions);

  // 6. 所得税の計算（累進課税）
  let incomeTax = 0;
  for (const bracket of TAX_RATES.incomeTax) {
    if (taxableIncome <= bracket.limit) {
      incomeTax = Math.floor(taxableIncome * bracket.rate - bracket.deduction);
      break;
    }
  }

  // 復興特別所得税
  const reconstructionTax = Math.floor(incomeTax * TAX_RATES.reconstructionTaxRate);
  incomeTax = incomeTax + reconstructionTax;

  // 7. 住民税の計算
  const residentDeductions = TAX_RATES.basicDeductionResidentTax + socialInsurance + spouseDeduction + dependentDeduction;
  const residentTaxableIncome = Math.max(0, incomeAfterSalaryDeduction - residentDeductions);
  const residentTax = Math.floor(residentTaxableIncome * TAX_RATES.residentTaxRate) + TAX_RATES.residentTaxFixed;

  // 8. 手取り額
  const totalDeducted = incomeTax + residentTax + socialInsurance;
  const tedori = Math.max(0, annualIncome - totalDeducted);
  const monthlyTedori = Math.floor(tedori / 12);
  const tedoriRate = annualIncome > 0 ? (tedori / annualIncome * 100) : 0;

  return {
    annualIncome,
    tedori,
    monthlyTedori,
    incomeTax,
    residentTax,
    socialInsurance,
    healthInsurance,
    nursingInsurance,
    pension,
    employmentInsurance,
    tedoriRate,
    salaryDeduction,
    taxableIncome,
  };
}

// ============================================================
// UI 制御
// ============================================================

const DOM = {};

function initDOM() {
  DOM.incomeInput = document.getElementById('incomeInput');
  DOM.incomeSlider = document.getElementById('incomeSlider');
  DOM.incomeDisplay = document.getElementById('incomeDisplay');
  DOM.spouseToggle = document.querySelectorAll('[data-spouse]');
  DOM.dependentsSelect = document.getElementById('dependentsSelect');
  DOM.ageToggle = document.querySelectorAll('[data-age]');

  DOM.resultTedori = document.getElementById('resultTedori');
  DOM.resultMonthly = document.getElementById('resultMonthly');
  DOM.resultRate = document.getElementById('resultRate');
  DOM.monthlyValue = document.getElementById('monthlyValue');

  DOM.breakdownIncomeTax = document.getElementById('breakdownIncomeTax');
  DOM.breakdownResidentTax = document.getElementById('breakdownResidentTax');
  DOM.breakdownHealth = document.getElementById('breakdownHealth');
  DOM.breakdownPension = document.getElementById('breakdownPension');
  DOM.breakdownEmployment = document.getElementById('breakdownEmployment');
  DOM.breakdownNursing = document.getElementById('breakdownNursing');
  DOM.breakdownNursingRow = document.getElementById('breakdownNursingRow');

  DOM.percentIncomeTax = document.getElementById('percentIncomeTax');
  DOM.percentResidentTax = document.getElementById('percentResidentTax');
  DOM.percentHealth = document.getElementById('percentHealth');
  DOM.percentPension = document.getElementById('percentPension');
  DOM.percentEmployment = document.getElementById('percentEmployment');
  DOM.percentNursing = document.getElementById('percentNursing');

  DOM.canvas = document.getElementById('donutChart');
}

function formatCurrency(value) {
  return Math.floor(value).toLocaleString('ja-JP');
}

function formatMan(value) {
  return Math.floor(value / 10000);
}

// ============================================================
// ドーナツチャートの描画
// ============================================================

function drawDonutChart(canvas, data) {
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const size = 220;

  canvas.width = size * dpr;
  canvas.height = size * dpr;
  canvas.style.width = size + 'px';
  canvas.style.height = size + 'px';
  ctx.scale(dpr, dpr);

  const cx = size / 2;
  const cy = size / 2;
  const outerRadius = 95;
  const innerRadius = 65;

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

  // Center text
  ctx.fillStyle = '#f1f5f9';
  ctx.font = '700 13px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('手取り率', cx, cy - 10);

  ctx.font = '800 24px Inter, sans-serif';
  const tedoriRate = data.find(d => d.label === '手取り');
  const rate = tedoriRate ? ((tedoriRate.value / total) * 100).toFixed(1) : '0';
  ctx.fillText(rate + '%', cx, cy + 16);
}

// ============================================================
// メイン更新ロジック
// ============================================================

function getOptions() {
  let hasSpouse = false;
  DOM.spouseToggle.forEach(btn => {
    if (btn.classList.contains('active')) {
      hasSpouse = btn.dataset.spouse === 'yes';
    }
  });

  const dependents = parseInt(DOM.dependentsSelect.value) || 0;

  let age = 'under40';
  DOM.ageToggle.forEach(btn => {
    if (btn.classList.contains('active')) {
      age = btn.dataset.age;
    }
  });

  return { hasSpouse, dependents, age };
}

function update() {
  const income = parseInt(DOM.incomeInput.value) || 0;
  const annualIncome = income * 10000; // 万円 → 円
  const options = getOptions();
  const result = calculateTedori(annualIncome, options);

  // Sync slider
  DOM.incomeSlider.value = income;
  DOM.incomeDisplay.textContent = formatCurrency(income);

  // Results
  DOM.resultTedori.textContent = '¥' + formatCurrency(result.tedori);
  DOM.resultMonthly.textContent = formatCurrency(result.monthlyTedori);
  DOM.resultRate.textContent = result.tedoriRate.toFixed(1);
  DOM.monthlyValue.textContent = '¥' + formatCurrency(result.monthlyTedori);

  // Breakdown
  DOM.breakdownIncomeTax.textContent = '¥' + formatCurrency(result.incomeTax);
  DOM.breakdownResidentTax.textContent = '¥' + formatCurrency(result.residentTax);
  DOM.breakdownHealth.textContent = '¥' + formatCurrency(result.healthInsurance);
  DOM.breakdownPension.textContent = '¥' + formatCurrency(result.pension);
  DOM.breakdownEmployment.textContent = '¥' + formatCurrency(result.employmentInsurance);

  // Nursing insurance row visibility
  if (result.nursingInsurance > 0) {
    DOM.breakdownNursingRow.style.display = 'flex';
    DOM.breakdownNursing.textContent = '¥' + formatCurrency(result.nursingInsurance);
    DOM.percentNursing.textContent = (result.nursingInsurance / annualIncome * 100).toFixed(1) + '%';
  } else {
    DOM.breakdownNursingRow.style.display = 'none';
  }

  // Percentages
  if (annualIncome > 0) {
    DOM.percentIncomeTax.textContent = (result.incomeTax / annualIncome * 100).toFixed(1) + '%';
    DOM.percentResidentTax.textContent = (result.residentTax / annualIncome * 100).toFixed(1) + '%';
    DOM.percentHealth.textContent = (result.healthInsurance / annualIncome * 100).toFixed(1) + '%';
    DOM.percentPension.textContent = (result.pension / annualIncome * 100).toFixed(1) + '%';
    DOM.percentEmployment.textContent = (result.employmentInsurance / annualIncome * 100).toFixed(1) + '%';
  }

  // Donut Chart
  const chartData = [
    { label: '手取り', value: result.tedori, color: '#10b981' },
    { label: '所得税', value: result.incomeTax, color: '#3b82f6' },
    { label: '住民税', value: result.residentTax, color: '#6366f1' },
    { label: '健康保険', value: result.healthInsurance + result.nursingInsurance, color: '#f59e0b' },
    { label: '厚生年金', value: result.pension, color: '#ef4444' },
    { label: '雇用保険', value: result.employmentInsurance, color: '#8b5cf6' },
  ];

  drawDonutChart(DOM.canvas, chartData);
}

// ============================================================
// イベントバインド
// ============================================================

function bindEvents() {
  // 年収入力
  DOM.incomeInput.addEventListener('input', () => {
    update();
  });

  // スライダー
  DOM.incomeSlider.addEventListener('input', (e) => {
    DOM.incomeInput.value = e.target.value;
    update();
  });

  // 配偶者トグル
  DOM.spouseToggle.forEach(btn => {
    btn.addEventListener('click', () => {
      DOM.spouseToggle.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      update();
    });
  });

  // 年齢トグル
  DOM.ageToggle.forEach(btn => {
    btn.addEventListener('click', () => {
      DOM.ageToggle.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      update();
    });
  });

  // 扶養家族セレクト
  DOM.dependentsSelect.addEventListener('change', update);
}

// ============================================================
// 初期化
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
  initDOM();
  bindEvents();
  update();
});
