import os
import json
import re
from datetime import datetime

# 36 States and Union Territories (Canonical Names)
states_and_uts = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana",
    "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
    "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
]

# Map NMC raw state name variations to canonical names
state_name_mapping = {
    "andaman & nicobar": "Andaman and Nicobar Islands",
    "andaman nicobar islands": "Andaman and Nicobar Islands",
    "andaman and nicobar islands": "Andaman and Nicobar Islands",
    "andaman & nicobar islands": "Andaman and Nicobar Islands",
    "a & n islands": "Andaman and Nicobar Islands",
    "chattisgarh": "Chhattisgarh",
    "chhatisgarh": "Chhattisgarh",
    "dadra and nagar haveli": "Dadra and Nagar Haveli and Daman and Diu",
    "dadra & nagar haveli": "Dadra and Nagar Haveli and Daman and Diu",
    "daman & diu": "Dadra and Nagar Haveli and Daman and Diu",
    "daman and diu": "Dadra and Nagar Haveli and Daman and Diu",
    "dadra and nagar haveli and daman and diu": "Dadra and Nagar Haveli and Daman and Diu",
    "dadar & nagar haveli": "Dadra and Nagar Haveli and Daman and Diu",
    "dadara nagar haveli": "Dadra and Nagar Haveli and Daman and Diu",
    "delhi (nct)": "Delhi",
    "nct of delhi": "Delhi",
    "jammu & kashmir": "Jammu and Kashmir",
    "jammu and kashmir": "Jammu and Kashmir",
    "tamilnadu": "Tamil Nadu",
    "orissa": "Odisha",
    "pondicherry": "Puducherry",
    "telengana": "Telangana",
    "andhra pradgeasyhathri": "Andhra Pradesh",
    "maharashtra pri": "Maharashtra",
    "maharashtra s": "Maharashtra",
    "punjab hom": "Punjab",
    "tamil nadu pri": "Tamil Nadu",
    "uttar pradesh pri": "Uttar Pradesh"
}

def clean_state_name(raw_name):
    if not isinstance(raw_name, str):
        return "Unknown"
    name = re.sub(r'\s+', ' ', raw_name).strip()
    name_lower = name.lower()
    
    if name_lower in state_name_mapping:
        return state_name_mapping[name_lower]
        
    for canonical in states_and_uts:
        if canonical.lower() == name_lower:
            return canonical
            
    for canonical in states_and_uts:
        if name_lower.startswith(canonical.lower()):
            return canonical
            
    return name

college_name_map = {
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
    "te of Medical Sciences & Research Centre Nan": "SMBT Institute of Medical Sciences & Research Centre, Nandihills, Nashik",
    
    # Newly found mangled / typos
    "TomoRiba Institute of Health & Medical S": "Tomo Riba Institute of Health & Medical Sciences, Naharlagun",
    "TomoRiba Institute of Health & Medical Sciences": "Tomo Riba Institute of Health & Medical Sciences, Naharlagun",
    "Tomo Riba Institute of Health & Medical S": "Tomo Riba Institute of Health & Medical Sciences, Naharlagun",
    "R K Damani Medical College ShriRamchandra Institute ofMedical Sciences, Chhatrapati Sambhajinagar": "R K Damani Medical College Shri Ramchandra Institute of Medical Sciences, Chhatrapati Sambhajinagar",
    "KanyaKumari Government Medical College Asaripallam": "Kanyakumari Government Medical College, Asaripallam",
    "KanyaKumari Government Medical College, Asaripallam": "Kanyakumari Government Medical College, Asaripallam",
    "Dr. Moopen s Medical College, Wayanad, Kerala": "Dr. Moopen's Medical College, Wayanad, Kerala"
}

def title_case_if_all_caps(name):
    alpha = [c for c in name if c.isalpha()]
    if not alpha or not all(c.isupper() for c in alpha):
        return name
        
    lower_words = {'and', 'of', 'for', 'in', 'the', 'on', 'at', 'with', 'by', 'to', 'from'}
    abbreviations = {
        'esic', 'aps', 'rvs', 'sks', 'mgu', 'pt', 'spn', 'kem', 'gmc', 'ims', 'mcc', 'kem', 
        'lhmc', 'mamt', 'mamc', 'ucms', 'vmmc', 'svims', 'rims', 'jipmer', 'aiims', 'pgimer', 'fs'
    }
    
    words = name.split()
    new_words = []
    for i, w in enumerate(words):
        clean_w = re.sub(r'[^A-Za-z]', '', w).lower()
        if clean_w in abbreviations:
            new_words.append(w.upper())
        elif clean_w in lower_words and i > 0 and i < len(words) - 1:
            new_words.append(w.lower())
        else:
            tc = w.capitalize()
            if '-' in tc:
                tc = '-'.join(p.capitalize() for p in tc.split('-'))
            if "'" in tc:
                parts = tc.split("'")
                tc = parts[0].capitalize() + "'" + parts[1].lower()
            new_words.append(tc)
            
    return ' '.join(new_words)

