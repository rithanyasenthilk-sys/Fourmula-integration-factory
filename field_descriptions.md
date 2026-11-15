# Source system notes (from the system owners)

## Patient registration system (REST API)
GET /patients returns every registered patient as JSON; GET /patients/{patient_id} returns one.
patient_id is the hospital-wide patient identifier. date_of_birth is day first. sex is F or M.

## Hospital database (SQL)
Legacy system, no current documentation. Visits of all kinds live in TBL_VISIT; LKP_VISIT_TYPE decodes VISIT_TYPE.

## Laboratory system (CSV export)
Nightly export, one row per numeric lab result. loinc_code is the LOINC code. collected_at is the sample collection time, day first.
