import json
import re
import os
import csv
import io
from datetime import date

def load_data():
    with open('public/data/ug/all.json', 'r', encoding='utf-8') as f:
        ug_all = json.load(f)

    with open('colleges-list/colleges-list.json', 'r', encoding='utf-8') as f:
        col_list = json.load(f)

    with open('aiq-cutoff-data/mbbs_cutoff_master.json', 'r', encoding='utf-8') as f:
        cutoff_master = json.load(f)

    return ug_all, col_list, cutoff_master

STATE_NORM = {
    'delhi (nct)': 'Delhi', 'delhi': 'Delhi', 'ncr delhi': 'Delhi',
    'andaman and nicobar islands': 'Andaman and Nicobar Islands', 'andaman & nicobar': 'Andaman and Nicobar Islands',
    'dadra & nagar haveli': 'Dadra and Nagar Haveli and Daman and Diu',
    'dadra and nagar haveli': 'Dadra and Nagar Haveli and Daman and Diu',
    'dadra and nagar haveli and daman and diu': 'Dadra and Nagar Haveli and Daman and Diu',
    'daman and diu': 'Dadra and Nagar Haveli and Daman and Diu',
    'jammu and kashmir': 'Jammu and Kashmir', 'jammu & kashmir': 'Jammu and Kashmir',
    'orissa': 'Odisha', 'pondicherry': 'Puducherry', 'u.p.': 'Uttar Pradesh', 'm.p.': 'Madhya Pradesh',
    'chhattisgarh': 'Chhattisgarh', 'chhatisgarh': 'Chhattisgarh', 'karnataka': 'Karnataka',
    'kerala': 'Kerala', 'tamil nadu': 'Tamil Nadu', 'maharashtra': 'Maharashtra',
    'gujarat': 'Gujarat', 'rajasthan': 'Rajasthan', 'punjab': 'Punjab', 'haryana': 'Haryana',
    'bihar': 'Bihar', 'jharkhand': 'Jharkhand', 'west bengal': 'West Bengal', 'assam': 'Assam',
    'odisha': 'Odisha', 'telangana': 'Telangana', 'andhra pradesh': 'Andhra Pradesh',
    'himachal pradesh': 'Himachal Pradesh', 'uttarakhand': 'Uttarakhand', 'tripura': 'Tripura',
    'meghalaya': 'Meghalaya', 'manipur': 'Manipur', 'mizoram': 'Mizoram', 'nagaland': 'Nagaland',
    'arunachal pradesh': 'Arunachal Pradesh', 'sikkim': 'Sikkim', 'goa': 'Goa',
    'puducherry': 'Puducherry', 'chandigarh': 'Chandigarh'
}

STOP_WORDS = {
    'government', 'govt', 'gmc', 'medical', 'college', 'hospital', 'institute', 
    'institutes', 'sciences', 'research', 'centre', 'center', 'and', 'dr', 
    'shri', 'society', 'societys', 'trust', 'memorial', 'of', 'for', 'at', 
    'in', 'near', 'post', 'dist', 'district', 'road', 'campus', 'new', 'no', 
    'st', 'nd', 'rd', 'th', 'pin', 'pincode', 'india'
}
for s in STATE_NORM.keys():
    for w in re.split(r'[^a-z0-9]', s.lower()):
        if len(w) > 1:
            STOP_WORDS.add(w)

def norm_state(st):
    if not st:
        return ''
    s = str(st).strip().lower()
    return STATE_NORM.get(s, st.strip().title())

def get_mcc_state(name, pincode):
    low = name.lower()
    for raw_st, nst in STATE_NORM.items():
        if raw_st in low:
            return nst
    if pincode and len(pincode) == 6:
        p2 = int(pincode[:2])
        if p2 == 11: return 'Delhi'
        if p2 in (12, 13): return 'Haryana'
        if p2 in (14, 15): return 'Punjab'
        if p2 == 16: return 'Chandigarh'
        if p2 == 17: return 'Himachal Pradesh'
        if p2 in (18, 19): return 'Jammu and Kashmir'
        if p2 in range(20, 29):
            if any(w in low for w in ['uttarakhand', 'dehradun', 'haldwani', 'rishikesh', 'srinagar garhwal', 'almora']):
                return 'Uttarakhand'
            return 'Uttar Pradesh'
        if p2 in range(30, 35): return 'Rajasthan'
        if p2 in range(36, 40): return 'Gujarat'
        if p2 in range(40, 45): return 'Maharashtra'
        if p2 in range(45, 49):
            if any(w in low for w in ['raipur', 'bilaspur', 'durg', 'raigarh', 'jagdalpur', 'ambikapur', 'korba', 'kanker', 'rajnandgaon']):
                return 'Chhattisgarh'
            return 'Madhya Pradesh'
        if p2 in range(50, 54):
            if any(w in low for w in ['hyderabad', 'warangal', 'karimnagar', 'nizamabad', 'khammam', 'mahabubnagar', 'nalgonda', 'bibinagar', 'siddipet', 'suryapet', 'ramagundam', 'sangareddy']):
                return 'Telangana'
            return 'Andhra Pradesh'
        if p2 in range(56, 60): return 'Karnataka'
        if p2 in range(60, 65):
            if any(w in low for w in ['puducherry', 'karaikal']): return 'Puducherry'
            return 'Tamil Nadu'
        if p2 in range(67, 70): return 'Kerala'
        if p2 in range(70, 75): return 'West Bengal'
        if p2 in range(75, 78): return 'Odisha'
        if p2 == 78: return 'Assam'
        if p2 == 79:
            if 'agartala' in low or 'tripura' in low: return 'Tripura'
            if 'imphal' in low or 'manipur' in low: return 'Manipur'
            if 'shillong' in low or 'meghalaya' in low: return 'Meghalaya'
            if 'aizawl' in low or 'mizoram' in low: return 'Mizoram'
            if 'kohima' in low or 'nagaland' in low: return 'Nagaland'
            if 'naharlagun' in low or 'arunachal' in low: return 'Arunachal Pradesh'
            if 'gangtok' in low or 'sikkim' in low: return 'Sikkim'
        if p2 in range(80, 86):
            if any(w in low for w in ['ranchi', 'jamshedpur', 'dhanbad', 'deoghar', 'dumka', 'hazaribagh', 'chaibasa', 'palamu']):
                return 'Jharkhand'
            return 'Bihar'
    return ''

