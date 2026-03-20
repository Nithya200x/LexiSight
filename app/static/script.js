/* ═══════════════════════════════════════════════════
   LexiSight — Frontend Script
═══════════════════════════════════════════════════ */

(() => {
  // ── DOM refs ──
  const dropzone       = document.getElementById('dropzone');
  const fileInput      = document.getElementById('fileInput');
  const browseBtn      = document.getElementById('browseBtn');
  const dropInner      = document.getElementById('dropInner');
  const previewWrap    = document.getElementById('previewWrap');
  const previewImg     = document.getElementById('previewImg');
  const previewMeta    = document.getElementById('previewMeta');
  const removeBtn      = document.getElementById('removeBtn');
  const groundTruth    = document.getElementById('groundTruth');
  const runBtn         = document.getElementById('runBtn');
  const btnLabel       = document.getElementById('btnLabel');
  const btnSpinner     = document.getElementById('btnSpinner');
  const errorBanner    = document.getElementById('errorBanner');
  const errorText      = document.getElementById('errorText');
  const resultsSection = document.getElementById('resultsSection');

  // Results DOM
  const textOutput     = document.getElementById('textOutput');
  const summaryOutput  = document.getElementById('summaryOutput');
  const headingsOutput = document.getElementById('headingsOutput');
  const headingsEmpty  = document.getElementById('headingsEmpty');
  const copyTextBtn    = document.getElementById('copyTextBtn');
  const cardMetrics    = document.getElementById('card-metrics');
  const cerValue       = document.getElementById('cerValue');
  const werValue       = document.getElementById('werValue');
  const cerFill        = document.getElementById('cerFill');
  const werFill        = document.getElementById('werFill');

  let selectedFile = null;

  // ── File Selection ──
  browseBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
  });

  dropzone.addEventListener('click', () => {
    if (!selectedFile) fileInput.click();
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) handleFile(fileInput.files[0]);
  });

  // ── Drag & Drop ──
  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('drag-over');
  });

  dropzone.addEventListener('dragleave', (e) => {
    if (!dropzone.contains(e.relatedTarget)) {
      dropzone.classList.remove('drag-over');
    }
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  });

  // ── Remove Image ──
  removeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    clearFile();
  });

  function handleFile(file) {
    const allowed = ['image/jpeg', 'image/png', 'image/webp', 'image/bmp', 'image/tiff'];
    if (!allowed.includes(file.type)) {
      showError(`File type "${file.type}" is not supported. Please use JPEG, PNG, WebP, BMP, or TIFF.`);
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      showError(`File is too large (${(file.size / 1024 / 1024).toFixed(1)} MB). Maximum allowed is 10 MB.`);
      return;
    }

    selectedFile = file;
    hideError();

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      previewMeta.textContent = `${file.name} · ${(file.size / 1024).toFixed(0)} KB`;
      dropInner.style.display = 'none';
      previewWrap.style.display = 'flex';
    };
    reader.readAsDataURL(file);

    runBtn.disabled = false;
  }

  function clearFile() {
    selectedFile = null;
    fileInput.value = '';
    previewImg.src = '';
    previewWrap.style.display = 'none';
    dropInner.style.display = 'block';
    runBtn.disabled = true;
    hideError();
  }

  // ── Copy Button ──
  copyTextBtn.addEventListener('click', () => {
    const txt = textOutput.textContent;
    if (!txt) return;
    navigator.clipboard.writeText(txt).then(() => {
      copyTextBtn.classList.add('copied');
      copyTextBtn.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
          <path d="M2 7l4 4 6-6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Copied!`;
      setTimeout(() => {
        copyTextBtn.classList.remove('copied');
        copyTextBtn.innerHTML = `
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <rect x="4" y="4" width="9" height="9" rx="1.5" stroke="currentColor" stroke-width="1.4"/>
            <path d="M4 3V2a1 1 0 011-1h6a1 1 0 011 1v7a1 1 0 01-1 1h-1" stroke="currentColor" stroke-width="1.4"/>
          </svg>
          Copy`;
      }, 2000);
    });
  });

  // ── OCR Submit ──
  runBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    setLoading(true);
    hideError();
    resultsSection.style.display = 'none';

    const formData = new FormData();
    formData.append('file', selectedFile);
    const gt = groundTruth.value.trim();
    if (gt) formData.append('ground_truth', gt);

    try {
      const res = await fetch('/ocr', {
        method: 'POST',
        body: formData
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || `Server error ${res.status}`);
      }

      renderResults(data);
    } catch (err) {
      showError(err.message || 'An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  });

  // ── Render Results ──
  function renderResults(data) {
    // Text
    textOutput.textContent = data.text || '(no text extracted)';

    // Summary
    summaryOutput.textContent = data.summary || 'No summary available.';

    // Headings
    headingsOutput.innerHTML = '';
    if (data.headings && data.headings.length > 0) {
      headingsEmpty.style.display = 'none';
      data.headings.forEach((h) => {
        const li = document.createElement('li');
        li.textContent = h;
        headingsOutput.appendChild(li);
      });
    } else {
      headingsEmpty.style.display = 'block';
    }

    // Metrics
    if (data.cer !== null && data.cer !== undefined) {
      cardMetrics.style.display = 'block';
      const cerPct = (data.cer * 100).toFixed(1);
      const werPct = (data.wer * 100).toFixed(1);
      cerValue.textContent = cerPct + '%';
      werValue.textContent = werPct + '%';
      // Animate bars after render
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          cerFill.style.width = Math.min(data.cer * 100, 100) + '%';
          werFill.style.width = Math.min(data.wer * 100, 100) + '%';
        });
      });
    } else {
      cardMetrics.style.display = 'none';
    }

    // Show results
    resultsSection.style.display = 'flex';

    // Scroll to results
    setTimeout(() => {
      resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  }

  // ── UI Helpers ──
  function setLoading(loading) {
    runBtn.disabled = loading;
    btnLabel.style.display  = loading ? 'none' : 'flex';
    btnSpinner.style.display = loading ? 'flex' : 'none';
  }

  function showError(msg) {
    errorText.textContent = msg;
    errorBanner.style.display = 'flex';
  }

  function hideError() {
    errorBanner.style.display = 'none';
    errorText.textContent = '';
  }

})();
