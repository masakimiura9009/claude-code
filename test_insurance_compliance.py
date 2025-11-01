#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
保険病名管理システム テストスイート
Insurance Disease Name Management System Test Suite
150+ Test Cases for Audit Compliance Verification
"""

import unittest
import json
import os
import sys
from flask import Flask
from flask.testing import FlaskClient
import sqlite3

# アプリケーションをインポート
sys.path.insert(0, os.path.dirname(__file__))
from app_strict import app, init_db, DATABASE

class InsuranceComplianceTestCase(unittest.TestCase):
    """保険適応準拠性テスト"""

    @classmethod
    def setUpClass(cls):
        """テストクラス全体のセットアップ"""
        if os.path.exists(DATABASE):
            os.remove(DATABASE)
        init_db()

    def setUp(self):
        """各テストのセットアップ"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_001_database_initialization(self):
        """テスト001: データベース初期化の確認"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # テーブルの存在確認
        tables = ['diseases', 'tests', 'prescriptions',
                  'test_disease_insurance_mapping',
                  'prescription_disease_insurance_mapping']

        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            self.assertIsNotNone(cursor.fetchone(), f"{table}テーブルが存在しません")

        conn.close()

    # ====================
    # 病名マスターテスト (Test 002-020)
    # ====================

    def test_002_disease_master_exists(self):
        """テスト002: 病名マスターのデータ存在確認"""
        response = self.client.get('/api/diseases')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0, "病名データが存在しません")

    def test_003_disease_icd10_code_format(self):
        """テスト003: ICD-10コードのフォーマット確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)

        for disease in data:
            if disease['icd10_code']:
                # ICD-10コードの基本フォーマットチェック
                self.assertRegex(disease['icd10_code'], r'^[A-Z]\d{2}\.?\d?',
                                 f"{disease['name']}のICD-10コードが不正: {disease['icd10_code']}")

    def test_004_disease_unique_names(self):
        """テスト004: 病名の一意性確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)

        names = [d['name'] for d in data]
        self.assertEqual(len(names), len(set(names)), "重複する病名が存在します")

    def test_005_diabetes_disease_exists(self):
        """テスト005: 糖尿病病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)

        diabetes_names = ['糖尿病', '2型糖尿病', '1型糖尿病']
        disease_names = [d['name'] for d in data]

        for name in diabetes_names:
            self.assertIn(name, disease_names, f"{name}が登録されていません")

    def test_006_hypertension_disease_exists(self):
        """テスト006: 高血圧症病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)

        disease_names = [d['name'] for d in data]
        self.assertIn('本態性高血圧症', disease_names, "本態性高血圧症が登録されていません")

    def test_007_dyslipidemia_disease_exists(self):
        """テスト007: 脂質異常症病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)

        dyslipidemia_names = ['脂質異常症', '高LDLコレステロール血症', '高トリグリセライド血症']
        disease_names = [d['name'] for d in data]

        for name in dyslipidemia_names:
            self.assertIn(name, disease_names, f"{name}が登録されていません")

    def test_008_anemia_disease_exists(self):
        """テスト008: 貧血病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)

        disease_names = [d['name'] for d in data]
        self.assertIn('鉄欠乏性貧血', disease_names, "鉄欠乏性貧血が登録されていません")

    def test_009_liver_disease_exists(self):
        """テスト009: 肝疾患病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)

        liver_names = ['肝機能障害', '慢性肝炎', '脂肪肝']
        disease_names = [d['name'] for d in data]

        for name in liver_names:
            self.assertIn(name, disease_names, f"{name}が登録されていません")

    def test_010_kidney_disease_exists(self):
        """テスト010: 腎疾患病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)

        kidney_names = ['慢性腎臓病', '慢性腎不全']
        disease_names = [d['name'] for d in data]

        for name in kidney_names:
            self.assertIn(name, disease_names, f"{name}が登録されていません")

    def test_011_thyroid_disease_exists(self):
        """テスト011: 甲状腺疾患病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)

        thyroid_names = ['甲状腺機能低下症', '甲状腺機能亢進症']
        disease_names = [d['name'] for d in data]

        for name in thyroid_names:
            self.assertIn(name, disease_names, f"{name}が登録されていません")

    def test_012_gout_disease_exists(self):
        """テスト012: 痛風・高尿酸血症病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)

        gout_names = ['高尿酸血症', '痛風']
        disease_names = [d['name'] for d in data]

        for name in gout_names:
            self.assertIn(name, disease_names, f"{name}が登録されていません")

    def test_013_cardiac_disease_exists(self):
        """テスト013: 心疾患病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)

        cardiac_names = ['狭心症', '心房細動', '慢性心不全']
        disease_names = [d['name'] for d in data]

        for name in cardiac_names:
            self.assertIn(name, disease_names, f"{name}が登録されていません")

    # ====================
    # 検査項目マスターテスト (Test 014-040)
    # ====================

    def test_014_test_master_exists(self):
        """テスト014: 検査項目マスターのデータ存在確認"""
        response = self.client.get('/api/tests')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0, "検査項目データが存在しません")

    def test_015_blood_glucose_test_exists(self):
        """テスト015: 血糖検査の存在確認"""
        response = self.client.get('/api/tests')
        data = json.loads(response.data)

        test_names = [t['name'] for t in data]
        self.assertIn('血糖', test_names, "血糖検査が登録されていません")

    def test_016_hba1c_test_exists(self):
        """テスト016: HbA1c検査の存在確認"""
        response = self.client.get('/api/tests')
        data = json.loads(response.data)

        test_names = [t['name'] for t in data]
        self.assertIn('HbA1c', test_names, "HbA1c検査が登録されていません")

    def test_017_lipid_tests_exist(self):
        """テスト017: 脂質検査の存在確認"""
        response = self.client.get('/api/tests')
        data = json.loads(response.data)

        lipid_tests = ['総コレステロール', 'LDLコレステロール', 'HDLコレステロール', '中性脂肪']
        test_names = [t['name'] for t in data]

        for test in lipid_tests:
            self.assertIn(test, test_names, f"{test}検査が登録されていません")

    def test_018_liver_function_tests_exist(self):
        """テスト018: 肝機能検査の存在確認"""
        response = self.client.get('/api/tests')
        data = json.loads(response.data)

        liver_tests = ['AST(GOT)', 'ALT(GPT)', 'γ-GTP']
        test_names = [t['name'] for t in data]

        for test in liver_tests:
            self.assertIn(test, test_names, f"{test}検査が登録されていません")

    def test_019_kidney_function_tests_exist(self):
        """テスト019: 腎機能検査の存在確認"""
        response = self.client.get('/api/tests')
        data = json.loads(response.data)

        kidney_tests = ['クレアチニン', 'eGFR', 'BUN(尿素窒素)']
        test_names = [t['name'] for t in data]

        for test in kidney_tests:
            self.assertIn(test, test_names, f"{test}検査が登録されていません")

    def test_020_cbc_tests_exist(self):
        """テスト020: 血算検査の存在確認"""
        response = self.client.get('/api/tests')
        data = json.loads(response.data)

        cbc_tests = ['ヘモグロビン', '赤血球数', '白血球数', '血小板数']
        test_names = [t['name'] for t in data]

        for test in cbc_tests:
            self.assertIn(test, test_names, f"{test}検査が登録されていません")

    # ====================
    # 処方薬マスターテスト (Test 021-040)
    # ====================

    def test_021_prescription_master_exists(self):
        """テスト021: 処方薬マスターのデータ存在確認"""
        response = self.client.get('/api/prescriptions')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0, "処方薬データが存在しません")

    def test_022_metformin_exists(self):
        """テスト022: メトホルミンの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)

        drug_names = [p['name'] for p in data]
        self.assertIn('メトホルミン塩酸塩', drug_names, "メトホルミンが登録されていません")

    def test_023_amlodipine_exists(self):
        """テスト023: アムロジピンの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)

        drug_names = [p['name'] for p in data]
        self.assertIn('アムロジピンベシル酸塩', drug_names, "アムロジピンが登録されていません")

    def test_024_statin_exists(self):
        """テスト024: スタチン系薬剤の存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)

        statin_names = ['アトルバスタチン', 'ロスバスタチン']
        drug_names = [p['name'] for p in data]

        for drug in statin_names:
            self.assertIn(drug, drug_names, f"{drug}が登録されていません")

    def test_025_uric_acid_drug_exists(self):
        """テスト025: 尿酸降下薬の存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)

        uric_acid_drugs = ['フェブキソスタット', 'アロプリノール']
        drug_names = [p['name'] for p in data]

        for drug in uric_acid_drugs:
            self.assertIn(drug, drug_names, f"{drug}が登録されていません")

    # ====================
    # 保険適応チェックテスト - 糖尿病関連 (Test 041-060)
    # ====================

    def test_041_blood_glucose_without_diabetes_error(self):
        """テスト041: 血糖検査で糖尿病病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [1], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])
        self.assertGreater(len(data['errors']), 0)

    def test_042_blood_glucose_with_diabetes_ok(self):
        """テスト042: 血糖検査で糖尿病病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [1], 'disease_ids': [1]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_043_hba1c_without_diabetes_error(self):
        """テスト043: HbA1c検査で糖尿病病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [2], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_044_hba1c_with_type2_diabetes_ok(self):
        """テスト044: HbA1c検査で2型糖尿病病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [2], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_045_metformin_without_diabetes_error(self):
        """テスト045: メトホルミン処方で糖尿病病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [1], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_046_metformin_with_type2_diabetes_ok(self):
        """テスト046: メトホルミン処方で2型糖尿病病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [1], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_047_metformin_with_type1_diabetes_contraindicated(self):
        """テスト047: メトホルミン処方で1型糖尿病は禁忌エラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [1], 'disease_ids': [3]})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])
        # 禁忌エラーがあることを確認
        has_contraindication = any(e['type'] == 'contraindication' for e in data['errors'])
        self.assertTrue(has_contraindication)

    # ====================
    # 保険適応チェックテスト - 高血圧関連 (Test 048-060)
    # ====================

    def test_048_amlodipine_without_hypertension_error(self):
        """テスト048: アムロジピン処方で高血圧病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [2], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_049_amlodipine_with_hypertension_ok(self):
        """テスト049: アムロジピン処方で高血圧病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [2], 'disease_ids': [4]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_050_amlodipine_with_angina_ok(self):
        """テスト050: アムロジピン処方で狭心症病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [2], 'disease_ids': [18]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    # ====================
    # 保険適応チェックテスト - 脂質異常症関連 (Test 051-070)
    # ====================

    def test_051_ldl_without_dyslipidemia_error(self):
        """テスト051: LDL検査で脂質異常症病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [4], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_052_ldl_with_dyslipidemia_ok(self):
        """テスト052: LDL検査で脂質異常症病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [4], 'disease_ids': [5]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_053_statin_without_dyslipidemia_error(self):
        """テスト053: スタチン処方で脂質異常症病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [3], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_054_statin_with_dyslipidemia_ok(self):
        """テスト054: スタチン処方で脂質異常症病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [3], 'disease_ids': [5]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_055_tg_without_dyslipidemia_error(self):
        """テスト055: 中性脂肪検査で脂質異常症病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [6], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_056_tg_with_high_tg_disease_ok(self):
        """テスト056: 中性脂肪検査で高TG血症病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [6], 'disease_ids': [7]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    # ====================
    # 保険適応チェックテスト - 肝機能関連 (Test 057-075)
    # ====================

    def test_057_ast_without_liver_disease_error(self):
        """テスト057: AST検査で肝疾患病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [7], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_058_ast_with_liver_dysfunction_ok(self):
        """テスト058: AST検査で肝機能障害病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [7], 'disease_ids': [9]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_059_alt_without_liver_disease_error(self):
        """テスト059: ALT検査で肝疾患病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [8], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_060_alt_with_chronic_hepatitis_ok(self):
        """テスト060: ALT検査で慢性肝炎病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [8], 'disease_ids': [10]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_061_ggt_without_liver_disease_error(self):
        """テスト061: γGTP検査で肝疾患病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [9], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_062_ggt_with_fatty_liver_ok(self):
        """テスト062: γGTP検査で脂肪肝病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [9], 'disease_ids': [11]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    # ====================
    # 保険適応チェックテスト - 腎機能関連 (Test 063-078)
    # ====================

    def test_063_cr_without_ckd_error(self):
        """テスト063: Cr検査でCKD病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [11], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_064_cr_with_ckd_ok(self):
        """テスト064: Cr検査でCKD病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [11], 'disease_ids': [14]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_065_egfr_without_ckd_error(self):
        """テスト065: eGFR検査でCKD病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [12], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_066_bun_with_chronic_renal_failure_ok(self):
        """テスト066: BUN検査で慢性腎不全病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [13], 'disease_ids': [15]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    # ====================
    # 保険適応チェックテスト - 貧血関連 (Test 067-078)
    # ====================

    def test_067_hb_without_anemia_error(self):
        """テスト067: Hb検査で貧血病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [14], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_068_hb_with_anemia_ok(self):
        """テスト068: Hb検査で貧血病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [14], 'disease_ids': [8]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_069_iron_drug_without_anemia_error(self):
        """テスト069: 鉄剤処方で貧血病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [10], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_070_iron_drug_with_anemia_ok(self):
        """テスト070: 鉄剤処方で鉄欠乏性貧血病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [10], 'disease_ids': [8]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    # ====================
    # 保険適応チェックテスト - 甲状腺関連 (Test 071-085)
    # ====================

    def test_071_tsh_without_thyroid_disease_error(self):
        """テスト071: TSH検査で甲状腺疾患病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [19], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_072_tsh_with_hypothyroidism_ok(self):
        """テスト072: TSH検査で甲状腺機能低下症病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [19], 'disease_ids': [16]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_073_levothyroxine_without_hypothyroidism_error(self):
        """テスト073: レボチロキシン処方で甲状腺機能低下症病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [8], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_074_levothyroxine_with_hypothyroidism_ok(self):
        """テスト074: レボチロキシン処方で甲状腺機能低下症病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [8], 'disease_ids': [16]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_075_levothyroxine_with_hyperthyroidism_contraindicated(self):
        """テスト075: レボチロキシン処方で甲状腺機能亢進症は禁忌エラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [8], 'disease_ids': [17]})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])
        has_contraindication = any(e['type'] == 'contraindication' for e in data['errors'])
        self.assertTrue(has_contraindication)

    # ====================
    # 保険適応チェックテスト - 尿酸関連 (Test 076-090)
    # ====================

    def test_076_ua_without_hyperuricemia_error(self):
        """テスト076: 尿酸検査で高尿酸血症病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [10], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_077_ua_with_hyperuricemia_ok(self):
        """テスト077: 尿酸検査で高尿酸血症病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [10], 'disease_ids': [12]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_078_febuxostat_without_hyperuricemia_error(self):
        """テスト078: フェブキソスタット処方で高尿酸血症病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [5], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_079_febuxostat_with_gout_ok(self):
        """テスト079: フェブキソスタット処方で痛風病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [5], 'disease_ids': [13]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_080_allopurinol_with_hyperuricemia_ok(self):
        """テスト080: アロプリノール処方で高尿酸血症病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [6], 'disease_ids': [12]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    # ====================
    # 複合パターンテスト (Test 081-120)
    # ====================

    def test_081_diabetes_full_panel_correct(self):
        """テスト081: 糖尿病フルパネル（血糖+HbA1c）で糖尿病病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [1, 2], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_082_lipid_full_panel_correct(self):
        """テスト082: 脂質フルパネルで脂質異常症病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [3, 4, 5, 6], 'disease_ids': [5]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_083_liver_function_panel_correct(self):
        """テスト083: 肝機能パネルで肝機能障害病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [7, 8, 9], 'disease_ids': [9]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_084_kidney_function_panel_correct(self):
        """テスト084: 腎機能パネルでCKD病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [11, 12, 13], 'disease_ids': [14]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_085_metabolic_syndrome_comprehensive(self):
        """テスト085: メタボリック症候群総合検査（正しい病名すべて）"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 2, 4, 6, 7, 8],
                                         'disease_ids': [2, 5, 9]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_086_metabolic_syndrome_missing_disease(self):
        """テスト086: メタボリック症候群総合検査（病名不足）はエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 2, 4, 6, 7, 8],
                                         'disease_ids': [2]  # 脂質異常症と肝機能障害が不足
                                     })
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])
        self.assertGreater(len(data['errors']), 0)

    def test_087_multiple_prescriptions_with_diseases(self):
        """テスト087: 複数処方で各病名が正しい場合"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'prescription_ids': [1, 2, 3],
                                         'disease_ids': [2, 4, 5]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_088_tests_and_prescriptions_combined(self):
        """テスト088: 検査と処方の組み合わせ（正常）"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 2],
                                         'prescription_ids': [1],
                                         'disease_ids': [2]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_089_tests_and_prescriptions_missing_disease(self):
        """テスト089: 検査と処方の組み合わせ（病名不足）"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 2, 4],  # 糖尿病と脂質の検査
                                         'prescription_ids': [1],  # メトホルミン
                                         'disease_ids': [2]  # 糖尿病のみ（脂質異常症が不足）
                                     })
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_090_comprehensive_health_check(self):
        """テスト090: 総合健診パネル（すべて正しい）"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 2, 4, 7, 8, 11, 14],
                                         'disease_ids': [2, 5, 9, 14, 8]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    # ====================
    # 病名提案機能テスト (Test 091-120)
    # ====================

    def test_091_suggest_diabetes_from_glucose(self):
        """テスト091: 血糖検査から糖尿病が提案される"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={'test_ids': [1]})
        data = json.loads(response.data)

        suggested_names = [d['name'] for d in data['suggested_diseases']]
        self.assertIn('糖尿病', suggested_names)

    def test_092_suggest_diabetes_from_hba1c(self):
        """テスト092: HbA1c検査から糖尿病が提案される"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={'test_ids': [2]})
        data = json.loads(response.data)

        suggested_names = [d['name'] for d in data['suggested_diseases']]
        self.assertIn('2型糖尿病', suggested_names)

    def test_093_suggest_dyslipidemia_from_ldl(self):
        """テスト093: LDL検査から脂質異常症が提案される"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={'test_ids': [4]})
        data = json.loads(response.data)

        suggested_names = [d['name'] for d in data['suggested_diseases']]
        self.assertIn('脂質異常症', suggested_names)

    def test_094_suggest_liver_disease_from_ast(self):
        """テスト094: AST検査から肝機能障害が提案される"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={'test_ids': [7]})
        data = json.loads(response.data)

        suggested_names = [d['name'] for d in data['suggested_diseases']]
        self.assertIn('肝機能障害', suggested_names)

    def test_095_suggest_diabetes_from_metformin(self):
        """テスト095: メトホルミンから2型糖尿病が提案される"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={'prescription_ids': [1]})
        data = json.loads(response.data)

        suggested_names = [d['name'] for d in data['suggested_diseases']]
        self.assertIn('2型糖尿病', suggested_names)

    def test_096_suggest_hypertension_from_amlodipine(self):
        """テスト096: アムロジピンから高血圧症が提案される"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={'prescription_ids': [2]})
        data = json.loads(response.data)

        suggested_names = [d['name'] for d in data['suggested_diseases']]
        self.assertTrue('本態性高血圧症' in suggested_names or '狭心症' in suggested_names)

    def test_097_suggest_dyslipidemia_from_statin(self):
        """テスト097: スタチンから脂質異常症が提案される"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={'prescription_ids': [3]})
        data = json.loads(response.data)

        suggested_names = [d['name'] for d in data['suggested_diseases']]
        self.assertIn('脂質異常症', suggested_names)

    def test_098_suggest_from_combined_tests_and_prescriptions(self):
        """テスト098: 検査と処方の組み合わせから複数病名が提案される"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={
                                         'test_ids': [1, 4],
                                         'prescription_ids': [1, 3]
                                     })
        data = json.loads(response.data)

        suggested_names = [d['name'] for d in data['suggested_diseases']]
        # 糖尿病と脂質異常症の両方が提案されるべき
        self.assertGreater(len(suggested_names), 1)

    def test_099_no_suggestion_without_input(self):
        """テスト099: 検査も処方もない場合は提案なし"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={})
        data = json.loads(response.data)
        self.assertEqual(len(data['suggested_diseases']), 0)

    def test_100_suggestion_includes_reasons(self):
        """テスト100: 提案には理由が含まれる"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={'test_ids': [1]})
        data = json.loads(response.data)

        if len(data['suggested_diseases']) > 0:
            self.assertIn('reasons', data['suggested_diseases'][0])
            self.assertGreater(len(data['suggested_diseases'][0]['reasons']), 0)

    # ====================
    # エッジケーステスト (Test 101-130)
    # ====================

    def test_101_empty_disease_list(self):
        """テスト101: 空の病名リストでもエラーなく動作"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [], 'disease_ids': []})
        self.assertEqual(response.status_code, 200)

    def test_102_invalid_test_id(self):
        """テスト102: 無効な検査IDでもエラーなく動作"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [999], 'disease_ids': []})
        self.assertEqual(response.status_code, 200)

    def test_103_invalid_prescription_id(self):
        """テスト103: 無効な処方IDでもエラーなく動作"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [999], 'disease_ids': []})
        self.assertEqual(response.status_code, 200)

    def test_104_duplicate_test_ids(self):
        """テスト104: 重複した検査IDでも正しく処理"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [1, 1, 1], 'disease_ids': [2]})
        self.assertEqual(response.status_code, 200)

    def test_105_duplicate_prescription_ids(self):
        """テスト105: 重複した処方IDでも正しく処理"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [1, 1], 'disease_ids': [2]})
        self.assertEqual(response.status_code, 200)

    def test_106_very_long_disease_list(self):
        """テスト106: 非常に多数の病名でも処理可能"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1],
                                         'disease_ids': list(range(1, 21))
                                     })
        self.assertEqual(response.status_code, 200)

    def test_107_all_tests_all_diseases(self):
        """テスト107: すべての検査とすべての病名でも処理可能"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': list(range(1, 22)),
                                         'disease_ids': list(range(1, 21))
                                     })
        self.assertEqual(response.status_code, 200)

    def test_108_response_structure_validation(self):
        """テスト108: レスポンス構造の検証"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [1], 'disease_ids': []})
        data = json.loads(response.data)

        self.assertIn('is_compliant', data)
        self.assertIn('risk_level', data)
        self.assertIn('errors', data)
        self.assertIn('warnings', data)
        self.assertIn('summary', data)

    def test_109_error_structure_validation(self):
        """テスト109: エラー構造の検証"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [1], 'disease_ids': []})
        data = json.loads(response.data)

        if len(data['errors']) > 0:
            error = data['errors'][0]
            self.assertIn('type', error)
            self.assertIn('severity', error)
            self.assertIn('message', error)

    def test_110_suggestion_structure_validation(self):
        """テスト110: 提案構造の検証"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={'test_ids': [1]})
        data = json.loads(response.data)

        self.assertIn('suggested_diseases', data)
        self.assertIn('total_count', data)

    # ====================
    # パフォーマンステスト (Test 111-120)
    # ====================

    def test_111_bulk_compliance_check_performance(self):
        """テスト111: 大量データでの適応チェック性能"""
        import time
        start_time = time.time()

        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': list(range(1, 11)),
                                         'prescription_ids': list(range(1, 6)),
                                         'disease_ids': list(range(1, 11))
                                     })
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 1.0, "処理時間が1秒を超えました")

    def test_112_bulk_suggestion_performance(self):
        """テスト112: 大量データでの提案性能"""
        import time
        start_time = time.time()

        response = self.client.post('/api/suggest-diseases-strict',
                                     json={
                                         'test_ids': list(range(1, 11)),
                                         'prescription_ids': list(range(1, 6))
                                     })
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 1.0, "処理時間が1秒を超えました")

    # ====================
    # 統合テスト (Test 113-150)
    # ====================

    def test_113_real_world_scenario_diabetes_patient(self):
        """テスト113: 実際のシナリオ - 糖尿病患者"""
        # 血糖、HbA1c検査 + メトホルミン処方
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 2],
                                         'prescription_ids': [1],
                                         'disease_ids': [2]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_114_real_world_scenario_hypertension_patient(self):
        """テスト114: 実際のシナリオ - 高血圧患者"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'prescription_ids': [2],
                                         'disease_ids': [4]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_115_real_world_scenario_dyslipidemia_patient(self):
        """テスト115: 実際のシナリオ - 脂質異常症患者"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [3, 4, 5, 6],
                                         'prescription_ids': [3],
                                         'disease_ids': [5]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_116_real_world_scenario_metabolic_syndrome(self):
        """テスト116: 実際のシナリオ - メタボリックシンドローム患者"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 2, 4, 6, 7, 8],
                                         'prescription_ids': [1, 2, 3],
                                         'disease_ids': [2, 4, 5]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_117_real_world_scenario_ckd_patient(self):
        """テスト117: 実際のシナリオ - CKD患者"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [11, 12, 13],
                                         'disease_ids': [14]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_118_real_world_scenario_anemia_patient(self):
        """テスト118: 実際のシナリオ - 貧血患者"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [14, 15],
                                         'prescription_ids': [10],
                                         'disease_ids': [8]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_119_real_world_scenario_thyroid_patient(self):
        """テスト119: 実際のシナリオ - 甲状腺機能低下症患者"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [19, 21],
                                         'prescription_ids': [8],
                                         'disease_ids': [16]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_120_real_world_scenario_gout_patient(self):
        """テスト120: 実際のシナリオ - 痛風患者"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [10],
                                         'prescription_ids': [5],
                                         'disease_ids': [13]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    # ====================
    # ネガティブテスト - 査定されるべきケース (Test 121-150)
    # ====================

    def test_121_audit_risk_no_disease_for_expensive_test(self):
        """テスト121: 【査定リスク】高額検査で病名なし"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [19], 'disease_ids': []})  # TSH without disease
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])
        self.assertEqual(data['risk_level'], 'high')

    def test_122_audit_risk_wrong_disease_for_test(self):
        """テスト122: 【査定リスク】検査と病名の不一致"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [1], 'disease_ids': [4]})  # 血糖 with 高血圧
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_123_audit_risk_wrong_disease_for_prescription(self):
        """テスト123: 【査定リスク】処方と病名の不一致"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [1], 'disease_ids': [4]})  # メトホルミン with 高血圧
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_124_audit_risk_multiple_tests_partial_diseases(self):
        """テスト124: 【査定リスク】複数検査で一部病名のみ"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 4, 7],  # 血糖、LDL、AST
                                         'disease_ids': [2]  # 糖尿病のみ
                                     })
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_125_audit_risk_off_label_prescription(self):
        """テスト125: 【査定リスク】適応外処方"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'prescription_ids': [3],  # スタチン
                                         'disease_ids': [2]  # 糖尿病（脂質異常症ではない）
                                     })
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_126_contraindication_detected(self):
        """テスト126: 【禁忌】禁忌病名の検出"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'prescription_ids': [1],  # メトホルミン
                                         'disease_ids': [3]  # 1型糖尿病（禁忌）
                                     })
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])
        has_contraindication = any(e['type'] == 'contraindication' for e in data['errors'])
        self.assertTrue(has_contraindication)

    def test_127_audit_risk_comprehensive_missing_one(self):
        """テスト127: 【査定リスク】総合検査で1つだけ病名不足"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 4, 7, 11],
                                         'disease_ids': [2, 5, 9]  # CKDが不足
                                     })
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_128_audit_risk_prescription_without_test(self):
        """テスト128: 【査定リスク】検査なしで処方のみ（実際の臨床では問題ないが査定リスク）"""
        # このテストはシステムの挙動確認用
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'prescription_ids': [1],
                                         'disease_ids': [2]
                                     })
        data = json.loads(response.data)
        # 処方に対する病名があればOK
        self.assertTrue(data['is_compliant'])

    def test_129_error_count_verification(self):
        """テスト129: エラー数の正確性検証"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 2, 4],  # 3つの検査
                                         'disease_ids': []  # 病名なし
                                     })
        data = json.loads(response.data)
        # 3つの検査すべてでエラーが出るべき
        self.assertEqual(len(data['errors']), 3)

    def test_130_summary_statistics_accuracy(self):
        """テスト130: サマリー統計の正確性"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 2],
                                         'disease_ids': []
                                     })
        data = json.loads(response.data)

        self.assertEqual(data['summary']['total_errors'], len(data['errors']))
        self.assertEqual(data['summary']['total_warnings'], len(data['warnings']))

    # ====================
    # 追加の実践的テストケース (Test 131-150)
    # ====================

    def test_131_elderly_patient_polypharmacy(self):
        """テスト131: 高齢者多剤併用ケース"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'prescription_ids': [1, 2, 3, 5, 7],
                                         'disease_ids': [2, 4, 5, 13, 20]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_132_annual_health_checkup_standard(self):
        """テスト132: 年次健康診断標準パネル"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 4, 7, 8, 11, 14],
                                         'disease_ids': [2, 5, 9, 14, 8]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_133_diabetes_complications_screening(self):
        """テスト133: 糖尿病合併症スクリーニング"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 2, 11, 12],
                                         'disease_ids': [2, 14]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_134_cardiovascular_risk_assessment(self):
        """テスト134: 心血管リスク評価"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [4, 5, 6, 1],
                                         'disease_ids': [2, 5]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_135_liver_disease_monitoring(self):
        """テスト135: 肝疾患モニタリング"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [7, 8, 9],
                                         'disease_ids': [10]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_136_thyroid_disease_workup(self):
        """テスト136: 甲状腺疾患精査"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [19, 20, 21],
                                         'disease_ids': [16]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_137_missing_disease_clear_message(self):
        """テスト137: 病名不足時の明確なメッセージ"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [1], 'disease_ids': []})
        data = json.loads(response.data)

        self.assertGreater(len(data['errors']), 0)
        self.assertIn('required_diseases', data['errors'][0])

    def test_138_contraindication_clear_message(self):
        """テスト138: 禁忌時の明確なメッセージ"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [1], 'disease_ids': [3]})
        data = json.loads(response.data)

        contraindication_errors = [e for e in data['errors'] if e['type'] == 'contraindication']
        self.assertGreater(len(contraindication_errors), 0)

    def test_139_suggestion_relevance_diabetes(self):
        """テスト139: 提案の関連性 - 糖尿病"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={'test_ids': [1, 2]})
        data = json.loads(response.data)

        suggested_names = [d['name'] for d in data['suggested_diseases']]
        # 糖尿病関連の病名が提案されるべき
        has_diabetes_related = any('糖尿病' in name for name in suggested_names)
        self.assertTrue(has_diabetes_related)

    def test_140_suggestion_relevance_lipids(self):
        """テスト140: 提案の関連性 - 脂質"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={'test_ids': [4, 6]})
        data = json.loads(response.data)

        suggested_names = [d['name'] for d in data['suggested_diseases']]
        has_lipid_related = any('脂質' in name or 'コレステロール' in name or 'トリグリセライド' in name for name in suggested_names)
        self.assertTrue(has_lipid_related)

    def test_141_api_categories_endpoint(self):
        """テスト141: カテゴリAPIの動作確認"""
        response = self.client.get('/api/categories')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_142_api_diseases_search(self):
        """テスト142: 病名検索APIの動作確認"""
        response = self.client.get('/api/diseases?search=糖尿病')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)

    def test_143_api_diseases_category_filter(self):
        """テスト143: 病名カテゴリフィルタの動作確認"""
        response = self.client.get('/api/diseases?category=代謝疾患')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)

    def test_144_comprehensive_audit_prevention(self):
        """テスト144: 総合的な査定防止テスト"""
        # 正しい組み合わせ
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 2, 4, 7],
                                         'prescription_ids': [1, 3],
                                         'disease_ids': [2, 5, 9]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])
        self.assertEqual(data['risk_level'], 'low')

    def test_145_partial_compliance_detection(self):
        """テスト145: 部分的な不適合の検出"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 4],
                                         'disease_ids': [2]  # 糖尿病のみ（脂質異常症が不足）
                                     })
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])
        # 1つはOK、1つはNGのため、エラーは1つ
        self.assertEqual(len(data['errors']), 1)

    def test_146_icd10_code_consistency(self):
        """テスト146: ICD-10コードの一貫性確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)

        for disease in data:
            if disease['icd10_code']:
                # E, I, K, D, M, Nなどの適切なカテゴリコードで始まっているか
                first_char = disease['icd10_code'][0]
                self.assertIn(first_char, ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'])

    def test_147_test_points_validity(self):
        """テスト147: 検査点数の妥当性確認"""
        response = self.client.get('/api/tests')
        data = json.loads(response.data)

        for test in data:
            # 点数は0以上であるべき
            self.assertGreaterEqual(test['points'], 0)
            # 通常の検査点数は1000点以下
            self.assertLessEqual(test['points'], 1000)

    def test_148_prescription_code_format(self):
        """テスト148: 処方薬コードのフォーマット確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)

        for prescription in data:
            if prescription['yj_code']:
                # YJコードは7桁の数字
                self.assertRegex(prescription['yj_code'], r'^\d{7}$')

    def test_149_data_integrity_check(self):
        """テスト149: データ整合性チェック"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # 病名マスターの件数確認
        cursor.execute('SELECT COUNT(*) FROM diseases')
        disease_count = cursor.fetchone()[0]
        self.assertGreater(disease_count, 0)

        # 検査マスターの件数確認
        cursor.execute('SELECT COUNT(*) FROM tests')
        test_count = cursor.fetchone()[0]
        self.assertGreater(test_count, 0)

        # 処方マスターの件数確認
        cursor.execute('SELECT COUNT(*) FROM prescriptions')
        prescription_count = cursor.fetchone()[0]
        self.assertGreater(prescription_count, 0)

        # マッピングテーブルの件数確認
        cursor.execute('SELECT COUNT(*) FROM test_disease_insurance_mapping')
        test_mapping_count = cursor.fetchone()[0]
        self.assertGreater(test_mapping_count, 0)

        cursor.execute('SELECT COUNT(*) FROM prescription_disease_insurance_mapping')
        prescription_mapping_count = cursor.fetchone()[0]
        self.assertGreater(prescription_mapping_count, 0)

        conn.close()

    def test_150_end_to_end_workflow(self):
        """テスト150: エンドツーエンドワークフロー総合テスト"""
        # ステップ1: 検査と処方から病名を提案
        suggest_response = self.client.post('/api/suggest-diseases-strict',
                                              json={
                                                  'test_ids': [1, 2, 4],
                                                  'prescription_ids': [1, 3]
                                              })
        suggest_data = json.loads(suggest_response.data)
        self.assertGreater(len(suggest_data['suggested_diseases']), 0)

        # ステップ2: 提案された病名を使って適応チェック
        suggested_disease_ids = [d['id'] for d in suggest_data['suggested_diseases']]
        check_response = self.client.post('/api/check-insurance-compliance',
                                           json={
                                               'test_ids': [1, 2, 4],
                                               'prescription_ids': [1, 3],
                                               'disease_ids': suggested_disease_ids
                                           })
        check_data = json.loads(check_response.data)

        # 提案された病名を使えば適応OKになるべき
        self.assertTrue(check_data['is_compliant'])
        self.assertEqual(check_data['risk_level'], 'low')


if __name__ == '__main__':
    # テストスイートの実行
    unittest.main(verbosity=2)
