// js/ocr.js

document.addEventListener('DOMContentLoaded', () => {
  const ocrBtn = document.getElementById('ocrBtn');
  const ocrInput = document.getElementById('ocrInput');
  const ocrStatus = document.getElementById('ocrStatus');
  const incomeSlider = document.getElementById('incomeSlider');
  const incomeInput = document.getElementById('incomeInput');

  if (!ocrBtn || !ocrInput) return;

  ocrBtn.addEventListener('click', () => {
    ocrInput.click();
  });

  ocrInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Show loading
    const originalBtnText = ocrBtn.innerHTML;
    ocrBtn.innerHTML = `<span style="display:inline-block; animation: pulse 1.5s infinite;">⏳</span> AIが給与明細を解析中... (約10秒)`;
    ocrBtn.style.opacity = '0.7';
    ocrBtn.style.pointerEvents = 'none';
    ocrStatus.textContent = "画像は端末内(ブラウザ)で処理しているため、サーバーには一切送信されません。安心してお待ちください。";
    ocrStatus.style.color = "var(--text-secondary)";

    try {
      if (typeof Tesseract === 'undefined') {
        throw new Error("OCR Library not loaded.");
      }

      // 日本語モデルでOCR実行
      const worker = await Tesseract.createWorker('jpn');
      const { data: { text } } = await worker.recognize(file);
      await worker.terminate();

      console.log("--- OCR Raw Text ---", text);

      // 抽出ロジック：カンマを除外し、5桁〜7桁の連続した数値を検索
      const cleanText = text.replace(/,/g, '').replace(/ /g, '');
      const numberMatches = cleanText.match(/\d{5,7}/g);
      
      if (numberMatches && numberMatches.length > 0) {
        // 月給の給与明細と仮定し、10万円〜200万円の範囲で最大のものを「総支給額」と推測する
        const numbers = numberMatches.map(Number).filter(n => n >= 100000 && n <= 2000000);
        
        if (numbers.length > 0) {
          const estimatedMonthly = Math.max(...numbers);
          
          // シミュレーターは「万円単位・年収」なので変換 (月収 * 12 / 10000)
          const annualMan = Math.round((estimatedMonthly * 12) / 10000);
          
          incomeInput.value = annualMan;
          incomeSlider.value = Math.min(annualMan, 3000);
          
          // シミュレーターを強制更新 (inputイベントを発火)
          incomeInput.dispatchEvent(new Event('input'));

          ocrStatus.textContent = `✅ 読み取り成功！推測された総支給額(月額${Math.round(estimatedMonthly/10000)}万円)から年収約 ${annualMan}万円をセットしました。`;
          ocrStatus.style.color = "var(--accent-green)";
          ocrStatus.style.fontWeight = "bold";
        } else {
          throw new Error("Valid salary amount not found in the extracted numbers.");
        }
      } else {
        throw new Error("No numbers found.");
      }
    } catch (err) {
      console.error("OCR Error:", err);
      ocrStatus.textContent = "❌ 文字の読み取りに失敗しました。手動で年収を入力してください。";
      ocrStatus.style.color = "#ef4444";
    } finally {
      ocrBtn.innerHTML = originalBtnText;
      ocrBtn.style.opacity = '1';
      ocrBtn.style.pointerEvents = 'auto';
      // 入力をリセットして連続アップロードを可能にする
      ocrInput.value = "";
    }
  });
});
