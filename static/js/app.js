// API基本URL
const API_BASE = '/api';

// グローバル変数
let diseases = [];
let tests = [];
let prescriptions = [];
let currentEditingId = null;

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', function() {
    initTabs();
    initModal();
    initEventListeners();
    loadCategories();
    loadDiseases();
    loadTests();
    loadPrescriptions();
});

// タブ機能の初期化
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // すべてのタブボタンとコンテンツを非アクティブに
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    // 選択されたタブをアクティブに
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(tabName).classList.add('active');

    // タブごとの初期化処理
    if (tabName === 'suggestion') {
        renderTestSelection();
        renderPrescriptionSelection();
    } else if (tabName === 'reference') {
        renderTestsTable();
        renderPrescriptionsTable();
    }
}

// モーダルの初期化
function initModal() {
    const modal = document.getElementById('diseaseModal');
    const closeBtn = document.querySelector('.close');
    const cancelBtn = document.getElementById('cancelBtn');

    closeBtn.addEventListener('click', () => modal.style.display = 'none');
    cancelBtn.addEventListener('click', () => modal.style.display = 'none');

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// イベントリスナーの初期化
function initEventListeners() {
    document.getElementById('searchBtn').addEventListener('click', searchDiseases);
    document.getElementById('searchInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchDiseases();
    });
    document.getElementById('categoryFilter').addEventListener('change', searchDiseases);
    document.getElementById('addDiseaseBtn').addEventListener('click', openAddModal);
    document.getElementById('diseaseForm').addEventListener('submit', saveDisease);
    document.getElementById('suggestBtn').addEventListener('click', suggestDiseases);
}

// カテゴリー一覧の読み込み
async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE}/categories`);
        const categories = await response.json();
        const select = document.getElementById('categoryFilter');

        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('カテゴリーの読み込みエラー:', error);
    }
}

// 病名一覧の読み込み
async function loadDiseases(search = '', category = '') {
    try {
        let url = `${API_BASE}/diseases?`;
        if (search) url += `search=${encodeURIComponent(search)}&`;
        if (category) url += `category=${encodeURIComponent(category)}`;

        const response = await fetch(url);
        diseases = await response.json();
        renderDiseases();
    } catch (error) {
        console.error('病名の読み込みエラー:', error);
        showMessage('病名の読み込みに失敗しました', 'error');
    }
}

// 病名の表示
async function renderDiseases() {
    const container = document.getElementById('diseaseList');

    if (diseases.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>病名が見つかりません</h3>
                <p>検索条件を変更するか、新しい病名を追加してください。</p>
            </div>
        `;
        return;
    }

    container.innerHTML = '';

    for (const disease of diseases) {
        const relatedTests = await fetchRelatedTests(disease.id);
        const relatedPrescriptions = await fetchRelatedPrescriptions(disease.id);

        const card = document.createElement('div');
        card.className = 'disease-card';
        card.innerHTML = `
            <h3>${disease.name}</h3>
            ${disease.name_kana ? `<div class="kana">${disease.name_kana}</div>` : ''}
            <div>
                ${disease.category ? `<span class="category">${disease.category}</span>` : ''}
                ${disease.icd10_code ? `<span class="icd10">${disease.icd10_code}</span>` : ''}
            </div>
            ${disease.description ? `<div class="description">${disease.description}</div>` : ''}
            ${renderRelatedItems(relatedTests, relatedPrescriptions)}
            <div class="actions">
                <button class="btn btn-primary" onclick="editDisease(${disease.id})">編集</button>
                <button class="btn btn-danger" onclick="deleteDisease(${disease.id})">削除</button>
            </div>
        `;
        container.appendChild(card);
    }
}

// 関連項目の表示
function renderRelatedItems(tests, prescriptions) {
    let html = '<div class="related-items">';

    if (tests && tests.length > 0) {
        html += '<h4>関連検査:</h4>';
        tests.forEach(test => {
            html += `<span class="tag">🔬 ${test.name}</span>`;
        });
    }

    if (prescriptions && prescriptions.length > 0) {
        html += '<h4>関連処方:</h4>';
        prescriptions.forEach(prescription => {
            html += `<span class="tag">💊 ${prescription.name}</span>`;
        });
    }

    html += '</div>';
    return html;
}

// 関連検査の取得
async function fetchRelatedTests(diseaseId) {
    try {
        const response = await fetch(`${API_BASE}/diseases/${diseaseId}/tests`);
        return await response.json();
    } catch (error) {
        console.error('関連検査の取得エラー:', error);
        return [];
    }
}