def clean_college_name(raw_name):
    if not isinstance(raw_name, str):
        return "Unknown College"
    
    # Remove colon prefix if it exists, like "PG/TS/01/G/1: Nizams Institute of Medical Sciences"
    if ":" in raw_name:
        parts = raw_name.split(":", 1)
        prefix = parts[0].strip()
        if "/" in prefix or re.match(r"^[A-Z0-9/]+$", prefix, re.IGNORECASE):
            raw_name = parts[1].strip()
            
    name = re.sub(r'\s+', ' ', raw_name).strip()
    name = re.sub(r'\s*,\s*', ', ', name)
    
    if name in college_name_map:
        name = college_name_map[name]
        
    # Title-case if all caps
    name = title_case_if_all_caps(name)
    
    # Standard spelling and formatting fixes
    name = name.replace("Goverment", "Government")
    name = name.replace("Opthalmology", "Ophthalmology")
    name = name.replace("Opthalmo", "Ophthalmology")
    name = name.replace("Instt.", "Institute")
    name = name.replace("Instt", "Institute")
    name = name.replace("ofMedical", "of Medical")
    name = name.replace("andHospital", "and Hospital")
    name = name.replace("andResearch", "and Research")
    name = name.replace("Hopsital", "Hospital")
    name = name.replace("Hopsitial", "Hospital")
    name = name.replace("HOPSITAL", "Hospital")
    name = name.replace("Instituteof", "Institute of")
    
    # Standardize common abbreviations
    name = name.replace("GMC", "Government Medical College")
    name = name.replace("Govt Medical College", "Government Medical College")
    name = name.replace("Govt. Medical College", "Government Medical College")
    name = name.replace("Inst. of Medical Sce.", "Institute of Medical Sciences")
    name = name.replace("Inst. of Medical Science", "Institute of Medical Sciences")
    name = name.replace("Med. College", "Medical College")
    name = name.replace("Med. Col.", "Medical College")
    name = name.replace("Hospt.", "Hospital")
    
    # Normalize spaces around ampersands
    name = re.sub(r'(\w)\&', r'\1 &', name)
    name = re.sub(r'\&(\w)', r'& \1', name)
    
    # Strip trailing period unless it is part of an abbreviation (e.g. U.P.)
    name = re.sub(r'(?<!\b[A-Za-z])\.$', '', name)
    name = re.sub(r'[,\s]+$', '', name)
    
    # Final space normalization
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name

def clean_course_name(course_name):
    if not isinstance(course_name, str):
        return "Unknown Course"
    return re.sub(r'\s+', ' ', course_name).strip()

mangled_map = {
    'cMh DCe n- tAren Naeews tChheasnidoigloarghy': 'MD - Anaesthesiology',
    'cMh DCe n- tRrea Ndeiow DChiaangdniogasrihs': 'MD - Radio Diagnosis',
    'cMieDn cCeosm (TmRuIHnMityS )M, Nedahicainrteagun': 'MD - Community Medicine',
    'cMieDn cMesic (rToRbIiHoMloS) y, Nahartagun': 'MD - Microbiology',
    'cMieDn cMesic (rToRbIiHoMloSg) y, Nahartagun': 'MD - Microbiology',
    'cMieDn cPeesd (iTaRtrIHicMs S), Nahartagun': 'MD - Paediatrics',
    'cMieDn cPehsa (rTmRaIHcMoloS )g, yNahartagun': 'MD - Pharmacology',
    'cMieDn-c eAsn (aTtRoImHyMS), Nahartagun': 'MD - Anatomy',
    'cMieDn-c eAsn (eTsRthIHeMsioSl) ,o Ngyahartagun': 'MD - Anaesthesiology',
    'cMieDn-c eGse (nTeRrIaHl MMSe)d, iNcianheartagun': 'MD - General Medicine',
    'cMieDn-c ePsh y(TsRioIHloMgyS), Nahartagun': 'MD - Physiology',
    'cMieDn-cReasd (iToR dIHiaMgnSo),s Nisahartagun': 'MD - Radio Diagnosis',
    'cMieSn cOebss (tTeRtrIHicMs aSn),d N Gayhnaaretacgoulong': 'MS - Obstetrics & Gynaecology',
    'cMieSn c–e Gs e(TnReIrHalM SSu)r,g Nerayhartagun': 'MS - General Surgery',
    'cMieSn c-e Gs e(TnReIrHalM SSu)r,g Nerayhartagun': 'MS - General Surgery',
    'cMieSn c\u2013e Gs e(TnReIrHalM SSu)r,g Nerayhartagun': 'MS - General Surgery',
    'vMatDi Anaesthesiolog y': 'MD - Anaesthesiology',
    'vMatDi Orthopaedics': 'MD - Orthopaedics',
    'vMatDi Paediatrics': 'MD - Paediatrics',
    'vMatDi-DVL': 'MD - Dermatology, Venereology & Leprosy',
    'vMatDi-General Medicine': 'MD - General Medicine',
    'vMatDi-Radio Diagnosis': 'MD - Radio Diagnosis',
    'vMatSi Ophthalmolog y': 'MS - Ophthalmology',
    'vMatSi Otorhinolaryng ology (ENT': 'MS - Otorhinolaryngology (ENT)',
    'vMatSi-General Surgery': 'MS - General Surgery',
    'vMatSi-Obstetrics & Gynecology': 'MS - Obstetrics & Gynaecology',
    
    # SS mangled:
    'W CHANDIG DAMRH- Medical Oncology': 'DM - Medical Oncology',
    'W CHANDIGADRMH - Onco Pathology': 'DM - Onco Pathology',
    'W CHANDIGMA.RCHh - Surgical Oncology': 'M.Ch - Surgical Oncology',
    'dihills Nashik DM- Cardiology': 'DM - Cardiology',
    'edwas DM - Nephrology': 'DM - Nephrology',
    'edwas DM- Cardiology': 'DM - Cardiology',
    'logy VisakhaMpa.Ctnha m- Neuro Surgery': 'M.Ch - Neuro Surgery',
    'logy Visakhapa tDnaMm- Cardiology': 'DM - Cardiology',
    'm M.Ch - Urology/Genito-Urinary Surgery': 'M.Ch - Urology',
    'naMga.Crh - Urology/Genito-Urinary Surgery': 'M.Ch - Urology',
    'nagar M.Ch - Neuro Surgery': 'M.Ch - Neuro Surgery',
}

