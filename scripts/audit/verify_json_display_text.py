import json
import glob
import os
import re

def audit_json_display_text():
    print("=============================================================")
    print("      AUDITING JSON DATASET DISPLAY FIELDS FOR ARTIFACTS      ")
    print("=============================================================\n")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'public', 'data'))
    json_files = glob.glob(os.path.join(base_dir, '**', '*.json'), recursive=True)

    md_pattern = re.compile(r'(\*\*|__|#{1,6}\s+|\[[^\]]+\]\([^)]+\)|`[^`]+`)')
    funny_pattern = re.compile(r'[\ufffd\u0080-\u009f\u00a0]')

    display_keys = {'college_name', 'course', 'state', 'city', 'quota', 'category', 'college_type', 'mcc_status', 'name'}

    display_issues = []

    for filepath in json_files:
        rel_path = os.path.relpath(filepath, base_dir)
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            try:
                data = json.load(f)
            except Exception as e:
                display_issues.append((rel_path, f"JSON parse error: {e}"))
                continue

        def check_object(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k in display_keys and isinstance(v, str):
                        if md_pattern.search(v):
                            display_issues.append((rel_path, f"Markdown artifact in display field '{k}': '{v}'"))
                        if funny_pattern.search(v):
                            display_issues.append((rel_path, f"Funny/Corrupted character in display field '{k}': '{v}'"))
                    else:
                        check_object(v)
            elif isinstance(obj, list):
                for item in obj:
                    check_object(item)

        check_object(data)

    print(f"Scanned {len(json_files)} JSON data files for display field artifacts...\n")
    if not display_issues:
        print("-> PASS: All JSON display fields (college names, courses, states, cities, quotas, categories) are 100% clean!")
        print("   Zero markdown artifacts, zero replacement characters, zero funny symbols in display data.")
    else:
        print(f"-> FINDINGS: {len(display_issues)} issues found in display fields:")
        for rel_path, issue in display_issues[:10]:
            print(f"   - {rel_path}: {issue}")

    print("\n=============================================================")
    print(f"   FINAL VERDICT: {'100% CLEAN' if not display_issues else 'ISSUES FOUND'}")
    print("=============================================================")

if __name__ == '__main__':
    audit_json_display_text()
