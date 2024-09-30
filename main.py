import os
from sqlalchemy import MetaData
from src.db_config import get_db_engine, get_session
from src.fhir_processor import process_fhir_data, define_patient_table, define_encounter_table


def main():
    # Initialise database connection
    engine = get_db_engine()
    session = get_session(engine)

    # Create a MetaData instance
    metadata = MetaData()

    # Define tables and attach them to the metadata
    define_patient_table(metadata)
    define_encounter_table(metadata)

    # Create tables if they don't exist
    metadata.create_all(engine)

    # Directory containing FHIR data files
    data_dir = 'data'

    # Process all files in the data directory
    for file_name in os.listdir(data_dir):
        # Ensure we're only processing JSON files
        if file_name.endswith(".json"):
            file_path = os.path.join(data_dir, file_name)
            print(f"Processing file: {file_path}")
            try:
                # Process FHIR data for each file
                process_fhir_data(file_path, session, metadata)
            except Exception as e:
                print(f"Failed to process {file_name}: {e}")

    # Close the session
    session.close()


if __name__ == "__main__":
    main()