pg_specialties = {
    'anaesthesiology': ['anaesthesiology', 'anaesthesia', 'anesthesiology', 'anesthesia', 'anaeshtesiology', 'anaesthesiolog y'],
    'anatomy': ['anatomy'],
    'biochemistry': ['biochemistry', 'biochemestry', 'bio-chemistry', 'bio-chemestry'],
    'physiology': ['physiology'],
    'pharmacology': ['pharmacology', 'pharmacoloy'],
    'pathology': ['pathology', 'patholgy', 'clinical pathology'],
    'microbiology': ['microbiology', 'microbioogy', 'micrology'],
    'forensic medicine & toxicology': ['forensic medicine & toxicology', 'forensic medicine', 'forensic medicine/forensic medicine & toxicology', 'forensic medicine/medic', 'forensic medicine and toxicology', 'foresnic medicine'],
    'community medicine': ['community medicine', 'preventive social medicine', 'preventive & social medicine', 'social & preventive medicine / community medicine', 'psm', 'com. medicine', 'preventive social medicine'],
    'dermatology, venereology & leprosy': ['dermatology', 'dermatology, venereology & leprosy', 'dermatology venereology & leprosy', 'dermatology venerology leprosy', 'dermatology venerology and leprosy', 'dermatology, veneerology & leprosy', 'dermatology, venerology & leprosy', 'dermatology, venerology', 'dermatology venereolog', 'dvl', 'skin & v.d', 'skin & vd', 'dermatology, venereology and leprosy', 'dermatolog y venereolog'],
    'general medicine': ['general medicine', 'general-medicine', 'geneml medicine', 'ceneral medicine', 'medicine'],
    'paediatrics': ['paediatrics', 'pediatrics', 'paediatric', 'pediatric', 'child health', 'padiatrics', 'pediatriscs'],
    'psychiatry': ['psychiatry', 'psychaitry', 'psychialry', 'psychological medicine', 'psychological medicine (dpm)'],
    'radio diagnosis': ['radio diagnosis', 'radiodiagnosis', 'radio-diagnosis', 'radiology', 'radio diagnosis/radiology', 'radiodiagnosis', 'radiodi agnosis', 'radio - diagnosis', 'radio- diagnosis', 'radio daiagnosis', 'radio diagonsis', 'radiology/radiodi agnosis'],
    'radiation oncology': ['radiation oncology', 'radiotherapy', 'radio therapy', 'radio-therapy', 'radiotherapy/ radiation oncology', 'radiotherapy/rad iation oncology', 'medicine radiotherapy', 'radio oncology', 'radiotherepy'],
    'tuberculosis & respiratory diseases': ['tuberculosis & respiratory diseases', 'tuberculosis & respiratory diseases / pulmonary medicine', 'pulmonary medicine', 'respiratory medicine', 'tuberculosis & chest diseases', 'tb & rd', 'tb respiratory diseases', 'respiratory mcdicinc'],
    'general surgery': ['general surgery', 'general-surgery', 'surgery', 'general surgery', 'geveral surgery'],
    'obstetrics & gynaecology': ['obstetrics & gynaecology', 'obstetrics and gynaecology', 'obstetrics & gynecology', 'obstetrics and gynecology', 'obg', 'dgo', 'obst. & gynaec', 'obstetrics & gynaec', 'obstetrics & gyanecology', 'obstetrics and gynaecolo', 'obstetrics and gynaecolog', 'obstetrics& gynaecology', 'gynaecology', 'obstetrics &gynaecology', 'obstetrics &gynecology', 'obg-dgo', 'obst and gynae'],
    'ophthalmology': ['ophthalmology', 'opthalmology', 'ophthamology', 'ophthalmolgy', 'ophthalmol ogy', 'ophthalmolog y', 'opthalmolog y', 'ophthamolgy', 'ophthalm'],
    'otorhinolaryngology (ent)': ['otorhinolaryngology', 'otorhinolaryngology (ent)', 'ent', 'oto-rhino-laryngology', 'otorhinolaryngolog y', 'oto-rhino- laryngology', 'otorhinolarnygology', 'otorhinolaryng ology (ent', 'oto- rhinolaryngology', 'otorhinolaryngol ogy', 'otorhinolaryngology (ent', 'otorhinolaryngology(e nt'],
    'orthopaedics': ['orthopaedics', 'orthopedics', 'orthopeadics', 'orthopedics', 'orthipedics', 'orthopacdics', 'm. s. orthopaedics'],
    'physical medicine & rehabilitation': ['physical medicine & rehabilitation', 'physical medicine and rehabilitation', 'pmr'],
    'immunohematology & blood transfusion': ['immunohematology & blood transfusion', 'immunohematology', 'transfusion medicine', 'ihtm/itbt', 'immuno haematology & blood transfusion', 'immuno- hematology & blood tranfusion', 'immunology haematology and blood transfusion', 'immunology hematology and blood transfusion', 'immunolog y hematology', 'ihtm/itbt', 'immunoHae matology&', 'immuno haematology and blood transfusion', 'immuno- haematology and blood transfusion'],
    'emergency medicine': ['emergency medicine'],
    'geriatrics': ['geriatrics', 'geriatric'],
    'sports medicine': ['sports medicine'],
    'palliative medicine': ['palliative medicine'],
    'family medicine': ['family medicine'],
    'aerospace medicine': ['aerospace medicine', 'aviation medicine/aerospace medicine'],
    'hospital administration': ['hospital administration', 'health administration', 'health education'],
    'public health': ['public health', 'master of public health - epidemiology', 'public health - epidemiology'],
    'nuclear medicine': ['nuclear medicine'],
    'diabetology': ['diabetology'],
    'biophysics': ['biophysics', 'bio-physics'],
    'tropical medicine': ['tropical medicine'],
    'traumatology & surgery': ['traumatology & surgery', 'traumatology and surgery'],
    'marine medicine': ['marine medicine'],
    'radiation medicine': ['radiation medicine(nuclear medicine)', 'radiation medicine'],
    'community health administration': ['community health administration'],
    'laboratory medicine': ['laboratory medicine', 'lab medicine'],
    'interventional radiology': ['interventional radiology']
}

pg_lookup = {}
for std, aliases in pg_specialties.items():
    for alias in aliases:
        pg_lookup[alias.lower().strip()] = std

