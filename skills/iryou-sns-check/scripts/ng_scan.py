#!/usr/bin/env python3
"""医療SNS原稿のNG表現一次スキャン。

references/ng_patterns.tsv の正規表現で原稿を走査し、行番号つきで候補を出す。
一致は「候補」にすぎない。最終判断は文脈で行うこと（例：「必ず主治医に相談を」は問題ない）。

使い方:
    python scripts/ng_scan.py 原稿.txt
    echo "本文" | python scripts/ng_scan.py
"""
import csv
import re
import sys
from pathlib import Path

PATTERNS = Path(__file__).resolve().parent.parent / "references" / "ng_patterns.tsv"
MARK = {"red": "🔴", "yellow": "🟡"}


def load_patterns():
    with PATTERNS.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    return [(re.compile(r["pattern"], re.IGNORECASE), r) for r in rows]


def main():
    text = Path(sys.argv[1]).read_text(encoding="utf-8") if len(sys.argv) > 1 else sys.stdin.read()
    patterns = load_patterns()
    hits = 0
    for lineno, line in enumerate(text.splitlines(), 1):
        for rx, row in patterns:
            for m in rx.finditer(line):
                hits += 1
                print(f"{MARK.get(row['severity'], '・')} L{lineno} 「{m.group(0)}」"
                      f" [{row['category']}] {row['reason']} → {row['suggestion']}")
    print(f"\n候補 {hits} 件（文脈で最終判断すること）")


if __name__ == "__main__":
    main()
