import pytest
import json
import os
import sys
from unittest import mock
from sqlalchemy import MetaData, Table, Column, String
from sqlalchemy.exc import SQLAlchemyError
from src.fhir_processor import process_fhir_data

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Mock the table definition function for testing
def mock_define_patient_table(metadata):
    return Table('patients', metadata,
                 Column('id', String(50), primary_key=True),
                 Column('first_name', String(100)),
                 Column('last_name', String(100)),
                 Column('gender', String(50)),
                 Column('birthdate', String(50)),
                 Column('city', String(100)),
                 Column('state', String(100)),
                 Column('country', String(100)))


def mock_define_encounter_table(metadata):
    return Table('encounters', metadata,
                 Column('id', String(50), primary_key=True),
                 Column('patient_id', String(50)),
                 Column('status', String(50)),
                 Column('encounter_type', String(100)),
                 Column('start_date', String(100)),
                 Column('end_date', String(100)),
                 Column('practitioner', String(100)))

# Mock the session execute and commit methods
@pytest.fixture
def mock_session():
    mock_session = mock.Mock()
    mock_session.execute = mock.Mock()
    mock_session.commit = mock.Mock()
    mock_session.rollback = mock.Mock()
    return mock_session


def test_fhir_patient_data_insertion(mock_session, tmpdir):
    """Test patient data processing with mocked session and file."""

    # Sample FHIR patient data
    fhir_data = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "12345",
                    "name": [{"given": ["John"], "family": "Doe"}],
                    "gender": "male",
                    "birthDate": "1980-05-15",
                    "address": [{"city": "New York", "state": "NY", "country": "US"}]
                }
            }
        ]
    }

    # Create a temporary file to simulate the FHIR JSON file
    json_file = tmpdir.join("fhir_patient.json")
    json_file.write(json.dumps(fhir_data))

    # Create MetaData object
    metadata = MetaData()

    # Use the mocked session and mock table definitions
    with mock.patch('src.fhir_processor.define_patient_table', side_effect=mock_define_patient_table):
        with mock.patch('src.fhir_processor.define_encounter_table', side_effect=mock_define_encounter_table):
            # Process FHIR data using the mock session
            process_fhir_data(str(json_file), mock_session, metadata)

    # Assertions to verify correct behavior
    assert mock_session.execute.call_count == 1, "Expected one execute call for patient insertion"
    assert mock_session.commit.called, "Expected the commit to be called"


def test_fhir_encounter_data_insertion(mock_session, tmpdir):
    """Test encounter data processing with mocked session and file."""

    # Sample FHIR encounter data
    fhir_data = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "resource": {
                    "resourceType": "Encounter",
                    "id": "enc_12345",
                    "status": "finished",
                    "subject": {"reference": "urn:uuid:12345"},
                    "period": {"start": "2021-09-01T10:00:00Z", "end": "2021-09-01T11:00:00Z"},
                    "type": [{"text": "General examination"}],
                    "participant": [{"individual": {"display": "Dr. Smith"}}]
                }
            }
        ]
    }

    # Create a temporary file to simulate the FHIR JSON file
    json_file = tmpdir.join("fhir_encounter.json")
    json_file.write(json.dumps(fhir_data))

    # Create MetaData object
    metadata = MetaData()

    # Use the mocked session and mock table definitions
    with mock.patch('src.fhir_processor.define_patient_table', side_effect=mock_define_patient_table):
        with mock.patch('src.fhir_processor.define_encounter_table', side_effect=mock_define_encounter_table):
            # Process FHIR data using the mock session
            process_fhir_data(str(json_file), mock_session, metadata)

    # Assertions to verify correct behavior
    assert mock_session.execute.call_count == 1, "Expected one execute call for encounter insertion"
    assert mock_session.commit.called, "Expected the commit to be called"


