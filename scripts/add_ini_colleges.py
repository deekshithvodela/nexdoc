import json
import os
import re

def main():
    ug_all_path = "public/data/ug/all.json"
    if not os.path.exists(ug_all_path):
        print("Error: all.json not found!")
        return

    with open(ug_all_path, "r", encoding="utf-8") as f:
        rows = json.load(f)

    # Remove any existing INI records to avoid duplicates if run multiple times
    rows = [r for r in rows if not r.get("college_id", "").startswith("ug_ini_")]

    # List of central INI colleges to add
    ini_records = [
        # Punjab
        {
            "college_id": "ug_ini_aiims_bathinda",
            "college_name": "AIIMS Bathinda",
            "college_type": "Government",
            "state": "Punjab",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 100,
            "seats_prev": 100,
            "seats_inc": 0
        },
        # Himachal Pradesh
        {
            "college_id": "ug_ini_aiims_bilaspur",
            "college_name": "AIIMS Bilaspur",
            "college_type": "Government",
            "state": "Himachal Pradesh",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 100,
            "seats_prev": 100,
            "seats_inc": 0
        },
        # Assam
        {
            "college_id": "ug_ini_aiims_guwahati",
            "college_name": "AIIMS Guwahati",
            "college_type": "Government",
            "state": "Assam",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 100,
            "seats_prev": 100,
            "seats_inc": 0
        },
        # Jammu and Kashmir
        {
            "college_id": "ug_ini_aiims_jammu",
            "college_name": "AIIMS Jammu",
            "college_type": "Government",
            "state": "Jammu and Kashmir",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 100,
            "seats_prev": 100,
            "seats_inc": 0
        },
        # Andhra Pradesh
        {
            "college_id": "ug_ini_aiims_mangalagiri",
            "college_name": "AIIMS Mangalagiri",
            "college_type": "Government",
            "state": "Andhra Pradesh",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 125,
            "seats_prev": 125,
            "seats_inc": 0
        },
        # Gujarat
        {
            "college_id": "ug_ini_aiims_rajkot",
            "college_name": "AIIMS Rajkot",
            "college_type": "Government",
            "state": "Gujarat",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 75,
            "seats_prev": 75,
            "seats_inc": 0
        },
        # Odisha
        {
            "college_id": "ug_ini_aiims_bhubaneswar",
            "college_name": "AIIMS Bhubaneswar",
            "college_type": "Government",
            "state": "Odisha",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 125,
            "seats_prev": 125,
            "seats_inc": 0
        },
        # Telangana
        {
            "college_id": "ug_ini_aiims_bibinagar",
            "college_name": "AIIMS Bibinagar",
            "college_type": "Government",
            "state": "Telangana",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 100,
            "seats_prev": 100,
            "seats_inc": 0
        },
        # Jharkhand
        {
            "college_id": "ug_ini_aiims_deoghar",
            "college_name": "AIIMS Deoghar",
            "college_type": "Government",
            "state": "Jharkhand",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 125,
            "seats_prev": 125,
            "seats_inc": 0
        },
        # Uttar Pradesh
        {
            "college_id": "ug_ini_aiims_gorakhpur",
            "college_name": "AIIMS Gorakhpur",
            "college_type": "Government",
            "state": "Uttar Pradesh",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 125,
            "seats_prev": 125,
            "seats_inc": 0
        },
        # Rajasthan
        {
            "college_id": "ug_ini_aiims_jodhpur",
            "college_name": "AIIMS Jodhpur",
            "college_type": "Government",
            "state": "Rajasthan",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 150,
            "seats_prev": 150,
            "seats_inc": 0
        },
        # West Bengal
        {
            "college_id": "ug_ini_aiims_kalyani",
            "college_name": "AIIMS Kalyani",
            "college_type": "Government",
            "state": "West Bengal",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 125,
            "seats_prev": 125,
            "seats_inc": 0
        },
        # Tamil Nadu
        {
            "college_id": "ug_ini_aiims_madurai",
            "college_name": "AIIMS Madurai",
            "college_type": "Government",
            "state": "Tamil Nadu",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 50,
            "seats_prev": 50,
            "seats_inc": 0
        },
        # Maharashtra
        {
            "college_id": "ug_ini_aiims_nagpur",
            "college_name": "AIIMS Nagpur",
            "college_type": "Government",
            "state": "Maharashtra",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 125,
            "seats_prev": 125,
            "seats_inc": 0
        },
        # Delhi
        {
            "college_id": "ug_ini_aiims_newdelhi",
            "college_name": "AIIMS New Delhi",
            "college_type": "Government",
            "state": "Delhi",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 132,
            "seats_prev": 132,
            "seats_inc": 0
        },
        # Bihar
        {
            "college_id": "ug_ini_aiims_patna",
            "college_name": "AIIMS Patna",
            "college_type": "Government",
            "state": "Bihar",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 125,
            "seats_prev": 125,
            "seats_inc": 0
        },
        # Uttar Pradesh
        {
            "college_id": "ug_ini_aiims_raebareli",
            "college_name": "AIIMS Raebareli",
            "college_type": "Government",
            "state": "Uttar Pradesh",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 100,
            "seats_prev": 100,
            "seats_inc": 0
        },
        # Chhattisgarh
        {
            "college_id": "ug_ini_aiims_raipur",
            "college_name": "AIIMS Raipur",
            "college_type": "Government",
            "state": "Chhattisgarh",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 125,
            "seats_prev": 125,
            "seats_inc": 0
        },
        # Uttarakhand
        {
            "college_id": "ug_ini_aiims_rishikesh",
            "college_name": "AIIMS Rishikesh",
            "college_type": "Government",
            "state": "Uttarakhand",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 125,
            "seats_prev": 125,
            "seats_inc": 0
        },
        # Madhya Pradesh
        {
            "college_id": "ug_ini_aiims_bhopal",
            "college_name": "AIIMS Bhopal",
            "college_type": "Government",
            "state": "Madhya Pradesh",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 125,
            "seats_prev": 125,
            "seats_inc": 0
        },
        # Puducherry JIPMER Karaikal 1
        {
            "college_id": "ug_ini_jipmer_karaikal",
            "college_name": "JIPMER Karaikal",
            "college_type": "Government",
            "state": "Puducherry",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 45,
            "seats_prev": 45,
            "seats_inc": 0
        },
        # Puducherry JIPMER Karaikal 2
        {
            "college_id": "ug_ini_jipmer_karaikal",
            "college_name": "JIPMER Karaikal",
            "college_type": "Government",
            "state": "Puducherry",
            "course": "MBBS",
            "counseling_route": "STATE",
            "quota_type": "Competent Authority Quota",
            "seats": 16,
            "seats_prev": 16,
            "seats_inc": 0
        },
        # Puducherry JIPMER Puducherry 1
        {
            "college_id": "ug_ini_jipmer_puducherry",
            "college_name": "JIPMER Puducherry",
            "college_type": "Government",
            "state": "Puducherry",
            "course": "MBBS",
            "counseling_route": "MCC",
            "quota_type": "All India Quota",
            "seats": 134,
            "seats_prev": 134,
            "seats_inc": 0
        },
        # Puducherry JIPMER Puducherry 2
        {
            "college_id": "ug_ini_jipmer_puducherry",
            "college_name": "JIPMER Puducherry",
            "college_type": "Government",
            "state": "Puducherry",
            "course": "MBBS",
            "counseling_route": "STATE",
            "quota_type": "Competent Authority Quota",
            "seats": 48,
            "seats_prev": 48,
            "seats_inc": 0
        }
    ]

    rows.extend(ini_records)

    # Save to all.json
    with open(ug_all_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print(f"Appended {len(ini_records)} INI records to all.json. Total records now: {len(rows)}")

    # Recalculate stats for summary.json
    col_count_set = set(r['college_id'] for r in rows)
    seat_count = sum(r['seats'] for r in rows)
    course_set = set(r['course'] for r in rows)
    quota_set = set(r['quota_type'] for r in rows)
    type_set = set(r['college_type'] for r in rows)
    
    # Retrieve sorted list of states
    states_and_uts = sorted(list(set(r['state'] for r in rows)))

    summary = {
        "totalColleges": len(col_count_set),
        "totalSeats": seat_count,
        "states": states_and_uts,
        "courses": sorted(list(course_set)),
        "quotas": sorted(list(quota_set)),
        "types": sorted(list(type_set))
    }

    summary_path = "public/data/ug/summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print("Updated summary.json")

    # Split into state-specific files in public/data/ug/states/
    states_dir = "public/data/ug/states"
    os.makedirs(states_dir, exist_ok=True)
    
    by_state = {state: [] for state in states_and_uts}
    for r in rows:
        by_state[r['state']].append(r)

    for state, state_rows in by_state.items():
        state_filename = f"{state.lower().replace(' ', '_').replace('&', 'and')}.json"
        with open(os.path.join(states_dir, state_filename), "w", encoding="utf-8") as f:
            json.dump(state_rows, f, indent=2, ensure_ascii=False)
        print(f"Wrote: {state_filename} ({len(state_rows)} records)")

if __name__ == "__main__":
    main()
