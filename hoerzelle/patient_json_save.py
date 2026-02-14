import json
from datetime import date
import patient_database_download
import paths
engine = patient_database_download.engine
def save_patients(patients_list, target_directory = paths.SAVED_PATIENTS_DIR):
    target_directory.mkdir(parents=True, exist_ok=True)
    file_path = target_directory / "patients.json"
    data_for_json = []
    
    for row in patients_list:
        date_of_birth = row['date_of_birth']
        if isinstance(date_of_birth, date):
            formatted_date = date_of_birth.strftime("%d.%m.%Y")
        else:
            formatted_date = date_of_birth
            
        data_for_json.append({
            "lastname": row['lastname'],
            "firstname": row['firstname'],
            "date_of_birth": formatted_date,
            "gender": row['gender'],
            "email": row['email'],
            "id": row['id']
        })

    try:
        with open(file_path, "w") as f:
            json.dump(data_for_json, f, indent=4)
            print(f"""Datei erfolgreich gespeichert unter: {file_path}. 
                     Es wurden {len(data_for_json)} Patient(en) gespeichert.""")
            engine.dispose()
        return file_path
    except IOError as e:
        print(f"Fehler beim Speichern der Datei {file_path}: {e}")
        return None