def clean_tokens(name):
    name = str(name).lower()
    name = re.sub(r'[^a-z0-9\s]', ' ', name)
    tokens = [w for w in name.split() if w not in STOP_WORDS and len(w) > 1]
    return set(tokens)

def merge_cutoff_records(records):
    if not records:
        return {}
    if len(records) == 1:
        return records[0]

    merged = {}
    for k in ['college_name', 'quota', 'category', 'course']:
        if k in records[0]:
            merged[k] = records[0][k]

    def clean_val(val):
        if val is None or str(val).strip() in ('-', '---', ''):
            return None
        try:
            return int(float(str(val).replace(',', '').strip()))
        except:
            return str(val).strip()

    # Merge rounds
    for rnd in ['r1', 'r2', 'r3']:
        open_ranks = []
        close_ranks = []
        total_allotted = 0
        for r in records:
            o = clean_val(r.get(f'{rnd}_opening_rank'))
            c = clean_val(r.get(f'{rnd}_closing_rank'))
            a = clean_val(r.get(f'{rnd}_total_allotted'))
            if isinstance(o, int): open_ranks.append(o)
            if isinstance(c, int): close_ranks.append(c)
            if isinstance(a, int): total_allotted += a
        merged[f'{rnd}_opening_rank'] = min(open_ranks) if open_ranks else '-'
        merged[f'{rnd}_closing_rank'] = max(close_ranks) if close_ranks else '-'
        merged[f'{rnd}_total_allotted'] = total_allotted

    # Merge final
    final_opens = []
    final_closes = []
    final_seats = 0
    for r in records:
        o = clean_val(r.get('final_opening_rank'))
        c = clean_val(r.get('final_closing_rank'))
        s = clean_val(r.get('final_total_seats'))
        if isinstance(o, int): final_opens.append(o)
        if isinstance(c, int): final_closes.append(c)
        if isinstance(s, int): final_seats += s
    merged['final_opening_rank'] = min(final_opens) if final_opens else '-'
    merged['final_closing_rank'] = max(final_closes) if final_closes else '-'
    merged['final_total_seats'] = final_seats
    
    # Carry over matched_college_name if present
    for r in records:
        if r.get('matched_college_name'):
            merged['matched_college_name'] = r['matched_college_name']
            break

    return merged

