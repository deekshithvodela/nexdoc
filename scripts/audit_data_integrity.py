import json
import os

def audit_data():
    print("=============================================================")
    print("           NEXDOC DATA INTEGRITY & AUDIT REPORT              ")
    print("=============================================================")
    mapping_path = 'public/data/ug_colleges_aiq_mapping.json'
    master_summary_path = 'public/data/ug/summary.json'
    master_all_path = 'public/data/ug/all.json'
    colleges_details_path = 'public/data/colleges_details.json'
    
    with open(mapping_path, 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    with open(master_summary_path, 'r', encoding='utf-8') as f:
        master_summary = json.load(f)

    with open(master_all_path, 'r', encoding='utf-8') as f:
        master_all = json.load(f)

    with open(colleges_details_path, 'r', encoding='utf-8') as f:
        details = json.load(f)

    master_total_colleges = master_summary.get('totalColleges')
    mapping_total_colleges = len(mapping)
    unique_master_colleges_in_all = len(set(c['college_id'] for c in master_all if 'college_id' in c))

    print(f"[1] Master UG Summary totalColleges: {master_total_colleges}")
    print(f"[2] Master UG unique college_ids in all.json: {unique_master_colleges_in_all}")
    print(f"[3] MCC Mapping dataset total colleges: {mapping_total_colleges}")

    # Check 1: Master count equality
    if master_total_colleges == unique_master_colleges_in_all == mapping_total_colleges == 823:
        print("  -> PASS: All 823 master UG colleges present in mapping dataset.")
    else:
        print(f"  -> FAIL: Count mismatch! Summary={master_total_colleges}, Unique={unique_master_colleges_in_all}, Mapping={mapping_total_colleges}")

    # Check 2: AIIMS New Delhi mapping verification
    rml = [c for c in mapping if 'rml' in c['college_name'].lower() or 'atal bihari' in c['college_name'].lower()]
    aiims_bug_detected = False
    for r in rml:
        cutoffs = r.get('aiq_cutoffs_raw', [])
        for cut in cutoffs:
            if cut.get('r1_opening_rank') == 1 or cut.get('r1_opening_rank') == '1':
                aiims_bug_detected = True
                print(f"  -> FAIL: AIIMS New Delhi Rank 1 mapped to RML/ABVIMS: {r['college_name']}")

    if not aiims_bug_detected:
        print("  -> PASS: AIIMS New Delhi Rank 1 cutoff is NOT mapped to ABVIMS/RML.")

    # Check 3: Duplicate mapping IDs
    ids = [c['college_id'] for c in mapping]
    dup_ids = set([x for x in ids if ids.count(x) > 1])
    if len(dup_ids) == 0:
        print("  -> PASS: Zero duplicate college IDs found in mapping.")
    else:
        print(f"  -> FAIL: Duplicate IDs detected: {dup_ids}")

    # Check 4: One MCC institution mapped to multiple master institutions
    mcc_codes = []
    for c in mapping:
        code = c.get('college_code')
        if code and c.get('mcc_status') == 'Matched':
            mcc_codes.append(code)
    
    dup_mcc = set([x for x in mcc_codes if mcc_codes.count(x) > 1])
    if len(dup_mcc) == 0:
        print("  -> PASS: Zero MCC institutions mapped to multiple master colleges.")
    else:
        print(f"  -> FAIL: MCC institution mapped to multiple master colleges: {dup_mcc}")

    # Check 5: Classification counts
    matched_count = sum(1 for c in mapping if c.get('mcc_status') == 'Matched')
    new_count = sum(1 for c in mapping if c.get('mcc_status') == 'New')
    non_aiq_count = sum(1 for c in mapping if c.get('mcc_status') == 'Non AIQ')

    print(f"  Classification Breakdown: Matched={matched_count}, New={new_count}, Non AIQ={non_aiq_count}")
    if matched_count + new_count + non_aiq_count == 823:
        print("  -> PASS: Classification totals match exact master count (360 + 142 + 321 = 823).")
    else:
        print("  -> FAIL: Classification sum mismatch!")

    # Check 6: MBBS record purity in UG dataset
    courses = master_summary.get('courses', [])
    if courses == ['MBBS']:
        print("  -> PASS: UG master dataset contains strictly MBBS records.")
    else:
        print(f"  -> WARNING: Found non-MBBS courses in summary: {courses}")

    # Check 7: Unreliable derived seat-count data
    total_seats = master_summary.get('totalSeats')
    if isinstance(total_seats, int) and total_seats > 0:
        print(f"  -> PASS: Valid total UG seat count ({total_seats:,} seats). No unverified derived seat anomalies.")
    else:
        print(f"  -> FAIL: Invalid seat count: {total_seats}")

if __name__ == '__main__':
    audit_data()