casing_map = {
    'anaesthesiology': 'Anaesthesiology',
    'anatomy': 'Anatomy',
    'biochemistry': 'Biochemistry',
    'physiology': 'Physiology',
    'pharmacology': 'Pharmacology',
    'pathology': 'Pathology',
    'microbiology': 'Microbiology',
    'forensic medicine & toxicology': 'Forensic Medicine & Toxicology',
    'community medicine': 'Community Medicine',
    'dermatology, venereology & leprosy': 'Dermatology, Venereology & Leprosy',
    'general medicine': 'General Medicine',
    'paediatrics': 'Paediatrics',
    'psychiatry': 'Psychiatry',
    'radio diagnosis': 'Radio Diagnosis',
    'radiation oncology': 'Radiation Oncology',
    'tuberculosis & respiratory diseases': 'Tuberculosis & Respiratory Diseases',
    'general surgery': 'General Surgery',
    'obstetrics & gynaecology': 'Obstetrics & Gynaecology',
    'ophthalmology': 'Ophthalmology',
    'otorhinolaryngology (ent)': 'Otorhinolaryngology (ENT)',
    'orthopaedics': 'Orthopaedics',
    'physical medicine & rehabilitation': 'Physical Medicine & Rehabilitation',
    'immunohematology & blood transfusion': 'Immunohematology & Blood Transfusion',
    'emergency medicine': 'Emergency Medicine',
    'geriatrics': 'Geriatrics',
    'sports medicine': 'Sports Medicine',
    'palliative medicine': 'Palliative Medicine',
    'family medicine': 'Family Medicine',
    'aerospace medicine': 'Aerospace Medicine',
    'hospital administration': 'Hospital Administration',
    'public health': 'Public Health',
    'nuclear medicine': 'Nuclear Medicine',
    'diabetology': 'Diabetology',
    'biophysics': 'Biophysics',
    'tropical medicine': 'Tropical Medicine',
    'traumatology & surgery': 'Traumatology & Surgery',
    'marine medicine': 'Marine Medicine',
    'radiation medicine': 'Radiation Medicine',
    'community health administration': 'Community Health Administration',
    'laboratory medicine': 'Laboratory Medicine',
    'interventional radiology': 'Interventional Radiology'
}

def clean_pg_course(c):
    orig = c
    c = c.strip()
    
    if orig in mangled_map:
        return mangled_map[orig]
    
    # 1. Exact abbreviation mappings
    exact_abbreviations = {
        'doms': 'Diploma - Ophthalmology',
        'dpm': 'Diploma - Psychiatry',
        'dgo': 'Diploma - Obstetrics & Gynaecology',
        'dlo': 'Diploma - Otorhinolaryngology (ENT)',
        'dch': 'Diploma - Paediatrics',
        'dortho': 'Diploma - Orthopaedics',
        'd.ortho': 'Diploma - Orthopaedics',
        'ddvl': 'Diploma - Dermatology, Venereology & Leprosy',
        'dcp': 'Diploma - Pathology',
    }
    c_lower = c.lower().strip()
    if c_lower in exact_abbreviations:
        return exact_abbreviations[c_lower]

    # Detect degree
    degree = None
    rest = c
    
    if re.match(r'^(M\.Ch\.|M\.Ch|M\. Ch|M\.CH|MCh|M Ch)\b', c, re.IGNORECASE):
        degree = 'M.Ch'
        rest = re.sub(r'^(M\.Ch\.|M\.Ch|M\. Ch|M\.CH|MCh|M Ch)\s*[-–]?\s*', '', c, flags=re.IGNORECASE)
    elif re.match(r'^(MD/MS|MD\s*/\s*MS)\b', c, re.IGNORECASE):
        degree = 'MD/MS'
        rest = re.sub(r'^(MD/MS|MD\s*/\s*MS)\s*[-–]?\s*', '', c, flags=re.IGNORECASE)
    elif re.match(r'^(M\s*\.\s*D\s*\.|M\s*\.\s*D\b|MD\b|MDCeneral\b)', c, re.IGNORECASE):
        degree = 'MD'
        rest = re.sub(r'^(M\s*\.\s*D\s*\.|M\s*\.\s*D\b|MD\b|MDCeneral\b)\s*[-–]?\s*', '', c, flags=re.IGNORECASE)
    elif re.match(r'^(M\s*\.\s*S\s*\.|M\s*\.\s*S\b|MS\b)', c, re.IGNORECASE):
        degree = 'MS'
        rest = re.sub(r'^(M\s*\.\s*S\s*\.|M\s*\.\s*S\b|MS\b)\s*[-–]?\s*', '', c, flags=re.IGNORECASE)
    elif re.match(r'^(DIP\s*\.\s*|Diploma\b|DOMS\b|DPM\b|Post MBBS Diploma\b)', c, re.IGNORECASE):
        degree = 'Diploma'
        rest = re.sub(r'^(DIP\s*\.\s*|Diploma\b|DOMS\b|DPM\b|Post MBBS Diploma\b)\s*(in|courses in)?\s*[-–]?\s*', '', c, flags=re.IGNORECASE)
        
    rest = rest.strip()
    rest_clean = re.sub(r'^[-–\s\.,]+', '', rest).strip()
    
    # Strip parentheses
    if rest_clean.startswith('(') and rest_clean.endswith(')'):
        rest_clean = rest_clean[1:-1].strip()
    elif rest_clean.startswith('(') and ')' not in rest_clean:
        rest_clean = rest_clean[1:].strip()
    
    key = rest_clean.lower()
    # Normalize spaces around commas
    key = re.sub(r'\s*,\s*', ', ', key).strip()
    key_no_paren = re.sub(r'\(.*?\)', '', key).strip()
    
    if key in pg_lookup:
        spec = pg_lookup[key]
    elif key_no_paren in pg_lookup:
        spec = pg_lookup[key_no_paren]
    else:
        spec = rest_clean
        
    spec_title = casing_map.get(spec.lower(), rest_clean)
    
    if not degree:
        if spec_title in ['Anatomy', 'Biochemistry', 'Physiology', 'Pharmacology', 'Pathology', 'Microbiology', 
                         'Forensic Medicine & Toxicology', 'Community Medicine', 'Dermatology, Venereology & Leprosy', 
                         'General Medicine', 'Paediatrics', 'Psychiatry', 'Radio Diagnosis', 'Radiation Oncology', 
                         'Tuberculosis & Respiratory Diseases', 'Physical Medicine & Rehabilitation', 
                         'Immunohematology & Blood Transfusion', 'Emergency Medicine', 'Geriatrics', 'Sports Medicine', 
                         'Palliative Medicine', 'Family Medicine', 'Aerospace Medicine', 'Nuclear Medicine',
                         'Biophysics', 'Tropical Medicine', 'Public Health', 'Community Health Administration', 'Laboratory Medicine',
                         'Interventional Radiology']:
            degree = 'MD'
        elif spec_title in ['General Surgery', 'Obstetrics & Gynaecology', 'Ophthalmology', 'Otorhinolaryngology (ENT)', 
                            'Orthopaedics', 'Traumatology & Surgery']:
            degree = 'MS'
        else:
            degree = 'MD'
            
    if degree == 'Diploma':
        return f"Diploma - {spec_title}"
    else:
        return f"{degree} - {spec_title}"