// 関連処方の取得
async function fetchRelatedPrescriptions(diseaseId) {
    try {
        const response = await fetch(`${API_BASE}/diseases/${diseaseId}/prescriptions`);
        return await response.json();
    } catch (error) {
        console.error('関連処方の取得エラー:', error);
        return [];
    }
}

// 検査項目の読み込み
async function loadTests() {
    try {
        const response = await fetch(`${API_BASE}/tests`);
        tests = await response.json();
    } catch (error) {
        console.error('検査項目の読み込みエラー:', error);
    }
}

// 処方薬の読み込み
async function loadPrescriptions() {
    try {
        const response = await fetch(`${API_BASE}/prescriptions`);
        prescriptions = await response.json();
    } catch (error) {
        console.error('処方薬の読み込みエラー:', error);
    }
}

// 検索
function searchDiseases() {
    const search = document.getElementById('searchInput').value;
    const category = document.getElementById('categoryFilter').value;
    loadDiseases(search, category);
}

// 追加モーダルを開く
function openAddModal() {
    currentEditingId = null;
    document.getElementById('modalTitle').textContent = '新規病名追加';
    document.getElementById('diseaseForm').reset();
    document.getElementById('diseaseId').value = '';
    document.getElementById('diseaseModal').style.display = 'block';
}

// 編集モーダルを開く
async function editDisease(id) {
    try {
        const response = await fetch(`${API_BASE}/diseases/${id}`);
        const disease = await response.json();

        currentEditingId = id;
        document.getElementById('modalTitle').textContent = '病名編集';
        document.getElementById('diseaseId').value = id;
        document.getElementById('diseaseName').value = disease.name || '';
        document.getElementById('diseaseKana').value = disease.name_kana || '';
        document.getElementById('diseaseCategory').value = disease.category || '';
        document.getElementById('diseaseIcd10').value = disease.icd10_code || '';
        document.getElementById('diseaseDescription').value = disease.description || '';
        document.getElementById('diseaseSymptoms').value = disease.symptoms || '';
        document.getElementById('diseaseTreatment').value = disease.treatment || '';

        document.getElementById('diseaseModal').style.display = 'block';
    } catch (error) {
        console.error('病名の読み込みエラー:', error);
        showMessage('病名の読み込みに失敗しました', 'error');
    }
}

// 病名の保存
async function saveDisease(e) {
    e.preventDefault();

    const id = document.getElementById('diseaseId').value;
    const data = {
        name: document.getElementById('diseaseName').value,
        name_kana: document.getElementById('diseaseKana').value,
        category: document.getElementById('diseaseCategory').value,
        icd10_code: document.getElementById('diseaseIcd10').value,
        description: document.getElementById('diseaseDescription').value,
        symptoms: document.getElementById('diseaseSymptoms').value,
        treatment: document.getElementById('diseaseTreatment').value
    };

    try {
        const url = id ? `${API_BASE}/diseases/${id}` : `${API_BASE}/diseases`;
        const method = id ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            showMessage(id ? '病名を更新しました' : '病名を追加しました', 'success');
            document.getElementById('diseaseModal').style.display = 'none';
            loadDiseases();
            loadCategories();
        } else {
            const error = await response.json();
            showMessage(error.error || '保存に失敗しました', 'error');
        }
    } catch (error) {
        console.error('保存エラー:', error);
        showMessage('保存に失敗しました', 'error');
    }
}

// 病名の削除
async function deleteDisease(id) {
    if (!confirm('この病名を削除してもよろしいですか?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/diseases/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showMessage('病名を削除しました', 'success');
            loadDiseases();
        } else {
            const error = await response.json();
            showMessage(error.error || '削除に失敗しました', 'error');
        }
    } catch (error) {
        console.error('削除エラー:', error);
        showMessage('削除に失敗しました', 'error');
    }
}

// 検査項目選択の表示
function renderTestSelection() {
    const container = document.getElementById('testSelection');
    container.innerHTML = '';

    tests.forEach(test => {
        const div = document.createElement('div');
        div.className = 'checkbox-item';
        div.innerHTML = `
            <input type="checkbox" id="test-${test.id}" value="${test.id}">
            <label for="test-${test.id}">
                ${test.name}
                ${test.code ? `<span class="code">(${test.code})</span>` : ''}
            </label>
        `;
        container.appendChild(div);
    });
}

