#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
厳格な保険病名管理システム - 査定対策版
Strict Insurance Disease Name Management System - Audit Prevention Edition
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False

DATABASE = 'diseases.db'

def get_db_connection():
    """データベース接続を取得"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """厳格な保険適応対応のデータベース初期化"""
    conn = get_db_connection()

    # 病名マスター（ICD-10準拠）
    conn.execute('''
        CREATE TABLE IF NOT EXISTS diseases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            name_kana TEXT,
            icd10_code TEXT,
            category TEXT,
            description TEXT,
            is_insurance_approved BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 検査項目マスター（診療報酬点数表準拠）
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT,
            receipt_code TEXT,
            category TEXT,
            points INTEGER,
            description TEXT,
            requires_disease_name BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 処方薬マスター（薬価基準収載医薬品コード準拠）
    conn.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            generic_name TEXT,
            yj_code TEXT,
            receipt_code TEXT,
            drug_class TEXT,
            description TEXT,
            requires_disease_name BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 検査と病名の保険適応マッピング（厳格なルール）
    conn.execute('''
        CREATE TABLE IF NOT EXISTS test_disease_insurance_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id INTEGER NOT NULL,
            disease_id INTEGER NOT NULL,
            is_required BOOLEAN DEFAULT 1,
            is_contraindicated BOOLEAN DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (test_id) REFERENCES tests (id),
            FOREIGN KEY (disease_id) REFERENCES diseases (id),
            UNIQUE(test_id, disease_id)
        )
    ''')

    # 処方と病名の保険適応マッピング（厳格なルール）
    conn.execute('''
        CREATE TABLE IF NOT EXISTS prescription_disease_insurance_mapping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prescription_id INTEGER NOT NULL,
            disease_id INTEGER NOT NULL,
            is_approved BOOLEAN DEFAULT 1,
            is_contraindicated BOOLEAN DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (prescription_id) REFERENCES prescriptions (id),
            FOREIGN KEY (disease_id) REFERENCES diseases (id),
            UNIQUE(prescription_id, disease_id)
        )
    ''')

    # 査定リスク履歴テーブル
    conn.execute('''
        CREATE TABLE IF NOT EXISTS audit_risk_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            risk_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT,
            test_id INTEGER,
            prescription_id INTEGER,
            disease_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # サンプルデータの追加
    cursor = conn.execute('SELECT COUNT(*) as count FROM diseases')
    if cursor.fetchone()['count'] == 0:
        # 厳密なICD-10コード付き病名マスター
        diseases_data = [
            ('糖尿病', 'とうにょうびょう', 'E14', '代謝疾患', 'インスリン作用不足による高血糖状態が慢性的に持続する疾患', 1),
            ('2型糖尿病', 'にがたとうにょうびょう', 'E11', '代謝疾患', 'インスリン分泌低下とインスリン抵抗性を主病態とする糖尿病', 1),
            ('1型糖尿病', 'いちがたとうにょうびょう', 'E10', '代謝疾患', 'インスリン欠乏を主病態とする糖尿病', 1),
            ('本態性高血圧症', 'ほんたいせいこうけつあつしょう', 'I10', '循環器疾患', '原因不明の高血圧症', 1),
            ('脂質異常症', 'ししついじょうしょう', 'E78', '代謝疾患', '血中脂質濃度の異常', 1),
            ('高LDLコレステロール血症', 'こうえるでぃーえるこれすてろーるけっしょう', 'E78.0', '代謝疾患', 'LDLコレステロール高値', 1),
            ('高トリグリセライド血症', 'こうとりぐりせらいどけっしょう', 'E78.1', '代謝疾患', '中性脂肪高値', 1),
            ('鉄欠乏性貧血', 'てつけつぼうせいひんけつ', 'D50', '血液疾患', '鉄欠乏による貧血', 1),
            ('肝機能障害', 'かんきのうしょうがい', 'K76.9', '消化器疾患', '肝機能検査値異常', 1),
            ('慢性肝炎', 'まんせいかんえん', 'K73', '消化器疾患', '6ヶ月以上持続する肝炎', 1),
            ('脂肪肝', 'しぼうかん', 'K76.0', '消化器疾患', '肝細胞への脂肪蓄積', 1),
            ('高尿酸血症', 'こうにょうさんけっしょう', 'E79.0', '代謝疾患', '血清尿酸値の上昇', 1),
            ('痛風', 'つうふう', 'M10', '代謝疾患', '尿酸結晶による関節炎', 1),
            ('慢性腎臓病', 'まんせいじんぞうびょう', 'N18', '腎疾患', '腎機能低下が3ヶ月以上持続', 1),
            ('慢性腎不全', 'まんせいじんふぜん', 'N18.9', '腎疾患', '腎機能の進行性低下', 1),
            ('甲状腺機能低下症', 'こうじょうせんきのうていかしょう', 'E03', '内分泌疾患', '甲状腺ホルモン分泌低下', 1),
            ('甲状腺機能亢進症', 'こうじょうせんきのうこうしんしょう', 'E05', '内分泌疾患', '甲状腺ホルモン過剰分泌', 1),
            ('狭心症', 'きょうしんしょう', 'I20', '循環器疾患', '冠動脈狭窄による心筋虚血', 1),
            ('心房細動', 'しんぼうさいどう', 'I48', '循環器疾患', '心房の不規則な興奮', 1),
            ('慢性心不全', 'まんせいしんふぜん', 'I50', '循環器疾患', '心臓のポンプ機能低下', 1),
        ]

        conn.executemany(
            'INSERT INTO diseases (name, name_kana, icd10_code, category, description, is_insurance_approved) VALUES (?, ?, ?, ?, ?, ?)',
            diseases_data
        )

        # 検査項目マスター（診療報酬点数表準拠）
        tests_data = [
            ('血糖', 'D007-11', '160007010', '生化学検査', 11, 'グルコース', 1),
            ('HbA1c', 'D007-52', '160145850', '生化学検査', 49, 'ヘモグロビンA1c', 1),
            ('総コレステロール', 'D007-17', '160016310', '生化学検査', 11, 'T-Cho', 1),
            ('LDLコレステロール', 'D007-23', '160149750', '生化学検査', 17, 'LDL-C', 1),
            ('HDLコレステロール', 'D007-24', '160140550', '生化学検査', 17, 'HDL-C', 1),
            ('中性脂肪', 'D007-18', '160017110', '生化学検査', 11, 'TG, トリグリセライド', 1),
            ('AST(GOT)', 'D007-1', '160006410', '生化学検査', 11, 'アスパラギン酸アミノトランスフェラーゼ', 1),
            ('ALT(GPT)', 'D007-2', '160006610', '生化学検査', 11, 'アラニンアミノトランスフェラーゼ', 1),
            ('γ-GTP', 'D007-9', '160006810', '生化学検査', 11, 'ガンマグルタミルトランスペプチダーゼ', 1),
            ('尿酸', 'D007-40', '160009210', '生化学検査', 11, 'UA', 1),
            ('クレアチニン', 'D007-28', '160018210', '生化学検査', 11, 'Cr, 腎機能マーカー', 1),
            ('eGFR', 'D007-34', '160210650', '生化学検査', 0, '推算糸球体濾過量', 1),
            ('BUN(尿素窒素)', 'D007-27', '160017910', '生化学検査', 11, '血中尿素窒素', 1),
            ('ヘモグロビン', 'D005-2', '160003850', '血液学検査', 16, 'Hb', 1),
            ('赤血球数', 'D005-2', '160003750', '血液学検査', 16, 'RBC', 1),
            ('白血球数', 'D005-2', '160004050', '血液学検査', 16, 'WBC', 1),
            ('血小板数', 'D005-2', '160004450', '血液学検査', 16, 'PLT', 1),
            ('CRP', 'D015-1', '160019010', '免疫学検査', 16, 'C反応性蛋白', 1),
            ('TSH', 'D008-14', '160129550', '内分泌検査', 110, '甲状腺刺激ホルモン', 1),
            ('FT3', 'D008-15', '160129850', '内分泌検査', 114, '遊離トリヨードサイロニン', 1),
            ('FT4', 'D008-16', '160129950', '内分泌検査', 114, '遊離サイロキシン', 1),
        ]

        conn.executemany(
            'INSERT INTO tests (name, code, receipt_code, category, points, description, requires_disease_name) VALUES (?, ?, ?, ?, ?, ?, ?)',
            tests_data
        )

        # 処方薬マスター（保険適応病名を厳格に管理）
        prescriptions_data = [
            ('メトホルミン塩酸塩', 'メトグルコ', '3961002', '496100201', 'ビグアナイド系糖尿病薬', '2型糖尿病治療薬', 1),
            ('アムロジピンベシル酸塩', 'ノルバスク', '2171022', '217102201', 'Ca拮抗薬', '高血圧症・狭心症', 1),
            ('アトルバスタチン', 'リピトール', '2189017', '218901701', 'HMG-CoA還元酵素阻害薬', '高コレステロール血症', 1),
            ('ロスバスタチン', 'クレストール', '2189018', '218901801', 'HMG-CoA還元酵素阻害薬', '高コレステロール血症', 1),
            ('フェブキソスタット', 'フェブリク', '3949104', '394910401', 'キサンチンオキシダーゼ阻害薬', '痛風・高尿酸血症', 1),
            ('アロプリノール', 'ザイロリック', '3943001', '394300101', 'キサンチンオキシダーゼ阻害薬', '痛風・高尿酸血症', 1),
            ('フロセミド', 'ラシックス', '2139001', '213900101', 'ループ利尿薬', '浮腫・高血圧', 1),
            ('レボチロキシン', 'チラーヂン', '2431002', '243100201', '甲状腺ホルモン製剤', '甲状腺機能低下症', 1),
            ('ワルファリン', 'ワーファリン', '3332001', '333200101', '抗凝固薬', '血栓塞栓症予防', 1),
            ('鉄剤(フェロミア)', 'フェロミア', '3222004', '322200401', '鉄剤', '鉄欠乏性貧血', 1),
        ]

        conn.executemany(
            'INSERT INTO prescriptions (name, generic_name, yj_code, receipt_code, drug_class, description, requires_disease_name) VALUES (?, ?, ?, ?, ?, ?, ?)',
            prescriptions_data
        )

        # 検査と病名の厳密なマッピング
        test_disease_mappings = [
            # 糖尿病関連検査
            (1, 1, 1, 0, '血糖測定には糖尿病関連の病名が必要'),  # 血糖 → 糖尿病
            (1, 2, 1, 0, ''),  # 血糖 → 2型糖尿病
            (1, 3, 1, 0, ''),  # 血糖 → 1型糖尿病
            (2, 1, 1, 0, 'HbA1c測定には糖尿病の確定診断が必要'),  # HbA1c → 糖尿病
            (2, 2, 1, 0, ''),  # HbA1c → 2型糖尿病
            (2, 3, 1, 0, ''),  # HbA1c → 1型糖尿病

            # 脂質検査
            (3, 5, 1, 0, '脂質検査には脂質異常症の病名が必要'),  # 総コレステロール → 脂質異常症
            (4, 5, 1, 0, ''),  # LDL → 脂質異常症
            (4, 6, 1, 0, ''),  # LDL → 高LDL血症
            (5, 5, 1, 0, ''),  # HDL → 脂質異常症
            (6, 5, 1, 0, ''),  # 中性脂肪 → 脂質異常症
            (6, 7, 1, 0, ''),  # 中性脂肪 → 高TG血症

            # 肝機能検査
            (7, 9, 1, 0, '肝機能検査には肝機能障害の病名が必要'),  # AST → 肝機能障害
            (7, 10, 1, 0, ''),  # AST → 慢性肝炎
            (7, 11, 1, 0, ''),  # AST → 脂肪肝
            (8, 9, 1, 0, ''),  # ALT → 肝機能障害
            (8, 10, 1, 0, ''),  # ALT → 慢性肝炎
            (8, 11, 1, 0, ''),  # ALT → 脂肪肝
            (9, 9, 1, 0, ''),  # γGTP → 肝機能障害
            (9, 10, 1, 0, ''),  # γGTP → 慢性肝炎
            (9, 11, 1, 0, ''),  # γGTP → 脂肪肝

            # 尿酸検査
            (10, 12, 1, 0, '尿酸測定には高尿酸血症の病名が必要'),  # 尿酸 → 高尿酸血症
            (10, 13, 1, 0, ''),  # 尿酸 → 痛風

            # 腎機能検査
            (11, 14, 1, 0, 'クレアチニン測定にはCKDの病名が必要'),  # Cr → CKD
            (11, 15, 1, 0, ''),  # Cr → 慢性腎不全
            (12, 14, 1, 0, ''),  # eGFR → CKD
            (12, 15, 1, 0, ''),  # eGFR → 慢性腎不全
            (13, 14, 1, 0, ''),  # BUN → CKD
            (13, 15, 1, 0, ''),  # BUN → 慢性腎不全

            # 貧血検査
            (14, 8, 1, 0, '血算には貧血の病名が必要'),  # Hb → 貧血
            (15, 8, 1, 0, ''),  # RBC → 貧血

            # 甲状腺検査
            (19, 16, 1, 0, '甲状腺ホルモン測定には甲状腺疾患の病名が必要'),  # TSH → 甲状腺機能低下症
            (19, 17, 1, 0, ''),  # TSH → 甲状腺機能亢進症
            (20, 16, 1, 0, ''),  # FT3 → 甲状腺機能低下症
            (20, 17, 1, 0, ''),  # FT3 → 甲状腺機能亢進症
            (21, 16, 1, 0, ''),  # FT4 → 甲状腺機能低下症
            (21, 17, 1, 0, ''),  # FT4 → 甲状腺機能亢進症
        ]

        conn.executemany(
            'INSERT INTO test_disease_insurance_mapping (test_id, disease_id, is_required, is_contraindicated, notes) VALUES (?, ?, ?, ?, ?)',
            test_disease_mappings
        )

        # 処方と病名の厳密なマッピング
        prescription_disease_mappings = [
            # メトホルミン（2型糖尿病のみ保険適応）
            (1, 2, 1, 0, 'メトホルミンの保険適応は2型糖尿病'),
            (1, 3, 0, 1, '1型糖尿病には禁忌'),

            # アムロジピン（高血圧症・狭心症のみ保険適応）
            (2, 4, 1, 0, 'アムロジピンの保険適応は高血圧症'),
            (2, 18, 1, 0, 'アムロジピンの保険適応は狭心症'),

            # スタチン系（脂質異常症）
            (3, 5, 1, 0, 'アトルバスタチンは脂質異常症に適応'),
            (3, 6, 1, 0, '高LDL血症に適応'),
            (4, 5, 1, 0, 'ロスバスタチンは脂質異常症に適応'),
            (4, 6, 1, 0, '高LDL血症に適応'),

            # 尿酸降下薬
            (5, 12, 1, 0, 'フェブキソスタットは高尿酸血症に適応'),
            (5, 13, 1, 0, '痛風に適応'),
            (6, 12, 1, 0, 'アロプリノールは高尿酸血症に適応'),
            (6, 13, 1, 0, '痛風に適応'),

            # 利尿薬
            (7, 4, 1, 0, 'フロセミドは高血圧に適応'),
            (7, 20, 1, 0, '心不全に適応'),

            # 甲状腺ホルモン
            (8, 16, 1, 0, 'レボチロキシンは甲状腺機能低下症に適応'),
            (8, 17, 0, 1, '甲状腺機能亢進症には禁忌'),

            # ワルファリン
            (9, 19, 1, 0, 'ワルファリンは心房細動に適応'),

            # 鉄剤
            (10, 8, 1, 0, '鉄剤は鉄欠乏性貧血に適応'),
        ]

        conn.executemany(
            'INSERT INTO prescription_disease_insurance_mapping (prescription_id, disease_id, is_approved, is_contraindicated, notes) VALUES (?, ?, ?, ?, ?)',
            prescription_disease_mappings
        )

    conn.commit()
    conn.close()

# ====================
# 基本的なCRUD API
# ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/diseases', methods=['GET'])
def get_diseases():
    """病名一覧の取得"""
    search = request.args.get('search', '')
    category = request.args.get('category', '')

    conn = get_db_connection()
    query = 'SELECT * FROM diseases WHERE 1=1'
    params = []

    if search:
        query += ' AND (name LIKE ? OR name_kana LIKE ? OR icd10_code LIKE ?)'
        search_param = f'%{search}%'
        params.extend([search_param, search_param, search_param])

    if category:
        query += ' AND category = ?'
        params.append(category)

    query += ' ORDER BY name'

    diseases = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify([dict(disease) for disease in diseases])

@app.route('/api/tests', methods=['GET'])
def get_tests():
    """検査項目一覧の取得"""
    conn = get_db_connection()
    tests = conn.execute('SELECT * FROM tests ORDER BY category, name').fetchall()
    conn.close()
    return jsonify([dict(test) for test in tests])

@app.route('/api/prescriptions', methods=['GET'])
def get_prescriptions():
    """処方薬一覧の取得"""
    conn = get_db_connection()
    prescriptions = conn.execute('SELECT * FROM prescriptions ORDER BY drug_class, name').fetchall()
    conn.close()
    return jsonify([dict(prescription) for prescription in prescriptions])

# ====================
# 保険適応チェックAPI
# ====================

@app.route('/api/check-insurance-compliance', methods=['POST'])
def check_insurance_compliance():
    """保険適応チェック（査定リスク評価）"""
    data = request.json
    test_ids = data.get('test_ids', [])
    prescription_ids = data.get('prescription_ids', [])
    disease_ids = data.get('disease_ids', [])

    conn = get_db_connection()
    risks = []
    warnings = []
    errors = []

    # 検査項目のチェック
    for test_id in test_ids:
        test = conn.execute('SELECT * FROM tests WHERE id = ?', (test_id,)).fetchone()
        if not test:
            continue

        # この検査に必要な病名を取得
        required_diseases = conn.execute('''
            SELECT d.*, m.notes, m.is_contraindicated
            FROM test_disease_insurance_mapping m
            JOIN diseases d ON m.disease_id = d.id
            WHERE m.test_id = ? AND m.is_required = 1
        ''', (test_id,)).fetchall()

        if required_diseases:
            # 必要な病名が登録されているかチェック
            has_required = any(rd['id'] in disease_ids for rd in required_diseases)
            if not has_required:
                errors.append({
                    'type': 'missing_disease',
                    'severity': 'critical',
                    'item_type': 'test',
                    'item_name': test['name'],
                    'message': f'【査定リスク】{test["name"]}には病名が必要です',
                    'required_diseases': [{'id': rd['id'], 'name': rd['name'], 'icd10_code': rd['icd10_code']} for rd in required_diseases]
                })

        # 禁忌病名のチェック
        contraindicated = conn.execute('''
            SELECT d.*
            FROM test_disease_insurance_mapping m
            JOIN diseases d ON m.disease_id = d.id
            WHERE m.test_id = ? AND m.is_contraindicated = 1 AND d.id IN ({})
        '''.format(','.join('?' * len(disease_ids))), [test_id] + disease_ids).fetchall()

        if contraindicated:
            errors.append({
                'type': 'contraindication',
                'severity': 'critical',
                'item_type': 'test',
                'item_name': test['name'],
                'message': f'【禁忌】{test["name"]}は以下の病名では実施できません',
                'contraindicated_diseases': [dict(c) for c in contraindicated]
            })

    # 処方薬のチェック
    for prescription_id in prescription_ids:
        prescription = conn.execute('SELECT * FROM prescriptions WHERE id = ?', (prescription_id,)).fetchone()
        if not prescription:
            continue

        # この薬剤に必要な病名を取得
        approved_diseases = conn.execute('''
            SELECT d.*, m.notes
            FROM prescription_disease_insurance_mapping m
            JOIN diseases d ON m.disease_id = d.id
            WHERE m.prescription_id = ? AND m.is_approved = 1
        ''', (prescription_id,)).fetchall()

        if approved_diseases:
            # 保険適応病名が登録されているかチェック
            has_approved = any(ad['id'] in disease_ids for ad in approved_diseases)
            if not has_approved:
                errors.append({
                    'type': 'off_label',
                    'severity': 'critical',
                    'item_type': 'prescription',
                    'item_name': prescription['name'],
                    'message': f'【査定リスク】{prescription["name"]}には保険適応病名が必要です',
                    'approved_diseases': [{'id': ad['id'], 'name': ad['name'], 'icd10_code': ad['icd10_code']} for ad in approved_diseases]
                })

        # 禁忌病名のチェック
        contraindicated = conn.execute('''
            SELECT d.*, m.notes
            FROM prescription_disease_insurance_mapping m
            JOIN diseases d ON m.disease_id = d.id
            WHERE m.prescription_id = ? AND m.is_contraindicated = 1 AND d.id IN ({})
        '''.format(','.join('?' * len(disease_ids))), [prescription_id] + disease_ids).fetchall()

        if contraindicated:
            errors.append({
                'type': 'contraindication',
                'severity': 'critical',
                'item_type': 'prescription',
                'item_name': prescription['name'],
                'message': f'【禁忌】{prescription["name"]}は以下の病名では処方できません',
                'contraindicated_diseases': [dict(c) for c in contraindicated]
            })

    conn.close()

    # 結果の集計
    result = {
        'is_compliant': len(errors) == 0,
        'risk_level': 'high' if len(errors) > 0 else 'low',
        'errors': errors,
        'warnings': warnings,
        'summary': {
            'total_errors': len(errors),
            'total_warnings': len(warnings),
            'critical_issues': len([e for e in errors if e['severity'] == 'critical'])
        }
    }

    return jsonify(result)

@app.route('/api/suggest-diseases-strict', methods=['POST'])
def suggest_diseases_strict():
    """厳格な病名提案（保険適応のみ）"""
    data = request.json
    test_ids = data.get('test_ids', [])
    prescription_ids = data.get('prescription_ids', [])

    conn = get_db_connection()
    suggested_diseases = {}

    # 検査項目から病名を提案
    for test_id in test_ids:
        diseases = conn.execute('''
            SELECT d.*, m.notes, 'test' as source_type
            FROM test_disease_insurance_mapping m
            JOIN diseases d ON m.disease_id = d.id
            JOIN tests t ON m.test_id = t.id
            WHERE m.test_id = ? AND m.is_required = 1 AND m.is_contraindicated = 0
        ''', (test_id,)).fetchall()

        test_name = conn.execute('SELECT name FROM tests WHERE id = ?', (test_id,)).fetchone()['name']

        for disease in diseases:
            disease_id = disease['id']
            if disease_id not in suggested_diseases:
                suggested_diseases[disease_id] = {
                    **dict(disease),
                    'reasons': []
                }
            suggested_diseases[disease_id]['reasons'].append(f'{test_name}の保険算定に必要')

    # 処方薬から病名を提案
    for prescription_id in prescription_ids:
        diseases = conn.execute('''
            SELECT d.*, m.notes, 'prescription' as source_type
            FROM prescription_disease_insurance_mapping m
            JOIN diseases d ON m.disease_id = d.id
            JOIN prescriptions p ON m.prescription_id = p.id
            WHERE m.prescription_id = ? AND m.is_approved = 1 AND m.is_contraindicated = 0
        ''', (prescription_id,)).fetchall()

        prescription_name = conn.execute('SELECT name FROM prescriptions WHERE id = ?', (prescription_id,)).fetchone()['name']

        for disease in diseases:
            disease_id = disease['id']
            if disease_id not in suggested_diseases:
                suggested_diseases[disease_id] = {
                    **dict(disease),
                    'reasons': []
                }
            suggested_diseases[disease_id]['reasons'].append(f'{prescription_name}の保険適応')

    conn.close()

    return jsonify({
        'suggested_diseases': list(suggested_diseases.values()),
        'total_count': len(suggested_diseases)
    })

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """カテゴリー一覧の取得"""
    conn = get_db_connection()
    categories = conn.execute(
        'SELECT DISTINCT category FROM diseases WHERE category != "" ORDER BY category'
    ).fetchall()
    conn.close()
    return jsonify([cat['category'] for cat in categories])

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
