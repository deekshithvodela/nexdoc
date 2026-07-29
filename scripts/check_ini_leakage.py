import json
import os
import re

def check_ini_leakage():
    print("=============================================================")
    print("      PROGRAMMATIC AUDIT FOR INI DATA LEAKAGE IN DATASETS     ")
    print("=============================================================\n")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'public', 'data'))
    
    ini_keywords = [
        r'\baiims\b',
        r'\bjipmer\b',
        r'\bpgimer\b',
        r'\bnimhans\b',
        r'\bsctimst\b',
        r'\binstitutes? of national importance\b'
    ]
    pattern = re.compile('|'.join(ini_keywords), re.IGNORECASE)

    datasets_to_check = [
        ('UG All Seats', os.path.join(base_dir, 'ug', 'all.json')),
        ('PG All Seats', os.path.join(base_dir, 'pg', 'all.json')),
        ('SS All Seats', os.path.join(base_dir, 'ss', 'all.json')),
        ('MCC AIQ Mapping', os.path.join(base_dir, 'ug_colleges_aiq_mapping.json')),
    ]

    for label, filepath in datasets_to_check:
        if not os.path.exists(filepath):
            print(f"[-] {label}: File not found ({filepath})")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        matches = []
        if isinstance(data, list):
            for idx, item in enumerate(data):
                item_str = json.dumps(item)
                if pattern.search(item_str):
                    cname = item.get('college_name') or item.get('name') or item.get('college_id') or f"Index {idx}"
                    matches.append((cname, item.get('college_id', 'N/A')))
        
        print(f"[{'PASS' if len(matches) == 0 else 'WARNING/INFO'}] {label}: {len(matches)} matches for INI keywords.")
        if len(matches) > 0:
            print("   Matches sample (first 5):")
            for name, cid in matches[:5]:
                print(f"    - [{cid}] {name}")
        print()

if __name__ == '__main__':
    check_ini_leakage()
