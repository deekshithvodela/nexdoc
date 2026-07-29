import json
import re
import os

def slugify(name):
    name = str(name).lower()
    name = re.sub(r'[^a-z0-9\s]', '', name)
    name = re.sub(r'\s+', '_', name).strip()
    return name

def clean_name_for_match(name):
    name = str(name).lower()
    name = re.sub(r'[^a-z0-9]', '', name)
    # Remove common filler words
    for word in ['government', 'govt', 'gmc', 'medicalcollege', 'medicalsciences', 'hospital', 'institute', 'instt', 'research', 'centre', 'center', 'and']:
        name = name.replace(word, '')
    return name

def main():
    colleges_list_path = "colleges-list/colleges-list.json"
    if not os.path.exists(colleges_list_path):
        print("Error: colleges-list.json not found!")
        return

    with open(colleges_list_path, "r", encoding="utf-8") as f:
        colleges_details = json.load(f)

    # Index details by slugified collegeCode and cleaned collegeName
    by_code = {}
    by_name = {}
    
    for item in colleges_details:
        code = item.get("collegeCode")
        if code:
            by_code[slugify(code)] = item
            
        name = item.get("collegeName")
        if name:
            by_name[clean_name_for_match(name)] = item

    matched = {}
    unmatched = []

    # Let's load all our compiled college IDs and names
    all_colleges = {}
    for level in ["ug", "pg", "ss"]:
        if level == "ug":
            all_path = "public/data/ug_colleges_aiq_mapping.json"
        else:
            all_path = f"public/data/{level}/all.json"
        if not os.path.exists(all_path):
            continue
        with open(all_path, "r", encoding="utf-8") as f:
            rows = json.load(f)
            for row in rows:
                cid = row["college_id"]
                all_colleges[cid] = {
                    "college_id": cid,
                    "college_name": row["college_name"],
                    "state": row["state"],
                    "college_type": row["college_type"]
                }

    print(f"Total unique colleges in seats database: {len(all_colleges)}")

    for cid, col in all_colleges.items():
        if cid.startswith("ug_ini_"):
            matched[cid] = {
                "collegeName": col["college_name"],
                "collegeCode": cid.upper().replace("UG_", "").replace("_", "/"),
                "address": col.get("address", col["college_name"]),
                "city": col.get("city", ""),
                "pincode": col.get("pincode", ""),
                "website": "N/A",
                "email": "N/A",
                "telephone": "N/A",
                "fax": "N/A",
                "yearOfInc": "N/A",
                "universityName": "Institute of National Importance",
                "managementText": "Government",
                "status": "Recognized",
                "statusText": "Institute of National Importance (INI) college.",
                "deanName": "N/A",
                "deanDesignation": "Director",
                "contacts": []
            }
            continue

        # Match 1: By slugified code (for UG IDs which contain the code)
        code_slug = cid.replace("ug_", "")
        if code_slug in by_code:
            matched[cid] = by_code[code_slug]
            continue

        # Match 2: By exact cleaned name
        cleaned_target = clean_name_for_match(col["college_name"])
        if cleaned_target in by_name:
            matched[cid] = by_name[cleaned_target]
            continue

        # Match 3: Substring check on names
        found = False
        for name_clean, item in by_name.items():
            if name_clean in cleaned_target or cleaned_target in name_clean:
                # Also verify state match to avoid false positives
                state_target = col["state"].lower().replace("and", "&")
                state_item = str(item.get("stateName", "")).lower().replace("and", "&")
                if state_target in state_item or state_item in state_target or col["state"].lower()[:5] == str(item.get("stateName", "")).lower()[:5]:
                    matched[cid] = item
                    found = True
                    break
        
        if found:
            continue

        unmatched.append(col)

    print(f"Matched: {len(matched)}")
    print(f"Unmatched: {len(unmatched)}")
    
    # Save the matched details to public/data/colleges_details.json
    output_details = {}
    for cid, item in matched.items():
        # Clean up contacts and structure the object nicely for frontend
        contacts = []
        for c in item.get("contacts", []):
            if c:
                name_str = str(c.get("name") or "").strip()
                desg_str = str(c.get("desgination") or c.get("designation") or "").strip()
                email_str = str(c.get("email") or "").strip()
                mobile_str = str(c.get("mobileNo") or c.get("mobile") or "").strip()
                office_str = str(c.get("officePh") or "").strip()
                
                if name_str or email_str or mobile_str:
                    contacts.append({
                        "name": name_str,
                        "designation": desg_str,
                        "email": email_str,
                        "mobile": mobile_str,
                        "office": office_str
                    })

        output_details[cid] = {
            "college_name": str(item.get("collegeName") or "").strip(),
            "college_code": str(item.get("collegeCode") or "").strip(),
            "address": str(item.get("address") or "").strip(),
            "city": str(item.get("city") or "").strip(),
            "pincode": str(item.get("pincode") or "").strip(),
            "website": str(item.get("website") or "").strip(),
            "email": str(item.get("email") or "").strip(),
            "telephone": str(item.get("telephone") or "").strip(),
            "fax": str(item.get("fax") or "").strip(),
            "year_of_inc": str(item.get("yearOfInc") or "").strip(),
            "university": str(item.get("universityName") or "").strip(),
            "management": str(item.get("managementText") or item.get("managementupdate") or "").strip(),
            "status": str(item.get("status") or "").strip(),
            "status_text": str(item.get("statusText") or "").strip(),
            "dean_name": str(item.get("deanName") or "").strip() or (contacts[0]["name"] if contacts else ""),
            "dean_designation": str(item.get("deanDesignation") or "").strip() or (contacts[0]["designation"] if contacts else ""),
            "contacts": contacts
        }

    # For unmatched, we can provide basic details from our database
    for col in unmatched:
        cid = col["college_id"]
        output_details[cid] = {
            "college_name": col["college_name"],
            "college_code": "",
            "address": "Address details not available in primary registry.",
            "city": "",
            "pincode": "",
            "website": "",
            "email": "",
            "telephone": "",
            "fax": "",
            "year_of_inc": "",
            "university": "",
            "management": col["college_type"],
            "status": "",
            "status_text": "",
            "dean_name": "",
            "dean_designation": "",
            "contacts": []
        }

    os.makedirs("public/data", exist_ok=True)
    with open("public/data/colleges_details.json", "w", encoding="utf-8") as f:
        json.dump(output_details, f, indent=2, ensure_ascii=False)
    print("Saved public/data/colleges_details.json")

if __name__ == "__main__":
    main()
