from datetime import datetime
import json
import paths_dir

def get_patient_data() -> dict:
    with open(paths_dir.JSON_FILE, "r", encoding="utf-8") as file:
        patient_data = json.load(file)
    return patient_data

def create_filename_from_patient(patient_data: dict) -> str:
    lastname = str(patient_data[0].get("lastname", ""))
    firstname = str(patient_data[0].get("firstname", ""))
    today = datetime.now().strftime('%Y-%m-%d')
    time = datetime.now().strftime('%H-%M-%S')
    return f"{lastname}_{firstname}_{today}_{time}"