def test_fhir_patient_data_with_missing_id(mock_session, tmpdir):
    """Test patient data processing when patient 'id' is missing."""

    # Sample FHIR patient data with missing 'id'
    fhir_data = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "name": [{"given": ["John"], "family": "Doe"}],
                    "gender": "male",
                    "birthDate": "1980-05-15",
                    "address": [{"city": "New York", "state": "NY", "country": "US"}]
                }
            }
        ]
    }

    # Create a temporary file to simulate the FHIR JSON file
    json_file = tmpdir.join("fhir_patient_missing_id.json")
    json_file.write(json.dumps(fhir_data))

    # Create MetaData object
    metadata = MetaData()

    # Use the mocked session and mock table definitions
    with mock.patch('src.fhir_processor.define_patient_table', side_effect=mock_define_patient_table):
        with mock.patch('src.fhir_processor.define_encounter_table', side_effect=mock_define_encounter_table):
            # Process FHIR data using the mock session
            process_fhir_data(str(json_file), mock_session, metadata)

    # Assertions to verify patient with missing 'id' was not processed
    assert mock_session.execute.call_count == 0, "Expected no execute call due to missing patient 'id'"
    assert not mock_session.commit.called, "Expected the commit to not be called due to missing patient 'id'"



def test_fhir_encounter_data_with_missing_subject(mock_session, tmpdir):
    """Test encounter data processing when encounter 'subject' (patient reference) is missing."""

    # Sample FHIR encounter data with missing 'subject'
    fhir_data = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "resource": {
                    "resourceType": "Encounter",
                    "id": "enc_67890",
                    "status": "finished",
                    "period": {"start": "2021-09-01T10:00:00Z", "end": "2021-09-01T11:00:00Z"},
                    "type": [{"text": "Consultation"}],
                    "participant": [{"individual": {"display": "Dr. Jones"}}]
                }
            }
        ]
    }

    # Create a temporary file to simulate the FHIR JSON file
    json_file = tmpdir.join("fhir_encounter_missing_subject.json")
    json_file.write(json.dumps(fhir_data))

    # Create MetaData object
    metadata = MetaData()

    # Use the mocked session and mock table definitions
    with mock.patch('src.fhir_processor.define_patient_table', side_effect=mock_define_patient_table):
        with mock.patch('src.fhir_processor.define_encounter_table', side_effect=mock_define_encounter_table):
            # Process FHIR data using the mock session
            process_fhir_data(str(json_file), mock_session, metadata)

    # Assertions to verify encounter with missing 'subject' was still processed
    assert mock_session.execute.call_count == 1, "Expected one execute call even though 'subject' is missing"
    assert mock_session.commit.called, "Expected the commit to be called"


def test_fhir_data_insertion_error(mock_session, tmpdir):
    """Test that rollback is called if an error occurs during data insertion."""

    # Sample FHIR patient data
    fhir_data = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "54321",
                    "name": [{"given": ["Jane"], "family": "Doe"}],
                    "gender": "female",
                    "birthDate": "1985-07-10",
                    "address": [{"city": "Los Angeles", "state": "CA", "country": "US"}]
                }
            }
        ]
    }

    # Create a temporary file to simulate the FHIR JSON file
    json_file = tmpdir.join("fhir_patient_error.json")
    json_file.write(json.dumps(fhir_data))

    # Simulate an error during session.execute call
    mock_session.execute.side_effect = SQLAlchemyError("Simulated database error")

    # Create MetaData object
    metadata = MetaData()

    # Use the mocked session and mock table definitions
    with mock.patch('src.fhir_processor.define_patient_table', side_effect=mock_define_patient_table):
        with mock.patch('src.fhir_processor.define_encounter_table', side_effect=mock_define_encounter_table):
            # Process FHIR data using the mock session, expecting an error
            process_fhir_data(str(json_file), mock_session, metadata)

    # Assertions to verify rollback is called due to error
    assert mock_session.rollback.called, "Expected rollback to be called due to error"
    assert not mock_session.commit.called, "Commit should not be called when an error occurs"
