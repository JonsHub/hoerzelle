import psutil
import time
import pyautogui
import win32gui
import win32process
import json
import logging
import gui_utils
import patient_manager
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from xml.dom import minidom


BASE_DIR = Path(".")
SAVED_PATIENTS_DIR = BASE_DIR / "data" / "saved_patients"
PATIENTS_JSON = SAVED_PATIENTS_DIR / "patients.json"
LOG_DIR = Path("logs")
XML_FILE_PATH = BASE_DIR / "data" / "xml_port" / "in.xml"

LOG_DIR.mkdir(parents=True, exist_ok=True)
log_file = LOG_DIR / f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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
    print("Waiting for maico32.exe")
    logging.info('Waiting for maico32.exe')
    
    while not is_maico_running():
        time.sleep(1)
    
    print("maico32.exe started")
    logging.info('maico32.exe started')
    time.sleep(3)
    
    while not is_maico_in_focus():
        time.sleep(0.5)
    
    print("maico32.exe is in focus")
    logging.info('maico32.exe is in focus')
    return True

def load_patients() -> Optional[List[dict[str, Any]]]:
    if not PATIENTS_JSON.exists():
        print("JSON not found, calling PatientManager")
        logging.error('JSON not found, calling PatientManager')
        SAVED_PATIENTS_DIR.mkdir(parents=True, exist_ok=True)
        patient_manager.get_all_patients()
        
        if not PATIENTS_JSON.exists():
            return None
    
    try:
        with open(PATIENTS_JSON, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading patient JSON: {e}")
        logging.error(f'Error loading patient JSON: {e}')
        return None

def create_xml_for_patient(patient: Dict[str, Any]) -> None:
    """Erstellt XML-Datei für den Patienten BEVOR der Test startet"""
    try:
        date_of_birth_string = str(patient.get("date_of_birth"))
        temp_date = datetime.strptime(date_of_birth_string, "%d.%m.%Y")
        formatted_date = temp_date.strftime("%Y%m%d")
        
        sex = 1 if str(patient.get("gender")).lower() == "m" else 0
        
        last_name = patient.get("lastname")
        first_name = patient.get("firstname")
        
        print("Hole Patienten-ID aus Maske...")
        logging.info("Hole Patienten-ID aus Maske...")
        patient_id = gui_utils.get_patient_id()
        print(f"ID gefunden: {patient_id}")
        logging.info(f"ID gefunden: {patient_id}")
        
        document = minidom.Document()
        root = document.createElement("patient")
        document.appendChild(root)
        
        id_element = document.createElement("idpatient")
        id_element.appendChild(document.createTextNode(str(patient_id)))
        root.appendChild(id_element)
        
        dob_element = document.createElement("datedenaissance")
        dob_element.appendChild(document.createTextNode(formatted_date))
        root.appendChild(dob_element)
        
        last_name_element = document.createElement("nom")
        last_name_element.appendChild(document.createTextNode(str(last_name)))
        root.appendChild(last_name_element)
        
        first_name_element = document.createElement("prenom")
        first_name_element.appendChild(document.createTextNode(str(first_name)))
        root.appendChild(first_name_element)
        
        sex_element = document.createElement("sexe")
        sex_element.appendChild(document.createTextNode(str(sex)))
        root.appendChild(sex_element)
        
        xml_content = document.toprettyxml(indent="  ", encoding="UTF-8").decode("UTF-8")
        
        with open(XML_FILE_PATH, "w", encoding="UTF-8") as file:
            file.write(xml_content)
        
        print(f"XML erfolgreich erstellt: {XML_FILE_PATH}")
        logging.info(f"XML erfolgreich erstellt: {XML_FILE_PATH}")
        
    except Exception as e:
        print(f"FEHLER beim XML erstellen: {e}")
        logging.error(f"FEHLER beim XML erstellen: {e}", exc_info=True)

def enter_patient(patient: Dict[str, Any]) -> None:
    if not is_maico_in_focus():
        print("MAICO not in focus, waiting again.")
        logging.warning("MAICO not in focus, waiting again.")
        while not is_maico_in_focus():
            time.sleep(0.5)

    patient_name = f"{patient.get('firstname', 'N/A')} {patient.get('lastname', 'N/A')}"
    print(f"Starting input for: {patient_name}")
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
    
    if gender == "w":
        pyautogui.press("tab")
        pyautogui.press("space")
        time.sleep(0.3)
        for _ in range(15):
            pyautogui.press("tab", interval=0.1)
        pyautogui.press("space")
        pyautogui.press("space")
    
    else:
        pyautogui.press("space")
        time.sleep(0.5)
        for _ in range(16):
            pyautogui.press("tab", interval=0.1)
        pyautogui.press("space")
        pyautogui.press("space")
    
    print(f"Input completed for: {patient_name}")
    logging.info(f"Input completed for: {patient_name}")
    time.sleep(2)
    
    create_xml_for_patient(patient)
    time.sleep(3)
    
    print("Everything done! Starting hearing test (F2)")
    logging.info("Starting hearing test (F2)")
    pyautogui.press("F2")
    time.sleep(1.0)
        
def run_automation():
    print("Program started")
    logging.info("Program started")
    
    patients = load_patients()
    
    if not patients or not isinstance(patients, list) or len(patients) == 0:
        print("No or empty patient list loaded. Exiting.")
        logging.error("No or empty patient list loaded. Exiting.")
        return
    
    total_patients = len(patients)
    print(f"{total_patients} patients loaded")
    logging.info(f"{total_patients} patients loaded")
    
    try:
        if wait_for_maico():
            time.sleep(2)
            
            for patient_number, patient in enumerate(patients, 1):
                print(f"Processing patient {patient_number}/{total_patients}")
                logging.info(f"Processing patient {patient_number}/{total_patients}")
                
                if patient_number > 1:
                    while not is_maico_in_focus():
                        print("Waiting for focus again for next patient.")
                        logging.info("Waiting for focus again for next patient.")
                        time.sleep(0.5)
                
                enter_patient(patient)
                time.sleep(5)
            
            print("All patients entered successfully")
            logging.info("All patients entered successfully")
            
    except KeyboardInterrupt:
        print("Program aborted by user (KeyboardInterrupt)")
        logging.info("Program aborted by user (KeyboardInterrupt)")
    except Exception as error:
        print(f"Critical error: {error}")
        logging.error(f"Critical error: {error}", exc_info=True)
    return None
