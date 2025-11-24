import psutil
import time
import pyautogui
import win32gui
import win32process
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import patient_manager
import logging
from datetime import datetime

BASE_DIR = Path("hoerzelle")
SAVED_PATIENTS_DIR = BASE_DIR / "saved_patients"
PATIENTS_JSON = SAVED_PATIENTS_DIR / "patients.json"
LOG_DIR = BASE_DIR / "log"

LOG_DIR.mkdir(parents=True, exist_ok=True)
log_file = LOG_DIR / f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

pyautogui.PAUSE = 0.2

def is_maico_running() -> bool:
    for process in psutil.process_iter(['name']):
        try:
            if process.info['name'].lower() == 'maico32.exe':
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def is_maico_in_focus() -> bool:
    try:
        foreground_window = win32gui.GetForegroundWindow()
        _, process_id = win32process.GetWindowThreadProcessId(foreground_window)
        process = psutil.Process(process_id)
        return process.name().lower() == 'maico32.exe'
    except Exception:
        return False

def wait_for_maico() -> bool:
    logging.info('Waiting for maico32.exe')
    
    while not is_maico_running():
        time.sleep(1)
    
    logging.info('maico32.exe started')
    time.sleep(3)
    
    while not is_maico_in_focus():
        time.sleep(0.5)
    
    logging.info('maico32.exe is in focus')
    return True

def load_patients() -> Optional[List[Dict[str, Any]]]:
    if not PATIENTS_JSON.exists():
        logging.error('JSON not found, calling PatientManager')
        SAVED_PATIENTS_DIR.mkdir(parents=True, exist_ok=True)
        patient_manager.get_all_patients()
        
        if not PATIENTS_JSON.exists():
            return None
    
    try:
        with open(PATIENTS_JSON, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        logging.error(f'Error loading patient JSON: {e}')
        return None

def enter_patient(patient: Dict[str, Any]) -> None:
    if not is_maico_in_focus():
        logging.warning("MAICO not in focus, waiting again.")
        while not is_maico_in_focus():
            time.sleep(0.5)

    patient_name = f"{patient.get('firstname', 'N/A')} {patient.get('lastname', 'N/A')}"
    logging.info(f"Starting input for: {patient_name}")
    
    lastname = str(patient.get("lastname", ""))
    pyautogui.write(lastname, interval=0.05)
    time.sleep(0.5)
    
    pyautogui.press("tab")
    time.sleep(0.3)
    
    firstname = str(patient.get("firstname", ""))
    pyautogui.write(firstname, interval=0.05)
    time.sleep(0.5)
    
    pyautogui.press("tab")
    time.sleep(0.3)
    
    date_of_birth = str(patient.get("date_of_birth", ""))
    pyautogui.write(date_of_birth, interval=0.05)
    time.sleep(0.5)
    
    pyautogui.press("tab")
    time.sleep(0.3)
    
    gender = str(patient.get("gender", "")).lower()
    tabs_to_save_button = 16
    
    if gender == "w":
        pyautogui.press("tab")
        time.sleep(0.3)
        tabs_to_save_button = 15
    
    pyautogui.press("space")
    time.sleep(0.5)
    
    for _ in range(tabs_to_save_button):
        pyautogui.press("tab")
        time.sleep(0.05)
    
    pyautogui.press("enter")
    time.sleep(1)
    
    logging.info(f"Input completed for: {patient_name}")
    time.sleep(1.5)
    logging.info("Starting hearing test (F2)")
    pyautogui.press("F2")
    time.sleep(1.0)

def run_automation():
    logging.info("Program started")
    
    patients = load_patients()
    
    if not patients or not isinstance(patients, list) or len(patients) == 0:
        logging.error("No or empty patient list loaded. Exiting.")
        return
    
    total_patients = len(patients)
    logging.info(f"{total_patients} patients loaded")
    
    try:
        if wait_for_maico():
            time.sleep(2)
            
            for patient_number, patient in enumerate(patients, 1):
                logging.info(f"Processing patient {patient_number}/{total_patients}")
                
                if patient_number > 1:
                    while not is_maico_in_focus():
                        logging.info("Waiting for focus again for next patient.")
                        time.sleep(0.5)
                
                enter_patient(patient)
                time.sleep(5)
            
            logging.info("All patients entered successfully")
            
    except KeyboardInterrupt:
        logging.info("Program aborted by user (KeyboardInterrupt)")
    except Exception as error:
        logging.error(f"Critical error: {error}", exc_info=True)