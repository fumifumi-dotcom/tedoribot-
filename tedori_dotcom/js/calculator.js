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

  // 9. 会社負担分（B2Bモード用）
  const companyHealthInsurance = healthInsurance; // 労使折半
  const companyNursingInsurance = nursingInsurance; // 労使折半
  const companyPension = pension; // 労使折半
  const companyEmploymentInsurance = Math.floor(annualIncome * 0.0095); // 事業主負担（一般事業: 9.5/1000）
  const childContribution = Math.floor(pensionBase * 0.0036 * 12); // 子ども・子育て拠出金
  const companySocialInsurance = companyHealthInsurance + companyNursingInsurance + companyPension + companyEmploymentInsurance + childContribution;

  return {
    annualIncome,
    tedori,
    monthlyTedori,
    incomeTax,
    residentTax,
    socialInsurance,
    companySocialInsurance,
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
let isMonthlyMode = false;
let isB2bMode = false;

// 偏差値テーブルの簡易定義（年代別の平均や上位層目安）
const DEVIATION_TABLE = {
  'under40': { avg: 400_0000, sd: 150_0000 },
  '40to64':  { avg: 550_0000, sd: 200_0000 }
};

// リアルタイムタイマー制御用
let taxTimerId = null;
let currentTaxCounter = 0;
let taxPerSecond = 0;
let lastTimerUpdate = 0;

function calculateDeviation(income, ageBracket) {
  const table = DEVIATION_TABLE[ageBracket] || DEVIATION_TABLE['under40'];
  // 簡易な偏差値計算（(値 - 平均) / 標準偏差 * 10 + 50）
  let score = Math.round((income - table.avg) / table.sd * 10 + 50);
  score = Math.max(20, Math.min(80, score)); // 20〜80の間に収める
  
  let rankStr = "平均的な層";
  if (score >= 70) rankStr = "上位 2%";
  else if (score >= 65) rankStr = "上位 6%";
  else if (score >= 60) rankStr = "上位 15%";
  else if (score >= 55) rankStr = "上位 30%";
  else if (score < 40) rankStr = "下位 15%";
  else if (score < 45) rankStr = "下位 30%";

  // 生涯賃金のショート額を適当に算出（煽り用）
  const deficitBase = Math.max(0, table.avg - income);
  // 年齢に応じて残り年数を仮定 (under40: 30年, 40to64: 15年)
  const yearsLeft = ageBracket === 'under40' ? 30 : 15;
  const lifetimeDeficit = deficitBase * yearsLeft;
  
  // 老後破産確率（偏差値が低いほど高くする）
  let bankruptcyProb = 0;
  if (score < 45) bankruptcyProb = 87 - (score - 30) * 2;
  else if (score < 55) bankruptcyProb = 60 - (score - 45) * 1.5;
  else bankruptcyProb = 12;
  bankruptcyProb = Math.max(0, Math.min(99, Math.round(bankruptcyProb)));

  return { score, rankStr, lifetimeDeficit, bankruptcyProb };
}

function startTaxMeter(totalAnnualTax) {
  // 1年 = 31,536,000秒
  taxPerSecond = totalAnnualTax / 31536000;
  currentTaxCounter = 0;
  lastTimerUpdate = performance.now();

  const valEl = document.getElementById('realtimeTaxValue');
  if (!valEl) return;

  function tick(now) {
    const deltaMs = now - lastTimerUpdate;
    lastTimerUpdate = now;
    
    // 秒間増加量を足し込む
    currentTaxCounter += taxPerSecond * (deltaMs / 1000);
    valEl.textContent = currentTaxCounter.toFixed(2);
    
    taxTimerId = requestAnimationFrame(tick);
  }

  if (taxTimerId) cancelAnimationFrame(taxTimerId);
  taxTimerId = requestAnimationFrame(tick);
}

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

  DOM.percentNursing = document.getElementById('percentNursing');

  DOM.canvas = document.getElementById('donutChart');
  
  DOM.modeYear = document.getElementById('mode-year');
  DOM.modeMonth = document.getElementById('mode-month');
  DOM.resultLabelText = document.getElementById('result-label-text');
  DOM.dynamicRecommendation = document.getElementById('dynamic-recommendation');
  DOM.shareTwitterBtn = document.getElementById('share-twitter-btn');

  DOM.modeB2cBtn = document.getElementById('mode-b2c-btn');
  DOM.modeB2bBtn = document.getElementById('mode-b2b-btn');
  DOM.ctaSection = document.getElementById('cta-section');
  DOM.b2bCtaSection = document.getElementById('b2b-cta-section');
}

