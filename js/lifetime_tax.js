/**
 * 一生涯の手取り・税金シミュレーター ロジック
 */

document.addEventListener('DOMContentLoaded', () => {
  const ageSlider = document.getElementById('ageSlider');
  const ageDisplay = document.getElementById('ageDisplay');
  const incomeSlider = document.getElementById('incomeSlider');
  const incomeDisplay = document.getElementById('incomeDisplay');
  const growthToggle = document.querySelectorAll('[data-growth]');
  
  const totalTaxDisplay = document.getElementById('totalTaxDisplay');
  const totalGrossDisplay = document.getElementById('totalGrossDisplay');
  const totalTedoriDisplay = document.getElementById('totalTedoriDisplay');
  
  let myLifetimeChart = null;

  function update() {
    const age = parseInt(ageSlider.value, 10);
    const startIncome = parseInt(incomeSlider.value, 10) * 10000;
    let growthRate = 1.02; // デフォルト2%
    
    growthToggle.forEach(btn => {
      if(btn.classList.contains('active')) {
        growthRate = 1 + (parseFloat(btn.dataset.growth) / 100);
      }
    });

    ageDisplay.innerHTML = `<span class="highlight">${age}</span> 歳`;
    incomeDisplay.innerHTML = `<span class="highlight">${incomeSlider.value}</span> 万円`;
    
    // 計算
    let totalGross = 0;
    let totalTax = 0;
    let totalTedori = 0;
    let currentIncome = startIncome;
    
    const maxAge = 65; // 65歳まで働く前提
    
    for (let i = age; i < maxAge; i++) {
        // calculator.js の calculateTedori を再利用
        // (関数は index.html の calculator.js から読み込まれている前提)
        let simData = null;
        if (typeof calculateTedori === 'function') {
            simData = calculateTedori(currentIncome, {
                age: i < 40 ? 'under40' : '40to64'
            });
        }
        
        if (simData) {
            totalGross += currentIncome;
            totalTedori += simData.tedori;
            totalTax += simData.incomeTax + simData.residentTax + Math.floor((simData.healthInsurance + simData.nursingInsurance + simData.pension + simData.employmentInsurance));
        }
        
        // 昇給を反映
        currentIncome = currentIncome * growthRate;
    }
    
    // 表示更新
    totalTaxDisplay.textContent = '¥' + Math.floor(totalTax).toLocaleString('ja-JP');
    totalGrossDisplay.textContent = Math.floor(totalGross).toLocaleString('ja-JP');
    totalTedoriDisplay.textContent = Math.floor(totalTedori).toLocaleString('ja-JP');
    
    // チャート更新
    updateChart(totalTedori, totalTax);
  }

  function updateChart(tedori, tax) {
      const ctx = document.getElementById('lifetimeChart').getContext('2d');
      const dataValues = [tedori, tax];
      const backgroundColors = ['#10b981', '#f43f5e']; // ミント、レッド
      const labels = ['生涯手取り総額', '生涯に支払う税金・保険料'];
      
      if (!myLifetimeChart) {
          myLifetimeChart = new Chart(ctx, {
              type: 'bar',
              data: {
                  labels: ['生涯の収入内訳'],
                  datasets: [
                      {
                          label: labels[0],
                          data: [dataValues[0]],
                          backgroundColor: backgroundColors[0]
                      },
                      {
                          label: labels[1],
                          data: [dataValues[1]],
                          backgroundColor: backgroundColors[1]
                      }
                  ]
              },
              options: {
                  responsive: true,
                  maintainAspectRatio: false,
                  indexAxis: 'y', // 横棒グラフ
                  scales: {
                      x: { stacked: true },
                      y: { stacked: true }
                  },
                  plugins: {
                      tooltip: {
                          callbacks: {
                              label: function(context) {
                                  return context.dataset.label + ': ' + 
                                         new Intl.NumberFormat('ja-JP', { style: 'currency', currency: 'JPY' })
                                         .format(context.raw);
                              }
                          }
                      }
                  }
              }
          });
      } else {
          myLifetimeChart.data.datasets[0].data = [dataValues[0]];
          myLifetimeChart.data.datasets[1].data = [dataValues[1]];
          myLifetimeChart.update();
      }
  }

  // イベントリスナー
  ageSlider.addEventListener('input', update);
  incomeSlider.addEventListener('input', update);
  
  growthToggle.forEach(btn => {
      btn.addEventListener('click', (e) => {
          growthToggle.forEach(b => b.classList.remove('active'));
          e.target.classList.add('active');
          update();
      });
  });

  // 初回ロード
  update();
});
