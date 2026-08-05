import json
import os
import re

workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
raw_cutoffs_path = os.path.join(workspace_dir, "reference", "raw_college_cutoffs_mapping.json")
alias_registry_path = os.path.join(workspace_dir, "reference", "alias-to-canonical.json")
master_list_path = os.path.join(workspace_dir, "reference", "master-lists-of-colleges.json")

def clean_name(name):
    if not name: return ""
    n = name.lower()
    n = re.sub(r'(?<=\b[a-z])\.(?=[a-z]\b)', '', n)
    n = re.sub(r"[^\w\s]", " ", n)
    n = " ".join(n.split())
    while re.search(r'\b([a-z])\s+([a-z])\b', n):
        n = re.sub(r'\b([a-z])\s+([a-z])\b', r'\1\2', n)
    return " ".join(n.split())

def expand_abbreviations(text):
    t = clean_name(text)
    t = re.sub(r'\baiims\b', 'all india institute of medical sciences', t)
    t = re.sub(r'\bjipmer\b', 'jawaharlal institute of postgraduate medical education and research', t)
    t = re.sub(r"\bgovt\b|\bgov\b", "government", t)
    t = re.sub(r"\bmed\b", "medical", t)
    t = re.sub(r"\binst\b|\binstt\b|\binstitut\b", "institute", t)
    t = re.sub(r"\bcol\b|\bcollage\b|\bcoll\b", "college", t)
    t = re.sub(r"\bhosp\b|\bhospt\b", "hospital", t)
    t = re.sub(r"\bres\b", "research", t)
    t = re.sub(r'\bsciences\b|\bsci\b|\bsce\b', 'science', t)
    t = re.sub(r'\bcolleges\b', 'college', t)
    t = re.sub(r'\binstitutes\b', 'institute', t)
    t = re.sub(r'\bhospitals\b', 'hospital', t)
    t = re.sub(r"\bdeogarh\b", "deoghar", t)
    t = re.sub(r"\brai bareli\b|\braebarely\b", "raebareli", t)
    t = re.sub(r'\bsholapur\b', 'solapur', t)
    t = re.sub(r'\bbanglore\b', 'bangalore', t)
    t = re.sub(r'\bmangaluru\b', 'mangalore', t)
    t = re.sub(r'\bpuducherry\b|\bpondicherry\b', 'puducherry', t)
    t = re.sub(r'\belamkara\b', 'kochi', t)
    return " ".join(t.split())

def main():
    print("=== Data Integrity & Category Audit ===")
    raw_cutoffs = json.load(open(raw_cutoffs_path, "r", encoding="utf-8"))
    alias_registry = json.load(open(alias_registry_path, "r", encoding="utf-8"))
    master_colleges = json.load(open(master_list_path, "r", encoding="utf-8"))

    master_set = set(master_colleges)
    
    # Map raw names to courses offered in dataset
    raw_courses = {}
    raw_records_count = {}
    for item in raw_cutoffs:
        r_name = item["college_name"]
        c_course = item["course"].upper()
        if r_name not in raw_courses:
            raw_courses[r_name] = set()
            raw_records_count[r_name] = 0
        raw_courses[r_name].add(c_course)
        raw_records_count[r_name] += 1

    unique_raw_names = sorted(list(raw_courses.keys()))

    cat_a_mbbs_matched = []
    cat_b_dental_matched = []
    cat_c_dental_unmatched = []
    cat_d_nursing_unmatched = []
    cat_e_mbbs_unmatched = []

    matched_canonical_mbbs = set()
    matched_canonical_dental = set()

    for r_name in unique_raw_names:
        c_r = clean_name(r_name)
        courses = raw_courses[r_name]
        is_dental = any("DENTAL" in c or "BDS" in c for c in courses) or "dental" in r_name.lower() or "dent" in r_name.lower()
        is_nursing = any("NURSING" in c or "BSC NURSING" in c for c in courses) or "nursing" in r_name.lower()

        res_canon = None
        if r_name in master_set:
            res_canon = r_name
        elif c_r in alias_registry:
            entry = alias_registry[c_r]
            res_canon = entry.get("canonical") if isinstance(entry, dict) else entry

        if res_canon:
            if is_dental:
                cat_b_dental_matched.append((r_name, res_canon))
                matched_canonical_dental.add(res_canon)
            else:
                cat_a_mbbs_matched.append((r_name, res_canon))
                matched_canonical_mbbs.add(res_canon)
        else:
            if is_nursing:
                cat_d_nursing_unmatched.append(r_name)
            elif is_dental:
                cat_c_dental_unmatched.append(r_name)
            else:
                cat_e_mbbs_unmatched.append(r_name)

    print(f"\nTotal Raw Cutoff Records: {len(raw_cutoffs)}")
    print(f"Total Unique Raw College Strings: {len(unique_raw_names)}")
    print("-" * 50)
    print(f"Category A - Matched MBBS Colleges: {len(cat_a_mbbs_matched)} raw strings -> {len(matched_canonical_mbbs)} distinct canonical MBBS institutions")
    print(f"Category B - Matched Dental Colleges: {len(cat_b_dental_matched)} raw strings -> {len(matched_canonical_dental)} distinct canonical Dental institutions")
    print(f"Category C - Unmatched Dental/BDS Colleges: {len(cat_c_dental_unmatched)} raw strings")
    print(f"Category D - Unmatched Nursing Colleges: {len(cat_d_nursing_unmatched)} raw strings")
    print(f"Category E - Unmatched MBBS Colleges: {len(cat_e_mbbs_unmatched)} raw strings")

    print("\n" + "=" * 50)
    print("CATEGORY E: UNMATCHED MBBS COLLEGES AUDIT (RECOVERY TARGETS)")
    print("=" * 50)
    for idx, r_name in enumerate(cat_e_mbbs_unmatched, 1):
        rec_count = raw_records_count[r_name]
        print(f"{idx:3d}. [{rec_count:2d} recs] {r_name}")

if __name__ == "__main__":
    main()
