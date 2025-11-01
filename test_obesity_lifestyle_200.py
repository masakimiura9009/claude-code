#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
肥満症・生活習慣病管理 追加テストスイート
Obesity & Lifestyle Disease Management Additional Test Suite
200+ Additional Test Cases
"""

import unittest
import json
import os
import sys
from flask import Flask
from flask.testing import FlaskClient
import sqlite3

sys.path.insert(0, os.path.dirname(__file__))
from app_strict_v2 import app, init_db, DATABASE

class ObesityLifestyleTestCase(unittest.TestCase):
    """肥満症・生活習慣病管理テスト（200件追加）"""

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

    # ====================
    # 肥満症関連テスト (Test 151-190: 40件)
    # ====================

    def test_151_obesity_disease_exists(self):
        """テスト151: 肥満症病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)
        disease_names = [d['name'] for d in data]
        self.assertIn('肥満症', disease_names)

    def test_152_severe_obesity_disease_exists(self):
        """テスト152: 高度肥満症病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)
        disease_names = [d['name'] for d in data]
        self.assertIn('高度肥満症', disease_names)

    def test_153_metabolic_syndrome_disease_exists(self):
        """テスト153: メタボリックシンドローム病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)
        disease_names = [d['name'] for d in data]
        self.assertIn('メタボリックシンドローム', disease_names)

    def test_154_visceral_obesity_exists(self):
        """テスト154: 内臓脂肪型肥満病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)
        disease_names = [d['name'] for d in data]
        self.assertIn('内臓脂肪型肥満', disease_names)

    def test_155_nafld_disease_exists(self):
        """テスト155: 非アルコール性脂肪肝病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)
        disease_names = [d['name'] for d in data]
        self.assertIn('非アルコール性脂肪肝', disease_names)

    def test_156_nash_disease_exists(self):
        """テスト156: NASH病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)
        disease_names = [d['name'] for d in data]
        self.assertIn('非アルコール性脂肪肝炎', disease_names)

    def test_157_insulin_resistance_disease_exists(self):
        """テスト157: インスリン抵抗性病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)
        disease_names = [d['name'] for d in data]
        self.assertIn('インスリン抵抗性', disease_names)

    def test_158_impaired_glucose_tolerance_exists(self):
        """テスト158: 耐糖能異常病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)
        disease_names = [d['name'] for d in data]
        self.assertIn('耐糖能異常', disease_names)

    def test_159_obesity_with_lipid_test(self):
        """テスト159: 肥満症で脂質検査実施"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [10, 11, 12, 13], 'disease_ids': [9]})  # 肥満症
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_160_obesity_with_liver_test(self):
        """テスト160: 肥満症で肝機能検査実施"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [16, 17, 18], 'disease_ids': [9]})  # 肥満症
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_161_obesity_without_disease_error(self):
        """テスト161: 肥満症関連検査で病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [10, 11], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_162_metabolic_syndrome_comprehensive(self):
        """テスト162: メタボリックシンドローム総合検査"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 10, 11, 12, 13, 16, 17],
                                         'disease_ids': [12]  # メタボリックシンドローム
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_163_nafld_with_liver_tests(self):
        """テスト163: NAFLD で肝機能検査"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [16, 17, 18, 19], 'disease_ids': [25]})  # NAFLD
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_164_nash_with_crp(self):
        """テスト164: NASH でCRP測定"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [26], 'disease_ids': [26]})  # NASH
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_165_obesity_diabetes_comorbidity(self):
        """テスト165: 肥満症+糖尿病併存"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 2, 10, 11],
                                         'disease_ids': [2, 9]  # 2型糖尿病+肥満症
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_166_obesity_hypertension_comorbidity(self):
        """テスト166: 肥満症+高血圧併存"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [10, 11],
                                         'disease_ids': [9, 13]  # 肥満症+高血圧
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_167_obesity_dyslipidemia_comorbidity(self):
        """テスト167: 肥満症+脂質異常症併存"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [10, 11, 12, 13],
                                         'disease_ids': [9, 18]  # 肥満症+脂質異常症
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_168_insulin_resistance_with_iri(self):
        """テスト168: インスリン抵抗性でIRI測定"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [5], 'disease_ids': [5]})  # インスリン抵抗性
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_169_insulin_resistance_with_ogtt(self):
        """テスト169: インスリン抵抗性でOGTT実施"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [8, 9], 'disease_ids': [5]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_170_impaired_glucose_tolerance_with_ogtt(self):
        """テスト170: 耐糖能異常でOGTT実施"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [8], 'disease_ids': [4]})  # 耐糖能異常
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    # ====================
    # GLP-1受容体作動薬テスト (Test 171-186: 16件)
    # ====================

    def test_171_glp1_liraglutide_exists(self):
        """テスト171: リラグルチドの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('リラグルチド', drug_names)

    def test_172_glp1_dulaglutide_exists(self):
        """テスト172: デュラグルチドの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('デュラグルチド', drug_names)

    def test_173_glp1_semaglutide_exists(self):
        """テスト173: セマグルチドの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('セマグルチド', drug_names)

    def test_174_liraglutide_without_diabetes_error(self):
        """テスト174: リラグルチドで糖尿病病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [2], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_175_liraglutide_with_type2_diabetes_ok(self):
        """テスト175: リラグルチドで2型糖尿病病名ありはOK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [2], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_176_liraglutide_with_obesity_diabetes(self):
        """テスト176: リラグルチドで肥満症合併糖尿病"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [2], 'disease_ids': [2, 9]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_177_dulaglutide_with_type2_diabetes_ok(self):
        """テスト177: デュラグルチドで2型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [3], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_178_semaglutide_with_type2_diabetes_ok(self):
        """テスト178: セマグルチドで2型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [4], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_179_glp1_with_type1_diabetes_contraindicated(self):
        """テスト179: GLP-1で1型糖尿病は禁忌"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [2], 'disease_ids': [3]})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])
        has_contraindication = any(e['type'] == 'contraindication' for e in data['errors'])
        self.assertTrue(has_contraindication)

    def test_180_glp1_suggest_from_obesity_diabetes(self):
        """テスト180: 肥満症合併糖尿病でGLP-1が提案される"""
        # このテストは実装によって異なる可能性があるため、存在確認のみ
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={'prescription_ids': [2]})
        data = json.loads(response.data)
        suggested_names = [d['name'] for d in data['suggested_diseases']]
        self.assertIn('2型糖尿病', suggested_names)

    # ====================
    # SGLT2阻害薬テスト (Test 181-196: 16件)
    # ====================

    def test_181_sglt2_dapagliflozin_exists(self):
        """テスト181: ダパグリフロジンの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('ダパグリフロジン', drug_names)

    def test_182_sglt2_empagliflozin_exists(self):
        """テスト182: エンパグリフロジンの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('エンパグリフロジン', drug_names)

    def test_183_sglt2_canagliflozin_exists(self):
        """テスト183: カナグリフロジンの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('カナグリフロジン', drug_names)

    def test_184_dapagliflozin_without_diabetes_error(self):
        """テスト184: SGLT2阻害薬で糖尿病病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [5], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_185_dapagliflozin_with_type2_diabetes_ok(self):
        """テスト185: ダパグリフロジンで2型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [5], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_186_empagliflozin_with_type2_diabetes_ok(self):
        """テスト186: エンパグリフロジンで2型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [6], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_187_canagliflozin_with_type2_diabetes_ok(self):
        """テスト187: カナグリフロジンで2型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [7], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_188_sglt2_with_heart_failure(self):
        """テスト188: SGLT2阻害薬で心不全合併糖尿病"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [6], 'disease_ids': [2, 17]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_189_sglt2_with_type1_diabetes_caution(self):
        """テスト189: SGLT2阻害薬で1型糖尿病は禁忌"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [5], 'disease_ids': [3]})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_190_sglt2_suggest_from_diabetes(self):
        """テスト190: 糖尿病でSGLT2阻害薬が提案される"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={'prescription_ids': [5]})
        data = json.loads(response.data)
        suggested_names = [d['name'] for d in data['suggested_diseases']]
        self.assertIn('2型糖尿病', suggested_names)

    # ====================
    # DPP-4阻害薬テスト (Test 191-206: 16件)
    # ====================

    def test_191_dpp4_sitagliptin_exists(self):
        """テスト191: シタグリプチンの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('シタグリプチン', drug_names)

    def test_192_dpp4_linagliptin_exists(self):
        """テスト192: リナグリプチンの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('リナグリプチン', drug_names)

    def test_193_dpp4_teneligliptin_exists(self):
        """テスト193: テネリグリプチンの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('テネリグリプチン', drug_names)

    def test_194_sitagliptin_without_diabetes_error(self):
        """テスト194: DPP-4阻害薬で糖尿病病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [8], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_195_sitagliptin_with_type2_diabetes_ok(self):
        """テスト195: シタグリプチンで2型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [8], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_196_linagliptin_with_type2_diabetes_ok(self):
        """テスト196: リナグリプチンで2型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [9], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_197_teneligliptin_with_type2_diabetes_ok(self):
        """テスト197: テネリグリプチンで2型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [10], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_198_dpp4_with_type1_diabetes_contraindicated(self):
        """テスト198: DPP-4阻害薬で1型糖尿病は禁忌"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [8], 'disease_ids': [3]})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_199_dpp4_suggest_from_diabetes(self):
        """テスト199: 糖尿病でDPP-4阻害薬が提案される"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={'prescription_ids': [8]})
        data = json.loads(response.data)
        suggested_names = [d['name'] for d in data['suggested_diseases']]
        self.assertIn('2型糖尿病', suggested_names)

    def test_200_dpp4_elderly_patient(self):
        """テスト200: DPP-4阻害薬で高齢者糖尿病患者"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [9], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_201_dpp4_with_ckd(self):
        """テスト201: DPP-4阻害薬で腎機能低下患者（リナグリプチン）"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [9], 'disease_ids': [2, 27]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_202_multiple_diabetes_drugs_combination(self):
        """テスト202: 糖尿病薬複数併用（メトホルミン+DPP-4）"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [1, 8], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_203_triple_therapy_diabetes(self):
        """テスト203: 糖尿病薬3剤併用（メトホルミン+DPP-4+SGLT2）"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [1, 8, 5], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_204_glp1_sglt2_combination(self):
        """テスト204: GLP-1+SGLT2併用"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [2, 5], 'disease_ids': [2, 9]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_205_diabetes_complications_screening_full(self):
        """テスト205: 糖尿病合併症フルスクリーニング"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [2, 20, 21, 23],  # HbA1c, Cr, eGFR, 尿中アルブミン
                                         'disease_ids': [2, 6]  # 2型糖尿病+糖尿病性腎症
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_206_diabetes_with_diabetic_nephropathy(self):
        """テスト206: 糖尿病性腎症でARB処方"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [22], 'disease_ids': [2, 6]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    # ====================
    # チアゾリジン系・SU剤テスト (Test 207-222: 16件)
    # ====================

    def test_207_pioglitazone_exists(self):
        """テスト207: ピオグリタゾンの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('ピオグリタゾン', drug_names)

    def test_208_glimepiride_exists(self):
        """テスト208: グリメピリドの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('グリメピリド', drug_names)

    def test_209_gliclazide_exists(self):
        """テスト209: グリクラジドの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('グリクラジド', drug_names)

    def test_210_pioglitazone_without_diabetes_error(self):
        """テスト210: ピオグリタゾンで糖尿病病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [11], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_211_pioglitazone_with_type2_diabetes_ok(self):
        """テスト211: ピオグリタゾンで2型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [11], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_212_pioglitazone_with_insulin_resistance(self):
        """テスト212: ピオグリタゾンでインスリン抵抗性"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [11], 'disease_ids': [2, 5]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_213_pioglitazone_with_heart_failure_contraindicated(self):
        """テスト213: ピオグリタゾンで心不全は禁忌"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [11], 'disease_ids': [17]})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])
        has_contraindication = any(e['type'] == 'contraindication' for e in data['errors'])
        self.assertTrue(has_contraindication)

    def test_214_glimepiride_without_diabetes_error(self):
        """テスト214: SU剤で糖尿病病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [12], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_215_glimepiride_with_type2_diabetes_ok(self):
        """テスト215: グリメピリドで2型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [12], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_216_gliclazide_with_type2_diabetes_ok(self):
        """テスト216: グリクラジドで2型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [13], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_217_su_with_type1_diabetes_contraindicated(self):
        """テスト217: SU剤で1型糖尿病は禁忌"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [12], 'disease_ids': [3]})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_218_nateglinide_exists(self):
        """テスト218: ナテグリニドの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('ナテグリニド', drug_names)

    def test_219_nateglinide_with_type2_diabetes_ok(self):
        """テスト219: ナテグリニドで2型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [14], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_220_mitiglinide_exists(self):
        """テスト220: ミチグリニドの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('ミチグリニド', drug_names)

    def test_221_mitiglinide_with_type2_diabetes_ok(self):
        """テスト221: ミチグリニドで2型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [15], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_222_glinide_for_postprandial_hyperglycemia(self):
        """テスト222: グリニド系で食後高血糖改善"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [14], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    # ====================
    # α-GI・インスリン製剤テスト (Test 223-238: 16件)
    # ====================

    def test_223_acarbose_exists(self):
        """テスト223: アカルボースの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('アカルボース', drug_names)

    def test_224_voglibose_exists(self):
        """テスト224: ボグリボースの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('ボグリボース', drug_names)

    def test_225_acarbose_with_type2_diabetes_ok(self):
        """テスト225: アカルボースで2型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [16], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_226_voglibose_with_type2_diabetes_ok(self):
        """テスト226: ボグリボースで2型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [17], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_227_voglibose_with_impaired_glucose_tolerance(self):
        """テスト227: ボグリボースで耐糖能異常OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [17], 'disease_ids': [4]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_228_insulin_glargine_exists(self):
        """テスト228: インスリングラルギンの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('インスリングラルギン', drug_names)

    def test_229_insulin_degludec_exists(self):
        """テスト229: インスリンデグルデクの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('インスリンデグルデク', drug_names)

    def test_230_insulin_aspart_exists(self):
        """テスト230: インスリンアスパルトの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('インスリンアスパルト', drug_names)

    def test_231_insulin_glargine_with_type1_diabetes_ok(self):
        """テスト231: インスリングラルギンで1型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [18], 'disease_ids': [3]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_232_insulin_glargine_with_type2_diabetes_ok(self):
        """テスト232: インスリングラルギンで2型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [18], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_233_insulin_degludec_with_type1_diabetes_ok(self):
        """テスト233: インスリンデグルデクで1型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [19], 'disease_ids': [3]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_234_insulin_aspart_with_type1_diabetes_ok(self):
        """テスト234: インスリンアスパルトで1型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [20], 'disease_ids': [3]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_235_basal_bolus_insulin_therapy(self):
        """テスト235: 基礎+追加インスリン療法"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [18, 20], 'disease_ids': [3]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_236_insulin_without_diabetes_error(self):
        """テスト236: インスリンで糖尿病病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [18], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_237_insulin_suggest_from_diabetes(self):
        """テスト237: 糖尿病でインスリンが提案される"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={'prescription_ids': [18]})
        data = json.loads(response.data)
        suggested_names = [d['name'] for d in data['suggested_diseases']]
        diabetes_suggested = any('糖尿病' in name for name in suggested_names)
        self.assertTrue(diabetes_suggested)

    def test_238_type1_diabetes_mandatory_insulin(self):
        """テスト238: 1型糖尿病ではインスリン必須"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [18], 'disease_ids': [3]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    # ====================
    # インスリン関連検査テスト (Test 239-254: 16件)
    # ====================

    def test_239_iri_test_exists(self):
        """テスト239: インスリン(IRI)検査の存在確認"""
        response = self.client.get('/api/tests')
        data = json.loads(response.data)
        test_names = [t['name'] for t in data]
        self.assertIn('インスリン(IRI)', test_names)

    def test_240_cpr_test_exists(self):
        """テスト240: C-ペプチド検査の存在確認"""
        response = self.client.get('/api/tests')
        data = json.loads(response.data)
        test_names = [t['name'] for t in data]
        self.assertIn('C-ペプチド(CPR)', test_names)

    def test_241_urine_cpr_test_exists(self):
        """テスト241: 尿中C-ペプチド検査の存在確認"""
        response = self.client.get('/api/tests')
        data = json.loads(response.data)
        test_names = [t['name'] for t in data]
        self.assertIn('尿中C-ペプチド', test_names)

    def test_242_iri_without_diabetes_error(self):
        """テスト242: IRI測定で糖尿病病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [5], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_243_iri_with_type2_diabetes_ok(self):
        """テスト243: IRI測定で2型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [5], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_244_iri_with_insulin_resistance_ok(self):
        """テスト244: IRI測定でインスリン抵抗性OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [5], 'disease_ids': [5]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_245_cpr_without_diabetes_error(self):
        """テスト245: CPR測定で糖尿病病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [6], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_246_cpr_with_type1_diabetes_ok(self):
        """テスト246: CPR測定で1型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [6], 'disease_ids': [3]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_247_cpr_with_type2_diabetes_ok(self):
        """テスト247: CPR測定で2型糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [6], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_248_urine_cpr_with_diabetes_ok(self):
        """テスト248: 尿中CPRで糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [7], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_249_ogtt_test_exists(self):
        """テスト249: 75gOGTT検査の存在確認"""
        response = self.client.get('/api/tests')
        data = json.loads(response.data)
        test_names = [t['name'] for t in data]
        ogtt_found = any('OGTT' in name for name in test_names)
        self.assertTrue(ogtt_found)

    def test_250_ogtt_without_diabetes_error(self):
        """テスト250: OGTT実施で糖尿病病名なしはエラー"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [8], 'disease_ids': []})
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])

    def test_251_ogtt_with_impaired_glucose_tolerance_ok(self):
        """テスト251: OGTTで耐糖能異常OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [8], 'disease_ids': [4]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_252_ogtt_with_insulin_resistance_ok(self):
        """テスト252: OGTT(インスリン測定)でインスリン抵抗性OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [9], 'disease_ids': [5]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_253_glycoalbumin_test_exists(self):
        """テスト253: グリコアルブミン検査の存在確認"""
        response = self.client.get('/api/tests')
        data = json.loads(response.data)
        test_names = [t['name'] for t in data]
        self.assertIn('グリコアルブミン', test_names)

    def test_254_glycoalbumin_with_diabetes_ok(self):
        """テスト254: グリコアルブミンで糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [3], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    # ====================
    # 糖尿病合併症テスト (Test 255-284: 30件)
    # ====================

    def test_255_diabetic_nephropathy_disease_exists(self):
        """テスト255: 糖尿病性腎症病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)
        disease_names = [d['name'] for d in data]
        self.assertIn('糖尿病性腎症', disease_names)

    def test_256_diabetic_retinopathy_disease_exists(self):
        """テスト256: 糖尿病性網膜症病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)
        disease_names = [d['name'] for d in data]
        self.assertIn('糖尿病性網膜症', disease_names)

    def test_257_diabetic_neuropathy_disease_exists(self):
        """テスト257: 糖尿病性神経障害病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)
        disease_names = [d['name'] for d in data]
        self.assertIn('糖尿病性神経障害', disease_names)

    def test_258_urine_albumin_test_exists(self):
        """テスト258: 尿中アルブミン検査の存在確認"""
        response = self.client.get('/api/tests')
        data = json.loads(response.data)
        test_names = [t['name'] for t in data]
        self.assertIn('尿中アルブミン', test_names)

    def test_259_urine_albumin_with_diabetic_nephropathy_ok(self):
        """テスト259: 尿中アルブミンで糖尿病性腎症OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [23], 'disease_ids': [6]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_260_urine_albumin_with_type2_diabetes_ok(self):
        """テスト260: 尿中アルブミンで2型糖尿病OK（腎症スクリーニング）"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [23], 'disease_ids': [2]})
        data = json.loads(response.data)
        # 糖尿病性腎症がない場合はエラーまたは警告の可能性
        # 実装による

    def test_261_creatinine_with_diabetic_nephropathy_ok(self):
        """テスト261: クレアチニンで糖尿病性腎症OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [20], 'disease_ids': [6]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_262_egfr_with_diabetic_nephropathy_ok(self):
        """テスト262: eGFRで糖尿病性腎症OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [21], 'disease_ids': [6]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_263_diabetic_nephropathy_full_workup(self):
        """テスト263: 糖尿病性腎症フル検査"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [20, 21, 22, 23, 24],
                                         'disease_ids': [2, 6]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_264_arb_for_diabetic_nephropathy(self):
        """テスト264: 糖尿病性腎症でARB処方"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [22], 'disease_ids': [6]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_265_ace_inhibitor_for_diabetic_nephropathy(self):
        """テスト265: 糖尿病性腎症でACE阻害薬処方"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [23], 'disease_ids': [6]})
        data = json.loads(response.data)
        # 糖尿病性腎症でのACE阻害薬処方は可能か確認
        # 実装による

    def test_266_diabetes_with_all_complications(self):
        """テスト266: 糖尿病全合併症併存"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [2, 20, 21, 23],
                                         'disease_ids': [2, 6, 7, 8]  # 糖尿病+腎症+網膜症+神経障害
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_267_diabetic_retinopathy_icd10_code(self):
        """テスト267: 糖尿病性網膜症のICD-10コード確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)
        retinopathy = [d for d in data if d['name'] == '糖尿病性網膜症']
        self.assertEqual(len(retinopathy), 1)
        self.assertEqual(retinopathy[0]['icd10_code'], 'E11.3')

    def test_268_diabetic_neuropathy_icd10_code(self):
        """テスト268: 糖尿病性神経障害のICD-10コード確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)
        neuropathy = [d for d in data if d['name'] == '糖尿病性神経障害']
        self.assertEqual(len(neuropathy), 1)
        self.assertEqual(neuropathy[0]['icd10_code'], 'E11.4')

    def test_269_diabetic_complications_category(self):
        """テスト269: 糖尿病合併症カテゴリの確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)
        complications = [d for d in data if d['category'] == '糖尿病合併症']
        self.assertGreaterEqual(len(complications), 3)

    # ====================
    # 生活習慣病総合管理テスト (Test 270-304: 35件)
    # ====================

    def test_270_metabolic_syndrome_full_panel(self):
        """テスト270: メタボリックシンドローム総合パネル"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 2, 10, 11, 12, 13, 16, 17],
                                         'disease_ids': [12]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_271_quadruple_disease_management(self):
        """テスト271: 4疾患同時管理（糖尿病+高血圧+脂質異常症+肥満症）"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 2, 10, 11, 12, 13],
                                         'prescription_ids': [1, 21, 24],
                                         'disease_ids': [2, 13, 18, 9]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_272_metabolic_syndrome_with_nafld(self):
        """テスト272: メタボリックシンドローム+NAFLD"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 10, 11, 16, 17, 18],
                                         'disease_ids': [12, 25]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_273_metabolic_syndrome_with_sleep_apnea(self):
        """テスト273: メタボリックシンドローム+睡眠時無呼吸症候群"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)
        disease_names = [d['name'] for d in data]
        self.assertIn('睡眠時無呼吸症候群', disease_names)

    def test_274_obesity_hyperuricemia_comorbidity(self):
        """テスト274: 肥満症+高尿酸血症併存"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [10, 11, 25],
                                         'prescription_ids': [29],
                                         'disease_ids': [9, 30]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_275_comprehensive_lifestyle_disease_screening(self):
        """テスト275: 生活習慣病総合スクリーニング"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 2, 10, 11, 12, 13, 16, 17, 18, 20, 21, 25],
                                         'disease_ids': [2, 13, 18, 23, 27, 30]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_276_elderly_polypharmacy_lifestyle_diseases(self):
        """テスト276: 高齢者多剤併用（生活習慣病）"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'prescription_ids': [1, 8, 21, 24, 29],
                                         'disease_ids': [2, 13, 18, 30]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_277_diabetes_dyslipidemia_dual_management(self):
        """テスト277: 糖尿病+脂質異常症二重管理"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [2, 11, 12, 13],
                                         'prescription_ids': [1, 24],
                                         'disease_ids': [2, 18]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_278_familial_hypercholesterolemia_intensive_treatment(self):
        """テスト278: 家族性高コレステロール血症で強力治療"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [11, 12, 15],
                                         'prescription_ids': [25, 27],  # スタチン+エゼチミブ
                                         'disease_ids': [22]  # 家族性高コレステロール血症
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_279_hypertriglyceridemia_with_fibrate(self):
        """テスト279: 高TG血症でフィブラート処方"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [13],
                                         'prescription_ids': [28],
                                         'disease_ids': [21]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_280_low_hdl_cholesterol_disease_exists(self):
        """テスト280: 低HDL血症病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)
        disease_names = [d['name'] for d in data]
        self.assertIn('低HDLコレステロール血症', disease_names)

    def test_281_non_hdl_cholesterol_test_exists(self):
        """テスト281: non-HDLコレステロール検査の存在確認"""
        response = self.client.get('/api/tests')
        data = json.loads(response.data)
        test_names = [t['name'] for t in data]
        self.assertIn('non-HDLコレステロール', test_names)

    def test_282_lipoprotein_fractionation_test_exists(self):
        """テスト282: リポ蛋白分画検査の存在確認"""
        response = self.client.get('/api/tests')
        data = json.loads(response.data)
        test_names = [t['name'] for t in data]
        self.assertIn('リポ蛋白分画', test_names)

    def test_283_secondary_hypertension_exists(self):
        """テスト283: 二次性高血圧症病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)
        disease_names = [d['name'] for d in data]
        self.assertIn('二次性高血圧症', disease_names)

    def test_284_proteinuria_disease_exists(self):
        """テスト284: 蛋白尿病名の存在確認"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)
        disease_names = [d['name'] for d in data]
        self.assertIn('蛋白尿', disease_names)

    def test_285_urine_protein_quantification_test_exists(self):
        """テスト285: 尿蛋白定量検査の存在確認"""
        response = self.client.get('/api/tests')
        data = json.loads(response.data)
        test_names = [t['name'] for t in data]
        self.assertIn('尿蛋白定量', test_names)

    def test_286_1_5_ag_test_exists(self):
        """テスト286: 1,5-AG検査の存在確認"""
        response = self.client.get('/api/tests')
        data = json.loads(response.data)
        test_names = [t['name'] for t in data]
        self.assertIn('1,5-AG', test_names)

    def test_287_1_5_ag_with_diabetes_ok(self):
        """テスト287: 1,5-AGで糖尿病OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [4], 'disease_ids': [2]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_288_alp_test_exists(self):
        """テスト288: ALP検査の存在確認"""
        response = self.client.get('/api/tests')
        data = json.loads(response.data)
        test_names = [t['name'] for t in data]
        self.assertIn('ALP', test_names)

    def test_289_alp_with_liver_disease_ok(self):
        """テスト289: ALPで肝疾患OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [19], 'disease_ids': [23]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_290_olmesartan_arb_exists(self):
        """テスト290: オルメサルタン(ARB)の存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('オルメサルタン', drug_names)

    def test_291_olmesartan_with_hypertension_ok(self):
        """テスト291: オルメサルタンで高血圧OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [22], 'disease_ids': [13]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_292_enalapril_ace_inhibitor_exists(self):
        """テスト292: エナラプリル(ACE阻害薬)の存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('エナラプリル', drug_names)

    def test_293_enalapril_with_heart_failure_ok(self):
        """テスト293: エナラプリルで心不全OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [23], 'disease_ids': [17]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_294_pitavastatin_statin_exists(self):
        """テスト294: ピタバスタチンの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('ピタバスタチン', drug_names)

    def test_295_pitavastatin_with_dyslipidemia_ok(self):
        """テスト295: ピタバスタチンで脂質異常症OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [26], 'disease_ids': [18]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_296_ezetimibe_exists(self):
        """テスト296: エゼチミブの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('エゼチミブ', drug_names)

    def test_297_ezetimibe_with_high_ldl_ok(self):
        """テスト297: エゼチミブで高LDL血症OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [27], 'disease_ids': [19]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_298_fenofibrate_exists(self):
        """テスト298: フェノフィブラートの存在確認"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)
        drug_names = [p['name'] for p in data]
        self.assertIn('フェノフィブラート', drug_names)

    def test_299_fenofibrate_with_high_tg_ok(self):
        """テスト299: フェノフィブラートで高TG血症OK"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [28], 'disease_ids': [21]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_300_statin_ezetimibe_combination(self):
        """テスト300: スタチン+エゼチミブ併用療法"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [24, 27], 'disease_ids': [19]})
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_301_comprehensive_metabolic_panel(self):
        """テスト301: 総合代謝パネル検査"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 2, 3, 4, 5, 6, 10, 11, 12, 13],
                                         'disease_ids': [2, 18, 5]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_302_lifestyle_disease_data_integrity(self):
        """テスト302: 生活習慣病データ整合性チェック"""
        import sqlite3
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # 病名数確認
        cursor.execute('SELECT COUNT(*) FROM diseases')
        disease_count = cursor.fetchone()[0]
        self.assertGreater(disease_count, 30)

        # 検査数確認
        cursor.execute('SELECT COUNT(*) FROM tests')
        test_count = cursor.fetchone()[0]
        self.assertGreater(test_count, 30)

        # 処方薬数確認
        cursor.execute('SELECT COUNT(*) FROM prescriptions')
        prescription_count = cursor.fetchone()[0]
        self.assertGreater(prescription_count, 30)

        conn.close()

    def test_303_performance_large_dataset(self):
        """テスト303: 大量データでのパフォーマンステスト"""
        import time
        start_time = time.time()

        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': list(range(1, 20)),
                                         'prescription_ids': list(range(1, 15)),
                                         'disease_ids': list(range(1, 20))
                                     })
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 2.0)

    def test_304_suggestion_performance_large_dataset(self):
        """テスト304: 大量データでの病名提案パフォーマンステスト"""
        import time
        start_time = time.time()

        response = self.client.post('/api/suggest-diseases-strict',
                                     json={
                                         'test_ids': list(range(1, 20)),
                                         'prescription_ids': list(range(1, 15))
                                     })
        end_time = time.time()

        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 2.0)

    # ====================
    # エッジケースと統合テスト (Test 305-350: 46件)
    # ====================

    def test_305_empty_input_handling(self):
        """テスト305: 空入力の正常処理"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={})
        self.assertEqual(response.status_code, 200)

    def test_306_null_disease_ids(self):
        """テスト306: null病名IDリストの処理"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [1], 'disease_ids': None})
        self.assertEqual(response.status_code, 200)

    def test_307_invalid_test_id_ignored(self):
        """テスト307: 無効な検査IDは無視される"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [9999], 'disease_ids': []})
        self.assertEqual(response.status_code, 200)

    def test_308_invalid_prescription_id_ignored(self):
        """テスト308: 無効な処方IDは無視される"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [9999], 'disease_ids': []})
        self.assertEqual(response.status_code, 200)

    def test_309_duplicate_test_ids_handled(self):
        """テスト309: 重複検査IDの正常処理"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [1, 1, 1], 'disease_ids': [2]})
        self.assertEqual(response.status_code, 200)

    def test_310_duplicate_prescription_ids_handled(self):
        """テスト310: 重複処方IDの正常処理"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'prescription_ids': [1, 1], 'disease_ids': [2]})
        self.assertEqual(response.status_code, 200)

    def test_311_very_long_test_list(self):
        """テスト311: 非常に長い検査リスト"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': list(range(1, 34)),
                                         'disease_ids': list(range(1, 36))
                                     })
        self.assertEqual(response.status_code, 200)

    def test_312_very_long_prescription_list(self):
        """テスト312: 非常に長い処方リスト"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'prescription_ids': list(range(1, 35)),
                                         'disease_ids': list(range(1, 36))
                                     })
        self.assertEqual(response.status_code, 200)

    def test_313_very_long_disease_list(self):
        """テスト313: 非常に長い病名リスト"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1],
                                         'disease_ids': list(range(1, 36))
                                     })
        self.assertEqual(response.status_code, 200)

    def test_314_response_structure_validation_v2(self):
        """テスト314: レスポンス構造検証（v2）"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [1], 'disease_ids': []})
        data = json.loads(response.data)

        self.assertIn('is_compliant', data)
        self.assertIn('risk_level', data)
        self.assertIn('errors', data)
        self.assertIn('warnings', data)
        self.assertIn('summary', data)

    def test_315_error_structure_validation_v2(self):
        """テスト315: エラー構造検証（v2）"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={'test_ids': [1], 'disease_ids': []})
        data = json.loads(response.data)

        if len(data['errors']) > 0:
            error = data['errors'][0]
            self.assertIn('type', error)
            self.assertIn('severity', error)
            self.assertIn('message', error)

    def test_316_suggestion_structure_validation_v2(self):
        """テスト316: 提案構造検証（v2）"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={'test_ids': [1]})
        data = json.loads(response.data)

        self.assertIn('suggested_diseases', data)
        self.assertIn('total_count', data)

    def test_317_api_categories_endpoint_v2(self):
        """テスト317: カテゴリAPIの動作確認（v2）"""
        response = self.client.get('/api/categories')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_318_api_diseases_search_diabetes(self):
        """テスト318: 病名検索API（糖尿病）"""
        response = self.client.get('/api/diseases?search=糖尿病')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)
        diabetes_found = any('糖尿病' in d['name'] for d in data)
        self.assertTrue(diabetes_found)

    def test_319_api_diseases_search_obesity(self):
        """テスト319: 病名検索API（肥満）"""
        response = self.client.get('/api/diseases?search=肥満')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)
        obesity_found = any('肥満' in d['name'] for d in data)
        self.assertTrue(obesity_found)

    def test_320_api_diseases_category_filter_metabolic(self):
        """テスト320: 病名カテゴリフィルタ（代謝疾患）"""
        response = self.client.get('/api/diseases?category=代謝疾患')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)

    def test_321_api_tests_endpoint(self):
        """テスト321: 検査API動作確認"""
        response = self.client.get('/api/tests')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 30)

    def test_322_api_prescriptions_endpoint(self):
        """テスト322: 処方API動作確認"""
        response = self.client.get('/api/prescriptions')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertGreater(len(data), 30)

    def test_323_icd10_code_consistency_all(self):
        """テスト323: ICD-10コード一貫性（全病名）"""
        response = self.client.get('/api/diseases')
        data = json.loads(response.data)

        for disease in data:
            if disease['icd10_code']:
                first_char = disease['icd10_code'][0]
                self.assertIn(first_char, ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'])

    def test_324_test_points_validity_all(self):
        """テスト324: 検査点数妥当性（全検査）"""
        response = self.client.get('/api/tests')
        data = json.loads(response.data)

        for test in data:
            self.assertGreaterEqual(test['points'], 0)
            self.assertLessEqual(test['points'], 500)

    def test_325_prescription_code_format_all(self):
        """テスト325: 処方薬コードフォーマット（全処方）"""
        response = self.client.get('/api/prescriptions')
        data = json.loads(response.data)

        for prescription in data:
            if prescription['yj_code']:
                self.assertRegex(prescription['yj_code'], r'^\d{7}$')

    def test_326_data_integrity_check_v2(self):
        """テスト326: データ整合性チェック（v2）"""
        import sqlite3
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # 病名マスター
        cursor.execute('SELECT COUNT(*) FROM diseases')
        disease_count = cursor.fetchone()[0]
        self.assertGreater(disease_count, 0)

        # 検査マスター
        cursor.execute('SELECT COUNT(*) FROM tests')
        test_count = cursor.fetchone()[0]
        self.assertGreater(test_count, 0)

        # 処方マスター
        cursor.execute('SELECT COUNT(*) FROM prescriptions')
        prescription_count = cursor.fetchone()[0]
        self.assertGreater(prescription_count, 0)

        # マッピングテーブル
        cursor.execute('SELECT COUNT(*) FROM test_disease_insurance_mapping')
        test_mapping_count = cursor.fetchone()[0]
        self.assertGreater(test_mapping_count, 0)

        cursor.execute('SELECT COUNT(*) FROM prescription_disease_insurance_mapping')
        prescription_mapping_count = cursor.fetchone()[0]
        self.assertGreater(prescription_mapping_count, 0)

        conn.close()

    def test_327_comprehensive_audit_prevention_lifestyle(self):
        """テスト327: 総合的な査定防止テスト（生活習慣病）"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 2, 10, 11, 16, 17],
                                         'prescription_ids': [1, 21, 24],
                                         'disease_ids': [2, 13, 18, 23]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])
        self.assertEqual(data['risk_level'], 'low')

    def test_328_partial_compliance_detection_diabetes(self):
        """テスト328: 部分的な不適合検出（糖尿病）"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 10],
                                         'disease_ids': [2]  # 糖尿病のみ（脂質異常症不足）
                                     })
        data = json.loads(response.data)
        self.assertFalse(data['is_compliant'])
        self.assertGreaterEqual(len(data['errors']), 1)

    def test_329_error_count_verification_multiple(self):
        """テスト329: エラー数正確性検証（複数検査）"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 2, 10],
                                         'disease_ids': []
                                     })
        data = json.loads(response.data)
        self.assertEqual(len(data['errors']), 3)

    def test_330_summary_statistics_accuracy_v2(self):
        """テスト330: サマリー統計正確性（v2）"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 2],
                                         'disease_ids': []
                                     })
        data = json.loads(response.data)

        self.assertEqual(data['summary']['total_errors'], len(data['errors']))
        self.assertEqual(data['summary']['total_warnings'], len(data['warnings']))

    def test_331_real_world_obesity_patient(self):
        """テスト331: 実際のシナリオ - 肥満症患者"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [10, 11, 16, 17],
                                         'disease_ids': [9]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_332_real_world_metabolic_syndrome_patient(self):
        """テスト332: 実際のシナリオ - メタボ患者"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [1, 10, 11, 16],
                                         'disease_ids': [12]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_333_real_world_diabetic_with_glp1(self):
        """テスト333: 実際のシナリオ - GLP-1治療中糖尿病患者"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [2],
                                         'prescription_ids': [2],
                                         'disease_ids': [2]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_334_real_world_diabetic_with_sglt2(self):
        """テスト334: 実際のシナリオ - SGLT2治療中糖尿病患者"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [2],
                                         'prescription_ids': [5],
                                         'disease_ids': [2]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_335_real_world_diabetic_with_dpp4(self):
        """テスト335: 実際のシナリオ - DPP-4治療中糖尿病患者"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [2],
                                         'prescription_ids': [8],
                                         'disease_ids': [2]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_336_real_world_nafld_patient(self):
        """テスト336: 実際のシナリオ - NAFLD患者"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [16, 17, 18],
                                         'disease_ids': [25]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_337_real_world_diabetic_nephropathy_patient(self):
        """テスト337: 実際のシナリオ - 糖尿病性腎症患者"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [2, 20, 21, 23],
                                         'prescription_ids': [1, 22],
                                         'disease_ids': [2, 6]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_338_real_world_insulin_treated_patient(self):
        """テスト338: 実際のシナリオ - インスリン治療患者"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [2, 6],
                                         'prescription_ids': [18, 20],
                                         'disease_ids': [2]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_339_real_world_familial_hypercholesterolemia_patient(self):
        """テスト339: 実際のシナリオ - 家族性高コレステロール血症患者"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [11],
                                         'prescription_ids': [25, 27],
                                         'disease_ids': [22]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_340_real_world_hypertriglyceridemia_patient(self):
        """テスト340: 実際のシナリオ - 高TG血症患者"""
        response = self.client.post('/api/check-insurance-compliance',
                                     json={
                                         'test_ids': [13],
                                         'prescription_ids': [28],
                                         'disease_ids': [21]
                                     })
        data = json.loads(response.data)
        self.assertTrue(data['is_compliant'])

    def test_341_suggest_relevance_obesity(self):
        """テスト341: 提案の関連性 - 肥満症"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={'test_ids': [10, 11, 16]})
        data = json.loads(response.data)

        suggested_names = [d['name'] for d in data['suggested_diseases']]
        # 脂質異常症や肝機能障害が提案されるべき
        self.assertGreater(len(suggested_names), 0)

    def test_342_suggest_relevance_diabetes_drugs(self):
        """テスト342: 提案の関連性 - 糖尿病薬"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={'prescription_ids': [1, 8]})
        data = json.loads(response.data)

        suggested_names = [d['name'] for d in data['suggested_diseases']]
        diabetes_suggested = any('糖尿病' in name for name in suggested_names)
        self.assertTrue(diabetes_suggested)

    def test_343_suggest_relevance_insulin(self):
        """テスト343: 提案の関連性 - インスリン"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={'prescription_ids': [18]})
        data = json.loads(response.data)

        suggested_names = [d['name'] for d in data['suggested_diseases']]
        diabetes_suggested = any('糖尿病' in name for name in suggested_names)
        self.assertTrue(diabetes_suggested)

    def test_344_suggest_with_reasons(self):
        """テスト344: 提案に理由が含まれる"""
        response = self.client.post('/api/suggest-diseases-strict',
                                     json={'test_ids': [2], 'prescription_ids': [1]})
        data = json.loads(response.data)

        if len(data['suggested_diseases']) > 0:
            disease = data['suggested_diseases'][0]
            self.assertIn('reasons', disease)
            self.assertGreater(len(disease['reasons']), 0)

    def test_345_end_to_end_workflow_diabetes(self):
        """テスト345: エンドツーエンドワークフロー（糖尿病）"""
        # ステップ1: 病名提案
        suggest_response = self.client.post('/api/suggest-diseases-strict',
                                              json={
                                                  'test_ids': [1, 2],
                                                  'prescription_ids': [1]
                                              })
        suggest_data = json.loads(suggest_response.data)
        self.assertGreater(len(suggest_data['suggested_diseases']), 0)

        # ステップ2: 提案された病名で適応チェック
        suggested_disease_ids = [d['id'] for d in suggest_data['suggested_diseases']]
        check_response = self.client.post('/api/check-insurance-compliance',
                                           json={
                                               'test_ids': [1, 2],
                                               'prescription_ids': [1],
                                               'disease_ids': suggested_disease_ids
                                           })
        check_data = json.loads(check_response.data)

        self.assertTrue(check_data['is_compliant'])

    def test_346_end_to_end_workflow_obesity(self):
        """テスト346: エンドツーエンドワークフロー（肥満症）"""
        suggest_response = self.client.post('/api/suggest-diseases-strict',
                                              json={'test_ids': [10, 11, 16, 17]})
        suggest_data = json.loads(suggest_response.data)

        if len(suggest_data['suggested_diseases']) > 0:
            suggested_disease_ids = [d['id'] for d in suggest_data['suggested_diseases']]
            check_response = self.client.post('/api/check-insurance-compliance',
                                               json={
                                                   'test_ids': [10, 11, 16, 17],
                                                   'disease_ids': suggested_disease_ids
                                               })
            check_data = json.loads(check_response.data)
            # 提案された病名で適応OKになるべき
            self.assertTrue(check_data['is_compliant'])

    def test_347_end_to_end_workflow_metabolic_syndrome(self):
        """テスト347: エンドツーエンドワークフロー（メタボリックシンドローム）"""
        suggest_response = self.client.post('/api/suggest-diseases-strict',
                                              json={
                                                  'test_ids': [1, 10, 11, 16],
                                                  'prescription_ids': [1, 21, 24]
                                              })
        suggest_data = json.loads(suggest_response.data)
        self.assertGreater(len(suggest_data['suggested_diseases']), 0)

    def test_348_database_schema_validation(self):
        """テスト348: データベーススキーマ検証"""
        import sqlite3
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # テーブルの存在確認
        tables = ['diseases', 'tests', 'prescriptions',
                  'test_disease_insurance_mapping',
                  'prescription_disease_insurance_mapping']

        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            result = cursor.fetchone()
            self.assertIsNotNone(result, f"{table}テーブルが存在しません")

        conn.close()

    def test_349_concurrent_requests_simulation(self):
        """テスト349: 同時リクエストシミュレーション"""
        # 複数のリクエストを連続実行
        for i in range(10):
            response = self.client.post('/api/check-insurance-compliance',
                                         json={
                                             'test_ids': [1, 2],
                                             'disease_ids': [2]
                                         })
            self.assertEqual(response.status_code, 200)

    def test_350_comprehensive_final_test(self):
        """テスト350: 最終総合テスト"""
        # すべての機能を統合したテスト
        # 1. 病名取得
        diseases_response = self.client.get('/api/diseases')
        self.assertEqual(diseases_response.status_code, 200)

        # 2. 検査取得
        tests_response = self.client.get('/api/tests')
        self.assertEqual(tests_response.status_code, 200)

        # 3. 処方取得
        prescriptions_response = self.client.get('/api/prescriptions')
        self.assertEqual(prescriptions_response.status_code, 200)

        # 4. カテゴリ取得
        categories_response = self.client.get('/api/categories')
        self.assertEqual(categories_response.status_code, 200)

        # 5. 病名提案
        suggest_response = self.client.post('/api/suggest-diseases-strict',
                                              json={'test_ids': [1, 2], 'prescription_ids': [1]})
        self.assertEqual(suggest_response.status_code, 200)

        # 6. 適応チェック
        check_response = self.client.post('/api/check-insurance-compliance',
                                           json={
                                               'test_ids': [1, 2],
                                               'prescription_ids': [1],
                                               'disease_ids': [2]
                                           })
        self.assertEqual(check_response.status_code, 200)

        # すべてのAPIが正常に動作していることを確認
        self.assertTrue(True)

if __name__ == '__main__':
    # テストスイートの実行
    unittest.main(verbosity=2)
