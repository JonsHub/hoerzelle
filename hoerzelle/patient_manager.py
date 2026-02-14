import patient_json_save
import patient_database_download
import paths

def get_all_patients():
    patients_list = patient_database_download.download_patients()
    patient_json_save.save_patients(patients_list, target_directory=paths.SAVED_PATIENTS_DIR)
    return patients_list