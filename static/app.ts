declare var lucide: any;

interface Source {
  company: string;
  year: number;
  file: string;
}

interface QueryResponse {
  answer: string;
  sources: Source[];
  confidence: number;
}

const queryInput = document.getElementById('query-input') as HTMLInputElement;
const sendButton = document.getElementById('send-button') as HTMLButtonElement;
const chatHistory = document.getElementById('chat-history') as HTMLDivElement;

async function submitQuery() {
  const rawQuery = queryInput.value.trim();
  if (!rawQuery) return;

  appendMessage(rawQuery, 'user-message');
  queryInput.value = '';

  const loadingId = appendMessage(
    '<div class="typing-dots"><span></span><span></span><span></span></div>',
    'bot-message',
  );
  sendButton.disabled = true;

  try {
    const response = await fetch('/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: rawQuery }),
    });

    if (!response.ok) throw new Error(`Server returned ${response.status}`);

    const data: QueryResponse = await response.json();
    updateMessageWithResponse(loadingId, data);
  } catch (error: any) {
    updateMessageText(loadingId, `⚠ Error: ${error.message}`);
  } finally {
    sendButton.disabled = false;
    queryInput.focus();
  }
}

let messageCounter = 0;

function appendMessage(html: string, className: string): string {
  const msgDiv = document.createElement('div');
  msgDiv.className = `message ${className}`;
  const id = `msg-${++messageCounter}`;
  msgDiv.id = id;
  const p = document.createElement('div');
  p.innerHTML = html;
  msgDiv.appendChild(p);
  chatHistory.appendChild(msgDiv);
  requestAnimationFrame(() => {
    chatHistory.scrollTop = chatHistory.scrollHeight;
  });
  return id;
}

function updateMessageText(id: string, text: string) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = `<div>${text}</div>`;
}

function updateMessageWithResponse(id: string, data: QueryResponse) {
  const el = document.getElementById(id);
  if (!el) return;

  let sourcesHTML = '';
  if (data.sources && data.sources.length > 0) {
    const items = data.sources
      .map((s) => {
        const ext = s.file.split('.').pop()?.toLowerCase() || 'pdf';
        return `
        <li class="source-item">
          <span class="source-type ${ext}">${ext.toUpperCase()}</span>
          <div class="source-info">
            <div class="source-company">${s.company}</div>
            <div class="source-file">${s.file}</div>
          </div>
          <span class="source-year">${s.year}</span>
        </li>`;
      })
      .join('');

    sourcesHTML = `
      <div class="sources-section">
        <span class="sources-label">Sources</span>
        <ul class="sources-list">${items}</ul>
      </div>`;
  }

  el.innerHTML = `<div>${data.answer}</div>${sourcesHTML}`;
  requestAnimationFrame(() => {
    chatHistory.scrollTop = chatHistory.scrollHeight;
  });
}

sendButton.addEventListener('click', submitQuery);
queryInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') submitQuery();
});

// ── Tab Switcher ──
const tabBtns = document.querySelectorAll('.tab-btn');
const tabViews: { [key: string]: HTMLElement } = {
  chat: document.getElementById('chat-view')!,
  documents: document.getElementById('documents-view')!,
};

tabBtns.forEach((btn) => {
  btn.addEventListener('click', () => {
    tabBtns.forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    Object.keys(tabViews).forEach((key) => {
      tabViews[key].classList.toggle(
        'active',
        key === btn.getAttribute('data-tab'),
      );
    });
    localStorage.setItem('activeTab', btn.getAttribute('data-tab') || 'chat');
  });
});

// Restore active tab on page load
const savedTab = localStorage.getItem('activeTab') || 'chat';
document
  .querySelector(`.tab-btn[data-tab="${savedTab}"]`)
  ?.classList.add('active');
Object.keys(tabViews).forEach((key) => {
  tabViews[key].classList.toggle('active', key === savedTab);
});

// ── Documents Tab ──
const selectFilesBtn = document.getElementById(
  'select-files-btn',
) as HTMLButtonElement;
const fileInput = document.getElementById('file-input') as HTMLInputElement;
const fileList = document.getElementById('file-list') as HTMLDivElement;
const processBtn = document.getElementById('process-btn') as HTMLButtonElement;
const ingestionLog = document.getElementById('ingestion-log') as HTMLDivElement;
const logSteps = document.getElementById('log-steps') as HTMLDivElement;
const documentList = document.getElementById('document-list') as HTMLDivElement;

let selectedFiles: File[] = [];

selectFilesBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', () => {
  addFiles(Array.from(fileInput.files || []));
  fileInput.value = '';
});

// Drag and drop
const uploadArea = document.getElementById('upload-area') as HTMLDivElement;

uploadArea.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
  uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadArea.classList.remove('drag-over');
  addFiles(Array.from(e.dataTransfer?.files || []));
});