EXACT_ALIAS_MAP = {
    # West Bengal
    "BURDWAN MEDICAL COLLEGE": "ug_wb003g1",
    "Government Medical College & Hospital, Jalpaiguri": "ug_wb019g1",
    "Tamralipto Government Medical College": "ug_wb040g1",
    "Prafulla Chandra Sen Government Medical College": "ug_wb031g1",
    "Barasat Government Medical College": "ug_wb002g1",
    "Jhargram Government Medical College": "ug_wb020g1",
    "Sarat Chandra Chattopadhyay Government Medical College": "ug_wb038g1",
    "ESIC PGIMSR, Joka": "ug_wb010g1",
    "Diamond Harbour Govt Medical College": "ug_wb008g1",
    
    # Tamil Nadu
    "VELS MEDICAL COLLEGE": "ug_tn076p3",
    "Govt. Medical College Karur": "ug_tn020g1",
    "COIMBATORE MEDICAL COLLEGE": "ug_tn009g1",
    "Government Medical College and ESIC Hospital, Coimbatore": "ug_tn016g1",
    "Meenakshi Medical College Hospital and Research Institute": "ug_tn048p3",
    
    # Karnataka
    "CHIKKABALLAPURA INSTITUTE OF MEDICAL SCIENCES": "ug_ka012g1",
    
    # Assam
    "Lakhimpur Medical College": "ug_as009g1",
    "Government Medical College, Kokrajhar": "ug_as008g1",
    "Nalbari Medical College": "ug_as011g1",
    "Nagaon Medical College": "ug_as010g1",
    
    # Telangana
    "Govt Medical College Nalgonda": "ug_ts032g1",
    "Govt. Medical College, Suryapet": "ug_ts042g1",
    "GOVERNMENT MEDICAL COLLEGE, MAHABUBABAD": "ug_ts026g1",
    "Government Medical College, Bhadradri Kothagudem": "ug_ts019g1",
    "Government Medical College, Jagtial": "ug_ts020g1",
    "Government Medical College, Nagarkurnool": "ug_ts031g1",
    "Government Medical College, Ramagundam": "ug_ts039g1",
    "Government Medical College, Wanaparthy": "ug_ts043g1",
    "GOVERNMENT MEDICAL COLLEGE, SANGAREDDY": "ug_ts040g1",
    
    # Odisha
    "GOVERNMENT MEDICAL COLLEGE & HOSPITAL, PHULBANI": "ug_od003g1",
    
    # Andhra Pradesh
    "Government Medical College, Machilipatnam": "ug_ap012g1",
    "Government Medical College, Rajamahendravaram": "ug_ap015g1",
    "Government Medical College, Eluru": "ug_ap011g1",
    "Government Medical College, Nandyal": "ug_ap013g1",
    "Government Medical College, Vizianagaram": "ug_ap016g1",
    "Sri Venkateswara Medical College, Tirupati": "ug_ap034g1",
    
    # Uttar Pradesh
    "Baba Kinaram Autonomous State Medical College": "ug_up020g1",
    "Autonomous State Medical College, Hardoi": "ug_up015g1",
    "Autonomous State Medical College, Mirzapur": "ug_up019g1",
    "Autonomous State Medical College, Pratapgarh": "ug_up011g1",
    "Autonomous State Medical College, Siddharthnagar": "ug_up017g1",
    "Autonomous State Medical College, Deoria": "ug_up054g1",
    "Autonomous State Medical College, Ghazipur": "ug_up012g1",
    "Autonomous State Medical College, Fatehpur": "ug_up014g1",
    "Autonomous State Medical College, Jaunpur": "ug_up082g1",
    "Autonomous State Medical College, Etah": "ug_up013g1",
    "Autonomous State Medical College, Kushinagar": "ug_up008g5",
    "Autonomous State Medical College, Lakhimpur Kheri": "ug_up007g5",
    "Autonomous State Medical Collage, Kushinagar": "ug_up008g5",
    "Autonomous State Medical College Society, Mirzapur": "ug_up019g1",
    "INST.OF MED.SCIENCES, BHU": "ug_up043g1",
    "GMC, Azamgarh": "ug_up032g1",
    "Govt Medical College Firozabad": "ug_up035g1",
    "GMC, Shahjhanpur": "ug_up038g1",
    "INST OF PG MED EDU & RESEARCH, KOLKATA": "ug_wb014g1",
    
    # Newly resolved mismatches
    "GOVERNMENT MEDICAL COLLEGE, ANANTNAG J&K": "ug_jk004g1",
    "Govt Medical College Baramati": "ug_mh022g1",
    "M.P. SHAH MEDICAL COLLEGE, JAMNAGAR": "ug_gj031g1",
    "Malla Reddy Institute of Medical Sciences": "ug_ts049p4",
    "Malla Reddy Medical College for Women": "ug_ts050p4",
    "MGM Medical College, Navi Mumbai, MGM Medical College, Plot No. 1-2, Sector 1, Kamothe": "ug_mh061p3",
    "Mahatma Gandhi Missions Medical College, Panvel": "ug_mh063p3",
    "Medinirai Medical College": "ug_jh007g1",
    "S.S. MEDICAL COLLEGE, REWA": "ug_mp030g1",
}

