#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
カルテ作成ツール
音声データの内容を500文字以内に要約してカルテ形式で出力
"""

import sys
from datetime import datetime


def summarize_text(text, max_length=500):
    """
    テキストを指定文字数以内に要約

    Args:
        text (str): 要約する元のテキスト
        max_length (int): 最大文字数（デフォルト500文字）

    Returns:
        str: 要約されたテキスト
    """
    # 改行や余分な空白を整理
    text = ' '.join(text.split())

    # 指定文字数以内の場合はそのまま返す
    if len(text) <= max_length:
        return text

    # 文末で切る（句点で区切る）
    sentences = text.split('。')
    summary = ""

    for sentence in sentences:
        if len(summary + sentence + '。') <= max_length:
            summary += sentence + '。'
        else:
            break

    # 句点で切れなかった場合は単純に切り詰め
    if not summary or len(summary) == 0:
        summary = text[:max_length - 3] + '...'

    return summary.strip()


def get_guidance_template():
    """
    厚生局要件を満たす指導内容のテンプレートを返す

    Returns:
        str: 指導内容テンプレート
    """
    return """・内服薬は指示通り継続すること
・食事はバランスよく摂取し、1日の塩分は6g未満に制限
・水分摂取は1日1500ml以上を目標とする
・毎日体重測定を行い、2日で2kg以上増加時は受診
・規則正しい生活を心がけること
・喫煙・アルコールの過剰摂取は控えること
・異常時（息切れ、浮腫、激しい動悸等）はすぐに連絡"""


def create_karte(date_str, content, max_length=500):
    """
    カルテ形式で出力（診療記録 + 指導内容）

    Args:
        date_str (str): 日付（例: 2025年10月28日）
        content (str): 診療内容
        max_length (int): 要約の最大文字数

    Returns:
        str: カルテ形式のテキスト
    """
    # 指導内容テンプレート（約200文字）
    guidance = get_guidance_template()

    # 診療記録用に残りの文字数を計算（300文字程度）
    remaining_length = max_length - len(guidance) - 30  # 余裕を持たせる

    summary = summarize_text(content, remaining_length)

    karte = f"""日付: {date_str}

【診療記録】
{summary}

【指導内容】
{guidance}"""
    return karte


def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python karte_creator.py <音声データファイル>")
        print("  または標準入力からテキストを受け取る:")
        print("  echo '診療内容...' | python karte_creator.py")
        sys.exit(1)

    # ファイルから読み込むか標準入力から読み込む
    if sys.argv[1] == '-':
        content = sys.stdin.read()
    else:
        try:
            with open(sys.argv[1], 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"エラー: ファイル '{sys.argv[1]}' が見つかりません")
            sys.exit(1)

    # 今日の日付
    today = datetime.now().strftime('%Y年%m月%d日')

    # カルテ作成
    karte = create_karte(today, content, max_length=500)
    print(karte)


if __name__ == '__main__':
    main()
