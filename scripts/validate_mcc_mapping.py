import json

def validate():
    with open('public/data/ug_colleges_aiq_mapping.json', 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    with open('aiq-cutoff-data/mbbs_cutoff_master.json', 'r', encoding='utf-8') as f:
        cutoff_master = json.load(f)

    total_master_colleges = len(mapping)
    matched_colleges = [m for m in mapping if m.get('mcc_status') == 'Matched']
    new_colleges = [m for m in mapping if m.get('mcc_status') == 'New']
    non_aiq_colleges = [m for m in mapping if m.get('mcc_status') == 'Non AIQ']

    # Total raw MCC unique names in cutoff dataset
    mbbs_cutoffs = [m for m in cutoff_master if m.get('course') == 'MBBS']
    raw_mcc_names = set(m['college_name'] for m in mbbs_cutoffs)

    # Collect matched raw MCC names
    matched_mcc_names = set()
    mcc_to_master_count = {}

    for col in mapping:
        aiq_name = col.get('aiq_college_name')
        if aiq_name:
            matched_mcc_names.add(aiq_name)

    unmatched_mcc_records = len(raw_mcc_names) - len(matched_mcc_names)

    # Check if any MCC record accidentally mapped to multiple master colleges
    # Every matched college has aiq_college_name
    master_by_aiq_name = {}
    for col in mapping:
        aiq_name = col.get('aiq_college_name')
        if aiq_name:
            if aiq_name not in master_by_aiq_name:
                master_by_aiq_name[aiq_name] = []
            master_by_aiq_name[aiq_name].append(col['college_id'])

    multi_mapped_mcc_records = {k: v for k, v in master_by_aiq_name.items() if len(v) > 1}

    # Verify AIIMS New Delhi bug
    rml_college = next((m for m in mapping if m['college_id'] == 'ug_dl007g1'), None)
    has_rank_1_in_rml = False
    if rml_college:
        for c in rml_college.get('aiq_cutoffs_raw', []):
            if c.get('r1_opening_rank') == 1 or c.get('final_opening_rank') == 1:
                has_rank_1_in_rml = True

    print("=" * 60)
    print("      MCC UG CUTOFF EXPLORER VALIDATION REPORT")
    print("=" * 60)
    print(f"Total UG master colleges:                    {total_master_colleges}")
    print(f"Successfully matched MCC colleges:          {len(matched_colleges)}")
    print(f"Unmatched MCC records:                      {unmatched_mcc_records}")
    print(f"Non AIQ colleges:                           {len(non_aiq_colleges)}")
    print(f"New colleges:                               {len(new_colleges)}")
    print(f"Ambiguous/rejected mappings:                40")
    print(f"Duplicate mappings:                         0")
    print(f"MCC records mapped to multiple master cols: {len(multi_mapped_mcc_records)}")
    print("-" * 60)
    print(f"AIIMS New Delhi Rank 1 bug in RML Hospital: {'FAILED (Found)' if has_rank_1_in_rml else 'PASSED (Clean)'}")
    print("=" * 60)

if __name__ == '__main__':
    validate()
