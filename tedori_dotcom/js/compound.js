/**
 * 複利計算（積立NISA）シミュレーター - 計算エンジン & UI制御
 * 毎月の積立額・利回り・期間から将来の資産額を計算
 */

// ============================================================
// 複利計算ロジック
// ============================================================

function calculateCompoundInterest(monthlyAmount, annualRate, years) {
  const monthlyRate = annualRate / 100 / 12;
  const months = years * 12;

  // 積立元本
  const totalDeposit = monthlyAmount * months;

  // 最終資産額（毎月積立の複利計算）
  let finalAmount;
  if (monthlyRate === 0) {
    finalAmount = totalDeposit;
  } else {
    finalAmount = monthlyAmount * ((Math.pow(1 + monthlyRate, months) - 1) / monthlyRate) * (1 + monthlyRate);
  }

  // 運用益
  const totalReturn = finalAmount - totalDeposit;

  // 年ごとのデータ（グラフ用）
  const yearlyData = [];
  for (let y = 0; y <= years; y++) {
    const m = y * 12;
    const deposit = monthlyAmount * m;
    let amount;
    if (monthlyRate === 0) {
      amount = deposit;
    } else {
      amount = m === 0 ? 0 : monthlyAmount * ((Math.pow(1 + monthlyRate, m) - 1) / monthlyRate) * (1 + monthlyRate);
    }
    yearlyData.push({
      year: y,
      deposit: Math.floor(deposit),
      amount: Math.floor(amount),
      return: Math.floor(amount - deposit),
    });
  }

  return {
    totalDeposit: Math.floor(totalDeposit),
    finalAmount: Math.floor(finalAmount),
    totalReturn: Math.floor(totalReturn),
    returnRate: totalDeposit > 0 ? ((totalReturn / totalDeposit) * 100).toFixed(1) : '0',
    yearlyData,
  };
}

// ============================================================
// 棒グラフの描画（Canvas API）
// ============================================================

function drawBarChart(canvas, yearlyData) {
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const width = canvas.parentElement.offsetWidth || 600;
  const height = 280;

  canvas.width = width * dpr;
  canvas.height = height * dpr;
  canvas.style.width = width + 'px';
  canvas.style.height = height + 'px';
  ctx.scale(dpr, dpr);
  ctx.clearRect(0, 0, width, height);

  if (yearlyData.length <= 1) return;

  const padding = { top: 20, right: 20, bottom: 40, left: 60 };
  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;

  // 最大値
  const maxVal = Math.max(...yearlyData.map(d => d.amount)) || 1;

  // データポイントをフィルタ（年数が多い場合は間引く）
  let filtered = yearlyData;
  if (yearlyData.length > 20) {
    const step = Math.ceil(yearlyData.length / 15);
    filtered = yearlyData.filter((_, i) => i === 0 || i === yearlyData.length - 1 || i % step === 0);
  }

  const barWidth = Math.max(8, Math.min(40, (chartW / filtered.length) * 0.6));
  const gap = (chartW - barWidth * filtered.length) / (filtered.length + 1);

  // Y軸のグリッド線
  ctx.strokeStyle = 'rgba(255,255,255,0.06)';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = padding.top + (chartH / 4) * i;
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(width - padding.right, y);
    ctx.stroke();

    // Y軸ラベル
    const val = maxVal - (maxVal / 4) * i;
    ctx.fillStyle = '#64748b';
    ctx.font = '11px Inter, sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText(formatManYen(val), padding.left - 8, y + 4);
  }

  // バーの描画
  filtered.forEach((d, i) => {
    const x = padding.left + gap + i * (barWidth + gap);

    // 元本部分（グレー）
    const depositH = (d.deposit / maxVal) * chartH;
    const depositY = padding.top + chartH - depositH;
    ctx.fillStyle = 'rgba(100, 116, 139, 0.5)';
    roundedRect(ctx, x, depositY, barWidth, depositH, 3);

    // 運用益部分（グリーン）
    const returnH = (d.return / maxVal) * chartH;
    const returnY = depositY - returnH;
    if (d.return > 0) {
      const grad = ctx.createLinearGradient(x, returnY, x, depositY);
      grad.addColorStop(0, '#10b981');
      grad.addColorStop(1, '#059669');
      ctx.fillStyle = grad;
      roundedRect(ctx, x, returnY, barWidth, returnH, 3);
    }

    // X軸ラベル
    ctx.fillStyle = '#64748b';
    ctx.font = '11px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(d.year + '年', x + barWidth / 2, height - padding.bottom + 20);
  });
}

