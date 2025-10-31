#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
病名管理システム - メインアプリケーション
Disease Management System - Main Application
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)
app.config['JSON_AS_ASCII'] = False  # 日本語のJSON対応

DATABASE = 'diseases.db'

def get_db_connection():
    """データベース接続を取得"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """データベースの初期化"""
    conn = get_db_connection()

    # 病名テーブル
    conn.execute('''
        CREATE TABLE IF NOT EXISTS diseases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            name_kana TEXT,
            category TEXT,
            icd10_code TEXT,
            description TEXT,
            symptoms TEXT,
            treatment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 検査項目テーブル
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 処方薬テーブル
    conn.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            generic_name TEXT,
            code TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 病名と検査の関連テーブル
    conn.execute('''
        CREATE TABLE IF NOT EXISTS disease_tests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_id INTEGER,
            test_id INTEGER,
            FOREIGN KEY (disease_id) REFERENCES diseases (id),
            FOREIGN KEY (test_id) REFERENCES tests (id)
        )
    ''')

    # 病名と処方の関連テーブル
    conn.execute('''
        CREATE TABLE IF NOT EXISTS disease_prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_id INTEGER,
            prescription_id INTEGER,
            FOREIGN KEY (disease_id) REFERENCES diseases (id),
            FOREIGN KEY (prescription_id) REFERENCES prescriptions (id)
        )
    ''')

    # サンプルデータの追加
    cursor = conn.execute('SELECT COUNT(*) as count FROM diseases')
    if cursor.fetchone()['count'] == 0:
        sample_diseases = [
            ('糖尿病', 'とうにょうびょう', '代謝疾患', 'E11',
             'インスリンの分泌不足または作用不足により血糖値が上昇する疾患',
             '多飲、多尿、体重減少、疲労感', '食事療法、運動療法、薬物療法'),
            ('高血圧症', 'こうけつあつしょう', '循環器疾患', 'I10',
             '血圧が正常範囲を超えて高い状態が続く疾患',
             '頭痛、めまい、動悸（無症状の場合も多い）', '生活習慣の改善、降圧薬'),
            ('インフルエンザ', 'いんふるえんざ', '感染症', 'J10',
             'インフルエンザウイルスによる急性呼吸器感染症',
             '高熱、全身倦怠感、筋肉痛、咳、鼻水', '抗ウイルス薬、対症療法'),
            ('気管支喘息', 'きかんしぜんそく', '呼吸器疾患', 'J45',
             '気管支の慢性的な炎症により呼吸困難を起こす疾患',
             '呼吸困難、喘鳴、咳、胸部圧迫感', '吸入ステロイド、気管支拡張薬'),
            ('急性胃腸炎', 'きゅうせいいちょうえん', '消化器疾患', 'K52',
             '細菌やウイルスによる胃腸の急性炎症',
             '下痢、嘔吐、腹痛、発熱', '水分補給、整腸剤、抗生物質（細菌性の場合）'),
            ('脂質異常症', 'ししついじょうしょう', '代謝疾患', 'E78',
             '血中の脂質（コレステロール、中性脂肪）が異常値を示す状態',
             '無症状（動脈硬化のリスク）', 'スタチン系薬剤、食事療法'),
            ('貧血', 'ひんけつ', '血液疾患', 'D50',
             '赤血球またはヘモグロビンの減少による疾患',
             '倦怠感、動悸、息切れ、めまい', '鉄剤、ビタミンB12投与'),
        ]

        conn.executemany(
            'INSERT INTO diseases (name, name_kana, category, icd10_code, description, symptoms, treatment) VALUES (?, ?, ?, ?, ?, ?, ?)',
            sample_diseases
        )

        # サンプル検査項目
        sample_tests = [
            ('血糖値', 'BS', '血液中のグルコース濃度を測定'),
            ('HbA1c', 'HbA1c', '過去1-2ヶ月の平均血糖値を反映'),
            ('総コレステロール', 'T-Cho', '血中の総コレステロール値'),
            ('LDLコレステロール', 'LDL-C', '悪玉コレステロール'),
            ('HDLコレステロール', 'HDL-C', '善玉コレステロール'),
            ('中性脂肪', 'TG', '血中のトリグリセリド値'),
            ('赤血球数', 'RBC', '血液中の赤血球の数'),
            ('ヘモグロビン', 'Hb', '赤血球中の酸素運搬タンパク質'),
            ('白血球数', 'WBC', '血液中の白血球の数'),
            ('CRP', 'CRP', 'C反応性蛋白、炎症マーカー'),
        ]

        conn.executemany(
            'INSERT INTO tests (name, code, description) VALUES (?, ?, ?)',
            sample_tests
        )

        # サンプル処方薬
        sample_prescriptions = [
            ('メトホルミン', 'メトグルコ', '621940401', '糖尿病治療薬、インスリン抵抗性改善'),
            ('アムロジピン', 'アムロジン', '621721801', '高血圧治療薬、Ca拮抗薬'),
            ('アトルバスタチン', 'リピトール', '621845801', '脂質異常症治療薬、スタチン系'),
            ('オセルタミビル', 'タミフル', '622900301', '抗インフルエンザウイルス薬'),
            ('フェロミア', '鉄剤', '631340801', '鉄欠乏性貧血治療薬'),
            ('レボフロキサシン', 'クラビット', '622310201', '抗菌薬、ニューキノロン系'),
        ]

        conn.executemany(
            'INSERT INTO prescriptions (name, generic_name, code, description) VALUES (?, ?, ?, ?)',
            sample_prescriptions
        )

        # 病名と検査の関連付け（糖尿病）
        conn.execute('INSERT INTO disease_tests (disease_id, test_id) VALUES (1, 1)')  # 血糖値
        conn.execute('INSERT INTO disease_tests (disease_id, test_id) VALUES (1, 2)')  # HbA1c

        # 病名と検査の関連付け（脂質異常症）
        conn.execute('INSERT INTO disease_tests (disease_id, test_id) VALUES (6, 3)')  # 総コレステロール
        conn.execute('INSERT INTO disease_tests (disease_id, test_id) VALUES (6, 4)')  # LDL
        conn.execute('INSERT INTO disease_tests (disease_id, test_id) VALUES (6, 5)')  # HDL
        conn.execute('INSERT INTO disease_tests (disease_id, test_id) VALUES (6, 6)')  # 中性脂肪

        # 病名と検査の関連付け（貧血）
        conn.execute('INSERT INTO disease_tests (disease_id, test_id) VALUES (7, 7)')  # 赤血球数
        conn.execute('INSERT INTO disease_tests (disease_id, test_id) VALUES (7, 8)')  # ヘモグロビン

        # 病名と処方の関連付け（糖尿病）
        conn.execute('INSERT INTO disease_prescriptions (disease_id, prescription_id) VALUES (1, 1)')  # メトホルミン

        # 病名と処方の関連付け（高血圧症）
        conn.execute('INSERT INTO disease_prescriptions (disease_id, prescription_id) VALUES (2, 2)')  # アムロジピン

        # 病名と処方の関連付け（脂質異常症）
        conn.execute('INSERT INTO disease_prescriptions (disease_id, prescription_id) VALUES (6, 3)')  # アトルバスタチン

        # 病名と処方の関連付け（インフルエンザ）
        conn.execute('INSERT INTO disease_prescriptions (disease_id, prescription_id) VALUES (3, 4)')  # オセルタミビル

        # 病名と処方の関連付け（貧血）
        conn.execute('INSERT INTO disease_prescriptions (disease_id, prescription_id) VALUES (7, 5)')  # フェロミア

    conn.commit()
    conn.close()

@app.route('/')
def index():
    """メインページ"""
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
        query += ' AND (name LIKE ? OR name_kana LIKE ? OR description LIKE ?)'
        search_param = f'%{search}%'
        params.extend([search_param, search_param, search_param])

    if category:
        query += ' AND category = ?'
        params.append(category)

    query += ' ORDER BY updated_at DESC'

    diseases = conn.execute(query, params).fetchall()
    conn.close()

    return jsonify([dict(disease) for disease in diseases])

@app.route('/api/diseases/<int:disease_id>', methods=['GET'])
def get_disease(disease_id):
    """特定の病名の取得"""
    conn = get_db_connection()
    disease = conn.execute('SELECT * FROM diseases WHERE id = ?', (disease_id,)).fetchone()
    conn.close()

    if disease is None:
        return jsonify({'error': '病名が見つかりません'}), 404

    return jsonify(dict(disease))

@app.route('/api/diseases', methods=['POST'])
def create_disease():
    """新しい病名の追加"""
    data = request.json

    required_fields = ['name']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field}は必須項目です'}), 400

    conn = get_db_connection()
    cursor = conn.execute(
        '''INSERT INTO diseases (name, name_kana, category, icd10_code, description, symptoms, treatment)
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (data['name'], data.get('name_kana', ''), data.get('category', ''),
         data.get('icd10_code', ''), data.get('description', ''),
         data.get('symptoms', ''), data.get('treatment', ''))
    )
    conn.commit()
    disease_id = cursor.lastrowid
    conn.close()

    return jsonify({'id': disease_id, 'message': '病名を追加しました'}), 201

@app.route('/api/diseases/<int:disease_id>', methods=['PUT'])
def update_disease(disease_id):
    """病名の更新"""
    data = request.json

    conn = get_db_connection()
    disease = conn.execute('SELECT * FROM diseases WHERE id = ?', (disease_id,)).fetchone()

    if disease is None:
        conn.close()
        return jsonify({'error': '病名が見つかりません'}), 404

    conn.execute(
        '''UPDATE diseases
           SET name = ?, name_kana = ?, category = ?, icd10_code = ?,
               description = ?, symptoms = ?, treatment = ?, updated_at = CURRENT_TIMESTAMP
           WHERE id = ?''',
        (data.get('name', disease['name']),
         data.get('name_kana', disease['name_kana']),
         data.get('category', disease['category']),
         data.get('icd10_code', disease['icd10_code']),
         data.get('description', disease['description']),
         data.get('symptoms', disease['symptoms']),
         data.get('treatment', disease['treatment']),
         disease_id)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': '病名を更新しました'})

@app.route('/api/diseases/<int:disease_id>', methods=['DELETE'])
def delete_disease(disease_id):
    """病名の削除"""
    conn = get_db_connection()
    disease = conn.execute('SELECT * FROM diseases WHERE id = ?', (disease_id,)).fetchone()

    if disease is None:
        conn.close()
        return jsonify({'error': '病名が見つかりません'}), 404

    conn.execute('DELETE FROM diseases WHERE id = ?', (disease_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': '病名を削除しました'})

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """カテゴリー一覧の取得"""
    conn = get_db_connection()
    categories = conn.execute(
        'SELECT DISTINCT category FROM diseases WHERE category != "" ORDER BY category'
    ).fetchall()
    conn.close()

    return jsonify([cat['category'] for cat in categories])

@app.route('/api/tests', methods=['GET'])
def get_tests():
    """検査項目一覧の取得"""
    conn = get_db_connection()
    tests = conn.execute('SELECT * FROM tests ORDER BY name').fetchall()
    conn.close()
    return jsonify([dict(test) for test in tests])

@app.route('/api/prescriptions', methods=['GET'])
def get_prescriptions():
    """処方薬一覧の取得"""
    conn = get_db_connection()
    prescriptions = conn.execute('SELECT * FROM prescriptions ORDER BY name').fetchall()
    conn.close()
    return jsonify([dict(prescription) for prescription in prescriptions])

@app.route('/api/diseases/<int:disease_id>/tests', methods=['GET'])
def get_disease_tests(disease_id):
    """病名に関連する検査項目の取得"""
    conn = get_db_connection()
    tests = conn.execute('''
        SELECT t.* FROM tests t
        INNER JOIN disease_tests dt ON t.id = dt.test_id
        WHERE dt.disease_id = ?
    ''', (disease_id,)).fetchall()
    conn.close()
    return jsonify([dict(test) for test in tests])

@app.route('/api/diseases/<int:disease_id>/prescriptions', methods=['GET'])
def get_disease_prescriptions(disease_id):
    """病名に関連する処方薬の取得"""
    conn = get_db_connection()
    prescriptions = conn.execute('''
        SELECT p.* FROM prescriptions p
        INNER JOIN disease_prescriptions dp ON p.id = dp.prescription_id
        WHERE dp.disease_id = ?
    ''', (disease_id,)).fetchall()
    conn.close()
    return jsonify([dict(prescription) for prescription in prescriptions])

@app.route('/api/tests/<int:test_id>/diseases', methods=['GET'])
def get_test_diseases(test_id):
    """検査項目に関連する病名の取得"""
    conn = get_db_connection()
    diseases = conn.execute('''
        SELECT d.* FROM diseases d
        INNER JOIN disease_tests dt ON d.id = dt.disease_id
        WHERE dt.test_id = ?
    ''', (test_id,)).fetchall()
    conn.close()
    return jsonify([dict(disease) for disease in diseases])

@app.route('/api/prescriptions/<int:prescription_id>/diseases', methods=['GET'])
def get_prescription_diseases(prescription_id):
    """処方薬に関連する病名の取得"""
    conn = get_db_connection()
    diseases = conn.execute('''
        SELECT d.* FROM diseases d
        INNER JOIN disease_prescriptions dp ON d.id = dp.disease_id
        WHERE dp.prescription_id = ?
    ''', (prescription_id,)).fetchall()
    conn.close()
    return jsonify([dict(disease) for disease in diseases])

@app.route('/api/suggest-diseases', methods=['POST'])
def suggest_diseases():
    """検査や処方から病名を提案"""
    data = request.json
    test_ids = data.get('test_ids', [])
    prescription_ids = data.get('prescription_ids', [])

    conn = get_db_connection()
    suggested_diseases = set()

    # 検査項目から病名を提案
    for test_id in test_ids:
        diseases = conn.execute('''
            SELECT d.* FROM diseases d
            INNER JOIN disease_tests dt ON d.id = dt.disease_id
            WHERE dt.test_id = ?
        ''', (test_id,)).fetchall()
        for disease in diseases:
            suggested_diseases.add(disease['id'])

    # 処方薬から病名を提案
    for prescription_id in prescription_ids:
        diseases = conn.execute('''
            SELECT d.* FROM diseases d
            INNER JOIN disease_prescriptions dp ON d.id = dp.disease_id
            WHERE dp.prescription_id = ?
        ''', (prescription_id,)).fetchall()
        for disease in diseases:
            suggested_diseases.add(disease['id'])

    # 提案された病名の詳細を取得
    result = []
    for disease_id in suggested_diseases:
        disease = conn.execute('SELECT * FROM diseases WHERE id = ?', (disease_id,)).fetchone()
        if disease:
            result.append(dict(disease))

    conn.close()
    return jsonify(result)

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
