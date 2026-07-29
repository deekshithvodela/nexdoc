import os
import json
import random
from datetime import datetime

# 36 States and Union Territories
states_and_uts = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana",
    "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
    "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
]

# Course Taxonomy from fundamentals.md (Excluding all Dental/BDS/MDS)
courses_by_level = {
    "ug": [
        "MBBS"
    ],
    "pg": [
        # MD Courses
        "MD General Medicine", "MD Medical Genetics", "MD Paediatrics", "MD Anaesthesiology", "MD Radiodiagnosis",
        "MD Dermatology, Venereology & Leprosy (DVL)", "MD Psychiatry",
        "MD Tuberculosis & Respiratory Diseases / Pulmonary Medicine", "MD Pathology", "MD Microbiology",
        "MD Pharmacology", "MD Physiology", "MD Anatomy", "MD Forensic Medicine",
        "MD Social & Preventive Medicine / Community Medicine", "MD Radiotherapy / Radiation Oncology",
        "MD Physical Medicine & Rehabilitation", "MD Transfusion Medicine / Immuno-Haematology",
        "MD Emergency Medicine", "MD Geriatrics", "MD Family Medicine", "MD Sports Medicine",
        "MD Aviation Medicine / Aerospace Medicine", "MD Marine Medicine", "MD Palliative Medicine",
        "MD Hospital Administration", "MD Biophysics", "MD Nuclear Medicine", "MD Laboratory Medicine",
        "MD Tropical Medicine",
        # MS Courses
        "MS General Surgery", "MS Orthopaedics", "MS Obstetrics & Gynaecology", "MS Ophthalmology",
        "MS ENT (Oto-Rhino-Laryngology)", "MS Traumatology & Surgery",
        # DNB Courses
        "DNB General Medicine", "DNB General Surgery", "DNB Paediatrics", "DNB Anaesthesiology", "DNB Radiodiagnosis",
        "DNB Dermatology, Venereology & Leprosy", "DNB Psychiatry", "DNB Respiratory Medicine",
        "DNB Orthopaedic Surgery", "DNB Obstetrics & Gynaecology", "DNB Ophthalmology", "DNB Otorhinolaryngology (ENT)",
        "DNB Radiotherapy", "DNB Pathology", "DNB Microbiology", "DNB Biochemistry", "DNB Forensic Medicine",
        "DNB Immunohematology & Transfusion Medicine", "DNB Emergency Medicine", "DNB Physical Medicine & Rehabilitation",
        "DNB Family Medicine", "DNB Anatomy", "DNB Physiology", "DNB Pharmacology", "DNB Nuclear Medicine",
        "DNB Radiation Oncology", "DNB Maternal and Child Health", "DNB Trauma and Acute Care Surgery",
        "DNB Health Administration",
        # NBEMS Diplomas
        "Diploma in Gynaecology & Obstetrics (DGO)", "Diploma in Child Health (DCH)", "Diploma in Anaesthesiology (DA)",
        "Diploma in Otorhinolaryngology (DLO)", "Diploma in Ophthalmology (DO)",
        "Diploma in Dermatology, Venereology and Leprosy (DDVL)", "Diploma in Medical Radio-Diagnosis (DMRD)",
        "Diploma in Tuberculosis & Chest Diseases (DTCD)", "Diploma in Family Medicine (DFM)", "Diploma in Psychiatry (DPM)"
    ],
    "ss": [
        # DM Courses
        "DM Cardiology", "DM Neurology", "DM Nephrology", "DM Gastroenterology", "DM Pulmonary Medicine",
        "DM Neonatology", "DM Medical Oncology", "DM Endocrinology", "DM Clinical Haematology", "DM Critical Care Medicine",
        "DM Clinical Immunology and Rheumatology", "DM Neuroradiology", "DM Medical Genetics", "DM Pediatric Neurology",
        "DM Infectious Diseases", "DM Hepatology", "DM Organ Transplant Anaesthesia & Critical Care",
        "DM Interventional Radiology", "DM Oncopathology", "DM Cardiac Anaesthesia", "DM Neuroanaesthesia",
        "DM Medical Gastroenterology",
        # MCh Courses
        "MCh Neurosurgery", "MCh Urology", "MCh Cardio Thoracic and Vascular Surgery (CTVS)",
        "MCh Plastic & Reconstructive Surgery", "MCh Surgical Oncology", "MCh Pediatric Surgery",
        "MCh Surgical Gastroenterology / Hepato-Pancreato-Biliary Surgery", "MCh Gynecological Oncology",
        "MCh Vascular Surgery", "MCh Head and Neck Surgery", "MCh Pediatric Cardiothoracic Surgery",
        "MCh Hand Surgery", "MCh Endocrine Surgery", "MCh Pediatric Orthopaedics", "MCh Reproductive Medicine & Surgery",
        # DrNB Courses
        "DrNB Cardiology", "DrNB Neurology", "DrNB Nephrology", "DrNB Medical Gastroenterology", "DrNB Medical Oncology",
        "DrNB Endocrinology", "DrNB Neonatology", "DrNB Clinical Haematology", "DrNB Critical Care Medicine",
        "DrNB Rheumatology", "DrNB Clinical Immunology and Rheumatology", "DrNB Neuroradiology", "DrNB Medical Genetics",
        "DrNB Pediatric Neurology", "DrNB Infectious Diseases", "DrNB Hepatology", "DrNB Interventional Radiology",
        "DrNB Oncopathology", "DrNB Neurosurgery", "DrNB Urology", "DrNB Cardio Thoracic & Vascular Surgery (CTVS)",
        "DrNB Plastic & Reconstructive Surgery", "DrNB Pediatric Surgery", "DrNB Surgical Oncology",
        "DrNB Surgical Gastroenterology", "DrNB Vascular Surgery", "DrNB Endocrine Surgery", "DrNB Gynecological Oncology",
        "DrNB Cardiac Anesthesia", "DrNB Neuroanesthesia", "DrNB Pediatric Orthopaedics", "DrNB Reproductive Medicine & Surgery"
    ]
}