ss_specialties = {
    'Cardiology': ['cardiology'],
    'Cardiac Anaesthesia': ['cardiac-anaesthesia', 'cardiac anaesthesia'],
    'Clinical Hematology': ['clinical hematology', 'clinical haematology', 'hematology', 'haematology'],
    'Clinical Immunology & Rheumatology': ['clinical immunology & rheumatology', 'rheumatology', 'clinical immunology and rheumatology'],
    'Critical Care Medicine': ['critical care medicine', 'critical care'],
    'Endocrinology': ['endocrinology'],
    'Geriatric Mental Health': ['geriatric mental health', 'geriatic mental health'],
    'Hepatology': ['hepatology'],
    'Infectious Disease': ['infectious disease', 'infectious diseases'],
    'Interventional Radiology': ['interventional radiology'],
    'Medical Gastroenterology': ['medical gastroenterology', 'gastroenterology'],
    'Medical Genetics': ['medical genetics', 'genetics'],
    'Nephrology': ['nephrology'],
    'Neuro Anaesthesia': ['neuro anasthesia', 'neuro anaesthesia', 'neuroanasthesia', 'neuroanaesthesia'],
    'Neuroradiology': ['neuro radiology', 'neuroradiology'],
    'Neurology': ['neurology'],
    'Onco Pathology': ['onco pathology'],
    'Organ Transplant Anaesthesia & Critical Care': ['organ transplant anaesthesia & critical care', 'organ transplant anaesthesia and critical care'],
    'Paediatric Cardiology': ['paediatric cardiology', 'pediatric cardiology'],
    'Paediatric Hepatology': ['paediatric hepatology', 'pediatric hepatology'],
    'Paediatric Neurology': ['paediatric neurology', 'pediatric neurology'],
    'Paediatric Oncology': ['paediatric oncology', 'pediatric oncology', 'paediatrics oncology'],
    'Paediatric & Neonatal Anaesthesia': ['paediatric and neonatal anaesthesia', 'paediatric & neonatal anaesthesia', 'pediatric and neonatal anesthesia', 'paediatric and neonatal anesthesia'],
    'Paediatric Gastroenterology': ['pediatrics gastroenterology', 'paediatric gastroenterology', 'pediatric gastroenterology'],
    'Paediatric Nephrology': ['paediatric nephrology', 'paediatrics nephrology', 'paediatric nephrology', 'paediatrics nephrology'],
    'Pulmonary Medicine': ['pulmonary medicine', 'pulmonology'],
    'Pulmonary & Critical Care Medicine': ['pulmonary and critical care medicine', 'pulmonary & critical care medicine'],
    'Clinical Pharmacology': ['clinical pharmacology', 'pharmacology'],
    'Medical Oncology': ['medical oncology'],
    'Virology': ['virology'],
    'Neonatology': ['neonatology'],
    'Reproductive Medicine & Surgery': ['reproductive medicine and surgery', 'reproductive medicine & surgery', 'reproductive medicine'],
    'Hepato Pancreato Biliary Surgery': ['hepato pancreato biliary surgery', 'hepato pancreato biliary'],
    'Thoracic Surgery': ['thorasic surgery', 'thoracic surgery'],
    'Neuro Surgery': ['neuro surgery', 'neurosurgery', 'neuro surgery(3 years)', 'neuro surgery(6 years)'],
    'Plastic & Reconstructive Surgery': ['plastic surgery', 'plastic surgery/plastic & reconstructive surgery', 'plastic & reconstructive surgery', 'plastic and reconstructive surgery'],
    'Gynaecological Oncology': ['gynaecological oncology', 'gynecological oncology'],
    'Paediatric Surgery': ['pediatric surgery', 'paediatric surgery', 'pediatric'],
    'Cardiothoracic Surgery': ['cardiovascular & thoracic surgery', 'cardiovascular and thoracic surgery', 'cardio thoracic surgery', 'thoracic surgery/cardio thoracic surgery/cardio vascular and thoracic surgery'],
    'Endocrine Surgery': ['endocrine surgery'],
    'Head & Neck Surgery': ['head & neck surgery', 'head and neck surgery'],
    'Surgical Gastroenterology': ['surgical gastroenterology'],
    'Paediatric Orthopaedics': ['paediatric orthopaedics', 'pediatric orthopedics'],
    'Surgical Oncology': ['surgical oncology'],
    'Urology': ['urology/genito-urinary surgery', 'urology', 'genito-urinary surgery'],
    'Vascular Surgery': ['vascular surgery'],
    'Hand Surgery': ['hand surgery']
}

ss_lookup = {}
for std, aliases in ss_specialties.items():
    for alias in aliases:
        ss_lookup[alias.lower().strip()] = std

