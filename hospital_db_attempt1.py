import re
from datetime import datetime

def extract_hospital_db(source, log):
    """hospital_db -> FHIR Encounter records.
    Rejected records are reported through log() with row number and field name only."""
    records = []
    cursor = source.execute("""
        SELECT v.VISIT_NO, v.PT_REF, v.VISIT_START, v.VISIT_END, l.TYPE_DESC
        FROM TBL_VISIT v
        LEFT JOIN LKP_VISIT_TYPE l ON v.VISIT_TYPE = l.TYPE_CD
    """)
    rows = cursor.fetchall()

    for row_number, row in enumerate(rows, start=1):
        visit_no, pt_ref, visit_start, visit_end, type_desc = row
        try:
            if visit_no is None or str(visit_no).strip() == "":
                raise ValueError("id")
            enc_id = f"ENC-{visit_no}"

            if not pt_ref or not isinstance(pt_ref, str) or not re.match(r"^[A-Za-z0-9-]+$", pt_ref.strip()):
                raise ValueError("subject.reference")
            patient_ref = f"Patient/{pt_ref.strip()}"

            if not visit_start or not isinstance(visit_start, str):
                raise ValueError("period.start")
            try:
                start_dt = datetime.strptime(visit_start.strip(), "%Y%m%d %H%M").strftime("%Y-%m-%dT%H:%M:%S")
            except Exception:
                raise ValueError("period.start")

            end_dt = None
            if visit_end and isinstance(visit_end, str) and visit_end.strip():
                try:
                    end_dt = datetime.strptime(visit_end.strip(), "%Y%m%d %H%M").strftime("%Y-%m-%dT%H:%M:%S")
                except Exception:
                    raise ValueError("period.end")

            status = "finished" if end_dt is not None else "in-progress"

            period = {"start": start_dt}
            if end_dt:
                period["end"] = end_dt

            record = {
                "resourceType": "Encounter",
                "id": enc_id,
                "status": status,
                "period": period,
                "subject": {"reference": patient_ref}
            }

            if type_desc and isinstance(type_desc, str) and type_desc.strip():
                record["serviceType"] = {"text": type_desc.strip()}

            records.append(record)
        except ValueError as problem:
            log(f"row {row_number}: rejected - {problem} missing or invalid")
            continue

    return records