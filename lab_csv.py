import csv
import re
from datetime import datetime

def extract_lab_csv(source, log):
    """lab_csv -> FHIR Observation records.
    Rejected records are reported through log() with row number and field name only."""
    records = []
    with open(source, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row_number, row in enumerate(reader, start=1):
            try:
                patient_ref = (row.get('patient_ref') or '').strip()
                if not patient_ref or not re.match(r'^[A-Za-z0-9\-]+$', patient_ref):
                    raise ValueError('patient_ref')

                collected_at = (row.get('collected_at') or '').strip()
                if not collected_at:
                    raise ValueError('collected_at')
                try:
                    dt = datetime.strptime(collected_at, '%d/%m/%Y %H:%M')
                    effective_datetime = dt.strftime('%Y-%m-%dT%H:%M:%S')
                except ValueError:
                    raise ValueError('collected_at')

                loinc_code = (row.get('loinc_code') or '').strip()
                if not loinc_code:
                    raise ValueError('loinc_code')

                result_value_str = (row.get('result_value') or '').strip()
                if not result_value_str:
                    raise ValueError('result_value')
                try:
                    result_value = float(result_value_str)
                except ValueError:
                    raise ValueError('result_value')

                result_unit = (row.get('result_unit') or '').strip()
                if not result_unit:
                    raise ValueError('result_unit')

                test_description = (row.get('test_description') or '').strip()

                code_obj = {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": loinc_code
                        }
                    ]
                }
                if test_description:
                    code_obj["text"] = test_description

                record = {
                    "resourceType": "Observation",
                    "id": f"LAB-{row_number}",
                    "status": "final",
                    "code": code_obj,
                    "subject": {
                        "reference": f"Patient/{patient_ref}"
                    },
                    "effectiveDateTime": effective_datetime,
                    "valueQuantity": {
                        "value": result_value,
                        "unit": result_unit
                    }
                }
                records.append(record)

            except ValueError as problem:
                log(f"row {row_number}: rejected - {problem} missing or invalid")
                continue

    return records