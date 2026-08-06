import json
import os

def update_college_course_levels():
    print("=== Updating College Offered Academic Levels (UG, PG, SS) ===")
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'public', 'data'))
    details_path = os.path.join(base_dir, 'colleges_details.json')
    
    if not os.path.exists(details_path):
        print(f"Error: {details_path} not found!")
        return

    with open(details_path, 'r', encoding='utf-8') as f:
        colleges_details = json.load(f)

    # Maps college_id -> set of level strings ('UG', 'PG', 'SS')
    college_levels = {}

    datasets = [
        ('UG', os.path.join(base_dir, 'ug', 'all.json')),
        ('PG', os.path.join(base_dir, 'pg', 'all.json')),
        ('SS', os.path.join(base_dir, 'ss', 'all.json')),
    ]

    for level, path in datasets:
        if not os.path.exists(path):
            print(f"Warning: {path} not found, skipping {level}")
            continue
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for row in data:
                cid = row.get('college_id')
                if cid:
                    if cid not in college_levels:
                        college_levels[cid] = set()
                    college_levels[cid].add(level)

    # Also check MCC AIQ mapping
    aiq_mapping_path = os.path.join(base_dir, 'ug_colleges_aiq_mapping.json')
    if os.path.exists(aiq_mapping_path):
        with open(aiq_mapping_path, 'r', encoding='utf-8') as f:
            aiq_data = json.load(f)
            for item in aiq_data:
                cid = item.get('college_id')
                if cid and item.get('aiq_cutoffs_raw') and len(item['aiq_cutoffs_raw']) > 0:
                    if cid not in college_levels:
                        college_levels[cid] = set()
                    college_levels[cid].add('UG')

    updated_count = 0
    order_map = {'UG': 1, 'PG': 2, 'SS': 3}

    for cid, details in colleges_details.items():
        levels = college_levels.get(cid, set())
        
        # If no level was found from seat matrices, default to UG if college_id starts with 'ug_'
        if len(levels) == 0:
            if cid.startswith('ug_'):
                levels.add('UG')

        sorted_levels = sorted(list(levels), key=lambda x: order_map.get(x, 99))
        details['courses'] = sorted_levels
        updated_count += 1

    with open(details_path, 'w', encoding='utf-8') as f:
        json.dump(colleges_details, f, indent=2, ensure_ascii=False)

    print(f"Successfully updated course levels for {updated_count} colleges in colleges_details.json")

if __name__ == '__main__':
    update_college_course_levels()