function addFiles(files: File[]) {
  for (const file of files) {
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext !== 'pdf' && ext !== 'json') continue;
    if (selectedFiles.some((f) => f.name === file.name)) continue;
    selectedFiles.push(file);
  }
  renderFileList();
}

function renderFileList() {
  if (selectedFiles.length === 0) {
    fileList.innerHTML = '';
    processBtn.disabled = true;
    return;
  }
  fileList.innerHTML = selectedFiles
    .map((f) => {
      const ext = f.name.split('.').pop()?.toLowerCase() || '';
      return `<div class="file-item"><span class="file-type ${ext}">${ext.toUpperCase()}</span><span class="file-name">${f.name}</span></div>`;
    })
    .join('');
  processBtn.disabled = false;
}

processBtn.addEventListener('click', async () => {
  if (selectedFiles.length === 0) return;

  processBtn.disabled = true;
  ingestionLog.hidden = false;
  logSteps.innerHTML = '';

  // Upload files
  const formData = new FormData();
  for (const file of selectedFiles) {
    formData.append('files', file);
  }

  try {
    const uploadRes = await fetch('/upload', {
      method: 'POST',
      body: formData,
    });
    if (!uploadRes.ok) throw new Error('Upload failed');
  } catch (err: any) {
    logSteps.innerHTML += `<div class="log-step log-error">❌ Upload failed: ${err.message}</div>`;
    processBtn.disabled = false;
    return;
  }

  // Stream ingestion log
  const ingestStart = Date.now();
  try {
    const ingestRes = await fetch('/ingest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ files: selectedFiles.map((f) => f.name) }),
    });
    if (!ingestRes.ok) throw new Error('Ingestion failed');

    const reader = ingestRes.body?.getReader();
    const decoder = new TextDecoder();
    if (!reader) throw new Error('No response stream');

    const stepEls = new Map<string, HTMLDivElement>();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      const text = decoder.decode(value, { stream: true });
      const lines = text.split('\n').filter((l) => l.trim());
      for (const line of lines) {
        if (line.startsWith('STEP:')) {
          const msg = line.slice(5);
          const el = document.createElement('div');
          el.className = 'log-step';
          el.textContent = '⏳ ' + msg;
          logSteps.appendChild(el);
          stepEls.set(msg, el);
          logSteps.scrollTop = logSteps.scrollHeight;
        } else if (line.startsWith('FILE:')) {
          const msg = 'Processing ' + line.slice(5);
          const el = document.createElement('div');
          el.className = 'log-step';
          el.textContent = '⏳ ' + msg;
          logSteps.appendChild(el);
          stepEls.set(msg, el);
          logSteps.scrollTop = logSteps.scrollHeight;
        } else if (line === 'DONE') {
          for (const [, el] of stepEls) {
            el.textContent = '✅ ' + el.textContent!.slice(2);
          }
          setTimeout(() => {
            ingestionLog.hidden = true;
          }, 3000);
        }
      }
    }
    lucide.createIcons();
    selectedFiles = [];
    renderFileList();
    const ingestTime = ((Date.now() - ingestStart) / 1000).toFixed(1);
    await loadDocuments(ingestTime);
  } catch (err: any) {
    logSteps.innerHTML += `<div class="log-step log-error">❌ Error: ${err.message}</div>`;
  } finally {
    processBtn.disabled = false;
  }
});

// ── Load Document List ──
async function loadDocuments(ingestTime?: string) {
  try {
    const res = await fetch('/documents');
    if (!res.ok) return;
    const docs: Array<{
      company: string;
      year: number;
      file: string;
      format: string;
    }> = await res.json();

    if (docs.length === 0) {
      documentList.innerHTML =
        '<p class="empty-documents">No documents ingested yet</p>';
      return;
    }

    const listEl = document.createElement('ul');
    listEl.className = 'document-list';
    listEl.innerHTML = docs
      .map((d) => {
        const cleanCompany = d.company.replace(/^Jab\s+/i, '');
        return `
        <li class="source-item">
          <span class="source-type ${d.format}">${d.format.toUpperCase()}</span>
          <div class="source-info">
            <div class="source-company">${cleanCompany}</div>
            <div class="source-file">${d.file}</div>
          </div>
          <span class="source-year">${d.year}</span>
        </li>`;
      })
      .join('');

    documentList.innerHTML = '';
    if (ingestTime) {
      const timeEl = document.createElement('p');
      timeEl.className = 'ingestion-summary';
      timeEl.textContent = `${docs.length} documents ingested in ${ingestTime} seconds`;
      documentList.appendChild(timeEl);
    }
    documentList.appendChild(listEl);
  } catch {
    documentList.innerHTML =
      '<p class="empty-documents">Could not load documents</p>';
  }
}

// Load documents on page load
loadDocuments();
