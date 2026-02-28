import patient_json_save
import patient_database_download
import paths_dir
import json
import shutil

def get_all_patients():
    patients_list = patient_database_download.download_patients()
    patient_json_save.save_patients(patients_list, target_directory=paths_dir.SAVED_PATIENTS_DIR)
    return patients_list

def remove_patient_from_json(patient_id):
    if not paths_dir.JSON_FILE.exists():
        print(f"JSON file not found: {paths_dir.JSON_FILE}")
        return False
    
    try:
        with open(paths_dir.JSON_FILE, 'r', encoding='utf-8') as file:
            patients = json.load(file)
        
        original_count = len(patients)
        patients = [p for p in patients if p.get('id') != patient_id]
        
        if len(patients) == original_count:
            print(f"Patient with ID {patient_id} not found in list")
            return False
        
        with open(paths_dir.JSON_FILE, 'w', encoding='utf-8') as file:
            json.dump(patients, file, indent=4)
        
        print(f"Patient {patient_id} removed from queue. Remaining: {len(patients)}")
        return True
        
    except Exception as e:
        print(f"Error removing patient: {e}")
        return False

def get_patient_count():
    if not paths_dir.JSON_FILE.exists():
        return 0
    
    try:
        with open(paths_dir.JSON_FILE, 'r', encoding='utf-8') as file:
            patients = json.load(file)
        return len(patients)
    except:
        return 0

def clear_all_patients():
    if paths_dir.JSON_FILE.exists():
        with open(paths_dir.JSON_FILE, 'w', encoding='utf-8') as file:
            json.dump([], file)
        print("All patients cleared from queue")
        return True
    return False

def move_to_test_archive():
    saved_tests_dir = paths_dir.SAVED_TESTS_DIR
    archive_dir = paths_dir.ARCHIVE_DIR
    
    for file in saved_tests_dir.glob("*.xml"):
        shutil.move(str(file), str(archive_dir / file.name))
    
    for file in saved_tests_dir.glob("*.pdf"):
        shutil.move(str(file), str(archive_dir / file.name))
    
    print(f"Files moved from {saved_tests_dir} to {archive_dir}")
    return True