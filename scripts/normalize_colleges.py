import os
import json
import re

# Exact name mapping
name_map = {
    "an International Institute of Medical Sciences B": "American International Institute of Medical Sciences, Bedwas",
    "as Institute of Medical Research Centre Srinivas": "Srinivas Institute of Medical Research Centre, Srinivasnagar, Mangalore",
    "ed Dr. D.Y.Patil Medical College, Pune": "Dr. D Y Patil Medical College, Hospital and Research Centre, Pimpri, Pune",
    "ed Santosh Medical College Ghaziabad": "Santosh Medical College, Ghaziabad",
    "edACS Medical College and Hospital Chennai": "ACS Medical College and Hospital, Chennai",
    "government medical college, jashpur-kunkuri": "Government Medical College, Jashpur-Kunkuri",
    "had Institute of Health Care & Medical Techno": "Gayathri Vidya Parishad Institute of Health Care & Medical Technology, Visakhapatnam",
    "sardar Patel Institute of medical education and health sciences": "Sardar Patel Institute of Medical Education and Health Sciences",
    "t Gandhi Medical College": "Gandhi Medical College, Secunderabad",
    "t Seth GS Medical College Mumbai": "Seth GS Medical College, and KEM Hospital, Mumbai",
    "t Shyam Shah Medical College Rewa": "Shyam Shah Medical College, Rewa",
    "tRegional Institute of Medical Sciences Imphal": "Regional Institute of Medical Sciences, Imphal",
    "te of Medical Sciences & Research Centre Nan": "SMBT Institute of Medical Sciences & Research Centre, Nandihills, Nashik"
}

# Explicit ID mapping
id_map = {
    # SS
    "ss_as_institute_of_medical_research_centre_srinivas_karnataka": "ss_srinivas_institute_of_medical_research_centre_srinivasnagar_mangalore_karnataka",
    "ss_ed_dr_dypatil_medical_college_pune_maharashtra": "ss_dr_d_y_patil_medical_college_hospital_and_research_centre_pimpri_pune_maharashtra",
    "ss_t_seth_gs_medical_college_mumbai_maharashtra": "ss_seth_gs_medical_college_and_kem_hospital_mumbai_maharashtra",
    "ss_te_of_medical_sciences_research_centre_nan_maharashtra": "ss_smbt_institute_of_medical_sciences_research_centre_nandihills_nashik_maharashtra",
    "ss_edacs_medical_college_and_hospital_chennai_tamil_nadu": "ss_acs_medical_college_and_hospital_chennai_tamil_nadu",
    "ss_t_gandhi_medical_college_telangana": "ss_gandhi_medical_college_secunderabad_telangana",
    # PG
    "pg_an_international_institute_of_medical_sciences_b_rajasthan": "pg_american_international_institute_of_medical_sciences_bedwas_rajasthan",
    "pg_ed_santosh_medical_college_ghaziabad_uttar_pradesh": "pg_santosh_medical_college_ghaziabad_uttar_pradesh",
    "pg_had_institute_of_health_care_medical_techno_andhra_pradesh": "pg_gayathri_vidya_parishad_institute_of_health_care_medical_technology_visakhapatnam_andhra_pradesh",
    "pg_t_shyam_shah_medical_college_rewa_madhya_pradesh": "pg_shyam_shah_medical_college_rewa_madhya_pradesh",
    "pg_tregional_institute_of_medical_sciences_imphal_manipur": "pg_regional_institute_of_medical_sciences_imphal_manipur",
}

def clean_file(filepath):
    if not filepath.endswith('.json') or 'colleges_details.json' in filepath or 'manifest.json' in filepath:
        return False, []

    modified = False
    changes = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return False, []

    if isinstance(data, list):
        for idx, row in enumerate(data):
            if not isinstance(row, dict):
                continue
            
            # Check college_name
            cname = row.get("college_name")
            if cname in name_map:
                new_name = name_map[cname]
                row["college_name"] = new_name
                modified = True
                changes.append((filepath, "name", cname, new_name))
            
            # Check college_id
            cid = row.get("college_id")
            if cid in id_map:
                new_id = id_map[cid]
                row["college_id"] = new_id
                modified = True
                changes.append((filepath, "id", cid, new_id))
                
    elif isinstance(data, dict):
        # In case we encounter summary.json or other dict format
        pass

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    return modified, changes

def main():
    data_dir = "public/data"
    all_changes = []
    modified_files_count = 0
    
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            path = os.path.join(root, file)
            mod, file_changes = clean_file(path)
            if mod:
                modified_files_count += 1
                all_changes.extend(file_changes)
                
    print(f"Cleaned {modified_files_count} files.")
    
    # Print summary of changes
    print(f"Total individual record updates: {len(all_changes)}")
    
if __name__ == "__main__":
    main()