INI_COLLEGES_MAP = {
    "AIIMS Bathinda, Jodhpur Romana near Giani Zail Singh College Mandi Dabwali Road Bathinda, Punjab, 151001": {
        "college_id": "ug_ini_aiims_bathinda",
        "college_name": "AIIMS Bathinda",
        "state": "Punjab",
        "pincode": "151001",
        "city": "Bathinda"
    },
    "AIIMS Bilaspur Changar Palasiyan, Himachal Pradesh, All India Institute of Medical Sciences AIIMS Bilaspur Kothipura BILASPUR Himachal Pradesh 174001, Himachal Pradesh, 174001": {
        "college_id": "ug_ini_aiims_bilaspur",
        "college_name": "AIIMS Bilaspur",
        "state": "Himachal Pradesh",
        "pincode": "174001",
        "city": "Bilaspur"
    },
    "AIIMS Guwahati, PO-CHANGSARI, DISTRICT-KAMRUP, Assam, 781101": {
        "college_id": "ug_ini_aiims_guwahati",
        "college_name": "AIIMS Guwahati",
        "state": "Assam",
        "pincode": "781101",
        "city": "Guwahati"
    },
    "AIIMS Jammu, AIIMS, Vijaypur, Jammu, Jammu and Kashmir, Jammu And Kashmir, 181134": {
        "college_id": "ug_ini_aiims_jammu",
        "college_name": "AIIMS Jammu",
        "state": "Jammu and Kashmir",
        "pincode": "181134",
        "city": "Jammu"
    },
    "AIIMS Mangalagiri, ALL INDIA INSTITUTE OF MEDICAL SCIENCES NEAR TADEPALLI MANGALAGIRI GUNTUR (Dt) ANDHRA PRADESH, Andhra Pradesh, 522503": {
        "college_id": "ug_ini_aiims_mangalagiri",
        "college_name": "AIIMS Mangalagiri",
        "state": "Andhra Pradesh",
        "pincode": "522503",
        "city": "Mangalagiri"
    },
    "AIIMS Rajkot, Admission cell, Academic section, First floor, Academic block, Permanent Campus, AIIMS Rajkot, Khand, Gujarat, 360110": {
        "college_id": "ug_ini_aiims_rajkot",
        "college_name": "AIIMS Rajkot",
        "state": "Gujarat",
        "pincode": "360110",
        "city": "Rajkot"
    },
    "AIIMS, Bhubaneswar, AT - Sijua, POST - DUMUDUMA, BHUBANESWAR-751019, Odisha, 751019": {
        "college_id": "ug_ini_aiims_bhubaneswar",
        "college_name": "AIIMS Bhubaneswar",
        "state": "Odisha",
        "pincode": "751019",
        "city": "Bhubaneswar"
    },
    "AIIMS, Bibi Nagar, Hyderabad, AIIMS Bibinagar (Hyderabad Metropolitan Region) Telangana 508126, Telangana, 508126": {
        "college_id": "ug_ini_aiims_bibinagar",
        "college_name": "AIIMS Bibinagar",
        "state": "Telangana",
        "pincode": "508126",
        "city": "Bibinagar"
    },
    "AIIMS, Deogarh, AIIMS Deoghar Devipur, Jharkhand India, PIN - 814152, Jharkhand, 814152": {
        "college_id": "ug_ini_aiims_deoghar",
        "college_name": "AIIMS Deoghar",
        "state": "Jharkhand",
        "pincode": "814152",
        "city": "Deoghar"
    },
    "AIIMS, Gorakhpur, AIIMS Gorakhpur, Medical College Building, Kunraghat, Gorakhpur, Uttar Pradesh, 273008": {
        "college_id": "ug_ini_aiims_gorakhpur",
        "college_name": "AIIMS Gorakhpur",
        "state": "Uttar Pradesh",
        "pincode": "273008",
        "city": "Gorakhpur"
    },
    "AIIMS, Jodhpur, BASNI PHASE - II, JODHPUR-342005, Rajasthan, 342005": {
        "college_id": "ug_ini_aiims_jodhpur",
        "college_name": "AIIMS Jodhpur",
        "state": "Rajasthan",
        "pincode": "342005",
        "city": "Jodhpur"
    },
    "AIIMS, Kalyani, NH-34 Connector, Basantapur, Saguna, Kalyani, 741245, West Bengal, India, West Bengal, 741245": {
        "college_id": "ug_ini_aiims_kalyani",
        "college_name": "AIIMS Kalyani",
        "state": "West Bengal",
        "pincode": "741245",
        "city": "Kalyani"
    },
    "AIIMS, Madurai, AIIMS MADURAI, Tamil Nadu, 625008": {
        "college_id": "ug_ini_aiims_madurai",
        "college_name": "AIIMS Madurai",
        "state": "Tamil Nadu",
        "pincode": "625008",
        "city": "Madurai"
    },
    "AIIMS, Nagpur, PLOT NO 2 SECTOR 20 MIHAN NAGPUR, Maharashtra, 441108": {
        "college_id": "ug_ini_aiims_nagpur",
        "college_name": "AIIMS Nagpur",
        "state": "Maharashtra",
        "pincode": "441108",
        "city": "Nagpur"
    },
    "AIIMS, New Delhi, AIIMS ANSARI NAGAR EAST AUROBINDO MARG NEW DELHI 110029, Delhi (NCT), 110029": {
        "college_id": "ug_ini_aiims_newdelhi",
        "college_name": "AIIMS New Delhi",
        "state": "Delhi",
        "pincode": "110029",
        "city": "New Delhi"
    },
    "AIIMS, Patna, Phulwarisharif, Patna, Bihar-801507, Bihar, 801507": {
        "college_id": "ug_ini_aiims_patna",
        "college_name": "AIIMS Patna",
        "state": "Bihar",
        "pincode": "801507",
        "city": "Patna"
    },
    "AIIMS, Rai Bareli, All India Institute of Medical Sciences Raebareli, Uttar Pradesh, 229405": {
        "college_id": "ug_ini_aiims_raebareli",
        "college_name": "AIIMS Raebareli",
        "state": "Uttar Pradesh",
        "pincode": "229405",
        "city": "Raebareli"
    },
    "AIIMS, Raipur, Tatibandh, G E Road, Raipur Chhattisgarh, Pin - 492099, Chhattisgarh, 492099": {
        "college_id": "ug_ini_aiims_raipur",
        "college_name": "AIIMS Raipur",
        "state": "Chhattisgarh",
        "pincode": "492099",
        "city": "Raipur"
    },
    "AIIMS, Rishikesh, ALL INDIA INSTITUTE OF MEDICAL SCIENCES, RISHIKESH Uttarakhand - 249203, Uttarakhand, 249203": {
        "college_id": "ug_ini_aiims_rishikesh",
        "college_name": "AIIMS Rishikesh",
        "state": "Uttarakhand",
        "pincode": "249203",
        "city": "Rishikesh"
    },
    "AIIMS-Bhopal, , SAKET NAGAR BHOPAL, Madhya Pradesh, 462020": {
        "college_id": "ug_ini_aiims_bhopal",
        "college_name": "AIIMS Bhopal",
        "state": "Madhya Pradesh",
        "pincode": "462020",
        "city": "Bhopal"
    },
    "JIPMER KARAIKAL, JIPMER Academic Campus, FCI Link Road, Kovilpathu, Karaikal - 609602, Puducherry, 609602": {
        "college_id": "ug_ini_jipmer_karaikal",
        "college_name": "JIPMER Karaikal",
        "state": "Puducherry",
        "pincode": "609602",
        "city": "Karaikal"
    },
    "JIPMER PUDUCHERRY, Dhanvantari Nagar Gorimedu Puducherry, Puducherry, 605006": {
        "college_id": "ug_ini_jipmer_puducherry",
        "college_name": "JIPMER Puducherry",
        "state": "Puducherry",
        "pincode": "605006",
        "city": "Puducherry"
    }
}