# Standardized short prefixes for college generation
college_adjectives = ["Government", "National", "Netaji Subhas", "Mahatma Gandhi", "Rajiv Gandhi", "Sardar Patel", "Acharya", "Christian", "Deccan", "Dr. B.R. Ambedkar"]
college_nouns = ["Medical College and Hospital", "Institute of Medical Sciences", "Medical Academy", "Memorial Medical Institute"]

def get_colleges_for_state(state):
    # Seed state name for deterministic generation of colleges
    random.seed(state)
    
    colleges = []
    
    # Establish college count based on state size (UTs get 1-2, large states get 4)
    is_ut = state in ["Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", "Ladakh", "Lakshadweep", "Puducherry"]
    count = 1 if state == "Lakshadweep" else (2 if is_ut else 4)
    
    for i in range(count):
        college_type = "Government"
        if i == 1 and not is_ut:
            college_type = "Private"
        elif i == 2:
            college_type = "Deemed"
        elif i == 3:
            college_type = "Government"
            
        adj = random.choice(college_adjectives)
        noun = random.choice(college_nouns)
        
        name = f"{adj} {noun}, {state}"
        
        # Create a unique short code ID
        words = [w[0] for w in name.split() if w[0].isupper()]
        code = "".join(words)[:5]
        col_id = f"{state[:2].upper()}_{code}_{i}"
        
        colleges.append({
            "id": col_id,
            "name": name,
            "type": college_type
        })
        
    return colleges

