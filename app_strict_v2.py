#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
厳格な保険病名管理システム - 肥満症・生活習慣病管理特化版
Strict Insurance Disease Name Management System - Obesity & Lifestyle Disease Edition
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

DATABASE = 'diseases_v2.db'

def get_db_connection():
    """データベース接続を取得"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """肥満症・生活習慣病管理特化のデータベース初期化"""
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

    # 検査と病名の保険適応マッピング
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

    # 処方と病名の保険適応マッピング
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

    # サンプルデータの追加
    cursor = conn.execute('SELECT COUNT(*) as count FROM diseases')
    if cursor.fetchone()['count'] == 0:
        # 拡充された病名マスター（肥満症・生活習慣病中心）
        diseases_data = [
            # 糖尿病関連
            ('糖尿病', 'とうにょうびょう', 'E14', '代謝疾患', 'インスリン作用不足による高血糖状態', 1),
            ('2型糖尿病', 'にがたとうにょうびょう', 'E11', '代謝疾患', 'インスリン分泌低下とインスリン抵抗性を主病態とする糖尿病', 1),
            ('1型糖尿病', 'いちがたとうにょうびょう', 'E10', '代謝疾患', 'インスリン欠乏を主病態とする糖尿病', 1),
            ('耐糖能異常', 'たいとうのういじょう', 'R73', '代謝疾患', '正常と糖尿病の中間の血糖値（境界型）', 1),
            ('インスリン抵抗性', 'いんすりんていこうせい', 'E88.8', '代謝疾患', 'インスリンの効きが悪い状態', 1),
            ('糖尿病性腎症', 'とうにょうびょうせいじんしょう', 'E11.2', '糖尿病合併症', '糖尿病による腎障害', 1),
            ('糖尿病性網膜症', 'とうにょうびょうせいもうまくしょう', 'E11.3', '糖尿病合併症', '糖尿病による網膜障害', 1),
            ('糖尿病性神経障害', 'とうにょうびょうせいしんけいしょうがい', 'E11.4', '糖尿病合併症', '糖尿病による神経障害', 1),

            # 肥満症関連
            ('肥満症', 'ひまんしょう', 'E66.0', '代謝疾患', 'BMI25以上で肥満に起因する健康障害を有する', 1),
            ('高度肥満症', 'こうどひまんしょう', 'E66.8', '代謝疾患', 'BMI35以上の肥満症', 1),
            ('内臓脂肪型肥満', 'ないぞうしぼうがたひまん', 'E66.9', '代謝疾患', '腹囲が基準値を超える肥満', 1),
            ('メタボリックシンドローム', 'めたぼりっくしんどろーむ', 'E88.9', '代謝疾患', '内臓脂肪蓄積に加え2つ以上の危険因子', 1),

            # 循環器疾患
            ('本態性高血圧症', 'ほんたいせいこうけつあつしょう', 'I10', '循環器疾患', '原因不明の高血圧症', 1),
            ('二次性高血圧症', 'にじせいこうけつあつしょう', 'I15', '循環器疾患', '原因疾患がある高血圧症', 1),
            ('狭心症', 'きょうしんしょう', 'I20', '循環器疾患', '冠動脈狭窄による心筋虚血', 1),
            ('心房細動', 'しんぼうさいどう', 'I48', '循環器疾患', '心房の不規則な興奮', 1),
            ('慢性心不全', 'まんせいしんふぜん', 'I50', '循環器疾患', '心臓のポンプ機能低下', 1),

            # 脂質異常症関連
            ('脂質異常症', 'ししついじょうしょう', 'E78', '代謝疾患', '血中脂質濃度の異常', 1),
            ('高LDLコレステロール血症', 'こうえるでぃーえるこれすてろーるけっしょう', 'E78.0', '代謝疾患', 'LDLコレステロール高値', 1),
            ('低HDLコレステロール血症', 'ていえいちでぃーえるこれすてろーるけっしょう', 'E78.6', '代謝疾患', 'HDLコレステロール低値', 1),
            ('高トリグリセライド血症', 'こうとりぐりせらいどけっしょう', 'E78.1', '代謝疾患', '中性脂肪高値', 1),
            ('家族性高コレステロール血症', 'かぞくせいこうこれすてろーるけっしょう', 'E78.01', '代謝疾患', '遺伝性の高コレステロール血症', 1),

            # 肝疾患関連
            ('肝機能障害', 'かんきのうしょうがい', 'K76.9', '消化器疾患', '肝機能検査値異常', 1),
            ('慢性肝炎', 'まんせいかんえん', 'K73', '消化器疾患', '6ヶ月以上持続する肝炎', 1),
            ('非アルコール性脂肪肝', 'ひあるこーるせいしぼうかん', 'K76.0', '消化器疾患', 'アルコール摂取が少ない脂肪肝（NAFLD）', 1),
            ('非アルコール性脂肪肝炎', 'ひあるこーるせいしぼうかんえん', 'K75.8', '消化器疾患', '炎症を伴う脂肪肝（NASH）', 1),

            # 腎疾患関連
            ('慢性腎臓病', 'まんせいじんぞうびょう', 'N18', '腎疾患', '腎機能低下が3ヶ月以上持続', 1),
            ('慢性腎不全', 'まんせいじんふぜん', 'N18.9', '腎疾患', '腎機能の進行性低下', 1),
            ('蛋白尿', 'たんぱくにょう', 'R80', '腎疾患', '尿中蛋白の持続的な出現', 1),

            # その他代謝疾患
            ('高尿酸血症', 'こうにょうさんけっしょう', 'E79.0', '代謝疾患', '血清尿酸値の上昇', 1),
            ('痛風', 'つうふう', 'M10', '代謝疾患', '尿酸結晶による関節炎', 1),
            ('鉄欠乏性貧血', 'てつけつぼうせいひんけつ', 'D50', '血液疾患', '鉄欠乏による貧血', 1),

            # 内分泌疾患
            ('甲状腺機能低下症', 'こうじょうせんきのうていかしょう', 'E03', '内分泌疾患', '甲状腺ホルモン分泌低下', 1),
            ('甲状腺機能亢進症', 'こうじょうせんきのうこうしんしょう', 'E05', '内分泌疾患', '甲状腺ホルモン過剰分泌', 1),

            # 睡眠障害
            ('睡眠時無呼吸症候群', 'すいみんじむこきゅうしょうこうぐん', 'G47.3', '呼吸器疾患', '睡眠中の無呼吸・低呼吸', 1),
        ]

        conn.executemany(
            'INSERT INTO diseases (name, name_kana, icd10_code, category, description, is_insurance_approved) VALUES (?, ?, ?, ?, ?, ?)',
            diseases_data
        )

        # 拡充された検査項目マスター
        tests_data = [
            # 基本的な糖代謝検査
            ('血糖', 'D007-11', '160007010', '生化学検査', 11, 'グルコース', 1),
            ('HbA1c', 'D007-52', '160145850', '生化学検査', 49, 'ヘモグロビンA1c', 1),
            ('グリコアルブミン', 'D007-53', '160145950', '生化学検査', 33, '過去2週間の平均血糖値', 1),
            ('1,5-AG', 'D007-54', '160190150', '生化学検査', 134, '1,5-アンヒドログルシトール', 1),

            # インスリン関連検査
            ('インスリン(IRI)', 'D008-4', '160124550', '内分泌検査', 111, '血中インスリン濃度', 1),
            ('C-ペプチド(CPR)', 'D008-5', '160124650', '内分泌検査', 111, 'インスリン分泌能の指標', 1),
            ('尿中C-ペプチド', 'D007-64', '160178950', '生化学検査', 111, '24時間尿中CPR', 1),

            # 75g糖負荷試験
            ('75gOGTT(血糖3回)', 'D287', '160287000', '負荷試験', 300, '経口ブドウ糖負荷試験', 1),
            ('75gOGTT(インスリン3回)', 'D287-2', '160287100', '負荷試験', 333, 'OGTT時のインスリン測定', 1),

            # 脂質検査
            ('総コレステロール', 'D007-17', '160016310', '生化学検査', 11, 'T-Cho', 1),
            ('LDLコレステロール', 'D007-23', '160149750', '生化学検査', 17, 'LDL-C', 1),
            ('HDLコレステロール', 'D007-24', '160140550', '生化学検査', 17, 'HDL-C', 1),
            ('中性脂肪', 'D007-18', '160017110', '生化学検査', 11, 'TG, トリグリセライド', 1),
            ('non-HDLコレステロール', 'D007-25', '160220450', '生化学検査', 0, 'TC-HDL', 1),
            ('リポ蛋白分画', 'D007-26', '160174050', '生化学検査', 150, 'LDL粒子数など', 1),

            # 肝機能検査
            ('AST(GOT)', 'D007-1', '160006410', '生化学検査', 11, 'アスパラギン酸アミノトランスフェラーゼ', 1),
            ('ALT(GPT)', 'D007-2', '160006610', '生化学検査', 11, 'アラニンアミノトランスフェラーゼ', 1),
            ('γ-GTP', 'D007-9', '160006810', '生化学検査', 11, 'ガンマグルタミルトランスペプチダーゼ', 1),
            ('ALP', 'D007-8', '160007610', '生化学検査', 11, 'アルカリホスファターゼ', 1),

            # 腎機能検査
            ('クレアチニン', 'D007-28', '160018210', '生化学検査', 11, 'Cr, 腎機能マーカー', 1),
            ('eGFR', 'D007-34', '160210650', '生化学検査', 0, '推算糸球体濾過量', 1),
            ('BUN(尿素窒素)', 'D007-27', '160017910', '生化学検査', 11, '血中尿素窒素', 1),
            ('尿中アルブミン', 'D007-65', '160183150', '尿検査', 110, '早期腎症マーカー', 1),
            ('尿蛋白定量', 'D006', '160006000', '尿検査', 24, '尿中蛋白量', 1),

            # その他
            ('尿酸', 'D007-40', '160009210', '生化学検査', 11, 'UA', 1),
            ('CRP', 'D015-1', '160019010', '免疫学検査', 16, 'C反応性蛋白', 1),
            ('ヘモグロビン', 'D005-2', '160003850', '血液学検査', 16, 'Hb', 1),
            ('赤血球数', 'D005-2', '160003750', '血液学検査', 16, 'RBC', 1),
            ('白血球数', 'D005-2', '160004050', '血液学検査', 16, 'WBC', 1),
            ('血小板数', 'D005-2', '160004450', '血液学検査', 16, 'PLT', 1),
            ('TSH', 'D008-14', '160129550', '内分泌検査', 110, '甲状腺刺激ホルモン', 1),
            ('FT3', 'D008-15', '160129850', '内分泌検査', 114, '遊離トリヨードサイロニン', 1),
            ('FT4', 'D008-16', '160129950', '内分泌検査', 114, '遊離サイロキシン', 1),
        ]

        conn.executemany(
            'INSERT INTO tests (name, code, receipt_code, category, points, description, requires_disease_name) VALUES (?, ?, ?, ?, ?, ?, ?)',
            tests_data
        )

        # 拡充された処方薬マスター（糖尿病薬中心）
        prescriptions_data = [
            # ビグアナイド系
            ('メトホルミン塩酸塩', 'メトグルコ', '3961002', '496100201', 'ビグアナイド系', '2型糖尿病・インスリン抵抗性改善', 1),

            # GLP-1受容体作動薬
            ('リラグルチド', 'ビクトーザ', '2499416', '249941601', 'GLP-1受容体作動薬', '2型糖尿病・体重減少効果', 1),
            ('デュラグルチド', 'トルリシティ', '2499419', '249941901', 'GLP-1受容体作動薬', '2型糖尿病・週1回投与', 1),
            ('セマグルチド', 'オゼンピック', '2499420', '249942001', 'GLP-1受容体作動薬', '2型糖尿病・強力な血糖降下', 1),

            # SGLT2阻害薬
            ('ダパグリフロジン', 'フォシーガ', '3969010', '396901001', 'SGLT2阻害薬', '2型糖尿病・尿糖排泄促進', 1),
            ('エンパグリフロジン', 'ジャディアンス', '3969011', '396901101', 'SGLT2阻害薬', '2型糖尿病・心血管保護効果', 1),
            ('カナグリフロジン', 'カナグル', '3969012', '396901201', 'SGLT2阻害薬', '2型糖尿病', 1),

            # DPP-4阻害薬
            ('シタグリプチン', 'ジャヌビア', '3969007', '396900701', 'DPP-4阻害薬', '2型糖尿病・インクレチン分解阻害', 1),
            ('リナグリプチン', 'トラゼンタ', '3969009', '396900901', 'DPP-4阻害薬', '2型糖尿病・腎機能低下時も使用可', 1),
            ('テネリグリプチン', 'テネリア', '3969013', '396901301', 'DPP-4阻害薬', '2型糖尿病', 1),

            # チアゾリジン系
            ('ピオグリタゾン', 'アクトス', '3969004', '396900401', 'チアゾリジン系', '2型糖尿病・インスリン抵抗性改善', 1),

            # SU剤
            ('グリメピリド', 'アマリール', '3961009', '396100901', 'スルホニル尿素薬', '2型糖尿病・インスリン分泌促進', 1),
            ('グリクラジド', 'グリミクロン', '3961001', '396100101', 'スルホニル尿素薬', '2型糖尿病', 1),

            # 速効型インスリン分泌促進薬
            ('ナテグリニド', 'ファスティック', '3969002', '396900201', 'グリニド系', '2型糖尿病・食後高血糖改善', 1),
            ('ミチグリニド', 'グルファスト', '3969003', '396900301', 'グリニド系', '2型糖尿病', 1),

            # α-グルコシダーゼ阻害薬
            ('アカルボース', 'グルコバイ', '3969001', '396900101', 'α-GI', '2型糖尿病・食後高血糖改善', 1),
            ('ボグリボース', 'ベイスン', '3969006', '396900601', 'α-GI', '2型糖尿病・耐糖能異常', 1),

            # インスリン製剤
            ('インスリングラルギン', 'ランタス', '2492413', '249241301', '持効型インスリン', '1型・2型糖尿病', 1),
            ('インスリンデグルデク', 'トレシーバ', '2492418', '249241801', '持効型インスリン', '1型・2型糖尿病', 1),
            ('インスリンアスパルト', 'ノボラピッド', '2492409', '249240901', '超速効型インスリン', '1型・2型糖尿病', 1),

            # 降圧薬
            ('アムロジピンベシル酸塩', 'ノルバスク', '2171022', '217102201', 'Ca拮抗薬', '高血圧症・狭心症', 1),
            ('オルメサルタン', 'オルメテック', '2149043', '214904301', 'ARB', '高血圧症', 1),
            ('エナラプリル', 'レニベース', '2144002', '214400201', 'ACE阻害薬', '高血圧症・心不全', 1),

            # 脂質異常症治療薬
            ('アトルバスタチン', 'リピトール', '2189017', '218901701', 'スタチン系', '高コレステロール血症', 1),
            ('ロスバスタチン', 'クレストール', '2189018', '218901801', 'スタチン系', '高コレステロール血症', 1),
            ('ピタバスタチン', 'リバロ', '2189020', '218902001', 'スタチン系', '高コレステロール血症', 1),
            ('エゼチミブ', 'ゼチーア', '2189022', '218902201', '小腸コレステロールトランスポーター阻害薬', '高コレステロール血症', 1),
            ('フェノフィブラート', 'リピディル', '2189006', '218900601', 'フィブラート系', '高トリグリセライド血症', 1),

            # 尿酸降下薬
            ('フェブキソスタット', 'フェブリク', '3949104', '394910401', 'キサンチンオキシダーゼ阻害薬', '痛風・高尿酸血症', 1),
            ('アロプリノール', 'ザイロリック', '3943001', '394300101', 'キサンチンオキシダーゼ阻害薬', '痛風・高尿酸血症', 1),

            # その他
            ('フロセミド', 'ラシックス', '2139001', '213900101', 'ループ利尿薬', '浮腫・高血圧・心不全', 1),
            ('レボチロキシン', 'チラーヂン', '2431002', '243100201', '甲状腺ホルモン製剤', '甲状腺機能低下症', 1),
            ('ワルファリン', 'ワーファリン', '3332001', '333200101', '抗凝固薬', '血栓塞栓症予防・心房細動', 1),
            ('鉄剤(フェロミア)', 'フェロミア', '3222004', '322200401', '鉄剤', '鉄欠乏性貧血', 1),
        ]

        conn.executemany(
            'INSERT INTO prescriptions (name, generic_name, yj_code, receipt_code, drug_class, description, requires_disease_name) VALUES (?, ?, ?, ?, ?, ?, ?)',
            prescriptions_data
        )

        # 検査と病名の保険適応マッピング（拡充版）
        test_disease_mappings = []

        # 糖代謝関連検査のマッピング
        # 血糖 (test_id=1)
        for disease_id in [1, 2, 3, 4, 5]:  # 糖尿病、2型、1型、耐糖能異常、インスリン抵抗性
            test_disease_mappings.append((1, disease_id, 1, 0, '血糖測定には糖尿病関連病名が必要'))

        # HbA1c (test_id=2)
        for disease_id in [1, 2, 3, 6, 7, 8]:  # 糖尿病、合併症含む
            test_disease_mappings.append((2, disease_id, 1, 0, 'HbA1c測定には糖尿病確定診断が必要'))

        # グリコアルブミン (test_id=3)
        for disease_id in [1, 2, 3]:
            test_disease_mappings.append((3, disease_id, 1, 0, 'グリコアルブミンは糖尿病管理に使用'))

        # 1,5-AG (test_id=4)
        for disease_id in [1, 2]:
            test_disease_mappings.append((4, disease_id, 1, 0, '1,5-AGは糖尿病食後高血糖評価'))

        # インスリン(IRI) (test_id=5)
        for disease_id in [1, 2, 3, 4, 5]:
            test_disease_mappings.append((5, disease_id, 1, 0, 'インスリン測定は糖尿病診断・評価に必要'))

        # C-ペプチド (test_id=6)
        for disease_id in [1, 2, 3]:
            test_disease_mappings.append((6, disease_id, 1, 0, 'CPRはインスリン分泌能評価'))

        # 尿中C-ペプチド (test_id=7)
        for disease_id in [1, 2, 3]:
            test_disease_mappings.append((7, disease_id, 1, 0, '24時間尿中CPRはインスリン分泌能評価'))

        # 75gOGTT (test_id=8)
        for disease_id in [1, 2, 4]:  # 糖尿病、2型、耐糖能異常
            test_disease_mappings.append((8, disease_id, 1, 0, 'OGTTは糖尿病確定診断に必要'))

        # 75gOGTT(インスリン) (test_id=9)
        for disease_id in [1, 2, 4, 5]:
            test_disease_mappings.append((9, disease_id, 1, 0, 'OGTTインスリンはインスリン抵抗性評価'))

        # 脂質検査のマッピング (test_id=10-15)
        lipid_diseases = [18, 19, 20, 21, 22]  # 脂質異常症、高LDL、低HDL、高TG、家族性
        for test_id in [10, 11, 12, 13, 14, 15]:
            for disease_id in lipid_diseases:
                test_disease_mappings.append((test_id, disease_id, 1, 0, '脂質検査には脂質異常症病名が必要'))

        # メタボ・肥満症でも脂質検査が必要
        for test_id in [10, 11, 12, 13]:
            for disease_id in [9, 10, 11, 12]:  # 肥満症、高度肥満症、内臓脂肪型、メタボ
                test_disease_mappings.append((test_id, disease_id, 1, 0, '肥満症管理に脂質検査が必要'))

        # 肝機能検査のマッピング (test_id=16-19)
        liver_diseases = [23, 24, 25, 26]  # 肝機能障害、慢性肝炎、NAFLD、NASH
        for test_id in [16, 17, 18, 19]:
            for disease_id in liver_diseases:
                test_disease_mappings.append((test_id, disease_id, 1, 0, '肝機能検査には肝疾患病名が必要'))

        # 肥満症・メタボでも肝機能検査
        for test_id in [16, 17, 18]:
            for disease_id in [9, 10, 12]:
                test_disease_mappings.append((test_id, disease_id, 1, 0, '肥満症では脂肪肝評価が必要'))

        # 腎機能検査のマッピング (test_id=20-24)
        kidney_diseases = [27, 28, 29]  # CKD、慢性腎不全、蛋白尿
        for test_id in [20, 21, 22, 23, 24]:
            for disease_id in kidney_diseases:
                test_disease_mappings.append((test_id, disease_id, 1, 0, '腎機能検査にはCKD病名が必要'))

        # 糖尿病性腎症でも腎機能検査
        for test_id in [20, 21, 22, 23, 24]:
            test_disease_mappings.append((test_id, 6, 1, 0, '糖尿病性腎症評価'))

        # 尿酸検査 (test_id=25)
        for disease_id in [30, 31]:  # 高尿酸血症、痛風
            test_disease_mappings.append((25, disease_id, 1, 0, '尿酸測定には高尿酸血症病名が必要'))

        # その他の検査
        test_disease_mappings.append((26, 26, 1, 0, 'CRP'))  # CRP → NASH
        test_disease_mappings.append((27, 32, 1, 0, 'Hb → 貧血'))
        test_disease_mappings.append((28, 32, 1, 0, 'RBC → 貧血'))
        test_disease_mappings.append((32, 33, 1, 0, 'TSH → 甲状腺機能低下症'))
        test_disease_mappings.append((32, 34, 1, 0, 'TSH → 甲状腺機能亢進症'))

        conn.executemany(
            'INSERT INTO test_disease_insurance_mapping (test_id, disease_id, is_required, is_contraindicated, notes) VALUES (?, ?, ?, ?, ?)',
            test_disease_mappings
        )

        # 処方と病名の保険適応マッピング（拡充版）
        prescription_disease_mappings = []

        # メトホルミン (prescription_id=1)
        prescription_disease_mappings.append((1, 2, 1, 0, '2型糖尿病に適応'))
        prescription_disease_mappings.append((1, 5, 1, 0, 'インスリン抵抗性改善'))
        prescription_disease_mappings.append((1, 12, 1, 0, 'メタボリックシンドローム'))
        prescription_disease_mappings.append((1, 3, 0, 1, '1型糖尿病には禁忌'))

        # GLP-1受容体作動薬 (2-4)
        for prescription_id in [2, 3, 4]:
            prescription_disease_mappings.append((prescription_id, 2, 1, 0, '2型糖尿病に適応'))
            prescription_disease_mappings.append((prescription_id, 9, 1, 0, '肥満症合併2型糖尿病'))
            prescription_disease_mappings.append((prescription_id, 3, 0, 1, '1型糖尿病には適応外'))

        # SGLT2阻害薬 (5-7)
        for prescription_id in [5, 6, 7]:
            prescription_disease_mappings.append((prescription_id, 2, 1, 0, '2型糖尿病に適応'))
            prescription_disease_mappings.append((prescription_id, 17, 1, 0, '心不全合併糖尿病'))
            prescription_disease_mappings.append((prescription_id, 3, 0, 1, '1型糖尿病は慎重投与'))

        # DPP-4阻害薬 (8-10)
        for prescription_id in [8, 9, 10]:
            prescription_disease_mappings.append((prescription_id, 2, 1, 0, '2型糖尿病に適応'))
            prescription_disease_mappings.append((prescription_id, 3, 0, 1, '1型糖尿病には適応外'))

        # チアゾリジン系 (11)
        prescription_disease_mappings.append((11, 2, 1, 0, '2型糖尿病・インスリン抵抗性改善'))
        prescription_disease_mappings.append((11, 5, 1, 0, 'インスリン抵抗性'))
        prescription_disease_mappings.append((11, 17, 0, 1, '心不全には禁忌'))

        # SU剤 (12-13)
        for prescription_id in [12, 13]:
            prescription_disease_mappings.append((prescription_id, 2, 1, 0, '2型糖尿病に適応'))
            prescription_disease_mappings.append((prescription_id, 3, 0, 1, '1型糖尿病には無効'))

        # グリニド系 (14-15)
        for prescription_id in [14, 15]:
            prescription_disease_mappings.append((prescription_id, 2, 1, 0, '2型糖尿病食後高血糖'))

        # α-GI (16-17)
        for prescription_id in [16, 17]:
            prescription_disease_mappings.append((prescription_id, 2, 1, 0, '2型糖尿病'))
            prescription_disease_mappings.append((prescription_id, 4, 1, 0, '耐糖能異常'))

        # インスリン製剤 (18-20)
        for prescription_id in [18, 19, 20]:
            prescription_disease_mappings.append((prescription_id, 1, 1, 0, '糖尿病'))
            prescription_disease_mappings.append((prescription_id, 2, 1, 0, '2型糖尿病'))
            prescription_disease_mappings.append((prescription_id, 3, 1, 0, '1型糖尿病'))

        # 降圧薬 (21-23)
        prescription_disease_mappings.append((21, 13, 1, 0, 'アムロジピン→高血圧'))
        prescription_disease_mappings.append((21, 15, 1, 0, 'アムロジピン→狭心症'))
        prescription_disease_mappings.append((22, 13, 1, 0, 'ARB→高血圧'))
        prescription_disease_mappings.append((22, 6, 1, 0, 'ARB→糖尿病性腎症'))
        prescription_disease_mappings.append((23, 13, 1, 0, 'ACE阻害薬→高血圧'))
        prescription_disease_mappings.append((23, 17, 1, 0, 'ACE阻害薬→心不全'))

        # スタチン系 (24-26)
        for prescription_id in [24, 25, 26]:
            for disease_id in [18, 19, 22]:  # 脂質異常症、高LDL、家族性高コレステロール
                prescription_disease_mappings.append((prescription_id, disease_id, 1, 0, 'スタチン→脂質異常症'))

        # エゼチミブ (27)
        prescription_disease_mappings.append((27, 18, 1, 0, 'エゼチミブ→脂質異常症'))
        prescription_disease_mappings.append((27, 19, 1, 0, 'エゼチミブ→高LDL血症'))

        # フィブラート (28)
        prescription_disease_mappings.append((28, 18, 1, 0, 'フィブラート→脂質異常症'))
        prescription_disease_mappings.append((28, 21, 1, 0, 'フィブラート→高TG血症'))

        # 尿酸降下薬 (29-30)
        for prescription_id in [29, 30]:
            prescription_disease_mappings.append((prescription_id, 30, 1, 0, '高尿酸血症'))
            prescription_disease_mappings.append((prescription_id, 31, 1, 0, '痛風'))

        # その他
        prescription_disease_mappings.append((31, 13, 1, 0, 'フロセミド→高血圧'))
        prescription_disease_mappings.append((31, 17, 1, 0, 'フロセミド→心不全'))
        prescription_disease_mappings.append((32, 33, 1, 0, 'レボチロキシン→甲状腺機能低下症'))
        prescription_disease_mappings.append((32, 34, 0, 1, '甲状腺機能亢進症には禁忌'))
        prescription_disease_mappings.append((33, 16, 1, 0, 'ワルファリン→心房細動'))
        prescription_disease_mappings.append((34, 32, 1, 0, '鉄剤→鉄欠乏性貧血'))

        conn.executemany(
            'INSERT INTO prescription_disease_insurance_mapping (prescription_id, disease_id, is_approved, is_contraindicated, notes) VALUES (?, ?, ?, ?, ?)',
            prescription_disease_mappings
        )

    conn.commit()
    conn.close()

# ====================
# 基本的なCRUD API（app_strict.pyと同じ）
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
# 保険適応チェックAPI（app_strict.pyと同じ）
# ====================

@app.route('/api/check-insurance-compliance', methods=['POST'])
def check_insurance_compliance():
    """保険適応チェック（査定リスク評価）"""
    data = request.json
    test_ids = data.get('test_ids', []) or []
    prescription_ids = data.get('prescription_ids', []) or []
    disease_ids = data.get('disease_ids', []) or []

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
        '''.format(','.join('?' * len(disease_ids)) if disease_ids else '0'), [test_id] + disease_ids).fetchall()

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
        '''.format(','.join('?' * len(disease_ids)) if disease_ids else '0'), [prescription_id] + disease_ids).fetchall()

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

        test_name = conn.execute('SELECT name FROM tests WHERE id = ?', (test_id,)).fetchone()
        if test_name:
            test_name = test_name['name']

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

        prescription_name = conn.execute('SELECT name FROM prescriptions WHERE id = ?', (prescription_id,)).fetchone()
        if prescription_name:
            prescription_name = prescription_name['name']

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
    app.run(debug=True, host='0.0.0.0', port=5001)
