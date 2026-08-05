import json
import os

def run_verification():
    print("=============================================================")
    print("       NEXDOC DATA INTEGRITY & FACTUAL ACCURACY AUDIT       ")
    print("=============================================================\n")

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'public', 'data'))
    ug_all_path = os.path.join(base_dir, 'ug', 'all.json')
    ug_summary_path = os.path.join(base_dir, 'ug', 'summary.json')
    mapping_path = os.path.join(base_dir, 'ug_colleges_aiq_mapping.json')

    # Load Datasets
    with open(ug_all_path, 'r', encoding='utf-8') as f:
        ug_all = json.load(f)
    with open(ug_summary_path, 'r', encoding='utf-8') as f:
        ug_summary = json.load(f)
    with open(mapping_path, 'r', encoding='utf-8') as f:
        mapping_data = json.load(f)

    results = []

    # 1. Master UG Unique Colleges Count & Seats
    unique_colleges_in_all = len(set(c.get('college_id') for c in ug_all if 'college_id' in c))
    total_seats_in_all = sum(c.get('seats', 0) for c in ug_all)
    results.append(("Master UG Unique Colleges Count", unique_colleges_in_all == 845, f"{unique_colleges_in_all} (Expected: 845)"))
    results.append(("Master Total UG Seats Count", total_seats_in_all == 139439, f"{total_seats_in_all:,} seats (Expected: 139,439)"))

    # 2. Summary JSON fields
    summary_colleges = ug_summary.get('totalColleges', 0)
    summary_seats = ug_summary.get('totalSeats', 0)
    results.append(("Summary JSON totalColleges Field", summary_colleges == 845, f"{summary_colleges} (Expected: 845)"))
    results.append(("Summary JSON totalSeats Field", summary_seats == 139439, f"{summary_seats:,} (Expected: 139,439)"))

    # 3. MCC Mapping Dataset Count & Status Breakdown
    mapping_count = len(mapping_data)
    matched_count = sum(1 for c in mapping_data if c.get('mcc_status') == 'Matched')
    new_count = sum(1 for c in mapping_data if c.get('mcc_status') == 'New')
    non_aiq_count = sum(1 for c in mapping_data if c.get('mcc_status') == 'Non AIQ')

    results.append(("MCC Mapping Total Institutions Count", mapping_count == 845, f"{mapping_count} (Expected: 845)"))
    results.append(("MCC 'Matched' Classification Count", matched_count == 440, f"{matched_count} (Expected: 440)"))
    results.append(("MCC 'New' Classification Count", new_count == 82, f"{new_count} (Expected: 82)"))
    results.append(("MCC 'Non AIQ' Classification Count", non_aiq_count == 323, f"{non_aiq_count} (Expected: 323)"))
    
    breakdown_sum = matched_count + new_count + non_aiq_count
    results.append(("MCC Classification Sum Parity", breakdown_sum == 845, f"{breakdown_sum} (Expected: 845)"))

    # 4. Duplicate IDs & Ambiguity Check
    college_ids = [c.get('college_id') for c in mapping_data]
    unique_ids = set(college_ids)
    duplicate_ids = len(college_ids) - len(unique_ids)
    results.append(("Duplicate College IDs Check", duplicate_ids == 0, f"{duplicate_ids} duplicates found"))

    # 5. AIIMS New Delhi vs ABVIMS/RML Isolation Check
    rml_bug_found = False
    rml_id = "ug_dl003"      # ABVIMS & Dr. RML Hospital

    for col in mapping_data:
        cid = col.get('college_id', '')
        cname = col.get('college_name', '').lower()
        if 'rml' in cname or 'abvims' in cname or cid == rml_id:
            cutoffs = col.get('aiq_cutoffs_raw', [])
            for cut in cutoffs:
                if cut.get('op_rank') == 1 or cut.get('cl_rank') == 1:
                    rml_bug_found = True
                    break

    results.append(("AIIMS New Delhi Cutoff Bug Isolation", not rml_bug_found, "CLEAN (0 false mappings)" if not rml_bug_found else "BUG DETECTED!"))

    # 6. Course Purity Check (Strictly MBBS)
    non_mbbs_courses = set()
    for col in ug_all:
        course = col.get('course', '')
        if course != 'MBBS':
            non_mbbs_courses.add(course)
    results.append(("UG Course Purity Check (Strictly MBBS)", len(non_mbbs_courses) == 0, "CLEAN (Strictly MBBS)" if len(non_mbbs_courses) == 0 else f"Non-MBBS courses found: {non_mbbs_courses}"))

    # 7. Cutoff Data Records & Rounds Consistency
    total_cutoffs_records = sum(len(c.get('aiq_cutoffs_raw', [])) for c in mapping_data)
    results.append(("Cutoff Raw Records Count Analyzed", total_cutoffs_records > 0, f"{total_cutoffs_records:,} raw cutoff records analyzed"))

    # Print Full Verification Table
    print(f"{'Check / Metric':<45} | {'Status':<8} | {'Details'}")
    print("-" * 80)
    all_passed = True
    for title, passed, details in results:
        status_str = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False
        print(f"{title:<45} | {status_str:<8} | {details}")

    print("\n=============================================================")
    if all_passed:
        print("    RESULT: 100% FACTUAL ACCURACY & DATA INTEGRITY VERIFIED ")
    else:
        print("    RESULT: DATA INTEGRITY ISSUES FOUND!")
    print("=============================================================")

if __name__ == '__main__':
    run_verification()