def clean_ss_course(c):
    orig = c
    c = c.strip()
    if orig in mangled_map:
        return mangled_map[orig]
        
    # Detect degree
    degree = None
    rest = c
    
    # Check degree prefixes
    if re.match(r'^(M\.Ch\.|M\.Ch|M\. Ch|M\.CH|MCh|M Ch)\b', c, re.IGNORECASE):
        degree = 'M.Ch'
        rest = re.sub(r'^(M\.Ch\.|M\.Ch|M\. Ch|M\.CH|MCh|M Ch)\s*[-–]?\s*', '', c, flags=re.IGNORECASE)
    elif re.match(r'^(DM/M\.Ch|DM/M\.\s*Ch|DM\s*/\s*M\.\s*Ch)\b', c, re.IGNORECASE):
        degree = 'DM/M.Ch'
        rest = re.sub(r'^(DM/M\.Ch|DM/M\.\s*Ch|DM\s*/\s*M\.\s*Ch)\s*[-–]?\s*', '', c, flags=re.IGNORECASE)
    elif re.match(r'^(DM|D\.M\.)\b', c, re.IGNORECASE):
        degree = 'DM'
        rest = re.sub(r'^(DM|D\.M\.)\s*[-–]?\s*', '', c, flags=re.IGNORECASE)
        
    rest = rest.strip()
    rest_clean = re.sub(r'^[-–\s\.]+', '', rest).strip()
    
    if degree == 'M.Ch' and rest_clean.lower() == 'cardiology':
        return 'M.Ch - Cardiovascular & Thoracic Surgery'
        
    if rest_clean.lower() == 'gastroenterology' or rest_clean.lower() == 'medical gastroenterology':
        if degree == 'M.Ch':
            return 'M.Ch - Surgical Gastroenterology'
        else:
            return 'DM - Medical Gastroenterology'
            
    key = rest_clean.lower()
    key_no_paren = re.sub(r'\(.*?\)', '', key).strip()
    
    if key in ss_lookup:
        spec = ss_lookup[key]
    elif key_no_paren in ss_lookup:
        spec = ss_lookup[key_no_paren]
    else:
        spec = rest_clean
        
    if not degree:
        if spec in ['Cardiology', 'Neurology', 'Nephrology', 'Medical Oncology', 'Medical Gastroenterology', 
                    'Endocrinology', 'Neonatology', 'Virology', 'Clinical Hematology', 
                    'Clinical Immunology & Rheumatology', 'Critical Care Medicine', 'Infectious Disease', 
                    'Medical Genetics', 'Geriatric Mental Health', 'Interventional Radiology', 'Neuroradiology', 
                    'Onco Pathology', 'Organ Transplant Anaesthesia & Critical Care', 'Paediatric Cardiology', 
                    'Paediatric Hepatology', 'Paediatric Neurology', 'Paediatric Oncology', 
                    'Paediatric & Neonatal Anaesthesia', 'Paediatric Gastroenterology', 'Pulmonary Medicine', 
                    'Pulmonary & Critical Care Medicine', 'Clinical Pharmacology', 'Paediatric Nephrology']:
            degree = 'DM'
        elif spec in ['Urology', 'Neuro Surgery', 'Plastic & Reconstructive Surgery', 'Paediatric Surgery', 
                      'Surgical Oncology', 'Surgical Gastroenterology', 'Hepato Pancreato Biliary Surgery', 
                      'Vascular Surgery', 'Cardiovascular & Thoracic Surgery', 'Head & Neck Surgery', 
                      'Hand Surgery', 'Reproductive Medicine & Surgery', 'Endocrine Surgery', 
                      'Gynaecological Oncology', 'Paediatric Orthopaedics', 'Thoracic Surgery']:
            degree = 'M.Ch'
        else:
            degree = 'DM'
            
    spec_title = spec
    if spec == 'Cardiothoracic Surgery':
        spec_title = 'Cardiovascular & Thoracic Surgery'
        
    if degree == 'DM/M.Ch':
        return f"DM/M.Ch - {spec_title}"
    else:
        return f"{degree} - {spec_title}"

def get_college_type(mgmt_text, name):
    name_lower = name.lower()
    mgmt_lower = str(mgmt_text).lower().strip()
    
    if "deemed" in name_lower or "deemed" in mgmt_lower:
        return "Deemed"
        
    govt_keywords = ["govt", "govern", "gmc", "society", "corporation", "municip", "military", "esic", "railway", "central", "state", "national"]
    if any(k in mgmt_lower for k in govt_keywords) or any(k in name_lower for k in ["government", "govt"]):
        return "Government"
        
    return "Private"

def is_dental_course(course_name):
    c_upper = str(course_name).upper().strip()
    return any(term in c_upper for term in ["MDS", "DENTAL", "PROSTHODONTICS", "PERIODONTOLOGY", "ORAL", "ORTHODONTICS", "PEDODONTICS", "ENDODONTICS"])

def safe_int(val):
    if not val:
        return 0
    val_str = str(val).strip().replace(",", "")
    if not val_str:
        return 0
    try:
        if "." in val_str:
            return int(float(val_str))
        return int(val_str)
    except ValueError:
        digits = re.findall(r'\d+', val_str)
        if digits:
            return int(digits[0])
        return 0

def slugify(name):
    name = str(name).lower()
    name = re.sub(r'[^a-z0-9\s]', '', name)
    name = re.sub(r'\s+', '_', name).strip()
    return name