// 処方薬選択の表示
function renderPrescriptionSelection() {
    const container = document.getElementById('prescriptionSelection');
    container.innerHTML = '';

    prescriptions.forEach(prescription => {
        const div = document.createElement('div');
        div.className = 'checkbox-item';
        div.innerHTML = `
            <input type="checkbox" id="prescription-${prescription.id}" value="${prescription.id}">
            <label for="prescription-${prescription.id}">
                ${prescription.name}
                ${prescription.generic_name ? `<span class="code">(${prescription.generic_name})</span>` : ''}
            </label>
        `;
        container.appendChild(div);
    });
}

// 病名提案
async function suggestDiseases() {
    const testIds = Array.from(document.querySelectorAll('#testSelection input:checked'))
        .map(cb => parseInt(cb.value));
    const prescriptionIds = Array.from(document.querySelectorAll('#prescriptionSelection input:checked'))
        .map(cb => parseInt(cb.value));

    if (testIds.length === 0 && prescriptionIds.length === 0) {
        showMessage('検査項目または処方薬を選択してください', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/suggest-diseases`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                test_ids: testIds,
                prescription_ids: prescriptionIds
            })
        });

        const suggestedDiseases = await response.json();
        renderSuggestedDiseases(suggestedDiseases);
    } catch (error) {
        console.error('病名提案エラー:', error);
        showMessage('病名の提案に失敗しました', 'error');
    }
}

// 提案された病名の表示
function renderSuggestedDiseases(suggestedDiseases) {
    const container = document.getElementById('suggestedDiseases');

    if (suggestedDiseases.length === 0) {
        container.innerHTML = `
            <div class="message error">
                選択した検査・処方に関連する病名が見つかりませんでした。
            </div>
        `;
        return;
    }

    container.innerHTML = '<h3>💡 提案された病名</h3>';

    suggestedDiseases.forEach(disease => {
        const div = document.createElement('div');
        div.className = 'suggestion-result';
        div.innerHTML = `
            <h4>${disease.name} ${disease.icd10_code ? `(${disease.icd10_code})` : ''}</h4>
            ${disease.category ? `<div><strong>カテゴリ:</strong> ${disease.category}</div>` : ''}
            ${disease.description ? `<div><strong>説明:</strong> ${disease.description}</div>` : ''}
        `;
        container.appendChild(div);
    });
}

// 検査テーブルの表示
async function renderTestsTable() {
    const tbody = document.querySelector('#testsTable tbody');
    tbody.innerHTML = '';

    for (const test of tests) {
        const relatedDiseases = await fetchTestDiseases(test.id);
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${test.name}</td>
            <td>${test.code || '-'}</td>
            <td>${test.description || '-'}</td>
            <td>${relatedDiseases.map(d => `<span class="disease-tag">${d.name}</span>`).join(' ')}</td>
        `;
        tbody.appendChild(tr);
    }
}

// 処方テーブルの表示
async function renderPrescriptionsTable() {
    const tbody = document.querySelector('#prescriptionsTable tbody');
    tbody.innerHTML = '';

    for (const prescription of prescriptions) {
        const relatedDiseases = await fetchPrescriptionDiseases(prescription.id);
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${prescription.name}</td>
            <td>${prescription.generic_name || '-'}</td>
            <td>${prescription.code || '-'}</td>
            <td>${prescription.description || '-'}</td>
            <td>${relatedDiseases.map(d => `<span class="disease-tag">${d.name}</span>`).join(' ')}</td>
        `;
        tbody.appendChild(tr);
    }
}

// 検査に関連する病名の取得
async function fetchTestDiseases(testId) {
    try {
        const response = await fetch(`${API_BASE}/tests/${testId}/diseases`);
        return await response.json();
    } catch (error) {
        console.error('検査関連病名の取得エラー:', error);
        return [];
    }
}

// 処方に関連する病名の取得
async function fetchPrescriptionDiseases(prescriptionId) {
    try {
        const response = await fetch(`${API_BASE}/prescriptions/${prescriptionId}/diseases`);
        return await response.json();
    } catch (error) {
        console.error('処方関連病名の取得エラー:', error);
        return [];
    }
}

// メッセージ表示
function showMessage(message, type = 'success') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;

    const container = document.querySelector('.tab-content.active');
    container.insertBefore(messageDiv, container.firstChild);

    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}