def generate_seat_matrix(level, state, colleges):
    # Seed state + level for deterministic generation
    random.seed(f"{state}_{level}")
    
    rows = []
    courses = courses_by_level[level]
    
    for col in colleges:
        col_type = col["type"]
        col_id = f"{level.upper()}_{col['id']}"
        col_name = col["name"]
        
        # Determine subset of courses offered by this college
        if level == "ug":
            college_courses = ["MBBS"]
        else:
            # PG or SS: pick a randomized subset of courses to represent realistic scenarios
            # Pick a mix of conventional and non-conventional courses
            college_courses = random.sample(courses, k=min(len(courses), random.randint(5, 12)))
            
            # Make sure non-conventional courses are explicitly injected in some colleges to show proof of feature
            if level == "pg" and "MD Medical Genetics" not in college_courses and random.random() < 0.3:
                college_courses.append("MD Medical Genetics")
            if level == "ss" and "DM Medical Genetics" not in college_courses and random.random() < 0.3:
                college_courses.append("DM Medical Genetics")

        for course in college_courses:
            # Base seats per course depending on type
            if col_type == "Government":
                base_seats = 180 if level == "ug" else (random.randint(6, 18))
                if level == "ss":
                    base_seats = random.randint(2, 6)
                
                if level == "ss":
                    # SS is 100% MCC
                    rows.append({
                        "college_id": col_id,
                        "college_name": col_name,
                        "college_type": col_type,
                        "state": state,
                        "course": course,
                        "counseling_route": "MCC",
                        "quota_type": "All India Basis",
                        "seats": base_seats
                    })
                else:
                    # UG/PG split: AIQ (15% UG, 50% PG) / State Quota (85% UG, 50% PG)
                    aiq_pct = 0.15 if level == "ug" else 0.50
                    aiq_seats = max(1, int(base_seats * aiq_pct))
                    sq_seats = max(1, base_seats - aiq_seats)
                    
                    rows.append({
                        "college_id": col_id,
                        "college_name": col_name,
                        "college_type": col_type,
                        "state": state,
                        "course": course,
                        "counseling_route": "MCC",
                        "quota_type": "All India Quota",
                        "seats": aiq_seats
                    })
                    rows.append({
                        "college_id": col_id,
                        "college_name": col_name,
                        "college_type": col_type,
                        "state": state,
                        "course": course,
                        "counseling_route": "STATE",
                        "quota_type": "Competent Authority Quota",
                        "seats": sq_seats
                    })
                    
            elif col_type == "Deemed":
                base_seats = 150 if level == "ug" else (random.randint(4, 10))
                if level == "ss":
                    base_seats = random.randint(2, 4)
                
                if level == "ss":
                    rows.append({
                        "college_id": col_id,
                        "college_name": col_name,
                        "college_type": col_type,
                        "state": state,
                        "course": course,
                        "counseling_route": "MCC",
                        "quota_type": "All India Basis",
                        "seats": base_seats
                    })
                else:
                    # Deemed: Management Quota (85%) / NRI Quota (15%) under MCC
                    nri_seats = max(1, int(base_seats * 0.15))
                    mgmt_seats = max(1, base_seats - nri_seats)
                    
                    rows.append({
                        "college_id": col_id,
                        "college_name": col_name,
                        "college_type": col_type,
                        "state": state,
                        "course": course,
                        "counseling_route": "MCC",
                        "quota_type": "Deemed Management / Paid",
                        "seats": mgmt_seats
                    })
                    rows.append({
                        "college_id": col_id,
                        "college_name": col_name,
                        "college_type": col_type,
                        "state": state,
                        "course": course,
                        "counseling_route": "MCC",
                        "quota_type": "Deemed NRI",
                        "seats": nri_seats
                    })
                    
            elif col_type == "Private":
                base_seats = 120 if level == "ug" else (random.randint(3, 8))
                if level == "ss":
                    base_seats = random.randint(1, 3)
                
                if level == "ss":
                    rows.append({
                        "college_id": col_id,
                        "college_name": col_name,
                        "college_type": col_type,
                        "state": state,
                        "course": course,
                        "counseling_route": "MCC",
                        "quota_type": "All India Basis",
                        "seats": base_seats
                    })
                else:
                    # Private: State Quota/CQ (50%), Management Quota (35%), NRI/Minority Quota (15%) under STATE
                    cq_seats = max(1, int(base_seats * 0.50))
                    mq_seats = max(1, int(base_seats * 0.35))
                    nri_min_seats = max(1, base_seats - cq_seats - mq_seats)
                    
                    rows.append({
                        "college_id": col_id,
                        "college_name": col_name,
                        "college_type": col_type,
                        "state": state,
                        "course": course,
                        "counseling_route": "STATE",
                        "quota_type": "Competent Authority Quota",
                        "seats": cq_seats
                    })
                    rows.append({
                        "college_id": col_id,
                        "college_name": col_name,
                        "college_type": col_type,
                        "state": state,
                        "course": course,
                        "counseling_route": "STATE",
                        "quota_type": "Management Quota",
                        "seats": mq_seats
                    })
                    rows.append({
                        "college_id": col_id,
                        "college_name": col_name,
                        "college_type": col_type,
                        "state": state,
                        "course": course,
                        "counseling_route": "STATE",
                        "quota_type": "NRI / Minority Quota",
                        "seats": nri_min_seats
                    })
    return rows

def main():
    base_dir = "public/data"
    os.makedirs(base_dir, exist_ok=True)
    
    manifest = {
        "version": "1.1.0-medical-only",
        "lastUpdated": datetime.utcnow().isoformat() + "Z",
        "levels": {
            "ug": { "name": "Undergraduate (UG)", "summaryPath": "ug/summary.json" },
            "pg": { "name": "Postgraduate (PG)", "summaryPath": "pg/summary.json" },
            "ss": { "name": "Super Specialty (SS)", "summaryPath": "ss/summary.json" }
        }
    }
    
    with open(os.path.join(base_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
        
    for level in ["ug", "pg", "ss"]:
        level_dir = os.path.join(base_dir, level)
        states_dir = os.path.join(level_dir, "states")
        os.makedirs(states_dir, exist_ok=True)
        
        all_seats = []
        states_list = sorted(states_and_uts)
        
        col_count = 0
        seat_count = 0
        quota_set = set()
        type_set = set()
        course_set = set()
        
        for state in states_list:
            colleges = get_colleges_for_state(state)
            col_count += len(colleges)
            state_seats = generate_seat_matrix(level, state, colleges)
            all_seats.extend(state_seats)
            
            # Save state detail JSON
            state_filename = f"{state.lower().replace(' ', '_').replace('&', 'and')}.json"
            with open(os.path.join(states_dir, state_filename), "w") as f:
                json.dump(state_seats, f, indent=2)
                
        # Calculate summary statistics
        for row in all_seats:
            seat_count += row["seats"]
            quota_set.add(row["quota_type"])
            type_set.add(row["college_type"])
            course_set.add(row["course"])
            
        summary = {
            "totalColleges": col_count,
            "totalSeats": seat_count,
            "states": states_list,
            "courses": sorted(list(course_set)),
            "quotas": sorted(list(quota_set)),
            "types": sorted(list(type_set))
        }
        
        with open(os.path.join(level_dir, "summary.json"), "w") as f:
            json.dump(summary, f, indent=2)
            
    print("Medical-only data generation complete!")

if __name__ == "__main__":
    main()