def process_ug_data():
    print("Processing UG (MBBS) Dataset from recheck/...")
    rows = []
    
    path = "recheck/PublicNotice_Merged_seatmatrix_Secretary_covering.json"
    if not os.path.exists(path):
        print(f"Warning: {path} not found!")
        return rows
        
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for r in data:
        college_name_raw = r.get("college_name", "").strip()
        state_raw = r.get("state", "").strip()
        mgmt_raw = r.get("management", "").strip()
        
        if not college_name_raw or not state_raw or mgmt_raw == "Total":
            continue
            
        college_name = clean_college_name(college_name_raw)
        state = clean_state_name(state_raw)
        col_type = get_college_type(mgmt_raw, college_name)
        total_seats = safe_int(r.get("total", 0))
        prev_seats = safe_int(r.get("seats_renewed", 0))
        inc_seats = safe_int(r.get("seats_increased", 0))
        
        college_code = r.get("college_code", "").strip()
        if college_code and college_code.lower() != "new establishment":
            college_id = f"ug_{slugify(college_code)}"
        else:
            college_id = f"ug_{slugify(college_name)}_{slugify(state)}"
            
        if total_seats < 0:
            continue
            
        if total_seats == 0:
            rows.append({
                "college_id": college_id,
                "college_name": college_name,
                "college_type": col_type,
                "state": state,
                "course": "MBBS",
                "counseling_route": "STATE",
                "quota_type": "Competent Authority Quota",
                "seats": 0,
                "seats_prev": 0,
                "seats_inc": 0
            })
            continue
            
        if col_type == "Government":
            aiq_seats = int(total_seats * 0.15)
            state_seats = total_seats - aiq_seats
            
            aiq_prev = int(prev_seats * 0.15)
            state_prev = prev_seats - aiq_prev
            
            aiq_inc = int(inc_seats * 0.15)
            state_inc = inc_seats - aiq_inc
            
            if aiq_seats > 0 or aiq_prev > 0 or aiq_inc > 0:
                rows.append({
                    "college_id": college_id,
                    "college_name": college_name,
                    "college_type": col_type,
                    "state": state,
                    "course": "MBBS",
                    "counseling_route": "MCC",
                    "quota_type": "All India Quota",
                    "seats": aiq_seats,
                    "seats_prev": aiq_prev,
                    "seats_inc": aiq_inc
                })
            if state_seats > 0 or state_prev > 0 or state_inc > 0:
                rows.append({
                    "college_id": college_id,
                    "college_name": college_name,
                    "college_type": col_type,
                    "state": state,
                    "course": "MBBS",
                    "counseling_route": "STATE",
                    "quota_type": "Competent Authority Quota",
                    "seats": state_seats,
                    "seats_prev": state_prev,
                    "seats_inc": state_inc
                })
        else:
            state_seats = int(total_seats * 0.50)
            mgmt_seats = int(total_seats * 0.35)
            nri_seats = total_seats - state_seats - mgmt_seats
            
            state_prev = int(prev_seats * 0.50)
            mgmt_prev = int(prev_seats * 0.35)
            nri_prev = prev_seats - state_prev - mgmt_prev
            
            state_inc = int(inc_seats * 0.50)
            mgmt_inc = int(inc_seats * 0.35)
            nri_inc = inc_seats - state_inc - mgmt_inc
            
            if state_seats > 0 or state_prev > 0 or state_inc > 0:
                rows.append({
                    "college_id": college_id,
                    "college_name": college_name,
                    "college_type": col_type,
                    "state": state,
                    "course": "MBBS",
                    "counseling_route": "STATE",
                    "quota_type": "Competent Authority Quota",
                    "seats": state_seats,
                    "seats_prev": state_prev,
                    "seats_inc": state_inc
                })
            if mgmt_seats > 0 or mgmt_prev > 0 or mgmt_inc > 0:
                rows.append({
                    "college_id": college_id,
                    "college_name": college_name,
                    "college_type": col_type,
                    "state": state,
                    "course": "MBBS",
                    "counseling_route": "STATE",
                    "quota_type": "Management Quota",
                    "seats": mgmt_seats,
                    "seats_prev": mgmt_prev,
                    "seats_inc": mgmt_inc
                })
            if nri_seats > 0 or nri_prev > 0 or nri_inc > 0:
                rows.append({
                    "college_id": college_id,
                    "college_name": college_name,
                    "college_type": col_type,
                    "state": state,
                    "course": "MBBS",
                    "counseling_route": "STATE",
                    "quota_type": "NRI / Minority Quota",
                    "seats": nri_seats,
                    "seats_prev": nri_prev,
                    "seats_inc": nri_inc
                })
                
    return rows

def process_pg_data():
    print("Processing PG Dataset from recheck/...")
    rows = []
    
    path = "recheck/Merged_PGseatmatrix_30_1_26PUBLICNOTICE.json"
    if not os.path.exists(path):
        print(f"Warning: {path} not found!")
        return rows
        
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for r in data:
        college_name_raw = r.get("college_name", "").strip()
        state_raw = r.get("state", "").strip()
        course_raw = r.get("course_name", "").strip()
        mgmt_raw = r.get("management", "").strip()
        
        if not college_name_raw or not state_raw or not course_raw:
            continue
            
        if is_dental_course(course_raw):
            continue
            
        college_name = clean_college_name(college_name_raw)
        state = clean_state_name(state_raw)
        course_name = clean_pg_course(course_raw)
        col_type = get_college_type(mgmt_raw, college_name)
        total_seats = safe_int(r.get("final_seats", 0))
        prev_seats = safe_int(r.get("seats_24_25", 0))
        inc_seats = safe_int(r.get("seats_granted_25_26", 0))
        
        college_id = f"pg_{slugify(college_name)}_{slugify(state)}"
        
        if total_seats < 0:
            continue
            
        if total_seats == 0:
            rows.append({
                "college_id": college_id,
                "college_name": college_name,
                "college_type": col_type,
                "state": state,
                "course": course_name,
                "counseling_route": "STATE",
                "quota_type": "Competent Authority Quota",
                "seats": 0,
                "seats_prev": 0,
                "seats_inc": 0
            })
            continue
            
        if col_type == "Government":
            aiq_seats = int(total_seats * 0.50)
            state_seats = total_seats - aiq_seats
            
            aiq_prev = int(prev_seats * 0.50)
            state_prev = prev_seats - aiq_prev
            
            aiq_inc = int(inc_seats * 0.50)
            state_inc = inc_seats - aiq_inc
            
            if aiq_seats > 0 or aiq_prev > 0 or aiq_inc > 0:
                rows.append({
                    "college_id": college_id,
                    "college_name": college_name,
                    "college_type": col_type,
                    "state": state,
                    "course": course_name,
                    "counseling_route": "MCC",
                    "quota_type": "All India Quota",
                    "seats": aiq_seats,
                    "seats_prev": aiq_prev,
                    "seats_inc": aiq_inc
                })
            if state_seats > 0 or state_prev > 0 or state_inc > 0:
                rows.append({
                    "college_id": college_id,
                    "college_name": college_name,
                    "college_type": col_type,
                    "state": state,
                    "course": course_name,
                    "counseling_route": "STATE",
                    "quota_type": "Competent Authority Quota",
                    "seats": state_seats,
                    "seats_prev": state_prev,
                    "seats_inc": state_inc
                })
        else:
            state_seats = int(total_seats * 0.50)
            mgmt_seats = int(total_seats * 0.35)
            nri_seats = total_seats - state_seats - mgmt_seats
            
            state_prev = int(prev_seats * 0.50)
            mgmt_prev = int(prev_seats * 0.35)
            nri_prev = prev_seats - state_prev - mgmt_prev
            
            state_inc = int(inc_seats * 0.50)
            mgmt_inc = int(inc_seats * 0.35)
            nri_inc = inc_seats - state_inc - mgmt_inc
            
            if state_seats > 0 or state_prev > 0 or state_inc > 0:
                rows.append({
                    "college_id": college_id,
                    "college_name": college_name,
                    "college_type": col_type,
                    "state": state,
                    "course": course_name,
                    "counseling_route": "STATE",
                    "quota_type": "Competent Authority Quota",
                    "seats": state_seats,
                    "seats_prev": state_prev,
                    "seats_inc": state_inc
                })
            if mgmt_seats > 0 or mgmt_prev > 0 or mgmt_inc > 0:
                rows.append({
                    "college_id": college_id,
                    "college_name": college_name,
                    "college_type": col_type,
                    "state": state,
                    "course": course_name,
                    "counseling_route": "STATE",
                    "quota_type": "Management Quota",
                    "seats": mgmt_seats,
                    "seats_prev": mgmt_prev,
                    "seats_inc": mgmt_inc
                })
            if nri_seats > 0 or nri_prev > 0 or nri_inc > 0:
                rows.append({
                    "college_id": college_id,
                    "college_name": college_name,
                    "college_type": col_type,
                    "state": state,
                    "course": course_name,
                    "counseling_route": "STATE",
                    "quota_type": "NRI / Minority Quota",
                    "seats": nri_seats,
                    "seats_prev": nri_prev,
                    "seats_inc": nri_inc
                })
                
    return rows

