import re
from datetime import datetime

def extract_patient_api(source, log):
    """Patient registration system (REST API) -> FHIR Patient records.
    Rejected records are reported through log() with row number and field name only."""
    records = []
    patients = source('/patients')
    if not isinstance(patients, list):
        return records

    for row_number, row in enumerate(patients, start=1):
        try:
            if not isinstance(row, dict):
                raise ValueError("id")

            pid = row.get("patient_id")
            if not pid or not isinstance(pid, str) or not re.match(r"^[a-zA-Z0-9-]+$", pid):
                raise ValueError("id")

            family = row.get("last_name")
            if not family or not isinstance(family, str):
                raise ValueError("name[0].family")

            sex = row.get("sex")
            if not sex or not isinstance(sex, str):
                raise ValueError("gender")
            gender_map = {"F": "female", "M": "male", "female": "female", "male": "male"}
            gender = gender_map.get(sex)
            if not gender:
                raise ValueError("gender")

            dob_str = row.get("date_of_birth")
            if not dob_str or not isinstance(dob_str, str):
                raise ValueError("birthDate")
            try:
                dob = datetime.strptime(dob_str, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError:
                raise ValueError("birthDate")

            first_name = row.get("first_name")
            name_entry = {"family": family}
            if isinstance(first_name, str) and first_name.strip():
                name_entry["given"] = [first_name.strip()]

            records.append({
                "resourceType": "Patient",
                "id": pid,
                "name": [name_entry],
                "gender": gender,
                "birthDate": dob
            })
        except ValueError as problem:
            log(f"row {row_number}: rejected - {problem} missing or invalid")
            continue

    return records