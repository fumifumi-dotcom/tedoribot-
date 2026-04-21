/**
 * 家賃・生活費シミュレーター ロジック
 */

document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('monthIncomeInput');
  const slider = document.getElementById('monthIncomeSlider');
  const display = document.getElementById('monthIncomeDisplay');
  
  const resultRent = document.getElementById('resultRent');
  const resultSaving = document.getElementById('resultSaving');
  const breakdownList = document.getElementById('lifestyle-breakdown');
  
  let lifestyleChart = null;
  
  // 生活費の黄金比率（合計100%）
  const RATIOS = [
    { id: 'rent', label: '家賃・住居費', percent: 30, color: '#10b981' },
    { id: 'food', label: '食費', percent: 15, color: '#f59e0b' },
    { id: 'savings', label: '貯金・投資', percent: 15, color: '#3b82f6' },
    { id: 'utilities', label: '水道光熱・通信', percent: 10, color: '#8b5cf6' },
    { id: 'hobby', label: '交際費・趣味美容', percent: 20, color: '#ec4899' },
    { id: 'others', label: '日用品・その他', percent: 10, color: '#64748b' }
  ];

  function formatMoney(amount) {
    return new Intl.NumberFormat('ja-JP').format(amount);
  }

  function initChart() {
    const ctx = document.getElementById('lifestyleChart').getContext('2d');
    
    // ダークモード考慮のテキスト色設定
    Chart.defaults.color = getComputedStyle(document.body).getPropertyValue('--text-primary') || '#334155';
    Chart.defaults.font.family = "'Outfit', 'Noto Sans JP', sans-serif";

    const centerTextPlugin = {
      id: 'centerText',
      beforeDraw: function(chart) {
        if (chart.config.options.elements && chart.config.options.elements.center) {
          const ctxC = chart.ctx;
          const centerConfig = chart.config.options.elements.center;
          const textStr = centerConfig.text;
          
          ctxC.save();
          ctxC.fillStyle = getComputedStyle(document.body).getPropertyValue('--text-primary') || '#1e293b'; 
          ctxC.font = 'bold 22px Outfit, sans-serif';
          ctxC.textAlign = 'center';
          ctxC.textBaseline = 'middle';
          
          const centerX = (chart.chartArea.left + chart.chartArea.right) / 2;
          const centerY = (chart.chartArea.top + chart.chartArea.bottom) / 2;
          
          ctxC.fillText(textStr, centerX, centerY);
          ctxC.restore();
        }
      }
    };

    lifestyleChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: RATIOS.map(r => r.label),
        datasets: [{
          data: RATIOS.map(r => r.percent),
          backgroundColor: RATIOS.map(r => r.color),
          borderWidth: 2,
          borderColor: getComputedStyle(document.body).getPropertyValue('--bg-card') || '#ffffff',
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => {
                const label = context.label || '';
                const incomeStr = input.value;
                const incomeMan = parseFloat(incomeStr);
                const val = incomeMan * 10000 * (context.raw / 100);
                return `${label}: ¥${formatMoney(Math.floor(val))}`;
              }
            }
          }
        },
        elements: {
          center: {
            text: ''
          }
        }
      },
      plugins: [centerTextPlugin]
    });
  }

  function renderBreakdown(incomeMan) {
    const totalYen = incomeMan * 10000;
    
    let html = '';
    RATIOS.forEach(r => {
      const amount = Math.floor(totalYen * (r.percent / 100));
      html += `
        <li class="breakdown-item">
          <div class="breakdown-left">
            <span class="breakdown-dot" style="background:${r.color};"></span>
            <span class="breakdown-name">${r.label}</span>
          </div>
          <div class="breakdown-right">
            <div class="breakdown-amount">¥${formatMoney(amount)}</div>
            <div class="breakdown-percent">${r.percent}%</div>
          </div>
        </li>
      `;
    });
    breakdownList.innerHTML = html;
  }

  function updateAll() {
    let incomeMan = parseFloat(input.value);
    if (isNaN(incomeMan) || incomeMan <= 0) incomeMan = 25;
    
    display.textContent = incomeMan.toFixed(1);
    
    const rentVal = Math.floor(incomeMan * 10000 * 0.3); // 30%
    const saveVal = Math.floor(incomeMan * 10000 * 0.15); // 15%
    
    resultRent.textContent = '¥' + formatMoney(rentVal);
    resultSaving.textContent = formatMoney(saveVal);
    
    renderBreakdown(incomeMan);
    
    // シェアボタンのリンク生成
    const shareBtn = document.getElementById('share-twitter-btn');
    if (shareBtn) {
      const shareText = `毎月の手取りが【${incomeMan}万円】の場合、適正な家賃の限界は【約${formatMoney(rentVal)}円】でした！🥲 これ以上高いと生活費が破綻・貯金ゼロになります。\n\n自分の生活費の黄金比シミュレーター👇\n`;
      const url = "https://tedori-keisan.com/lifestyle.html";
      const hashtags = "一人暮らし,手取り計算,家賃高すぎ";
      shareBtn.href = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(url)}&hashtags=${encodeURIComponent(hashtags)}`;
    }
    
    // グラフ更新
    if (!lifestyleChart) {
      initChart();
    }
    
    // チャート中央のテキストを更新（月収の金額）
    const totalYen = incomeMan * 10000;
    lifestyleChart.options.elements = lifestyleChart.options.elements || {};
    lifestyleChart.options.elements.center = { text: '¥' + formatMoney(totalYen) };
    lifestyleChart.data.datasets[0].borderColor = getComputedStyle(document.body).getPropertyValue('--bg-card') || '#ffffff';
    lifestyleChart.update();
  }

  // イーベントリスナー
  input.addEventListener('input', (e) => {
    slider.value = e.target.value;
    updateAll();
  });

  slider.addEventListener('input', (e) => {
    input.value = e.target.value;
    updateAll();
  });

  // 初回レンダリング
  updateAll();
});
