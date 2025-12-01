import pyautogui
from datetime import datetime
import json
from typing import Dict, Any

def get_patient_data() -> dict:
    with open("saved_patients/patients.json", "r", encoding="utf-8") as file:
        patient_data = json.load(file)
    return patient_data

def create_filename_from_patient(patient_data: dict) -> str:
    lastname = str(patient_data.get("lastname", ""))
    firstname = str(patient_data.get("firstname", ""))
    today = datetime.now().strftime('%Y-%m-%d')
    time = datetime.now().strftime('%H-%M-%S')

    filename = f"test_{lastname}_{firstname}_{today}_{time}"
    return filename

def enter_filename(patient_data: Dict[str, Any]) -> str:
    filename = create_filename_from_patient(patient_data)
    
    print(f"Generated filename: {filename}")
    
    pyautogui.write(filename, interval=0.05)
    
    return filename