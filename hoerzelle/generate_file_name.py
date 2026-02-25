from datetime import datetime
import json
import paths_dir
from typing import Dict, List, Any

def get_patient_data() -> List[Dict[str, Any]]:
    if not paths_dir.JSON_FILE.exists():
        raise FileNotFoundError(f"Patient JSON nicht gefunden: {paths_dir.JSON_FILE}")
    
    with open(paths_dir.JSON_FILE, "r", encoding="utf-8") as file:
        patient_data = json.load(file)
    
    if not isinstance(patient_data, list) or len(patient_data) == 0:
        raise ValueError("Keine Patienten in JSON gefunden")
    
    return patient_data

def create_filename_from_patient(patient_data: List[Dict[str, Any]]) -> str:
    if not patient_data or not isinstance(patient_data, list):
        raise ValueError("Ungültige Patientendaten")
    
    patient = patient_data[0]
    lastname = str(patient.get("lastname", "Unknown"))
    firstname = str(patient.get("firstname", "Unknown"))
    
    lastname = lastname.replace(" ", "_").replace("/", "-")
    firstname = firstname.replace(" ", "_").replace("/", "-")
    
    today = datetime.now().strftime('%Y-%m-%d')
    time = datetime.now().strftime('%H-%M-%S')
    
    return f"{lastname}_{firstname}_{today}_{time}"

def create_filename_for_specific_patient(patient: Dict[str, Any]) -> str:
    return create_filename_from_patient([patient])