import patient_json_save
from core import patient_database_download
from pathlib import Path

BASE_DIR = Path(".")
SAVED_PATIENTS_DIR = BASE_DIR / "data/saved_patients"

def get_all_patients():
    patients_list = patient_database_download.download_patients()
    patient_json_save.save_patients(patients_list, target_directory=SAVED_PATIENTS_DIR)
    return patients_list