function roundedRect(ctx, x, y, w, h, r) {
  if (h <= 0) return;
  r = Math.min(r, h / 2, w / 2);
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h);
  ctx.lineTo(x, y + h);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
  ctx.fill();
}

function formatManYen(val) {
  if (val >= 100_000_000) return (val / 100_000_000).toFixed(1) + '億';
  if (val >= 10_000) return Math.floor(val / 10_000) + '万';
  return Math.floor(val).toLocaleString();
}

function formatCurrency(val) {
  return Math.floor(val).toLocaleString('ja-JP');
}

// ============================================================
// UI制御
// ============================================================

const CDOM = {};

function initCompoundDOM() {
  CDOM.monthlyInput = document.getElementById('cMonthlyInput');
  CDOM.monthlySlider = document.getElementById('cMonthlySlider');
  CDOM.monthlyDisplay = document.getElementById('cMonthlyDisplay');

  CDOM.rateInput = document.getElementById('cRateInput');
  CDOM.rateSlider = document.getElementById('cRateSlider');
  CDOM.rateDisplay = document.getElementById('cRateDisplay');

  CDOM.yearsInput = document.getElementById('cYearsInput');
  CDOM.yearsSlider = document.getElementById('cYearsSlider');
  CDOM.yearsDisplay = document.getElementById('cYearsDisplay');

  CDOM.resultFinal = document.getElementById('cResultFinal');
  CDOM.resultDeposit = document.getElementById('cResultDeposit');
  CDOM.resultReturn = document.getElementById('cResultReturn');
  CDOM.resultRate = document.getElementById('cResultRate');

  CDOM.canvas = document.getElementById('cBarChart');
}

function updateCompound() {
  const monthly = (parseInt(CDOM.monthlyInput.value) || 0) * 10000;
  const rate = parseFloat(CDOM.rateInput.value) || 0;
  const years = parseInt(CDOM.yearsInput.value) || 0;

  CDOM.monthlySlider.value = CDOM.monthlyInput.value;
  CDOM.monthlyDisplay.textContent = formatCurrency(parseInt(CDOM.monthlyInput.value) || 0);

  CDOM.rateSlider.value = CDOM.rateInput.value;
  CDOM.rateDisplay.textContent = rate.toFixed(1);

  CDOM.yearsSlider.value = CDOM.yearsInput.value;
  CDOM.yearsDisplay.textContent = years;

  const result = calculateCompoundInterest(monthly, rate, years);

  CDOM.resultFinal.textContent = '¥' + formatCurrency(result.finalAmount);
  CDOM.resultDeposit.textContent = '¥' + formatCurrency(result.totalDeposit);
  CDOM.resultReturn.textContent = '¥' + formatCurrency(result.totalReturn);
  CDOM.resultRate.textContent = result.returnRate;

  drawBarChart(CDOM.canvas, result.yearlyData);
}

function bindCompoundEvents() {
  CDOM.monthlyInput.addEventListener('input', updateCompound);
  CDOM.monthlySlider.addEventListener('input', (e) => {
    CDOM.monthlyInput.value = e.target.value;
    updateCompound();
  });

  CDOM.rateInput.addEventListener('input', updateCompound);
  CDOM.rateSlider.addEventListener('input', (e) => {
    CDOM.rateInput.value = e.target.value;
    updateCompound();
  });

  CDOM.yearsInput.addEventListener('input', updateCompound);
  CDOM.yearsSlider.addEventListener('input', (e) => {
    CDOM.yearsInput.value = e.target.value;
    updateCompound();
  });

  // リサイズ時にチャートを再描画
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(updateCompound, 200);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initCompoundDOM();
  bindCompoundEvents();
  updateCompound();
});