def generate_mapping():
    ug_all, col_list, cutoff_master = load_data()

    master_colleges = {}
    for c in ug_all:
        cid = c['college_id']
        if cid not in master_colleges:
            master_colleges[cid] = {
                'college_id': cid,
                'college_name': c['college_name'],
                'state': norm_state(c.get('state')),
                'college_type': c.get('college_type', 'Government'),
                'counseling_route': c.get('counseling_route', 'STATE'),
                'seats': c.get('seats', 0),
                'cutoffs_raw': []
            }

    nmc_by_code = {}
    for item in col_list:
        code = item.get('collegeCode')
        if code:
            norm_code = 'ug_' + code.lower().replace('/', '')
            nmc_by_code[norm_code] = item

    for cid, col in master_colleges.items():
        if cid in nmc_by_code:
            nmc = nmc_by_code[cid]
            col['pincode'] = str(nmc.get('pincode', '')).strip()
            col['city'] = str(nmc.get('city', '')).strip()
            col['address'] = str(nmc.get('address', '')).strip()
            col['nmc_name'] = str(nmc.get('collegeName', '')).strip()
            col['college_code'] = str(nmc.get('collegeCode', '')).strip()
        else:
            col['pincode'] = ''
            col['city'] = ''
            col['address'] = ''
            col['nmc_name'] = ''
            col['college_code'] = ''

    # Dynamically inject INI Colleges for Cutoff Explorer ONLY
    for raw_name, info in INI_COLLEGES_MAP.items():
        cid = info['college_id']
        master_colleges[cid] = {
            'college_id': cid,
            'college_name': info['college_name'],
            'state': info['state'],
            'college_type': 'Government',
            'counseling_route': 'ALL_INDIA',
            'seats': 0,
            'pincode': info['pincode'],
            'city': info['city'],
            'address': raw_name,
            'nmc_name': info['college_name'],
            'college_code': cid.upper().replace('UG_', ''),
            'cutoffs_raw': []
        }

    mbbs_cutoffs_raw = [m for m in cutoff_master if m.get('course') == 'MBBS']

    # Merge duplicate records by (college_name, quota, category, course)
    grouped = {}
    for m in mbbs_cutoffs_raw:
        key = (m['college_name'], m.get('quota', ''), m.get('category', ''), m.get('course', ''))
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(m)

    mbbs_cutoffs = [merge_cutoff_records(records) for records in grouped.values()]

    mcc_by_raw_name = {}
    for m in mbbs_cutoffs:
        raw_name = m['college_name']
        if raw_name not in mcc_by_raw_name:
            mcc_by_raw_name[raw_name] = []
        mcc_by_raw_name[raw_name].append(m)

    raw_mcc_names = list(mcc_by_raw_name.keys())

    master_by_state = {}
    for cid, col in master_colleges.items():
        st = col['state']
        if st not in master_by_state:
            master_by_state[st] = []
        master_by_state[st].append(col)

    mcc_to_master = {}
    mcc_record_mapped_counts = {raw_name: 0 for raw_name in raw_mcc_names}
    ambiguous_rejected = []
    duplicate_mappings_count = 0

    for raw_name in raw_mcc_names:
        if raw_name in INI_COLLEGES_MAP:
            mcc_to_master[raw_name] = INI_COLLEGES_MAP[raw_name]['college_id']
            mcc_record_mapped_counts[raw_name] += 1
            continue

        override_cid = None
        for alias_key, target_cid in EXACT_ALIAS_MAP.items():
            if alias_key.lower() in raw_name.lower():
                if target_cid in master_colleges:
                    override_cid = target_cid
                    break
        
        if override_cid:
            mcc_to_master[raw_name] = override_cid
            mcc_record_mapped_counts[raw_name] += 1
            continue

        pin_match = re.search(r'\b(\d{6})\b', raw_name)
        mcc_pin = pin_match.group(1) if pin_match else None
        mcc_st = get_mcc_state(raw_name, mcc_pin)

        is_aiims = 'aiims' in raw_name.lower() or 'all india institute of medical sciences' in raw_name.lower()
        is_jipmer = 'jipmer' in raw_name.lower() or 'jawaharlal institute of postgraduate' in raw_name.lower()

        candidates = master_by_state.get(mcc_st, [])
        if is_aiims:
            candidates = [c for c in candidates if 'aiims' in c['college_name'].lower() or 'all india institute of medical sciences' in c['college_name'].lower()]
        elif is_jipmer:
            candidates = [c for c in candidates if 'jipmer' in c['college_name'].lower() or 'jawaharlal institute' in c['college_name'].lower()]
        else:
            candidates = [c for c in candidates if not ('aiims' in c['college_name'].lower() or 'jipmer' in c['college_name'].lower())]

        mcc_tokens = clean_tokens(raw_name)
        matched_cand = None

        if mcc_pin and not is_aiims and not is_jipmer:
            pin_matches = [c for c in candidates if c['pincode'] == mcc_pin]
            if len(pin_matches) == 1:
                matched_cand = pin_matches[0]
            elif len(pin_matches) > 1:
                best_score = -1
                best_cands = []
                for c in pin_matches:
                    c_toks = clean_tokens(c['college_name']) | clean_tokens(c['nmc_name'])
                    overlap = len(mcc_tokens & c_toks)
                    if overlap > best_score:
                        best_score = overlap
                        best_cands = [c]
                    elif overlap == best_score:
                        best_cands.append(c)
                if len(best_cands) == 1 and best_score > 0:
                    matched_cand = best_cands[0]

        if not matched_cand and candidates:
            best_score = -1
            best_cands = []
            for c in candidates:
                c_toks = clean_tokens(c['college_name']) | clean_tokens(c['nmc_name'])
                overlap = len(mcc_tokens & c_toks)
                if overlap > best_score:
                    best_score = overlap
                    best_cands = [c]
                elif overlap == best_score:
                    best_cands.append(c)
            if len(best_cands) == 1 and best_score >= 1:
                matched_cand = best_cands[0]
            elif len(best_cands) > 1 and best_score >= 2:
                ambiguous_rejected.append({
                    'mcc_raw': raw_name,
                    'candidates': [c['college_name'] for c in best_cands]
                })

        if matched_cand:
            mcc_to_master[raw_name] = matched_cand['college_id']
            mcc_record_mapped_counts[raw_name] += 1

    master_matched_mcc_names = {}
    for raw_name, cid in mcc_to_master.items():
        cutoffs = mcc_by_raw_name[raw_name]
        master_colleges[cid]['cutoffs_raw'].extend(cutoffs)
        if cid not in master_matched_mcc_names:
            master_matched_mcc_names[cid] = set()
        master_matched_mcc_names[cid].add(raw_name)

    matched_master_count = 0
    new_colleges_count = 0
    non_aiq_colleges_count = 0

    final_output = []
    for cid, col in master_colleges.items():
        has_cutoffs = len(col['cutoffs_raw']) > 0
        c_route = col.get('counseling_route', '')
        c_type = col.get('college_type', '')

        if has_cutoffs:
            col['matched_in_aiq'] = True
            col['mcc_status'] = 'Matched'
            col['aiq_college_name'] = list(master_matched_mcc_names[cid])[0] if cid in master_matched_mcc_names else None
            matched_master_count += 1
        else:
            col['matched_in_aiq'] = False
            col['aiq_college_name'] = None
            if c_route == 'ALL_INDIA' or c_type in ('Government', 'Deemed'):
                col['mcc_status'] = 'New'
                new_colleges_count += 1
            else:
                col['mcc_status'] = 'Non AIQ'
                non_aiq_colleges_count += 1

        # Group cutoffs by key (quota, category, course) and merge them
        grouped_cutoffs = {}
        for c in col['cutoffs_raw']:
            key = f"{c.get('quota')}_{c.get('category')}_{c.get('course')}"
            if key not in grouped_cutoffs:
                grouped_cutoffs[key] = []
            grouped_cutoffs[key].append(c)
        
        col['aiq_cutoffs_raw'] = [merge_cutoff_records(records) for records in grouped_cutoffs.values()]
        del col['cutoffs_raw']

        final_output.append(col)

    # --- Output 1: public/data/ug_colleges_aiq_mapping.json (website) ---
    output_path = 'public/data/ug_colleges_aiq_mapping.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)

    # --- Output 2: mapping-to-nexdoc JSON files ---
    # Build a simpler mapping record (without mcc_status, with aiq_cutoffs_raw)
    mapping_nexdoc = []
    for col in final_output:
        mapping_nexdoc.append({
            'college_id': col['college_id'],
            'college_name': col['college_name'],
            'state': col['state'],
            'city': col.get('city', ''),
            'college_type': col.get('college_type', ''),
            'college_code': col.get('college_code', ''),
            'counseling_route': col.get('counseling_route', ''),
            'pincode': col.get('pincode', ''),
            'matched_in_aiq': col.get('matched_in_aiq', False),
            'aiq_college_name': col.get('aiq_college_name'),
            'aiq_cutoffs_raw': col.get('aiq_cutoffs_raw', []),
        })

    for nexdoc_dir in ['aiq-cutoff-data/mapping-to-nexdoc', 'aiq-counselling-data/mapping-to-nexdoc']:
        os.makedirs(nexdoc_dir, exist_ok=True)
        nexdoc_path = os.path.join(nexdoc_dir, 'ug_colleges_aiq_mapping.json')
        with open(nexdoc_path, 'w', encoding='utf-8') as f:
            json.dump(mapping_nexdoc, f, indent=2, ensure_ascii=False)

    # --- Output 3: mapping-to-nexdoc CSV (aiq-cutoff-data only) ---
    csv_output_path = 'aiq-cutoff-data/mapping-to-nexdoc/ug_colleges_aiq_mapping.csv'
    csv_fields = [
        'college_id', 'college_name', 'state', 'college_type', 'college_code',
        'pincode', 'city', 'matched_in_aiq', 'match_status', 'aiq_college_name',
        'aiq_records_count', 'available_quotas',
        'open_r1_opening', 'open_r1_closing', 'open_r2_opening', 'open_r2_closing',
        'open_r3_opening', 'open_r3_closing', 'open_final_opening', 'open_final_closing',
        'open_pwd_final_opening', 'open_pwd_final_closing',
        'obc_r1_opening', 'obc_r1_closing', 'obc_r2_opening', 'obc_r2_closing',
        'obc_r3_opening', 'obc_r3_closing', 'obc_final_opening', 'obc_final_closing',
        'obc_pwd_final_opening', 'obc_pwd_final_closing',
        'ews_r1_opening', 'ews_r1_closing', 'ews_r2_opening', 'ews_r2_closing',
        'ews_r3_opening', 'ews_r3_closing', 'ews_final_opening', 'ews_final_closing',
        'ews_pwd_final_opening', 'ews_pwd_final_closing',
        'sc_r1_opening', 'sc_r1_closing', 'sc_r2_opening', 'sc_r2_closing',
        'sc_r3_opening', 'sc_r3_closing', 'sc_final_opening', 'sc_final_closing',
        'sc_pwd_final_opening', 'sc_pwd_final_closing',
        'st_r1_opening', 'st_r1_closing', 'st_r2_opening', 'st_r2_closing',
        'st_r3_opening', 'st_r3_closing', 'st_final_opening', 'st_final_closing',
        'st_pwd_final_opening', 'st_pwd_final_closing',
        'nri_final_opening', 'nri_final_closing',
    ]

    csv_buf = io.StringIO()
    writer = csv.DictWriter(csv_buf, fieldnames=csv_fields, lineterminator='\r\n', extrasaction='ignore')
    writer.writeheader()

    # Main categories get r1/r2/r3/final columns; PwD categories get final-only
    main_categories = {'Open': 'open', 'OBC': 'obc', 'EWS': 'ews', 'SC': 'sc', 'ST': 'st'}
    pwd_categories = {'Open PwD': 'open_pwd', 'OBC PwD': 'obc_pwd', 'EWS PwD': 'ews_pwd', 'SC PwD': 'sc_pwd', 'ST PwD': 'st_pwd'}

    for col in final_output:
        cutoffs = col.get('aiq_cutoffs_raw', [])
        quotas_set = set(c.get('quota', '') for c in cutoffs if c.get('quota'))

        row = {
            'college_id': col['college_id'],
            'college_name': col['college_name'],
            'state': col['state'],
            'college_type': col.get('college_type', ''),
            'college_code': col.get('college_code', ''),
            'pincode': col.get('pincode', ''),
            'city': col.get('city', ''),
            'matched_in_aiq': str(col.get('matched_in_aiq', False)).upper(),
            'match_status': 'VERIFIED_MATCH' if col.get('matched_in_aiq') else 'NOT_IN_AIQ',
            'aiq_college_name': col.get('aiq_college_name', ''),
            'aiq_records_count': len(cutoffs),
            'available_quotas': ';'.join(sorted(quotas_set)),
        }

        # Main categories: all round columns
        for cat_label, prefix in main_categories.items():
            cat_cutoff = next((c for c in cutoffs if c.get('category') == cat_label), None)
            if cat_cutoff:
                for rnd in ['r1', 'r2', 'r3']:
                    row[f'{prefix}_{rnd}_opening'] = cat_cutoff.get(f'{rnd}_opening_rank', '-')
                    row[f'{prefix}_{rnd}_closing'] = cat_cutoff.get(f'{rnd}_closing_rank', '-')
                row[f'{prefix}_final_opening'] = cat_cutoff.get('final_opening_rank', '-')
                row[f'{prefix}_final_closing'] = cat_cutoff.get('final_closing_rank', '-')
            else:
                for rnd in ['r1', 'r2', 'r3']:
                    row[f'{prefix}_{rnd}_opening'] = '-'
                    row[f'{prefix}_{rnd}_closing'] = '-'
                row[f'{prefix}_final_opening'] = '-'
                row[f'{prefix}_final_closing'] = '-'

        # PwD categories: final-only columns
        for cat_label, prefix in pwd_categories.items():
            cat_cutoff = next((c for c in cutoffs if c.get('category') == cat_label), None)
            if cat_cutoff:
                row[f'{prefix}_final_opening'] = cat_cutoff.get('final_opening_rank', '-')
                row[f'{prefix}_final_closing'] = cat_cutoff.get('final_closing_rank', '-')
            else:
                row[f'{prefix}_final_opening'] = '-'
                row[f'{prefix}_final_closing'] = '-'

        # NRI
        nri_cutoff = next((c for c in cutoffs if c.get('category') == 'Open' and 'non-resident' in c.get('quota', '').lower()), None)
        if nri_cutoff:
            row['nri_final_opening'] = nri_cutoff.get('final_opening_rank', '-')
            row['nri_final_closing'] = nri_cutoff.get('final_closing_rank', '-')
        else:
            row['nri_final_opening'] = '-'
            row['nri_final_closing'] = '-'

        writer.writerow(row)

    with open(csv_output_path, 'w', encoding='utf-8', newline='') as f:
        f.write(csv_buf.getvalue())

    # --- Output 4: public/data/aiq_cutoffs_master.json ---
    # Flat list of all MBBS cutoff records with matched college name
    master_cid_to_name = {}
    for col in final_output:
        if col.get('matched_in_aiq'):
            aiq_name = col.get('aiq_college_name', '')
            master_cid_to_name[aiq_name] = col['college_name']

    cutoffs_master_output = []
    seen_combos = set()
    for m in mbbs_cutoffs:
        raw_name = m['college_name']
        matched_name = master_cid_to_name.get(raw_name, None)

        # Deduplicate by college_name + quota + category + course
        combo_key = f"{raw_name}|{m.get('quota')}|{m.get('category')}|{m.get('course')}"
        if combo_key in seen_combos:
            continue
        seen_combos.add(combo_key)

        record = dict(m)
        record['matched_college_name'] = matched_name
        cutoffs_master_output.append(record)

    # Sort by matched_college_name (matched first), then by college_name
    cutoffs_master_output.sort(key=lambda r: (
        0 if r.get('matched_college_name') else 1,
        r.get('matched_college_name', ''),
        r.get('college_name', ''),
        r.get('quota', ''),
        r.get('category', ''),
    ))

    with open('public/data/aiq_cutoffs_master.json', 'w', encoding='utf-8') as f:
        json.dump(cutoffs_master_output, f, indent=2, ensure_ascii=False)

    # --- Output 5: public/data/aiq_cutoffs_summary.json ---
    all_categories = sorted(set(m.get('category', '') for m in cutoffs_master_output if m.get('category')))
    all_quotas = sorted(set(m.get('quota', '') for m in cutoffs_master_output if m.get('quota')))
    matched_colleges_in_master = set(m.get('matched_college_name') for m in cutoffs_master_output if m.get('matched_college_name'))

    summary = {
        'total_records': len(cutoffs_master_output),
        'total_colleges': len(matched_colleges_in_master),
        'categories': all_categories,
        'quotas': all_quotas,
        'lastUpdated': date.today().isoformat(),
    }

    with open('public/data/aiq_cutoffs_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    unmatched_mcc_records_count = len(raw_mcc_names) - len(mcc_to_master)
    multi_mapped_mcc_count = sum(1 for cnt in mcc_record_mapped_counts.values() if cnt > 1)

    print("Mapping generated successfully.")
    print(f"Total Master UG Colleges: {len(master_colleges)}")
    print(f"Successfully Matched MCC Colleges: {matched_master_count}")
    print(f"Unmatched MCC Records: {unmatched_mcc_records_count}")
    print(f"New Colleges: {new_colleges_count}")
    print(f"Non AIQ Colleges: {non_aiq_colleges_count}")
    print(f"Ambiguous / Rejected Mappings: {len(ambiguous_rejected)}")
    print(f"Duplicate Mappings: {duplicate_mappings_count}")
    print(f"MCC Records Mapped to Multiple Master Colleges: {multi_mapped_mcc_count}")
    print(f"AIQ Cutoffs Master Records: {len(cutoffs_master_output)}")
    print(f"AIQ Cutoffs Master Matched Colleges: {len(matched_colleges_in_master)}")
    print()
    print("Output files written:")
    print(f"  {output_path}")
    print(f"  aiq-cutoff-data/mapping-to-nexdoc/ug_colleges_aiq_mapping.json")
    print(f"  aiq-cutoff-data/mapping-to-nexdoc/ug_colleges_aiq_mapping.csv")
    print(f"  aiq-counselling-data/mapping-to-nexdoc/ug_colleges_aiq_mapping.json")
    print(f"  public/data/aiq_cutoffs_master.json")
    print(f"  public/data/aiq_cutoffs_summary.json")

if __name__ == '__main__':
    generate_mapping()
