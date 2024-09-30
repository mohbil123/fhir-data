import json
import logging
from sqlalchemy import Table, Column, String, ForeignKey
from sqlalchemy.exc import SQLAlchemyError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the patient table
def define_patient_table(metadata):
    return Table('patients', metadata,
                 Column('id', String(50), primary_key=True),
                 Column('first_name', String(100)),
                 Column('last_name', String(100)),
                 Column('gender', String(50)),
                 Column('birthdate', String(50)),
                 Column('city', String(100)),
                 Column('state', String(100)),
                 Column('country', String(100)),
                 extend_existing=True
                 )

# Define the encounter table
def define_encounter_table(metadata):
    return Table('encounters', metadata,
                 Column('id', String(50), primary_key=True),
                 Column('patient_id', String(50), ForeignKey('patients.id')),  # Added foreign key constraint
                 Column('status', String(50)),
                 Column('encounter_type', String(100)),
                 Column('start_date', String(100)),
                 Column('end_date', String(100)),
                 Column('practitioner', String(100)),
                 extend_existing=True
                 )

# Process FHIR data entries for Patient
def process_patient(resource):
    patient_id = resource.get('id', None)
    if not patient_id:
        logger.warning("Patient resource missing 'id'. Skipping.")
        return None

    first_name = resource.get('name', [{}])[0].get('given', [None])[0]
    last_name = resource.get('name', [{}])[0].get('family', None)
    gender = resource.get('gender', None)
    birthdate = resource.get('birthDate', None)
    address = resource.get('address', [{}])[0]
    city = address.get('city', None)
    state = address.get('state', None)
    country = address.get('country', None)

    return {
        'id': patient_id,
        'first_name': first_name,
        'last_name': last_name,
        'gender': gender,
        'birthdate': birthdate,
        'city': city,
        'state': state,
        'country': country
    }

# Process FHIR data entries for Encounter
def process_encounter(resource):
    encounter_id = resource.get('id', None)
    if not encounter_id:
        logger.warning("Encounter resource missing 'id'. Skipping.")
        return None

    patient_reference = resource.get('subject', {}).get('reference', '').split('/')[-1]
    patient_reference = patient_reference.replace('urn:uuid:', '')  # Normalise patient_id
    status = resource.get('status', None)
    encounter_type = resource.get('type', [{}])[0].get('text', None)
    period = resource.get('period', {})
    start_date = period.get('start', None)
    end_date = period.get('end', None)
    practitioner = resource.get('participant', [{}])[0].get('individual', {}).get('display', None)

    return {
        'id': encounter_id,
        'patient_id': patient_reference,
        'status': status,
        'encounter_type': encounter_type,
        'start_date': start_date,
        'end_date': end_date,
        'practitioner': practitioner
    }

# Main function to process FHIR data file
def process_fhir_data(file_path, session, metadata):
    # Define tables once
    patient_table = define_patient_table(metadata)
    encounter_table = define_encounter_table(metadata)

    try:
        # Load the FHIR JSON data using UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return

    patient_data = []
    encounter_data = []

    # Loop through the FHIR data entries
    for entry in data.get('entry', []):
        resource = entry.get('resource', {})

        # Handle Patient resource
        if resource.get('resourceType') == 'Patient':
            patient_record = process_patient(resource)
            if patient_record:
                patient_data.append(patient_record)

        # Handle Encounter resource
        elif resource.get('resourceType') == 'Encounter':
            encounter_record = process_encounter(resource)
            if encounter_record:
                encounter_data.append(encounter_record)

    try:
        # Only execute if there is patient data to insert
        if patient_data:
            session.execute(patient_table.insert(), patient_data)
            logger.info(f"Inserted {len(patient_data)} patient records.")

        # Only execute if there is encounter data to insert
        if encounter_data:
            session.execute(encounter_table.insert(), encounter_data)
            logger.info(f"Inserted {len(encounter_data)} encounter records.")

        # Only commit if data was inserted
        if patient_data or encounter_data:
            session.commit()

    except SQLAlchemyError as e:
        logger.error(f"Error inserting data into the database: {e}")
        session.rollback()
    except Exception as e:
        logger.error(f"Unexpected error during database operation: {e}")
