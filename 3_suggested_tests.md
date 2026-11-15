# Tests suggested by the agent (for Person 3)

## Patient registration system (REST API)
- Test successful extraction with a valid patient record having DD/MM/YYYY birthDate and 'F' sex code.
- Test rejection when patient_id contains invalid characters such as special punctuation.
- Test rejection when date_of_birth is improperly formatted or an invalid calendar date.
- Test rejection when sex is missing or not recognized in the code mapping table.

## Hospital database (SQL)
- Test valid completed visit row correctly produces Encounter resource with 'finished' status, ISO timestamps, and formatted serviceType.
- Test in-progress visit with null VISIT_END produces Encounter with 'in-progress' status and no period.end field.
- Test invalid patient reference containing special characters or invalid datetime string logs a rejected message with field name and skips output.

## Laboratory system (CSV file)
- Verify successful transformation of valid CSV lab result records into FHIR Observation resources.
- Verify rejection and correct log message formatting when result_value is non-numeric or missing.
- Verify rejection when collected_at timestamp does not follow the required DD/MM/YYYY HH:mm format.