function formatCurrency(value) {
  return Math.floor(value).toLocaleString('ja-JP');
}

function formatMan(value) {
  return Math.floor(value / 10000);
}

// ============================================================
// ドーナツチャートの描画 (Chart.js版)
// ============================================================

let myChart = null;

function drawDonutChart(canvas, data, rate) {
  const ctx = canvas.getContext('2d');
  
  const labels = data.map(d => d.label);
  const values = data.map(d => d.value);
  const colors = data.map(d => d.color);

  // 初回のみChartを生成、以降はUpdateでアニメーション変化
  if (!myChart) {
    // センターテキストを描画するためのカスタムプラグイン
    const centerTextPlugin = {
      id: 'centerText',
      beforeDraw: function(chart) {
        if (chart.config.options.elements.center) {
          const ctxC = chart.ctx;
          const centerConfig = chart.config.options.elements.center;
          const text = centerConfig.text;
          
          ctxC.save();
          // ライトテーマ用のネイビー文字
          ctxC.fillStyle = '#1e293b'; 
          ctxC.font = 'bold 24px Inter, sans-serif';
          ctxC.textAlign = 'center';
          ctxC.textBaseline = 'middle';
          
          const centerX = (chart.chartArea.left + chart.chartArea.right) / 2;
          const centerY = (chart.chartArea.top + chart.chartArea.bottom) / 2;
          
          ctxC.fillText(text, centerX, centerY);
          ctxC.restore();
        }
      }
    };

    Chart.register(centerTextPlugin);

    myChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: values,
          backgroundColor: colors,
          borderWidth: 2,
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        animation: {
          animateScale: true,
          animateRotate: true,
          duration: 800,
          easing: 'easeOutQuart'
        },
        plugins: {
          legend: {
            display: false // ツールチップのみで凡例非表示
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                let label = context.label || '';
                if (label) {
                  label += ': ';
                }
                if (context.parsed !== null) {
                  label += new Intl.NumberFormat('ja-JP', { style: 'currency', currency: 'JPY' }).format(context.parsed);
                }
                return label;
              }
            }
          }
        },
        elements: {
          center: {
            text: rate
          }
        }
      }
    });
  } else {
    // データ更新（アニメーションでヌルヌル動く）
    myChart.data.datasets[0].data = values;
    myChart.options.elements.center.text = rate;
    myChart.update();
  }
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
  const divisor = isMonthlyMode ? 12 : 1;
  
  if (!isB2bMode) {
    DOM.resultLabelText.textContent = isMonthlyMode ? '1ヶ月分の手取り概算' : '年間の手取り額';
    DOM.resultTedori.textContent = '¥' + formatCurrency(result.tedori / divisor);
    DOM.resultMonthly.textContent = formatCurrency(result.monthlyTedori);
    DOM.resultRate.textContent = result.tedoriRate.toFixed(1);
    document.querySelector('.result-sub').innerHTML = `手取り率 <strong><span id="resultRate">${result.tedoriRate.toFixed(1)}</span>%</strong> ｜月額 <strong>¥<span id="resultMonthly">${formatCurrency(result.monthlyTedori)}</span></strong>`;
  } else {
    DOM.resultLabelText.textContent = isMonthlyMode ? '1ヶ月分の総人件費 (会社負担)' : '年間の総人件費 (会社負担)';
    const totalCost = result.annualIncome + result.companySocialInsurance;
    DOM.resultTedori.textContent = '¥' + formatCurrency(totalCost / divisor);
    document.querySelector('.result-sub').innerHTML = `見えない法定福利費 <strong>¥${formatCurrency(result.companySocialInsurance / divisor)}</strong>`;
  }
  DOM.monthlyValue.textContent = '¥' + formatCurrency(result.monthlyTedori);

  // Breakdown
  DOM.breakdownIncomeTax.textContent = '¥' + formatCurrency(result.incomeTax / divisor);
  DOM.breakdownResidentTax.textContent = '¥' + formatCurrency(result.residentTax / divisor);
  DOM.breakdownHealth.textContent = '¥' + formatCurrency(result.healthInsurance / divisor);
  DOM.breakdownPension.textContent = '¥' + formatCurrency(result.pension / divisor);
  DOM.breakdownEmployment.textContent = '¥' + formatCurrency(result.employmentInsurance / divisor);

  // Nursing insurance row visibility
  if (result.nursingInsurance > 0) {
    DOM.breakdownNursingRow.style.display = 'flex';
    DOM.breakdownNursing.textContent = '¥' + formatCurrency(result.nursingInsurance / divisor);
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

  let chartData;
  let centerAmountLabel;
  if (!isB2bMode) {
    chartData = [
      { label: '手取り', value: Math.floor(result.tedori / divisor), color: '#10b981' },
      { label: '所得税', value: Math.floor(result.incomeTax / divisor), color: '#f43f5e' },
      { label: '住民税', value: Math.floor(result.residentTax / divisor), color: '#ec4899' },
      { label: '社会保険料', value: Math.floor(result.socialInsurance / divisor), color: '#f59e0b' }
    ];
    centerAmountLabel = '¥' + formatCurrency(Math.floor(result.tedori / divisor));
  } else {
    chartData = [
      { label: '社員の手取り', value: Math.floor(result.tedori / divisor), color: '#10b981' },
      { label: '社員負担分(税+社保)', value: Math.floor((result.incomeTax + result.residentTax + result.socialInsurance) / divisor), color: '#f43f5e' },
      { label: '会社負担の法定福利費', value: Math.floor(result.companySocialInsurance / divisor), color: '#3b82f6' }
    ];
    const totalCost = result.annualIncome + result.companySocialInsurance;
    centerAmountLabel = '¥' + formatCurrency(Math.floor(totalCost / divisor));
  }

  drawDonutChart(DOM.canvas, chartData, centerAmountLabel);

  // 動的CTAの呼び出し
  if (typeof window.renderDynamicRecommendation === 'function') {
    window.renderDynamicRecommendation(annualIncome);
  }

  // ==== 診断メッセージとシェア機能 ====
  if (DOM.dynamicRecommendation && DOM.shareTwitterBtn) {
    const totalTax = result.incomeTax + result.residentTax + result.socialInsurance;
    const isZeroTax = totalTax <= 0;

    // 偏差値と生涯欠損額のロジック
    const deviation = calculateDeviation(annualIncome, options.age);

    // リアルタイム税金メーターの起動
    startTaxMeter(totalTax);

    let diagnosticHtml = `<div style="background: #111827; border: 2px solid #ef4444; padding: 24px; border-radius: 12px; margin-top: 16px; box-shadow: 0 10px 25px -5px rgba(239, 68, 68, 0.3); color: white; text-align: center; position: relative; overflow: hidden;">`;
    diagnosticHtml += `<div style="position: absolute; top: 0; left: 0; right: 0; background: #ef4444; color: white; font-weight: 900; font-size: 14px; padding: 4px 0; letter-spacing: 2px;">⚠️ 絶望メーター ⚠️</div>`;
    
    if (deviation.score < 50 && deviation.lifetimeDeficit > 0) {
      // 絶望ルート
      diagnosticHtml += `<div style="margin-top: 24px; margin-bottom: 8px; font-size: 14px; color: #9ca3af;">同年代と比較したあなたの給与偏差値</div>`;
      diagnosticHtml += `<div style="font-size: 48px; font-weight: 900; color: #ef4444; line-height: 1; margin-bottom: 4px;">${deviation.score}</div>`;
      diagnosticHtml += `<div style="font-size: 16px; font-weight: bold; margin-bottom: 24px;">（同年代の ${deviation.rankStr}）</div>`;
      
      diagnosticHtml += `<div style="background: rgba(239,68,68,0.1); border-radius: 8px; padding: 16px; margin-bottom: 24px; text-align: left; border: 1px solid rgba(239,68,68,0.3);">`;
      diagnosticHtml += `<p style="margin: 0 0 8px; font-size: 14px; color: #f87171; font-weight: bold;">🚨 【警告】生涯手取りの欠損額</p>`;
      diagnosticHtml += `<div style="font-size: 28px; font-weight: 900; color: white;">約 -${formatMan(deviation.lifetimeDeficit)}万円</div>`;
      diagnosticHtml += `<p style="margin: 8px 0 0; font-size: 13px; color: #d1d5db;">このまま放置した場合、同年代の平均的な生活レベルからこれだけのお金が不足します。<strong style="color: #f87171;">老後破産確率は推定 ${deviation.bankruptcyProb}%</strong> です。</p>`;
      diagnosticHtml += `</div>`;
      
      // 解決策としてのキャリア相談CTA
      diagnosticHtml += `<p style="font-size: 13px; color: #9ca3af; margin-bottom: 12px;">※絶望的な状況を「無料」で回避する唯一の手段↓</p>`;
      diagnosticHtml += `<a href="https://px.a8.net/svt/ejp?a8mat=4B1OTT+6P4KS2+47GS+5YRHE" style="display: block; width: 100%; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; text-decoration: none; padding: 18px; border-radius: 12px; font-weight: 900; font-size: 17px; margin-bottom: 12px; transition: transform 0.2s; box-shadow: 0 8px 15px rgba(16,185,129,0.3);" target="_blank" rel="noopener sponsored" onmouseover="this.style.transform='scale(1.02)';" onmouseout="this.style.transform='none';">👨‍💻 プロに無料でキャリア相談し、年収を上げる</a>`;
      diagnosticHtml += `<p style="font-size: 11px; color: #6b7280; text-align: right; margin-top: 4px;">PR</p>`;
    } else {
      // 平均以上ルート
      diagnosticHtml += `<div style="margin-top: 24px; margin-bottom: 8px; font-size: 14px; color: #9ca3af;">同年代と比較したあなたの給与偏差値</div>`;
      diagnosticHtml += `<div style="font-size: 48px; font-weight: 900; color: #10b981; line-height: 1; margin-bottom: 4px;">${deviation.score}</div>`;
      diagnosticHtml += `<div style="font-size: 16px; font-weight: bold; margin-bottom: 24px;">（同年代の ${deviation.rankStr}）</div>`;
      diagnosticHtml += `<p style="margin: 8px 0 24px; color: #d1d5db; font-size: 14px;">あなたは平均以上です。さらに資産を爆発的に増やすために、非課税のNISAを活用しましょう。</p>`;
      diagnosticHtml += `<a href="https://px.a8.net/svt/ejp?a8mat=4B1PLP+ACPDGY+3XCC+6AZAQ" style="display: block; width: 100%; background: #f59e0b; color: white; text-decoration: none; padding: 18px; border-radius: 12px; font-weight: 900; font-size: 17px; margin-bottom: 12px; transition: transform 0.2s;" target="_blank" rel="noopener sponsored" onmouseover="this.style.transform='scale(1.02)';" onmouseout="this.style.transform='none';">📈 手数料最安の松井証券でNISAを始める</a>`;
    }
    
    diagnosticHtml += `</div>`;
    DOM.dynamicRecommendation.innerHTML = diagnosticHtml;
    DOM.dynamicRecommendation.style.display = 'block';

    const shareRank = isZeroTax ? "無税の神" : `偏差値${deviation.score}(${deviation.rankStr})`;
    const deficitText = deviation.lifetimeDeficit > 0 ? `\n生涯手取りは同年代より -${formatMan(deviation.lifetimeDeficit)}万円不足😇` : '';
    const shareText = `【🚨絶望の給与明細🚨】\n私の社畜偏差値：${shareRank}${deficitText}\n\n手取り率（年収${formatMan(annualIncome)}万円）は【 ${(result.tedoriRate).toFixed(1)}% 】でした。\n\n#手取り計算 #絶望メーター\n`;
    const shareUrl = "https://tedori-keisan.com/";
    DOM.shareTwitterBtn.href = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(shareUrl)}`;
  }
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

  // 月額・年額モード切替
  if (DOM.modeYear && DOM.modeMonth) {
    DOM.modeYear.addEventListener('click', () => {
      isMonthlyMode = false;
      DOM.modeYear.classList.add('active');
      DOM.modeYear.style.background = 'var(--bg-card)';
      DOM.modeYear.style.color = 'var(--text-primary)';
      DOM.modeYear.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
      DOM.modeMonth.classList.remove('active');
      DOM.modeMonth.style.background = 'transparent';
      DOM.modeMonth.style.color = 'var(--text-muted)';
      DOM.modeMonth.style.boxShadow = 'none';
      update();
    });
    DOM.modeMonth.addEventListener('click', () => {
      isMonthlyMode = true;
      DOM.modeMonth.classList.add('active');
      DOM.modeMonth.style.background = 'var(--bg-card)';
      DOM.modeMonth.style.color = 'var(--text-primary)';
      DOM.modeMonth.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
      DOM.modeYear.classList.remove('active');
      DOM.modeYear.style.background = 'transparent';
      DOM.modeYear.style.color = 'var(--text-muted)';
      DOM.modeYear.style.boxShadow = 'none';
      update();
    });
  }

  // B2C / B2B モード切替
  if (DOM.modeB2cBtn && DOM.modeB2bBtn) {
    DOM.modeB2cBtn.addEventListener('click', () => {
      isB2bMode = false;
      DOM.modeB2cBtn.style.background = 'var(--accent-blue)';
      DOM.modeB2cBtn.style.color = 'white';
      DOM.modeB2cBtn.style.boxShadow = '0 2px 4px rgba(59,130,246,0.3)';
      DOM.modeB2bBtn.style.background = 'transparent';
      DOM.modeB2bBtn.style.color = 'var(--text-secondary)';
      DOM.modeB2bBtn.style.boxShadow = 'none';
      if(DOM.ctaSection) DOM.ctaSection.style.display = 'block';
      if(DOM.b2bCtaSection) DOM.b2bCtaSection.style.display = 'block'; // Block CTA at bottom, wait, we want to hide it.
      if(DOM.b2bCtaSection) DOM.b2bCtaSection.style.display = 'none';
      update();
    });
    DOM.modeB2bBtn.addEventListener('click', () => {
      isB2bMode = true;
      DOM.modeB2bBtn.style.background = 'var(--accent-blue)';
      DOM.modeB2bBtn.style.color = 'white';
      DOM.modeB2bBtn.style.boxShadow = '0 2px 4px rgba(59,130,246,0.3)';
      DOM.modeB2cBtn.style.background = 'transparent';
      DOM.modeB2cBtn.style.color = 'var(--text-secondary)';
      DOM.modeB2cBtn.style.boxShadow = 'none';
      if(DOM.ctaSection) DOM.ctaSection.style.display = 'none';
      if(DOM.b2bCtaSection) DOM.b2bCtaSection.style.display = 'block';
      update();
    });
  }
}

// ============================================================
// 初期化
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
  initDOM();
  bindEvents();
  update();
});
