#!/usr/bin/env python3
"""
Sort all JSON data files in public/data alphabetically.
Applies to:
- ug/all.json, pg/all.json, ss/all.json
- ug/summary.json, pg/summary.json, ss/summary.json
- ug/states/*.json, pg/states/*.json, ss/states/*.json
- ug_colleges_aiq_mapping.json
- colleges_details.json
"""

import os
import json

def sort_all_data():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'public', 'data')

    processed = 0

    for root, dirs, files in os.walk(data_dir):
        for file in sorted(files):
            if file.endswith('.json') and file != 'manifest.json':
                full_path = os.path.join(root, file)
                with open(full_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                modified = False

                if file == 'ug_colleges_aiq_mapping.json' and isinstance(data, list):
                    # Sort cutoffs inside each college
                    for col in data:
                        if 'aiq_cutoffs_raw' in col and isinstance(col['aiq_cutoffs_raw'], list):
                            col['aiq_cutoffs_raw'].sort(key=lambda x: (
                                (x.get('quota') or '').lower(),
                                (x.get('category') or '').lower(),
                                (x.get('course') or '').lower()
                            ))
                    # Sort colleges by college_name
                    data.sort(key=lambda x: (x.get('college_name') or '').lower())
                    modified = True

                elif file.endswith('summary.json') and isinstance(data, dict):
                    for k in ['states', 'courses', 'quotas', 'types']:
                        if k in data and isinstance(data[k], list):
                            data[k].sort()
                    modified = True

                elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict) and 'college_name' in data[0]:
                    data.sort(key=lambda x: (
                        (x.get('college_name') or '').lower(),
                        (x.get('course') or '').lower(),
                        (x.get('quota_type') or '').lower(),
                        (x.get('counseling_route') or '').lower()
                    ))
                    modified = True

                elif file == 'colleges_details.json' and isinstance(data, dict):
                    sorted_dict = {k: data[k] for k in sorted(data.keys())}
                    data = sorted_dict
                    modified = True

                if modified:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                        f.write('\n')
                    processed += 1

    print(f"Successfully sorted {processed} data files alphabetically.")

if __name__ == '__main__':
    sort_all_data()
