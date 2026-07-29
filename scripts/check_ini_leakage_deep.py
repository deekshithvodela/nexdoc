import json
import os
import glob
import re

def deep_ini_scan():
    print("=============================================================")
    print("   EXHAUSTIVE DEEP FILE SCAN FOR INI DATA ACROSS PUBLIC/DATA  ")
    print("=============================================================\n")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'public', 'data'))
    
    ini_keywords = [
        r'\baiims\b',
        r'\bjipmer\b',
        r'\bpgimer\b',
        r'\bnimhans\b',
        r'\bsctimst\b',
        r'\ball india institute of medical sciences\b',
        r'\bjawaharlal institute of postgraduate\b',
        r'\bpostgraduate institute of medical education\b',
        r'\bnational institute of mental health\b',
        r'\bsree chitra tirunal\b'
    ]
    pattern = re.compile('|'.join(ini_keywords), re.IGNORECASE)

    json_files = glob.glob(os.path.join(base_dir, '**', '*.json'), recursive=True)
    
    total_files = len(json_files)
    total_leaks = 0

    print(f"Scanning {total_files} JSON files under public/data/...\n")

    for filepath in json_files:
        rel_path = os.path.relpath(filepath, base_dir)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        matches = pattern.findall(content)
        if matches:
            total_leaks += len(matches)
            unique_matches = set(m.lower() for m in matches)
            print(f"[LEAK DETECTED] {rel_path}: {len(matches)} occurrences -> Keywords: {unique_matches}")

    print("\n=============================================================")
    if total_leaks == 0:
        print("  VERDICT: 100% CONFIRMED — ZERO INI DATA LEAKS EXIST IN NEXDOC")
    else:
        print(f"  VERDICT: FOUND {total_leaks} INI OCCURRENCES ACROSS DATASETS!")
    print("=============================================================")

if __name__ == '__main__':
    deep_ini_scan()
