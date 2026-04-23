var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var _a;
const queryInput = document.getElementById('query-input');
const sendButton = document.getElementById('send-button');
const chatHistory = document.getElementById('chat-history');
function submitQuery() {
    return __awaiter(this, void 0, void 0, function* () {
        const rawQuery = queryInput.value.trim();
        if (!rawQuery)
            return;
        appendMessage(rawQuery, 'user-message');
        queryInput.value = '';
        const loadingId = appendMessage('<div class="typing-dots"><span></span><span></span><span></span></div>', 'bot-message');
        sendButton.disabled = true;
        try {
            const response = yield fetch('/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: rawQuery }),
            });
            if (!response.ok)
                throw new Error(`Server returned ${response.status}`);
            const data = yield response.json();
            updateMessageWithResponse(loadingId, data);
        }
        catch (error) {
            updateMessageText(loadingId, `⚠ Error: ${error.message}`);
        }
        finally {
            sendButton.disabled = false;
            queryInput.focus();
        }
    });
}
let messageCounter = 0;
function appendMessage(html, className) {
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
function updateMessageText(id, text) {
    const el = document.getElementById(id);
    if (el)
        el.innerHTML = `<div>${text}</div>`;
}
function updateMessageWithResponse(id, data) {
    const el = document.getElementById(id);
    if (!el)
        return;
    let sourcesHTML = '';
    if (data.sources && data.sources.length > 0) {
        const items = data.sources
            .map((s) => {
            var _a;
            const ext = ((_a = s.file.split('.').pop()) === null || _a === void 0 ? void 0 : _a.toLowerCase()) || 'pdf';
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
    if (e.key === 'Enter')
        submitQuery();
});
const tabBtns = document.querySelectorAll('.tab-btn');
const tabViews = {
    chat: document.getElementById('chat-view'),
    documents: document.getElementById('documents-view'),
};
tabBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
        tabBtns.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        Object.keys(tabViews).forEach((key) => {
            tabViews[key].classList.toggle('active', key === btn.getAttribute('data-tab'));
        });
        localStorage.setItem('activeTab', btn.getAttribute('data-tab') || 'chat');
    });
});
const savedTab = localStorage.getItem('activeTab') || 'chat';
(_a = document
    .querySelector(`.tab-btn[data-tab="${savedTab}"]`)) === null || _a === void 0 ? void 0 : _a.classList.add('active');
Object.keys(tabViews).forEach((key) => {
    tabViews[key].classList.toggle('active', key === savedTab);
});
const selectFilesBtn = document.getElementById('select-files-btn');
const fileInput = document.getElementById('file-input');
const fileList = document.getElementById('file-list');
const processBtn = document.getElementById('process-btn');
const ingestionLog = document.getElementById('ingestion-log');
const logSteps = document.getElementById('log-steps');
const documentList = document.getElementById('document-list');
let selectedFiles = [];
selectFilesBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', () => {
    addFiles(Array.from(fileInput.files || []));
    fileInput.value = '';
});
const uploadArea = document.getElementById('upload-area');
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});
uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});
uploadArea.addEventListener('drop', (e) => {
    var _a;
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    addFiles(Array.from(((_a = e.dataTransfer) === null || _a === void 0 ? void 0 : _a.files) || []));
});
function addFiles(files) {
    var _a;
    for (const file of files) {
        const ext = (_a = file.name.split('.').pop()) === null || _a === void 0 ? void 0 : _a.toLowerCase();
        if (ext !== 'pdf' && ext !== 'json')
            continue;
        if (selectedFiles.some((f) => f.name === file.name))
            continue;
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
        var _a;
        const ext = ((_a = f.name.split('.').pop()) === null || _a === void 0 ? void 0 : _a.toLowerCase()) || '';
        return `<div class="file-item"><span class="file-type ${ext}">${ext.toUpperCase()}</span><span class="file-name">${f.name}</span></div>`;
    })
        .join('');
    processBtn.disabled = false;
}
processBtn.addEventListener('click', () => __awaiter(this, void 0, void 0, function* () {
    var _b;
    if (selectedFiles.length === 0)
        return;
    processBtn.disabled = true;
    ingestionLog.hidden = false;
    logSteps.innerHTML = '';
    const formData = new FormData();
    for (const file of selectedFiles) {
        formData.append('files', file);
    }
    try {
        const uploadRes = yield fetch('/upload', {
            method: 'POST',
            body: formData,
        });
        if (!uploadRes.ok)
            throw new Error('Upload failed');
    }
    catch (err) {
        logSteps.innerHTML += `<div class="log-step log-error">❌ Upload failed: ${err.message}</div>`;
        processBtn.disabled = false;
        return;
    }
    const ingestStart = Date.now();
    try {
        const ingestRes = yield fetch('/ingest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ files: selectedFiles.map((f) => f.name) }),
        });
        if (!ingestRes.ok)
            throw new Error('Ingestion failed');
        const reader = (_b = ingestRes.body) === null || _b === void 0 ? void 0 : _b.getReader();
        const decoder = new TextDecoder();
        if (!reader)
            throw new Error('No response stream');
        const stepEls = new Map();
        while (true) {
            const { done, value } = yield reader.read();
            if (done)
                break;
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
                }
                else if (line.startsWith('FILE:')) {
                    const msg = 'Processing ' + line.slice(5);
                    const el = document.createElement('div');
                    el.className = 'log-step';
                    el.textContent = '⏳ ' + msg;
                    logSteps.appendChild(el);
                    stepEls.set(msg, el);
                    logSteps.scrollTop = logSteps.scrollHeight;
                }
                else if (line === 'DONE') {
                    for (const [, el] of stepEls) {
                        el.textContent = '✅ ' + el.textContent.slice(2);
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
        yield loadDocuments(ingestTime);
    }
    catch (err) {
        logSteps.innerHTML += `<div class="log-step log-error">❌ Error: ${err.message}</div>`;
    }
    finally {
        processBtn.disabled = false;
    }
}));
function loadDocuments(ingestTime) {
    return __awaiter(this, void 0, void 0, function* () {
        try {
            const res = yield fetch('/documents');
            if (!res.ok)
                return;
            const docs = yield res.json();
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
        }
        catch (_a) {
            documentList.innerHTML =
                '<p class="empty-documents">Could not load documents</p>';
        }
    });
}
loadDocuments();