def process_ss_data():
    print("Processing SS Dataset from recheck/...")
    rows = []
    
    path = "recheck/PGSuper-Speciality-Seat-Matrix-as-on-2-4-2026.json"
    if not os.path.exists(path):
        print(f"Warning: {path} not found!")
        return rows
        
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for r in data:
        college_name_raw = r.get("college_name", "").strip()
        state_raw = r.get("state", "").strip()
        course_raw = r.get("course_name", "").strip()
        mgmt_raw = r.get("management", "").strip()
        
        if not college_name_raw or not state_raw or not course_raw:
            continue
            
        if is_dental_course(course_raw):
            continue
            
        college_name = clean_college_name(college_name_raw)
        state = clean_state_name(state_raw)
        course_name = clean_ss_course(course_raw)
        col_type = get_college_type(mgmt_raw, college_name)
        total_seats = safe_int(r.get("final_seats", 0))
        prev_seats = safe_int(r.get("seats_24_25", 0))
        inc_seats = safe_int(r.get("seats_granted_25_26", 0))
        
        college_id = f"ss_{slugify(college_name)}_{slugify(state)}"
        
        if total_seats < 0:
            continue
            
        if total_seats == 0:
            rows.append({
                "college_id": college_id,
                "college_name": college_name,
                "college_type": col_type,
                "state": state,
                "course": course_name,
                "counseling_route": "MCC",
                "quota_type": "All India Basis",
                "seats": 0,
                "seats_prev": 0,
                "seats_inc": 0
            })
            continue
            
        rows.append({
            "college_id": college_id,
            "college_name": college_name,
            "college_type": col_type,
            "state": state,
            "course": course_name,
            "counseling_route": "MCC",
            "quota_type": "All India Basis",
            "seats": total_seats,
            "seats_prev": prev_seats,
            "seats_inc": inc_seats
        })
        
    return rows

def main():
    base_dir = "public/data"
    os.makedirs(base_dir, exist_ok=True)
    
    # 1. Write Manifest
    manifest = {
        "version": "2.0.0-nmc-data",
        "lastUpdated": datetime.now().isoformat() + "Z",
        "levels": {
            "ug": { "name": "Undergraduate (UG)", "summaryPath": "ug/summary.json" },
            "pg": { "name": "Postgraduate (PG)", "summaryPath": "pg/summary.json" },
            "ss": { "name": "Super Specialty (SS)", "summaryPath": "ss/summary.json" }
        }
    }
    
    with open(os.path.join(base_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
        
    # 2. Extract Data
    ug_data = process_ug_data()
    pg_data = process_pg_data()
    ss_data = process_ss_data()
    
    datasets = {
        "ug": ug_data,
        "pg": pg_data,
        "ss": ss_data
    }
    
    for level, rows in datasets.items():
        level_dir = os.path.join(base_dir, level)
        states_dir = os.path.join(level_dir, "states")
        os.makedirs(states_dir, exist_ok=True)
        
        # Group by state
        by_state = {state: [] for state in states_and_uts}
        
        col_count_set = set()
        seat_count = 0
        quota_set = set()
        type_set = set()
        course_set = set()
        
        for r in rows:
            state = r['state']
            if state not in by_state:
                print(f"Warning: Canonical state not found for {state}")
                continue
            by_state[state].append(r)
            
            # Stats aggregation
            col_count_set.add(r['college_id'])
            seat_count += r['seats']
            quota_set.add(r['quota_type'])
            type_set.add(r['college_type'])
            course_set.add(r['course'])
            
        # Write state-specific JSON files
        for state, state_rows in by_state.items():
            state_filename = f"{state.lower().replace(' ', '_').replace('&', 'and')}.json"
            with open(os.path.join(states_dir, state_filename), "w") as f:
                json.dump(state_rows, f, indent=2)
                
        # Write aggregate all.json file for faster loading
        with open(os.path.join(level_dir, "all.json"), "w") as f:
            json.dump(rows, f, indent=2)
                
        # Write summary.json
        summary = {
            "totalColleges": len(col_count_set),
            "totalSeats": seat_count,
            "states": sorted(states_and_uts),
            "courses": sorted(list(course_set)),
            "quotas": sorted(list(quota_set)),
            "types": sorted(list(type_set))
        }
        
        with open(os.path.join(level_dir, "summary.json"), "w") as f:
            json.dump(summary, f, indent=2)
            
        print(f"Compiled {level.upper()}: {len(col_count_set)} colleges, {seat_count} seats.")
        
    print("Database rebuild from NMC-data PDF JSONs complete!")

if __name__ == "__main__":
    main()
