import json
import fill_in_patient
import hearing_test_automation
import os
import qr_code_validate
import qr_code_create
import test_evaluator
import patient_database_download
import patient_manager
import gui_utils
import time
import generate_file_name
import paths_dir
from test_start_gui import PatientStartScreen
from test_result_gui import EvaluationGUI
from gui_utils import TestBlackScreen

TEST_CONFIG = {
    "test_qr_code_creation": 0,
    "test_qr_code_validation": 0,
    "test_patient_download": 0,
    "test_patient_json_load": 0,
    "test_start_gui": 0,
    "test_test_in_progress_gui": 0,
    "test_maico_detection": 0,
    "test_ma33_detection": 0,
    "test_patient_input": 0,
    "test_patient_json_removal": 0,
    "test_hearing_test": 0,
    "test_xml_reading": 0,
    "test_evaluation_logic": 0,
    "test_pdf_generation": 0,
    "test_result_gui_with_diagrams": 0,
    "test_result_gui": 0,
    "test_filename_generation": 0,
    "check_directories": 0,
    "move_to_archive": 0,
    "run_full_workflow": 0,
}

def test_qr_code_validation():
    print("\n" + "="*60)
    print("TEST: QR-Code Validation")
    print("="*60)
    
    try:
        is_valid, patient_id = qr_code_validate.check_qr_code()
        print(f"✓ QR-Code Validation: Valid={is_valid}, Patient ID={patient_id}")
    except Exception as e:
        print(f"✗ Fehler: {e}")


def test_qr_code_creation():
    print("\n" + "="*60)
    print("TEST: QR-Code Creation")
    print("="*60)
    
    try:
        qr_code_create.create_qr_code()
        print(f"✓ QR-Codes erstellt in: {paths_dir.QR_CODE_DIR}")
    except Exception as e:
        print(f"✗ Fehler: {e}")


def test_patient_download():
    print("\n" + "="*60)
    print("TEST: Patient Download")
    print("="*60)
    
    try:
        patients = patient_database_download.download_patients()
        print(f"✓ {len(patients)} Patienten geladen")
        if patients:
            print(f"   Beispiel: {patients[0]}")
    except Exception as e:
        print(f"✗ Fehler: {e}")


def test_patient_json_load():
    print("\n" + "="*60)
    print("TEST: Patient JSON Load")
    print("="*60)
    
    try:
        patients = fill_in_patient.load_patients()
        if patients:
            print(f"✓ {len(patients)} Patienten aus JSON geladen")
            print(f"   Erster Patient: {patients[0].get('firstname')} {patients[0].get('lastname')}")
        else:
            print("✗ Keine Patienten gefunden")
    except Exception as e:
        print(f"✗ Fehler: {e}")


def test_start_gui():
    print("\n" + "="*60)
    print("TEST: Start GUI")
    print("="*60)
    
    try:
        start_screen = PatientStartScreen()
        start_screen.run()
        print("✓ Start GUI geschlossen")
    except Exception as e:
        print(f"✗ Fehler: {e}")


def test_result_gui():
    print("\n" + "="*60)
    print("TEST: Result GUI (OHNE Diagramme)")
    print("="*60)
    
    scenarios = [
        {
            'name': 'Beide Ohren OK',
            'left': 'green',
            'right': 'green',
            'warning_left': False,
            'warning_right': False
        },
        {
            'name': 'Hochtonverlust Links',
            'left': 'yellow',
            'right': 'green',
            'warning_left': True,
            'warning_right': False
        },
        {
            'name': 'Kritisch Rechts',
            'left': 'green',
            'right': 'red',
            'warning_left': False,
            'warning_right': True
        },
    ]
    
    print("Wähle Szenario:")
    for i, scenario in enumerate(scenarios, 1):
        print(f"  {i}. {scenario['name']}")
    
    try:
        choice = int(input("Auswahl (1-3): ")) - 1
        scenario = scenarios[choice]
        
        gui = EvaluationGUI(
            left_result=scenario['left'],
            right_result=scenario['right'],
            high_freq_warning_left=scenario['warning_left'],
            high_freq_warning_right=scenario['warning_right']
        )
        gui.run()
        print(f"✓ GUI Test abgeschlossen: {scenario['name']}")
    except Exception as e:
        print(f"✗ Fehler: {e}")

def test_result_gui_with_diagrams():
    print("\n" + "="*60)
    print("TEST: Result GUI MIT Diagrammen")
    print("="*60)
    print("Nutzt neueste XML-Datei aus SAVED_TESTS_DIR")
    
    try:
        xml_files = list(paths_dir.SAVED_TESTS_DIR.glob("*.xml"))
        
        if not xml_files:
            print("✗ Keine XML-Dateien gefunden")
            return
        
        latest_xml = max(xml_files, key=lambda x: x.stat().st_mtime)
        print(f"Verwende XML: {latest_xml.name}")
        
        patient_data = test_evaluator.read_patient_xml(latest_xml)
        
        with open(paths_dir.THRESHOLDS_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        results = test_evaluator.evaluate_patient(patient_data, config)
        
        gui = EvaluationGUI(
            left_result=results['left']['color'],
            right_result=results['right']['color'],
            high_freq_warning_left=results['left']['high_freq_warning'],
            high_freq_warning_right=results['right']['high_freq_warning'],
            patient_data=patient_data
        )
        gui.run()
        print("✓ GUI mit Diagrammen abgeschlossen")
    except Exception as e:
        print(f"✗ Fehler: {e}")
        import traceback
        traceback.print_exc()

def test_pdf_generation():
    print("\n" + "="*60)
    print("TEST: PDF Generation")
    print("="*60)
    print("Erstellt PDF aus neuester XML-Datei")
    
    try:
        import pdf_generator
        
        xml_files = list(paths_dir.SAVED_TESTS_DIR.glob("*.xml"))
        
        if not xml_files:
            print("✗ Keine XML-Dateien gefunden")
            return
        
        latest_xml = max(xml_files, key=lambda x: x.stat().st_mtime)
        print(f"Verwende XML: {latest_xml.name}")
        
        with open(paths_dir.THRESHOLDS_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        pdf_path = pdf_generator.generate_report_for_patient(latest_xml, config)
        
        print(f"✓ PDF erstellt: {pdf_path}")
        print(f"  Größe: {pdf_path.stat().st_size / 1024:.1f} KB")
        
    except Exception as e:
        print(f"✗ Fehler: {e}")
        import traceback
        traceback.print_exc()

def test_patient_removal():
    print("\n" + "="*60)
    print("TEST: Patient Removal")
    print("="*60)
    
    try:
        patients = fill_in_patient.load_patients()
        if not patients:
            print("✗ Keine Patienten in JSON")
            return
        
        print(f"Aktuelle Patienten: {len(patients)}")
        for i, p in enumerate(patients[:3], 1):
            print(f"  {i}. ID: {p.get('id')} - {p.get('firstname')} {p.get('lastname')}")
        
        if len(patients) > 3:
            print(f"  ... und {len(patients)-3} weitere")
        
        patient_id = input("\nPatient-ID zum Entfernen (oder Enter für Abbruch): ").strip()
        
        if not patient_id:
            print("Abgebrochen")
            return
        
        try:
            patient_id = int(patient_id)
        except:
            print("✗ Ungültige ID")
            return
        
        success = patient_manager.remove_patient_from_json(patient_id)
        
        if success:
            remaining = patient_manager.get_patient_count()
            print(f"✓ Patient entfernt. Verbleibend: {remaining}")
        else:
            print("✗ Patient konnte nicht entfernt werden")
        
    except Exception as e:
        print(f"✗ Fehler: {e}")

def test_test_in_progress_gui():
    print("\n" + "="*60)
    print("TEST: Test In Progress GUI")
    print("="*60)
    
    try:
        blackscreen = TestBlackScreen()
        blackscreen.run()
    except Exception as e:
        print(f"✗ Fehler: {e}")

def test_maico_detection():
    print("\n" + "="*60)
    print("TEST: Maico Detection")
    print("="*60)
    
    try:
        is_running = fill_in_patient.is_maico_running()
        is_focused = fill_in_patient.is_maico_in_focus()
        
        print("\n" + "="*60)
        print(f"Maico läuft: {is_running}")
        print(f"Maico im Fokus: {is_focused}")
        
        if is_running:
            print("Maico erkannt")
        else:
            print("Maico nicht gestartet")
        
        while True:
            time.sleep(2)
            os.system('cls' if os.name == 'nt' else 'clear')
            is_running = fill_in_patient.is_maico_running()
            is_focused = fill_in_patient.is_maico_in_focus()
            print("\n" + "="*60)
            print(f"Maico läuft: {is_running}")
            print(f"Maico im Fokus: {is_focused}")
    except KeyboardInterrupt:
        print("\nProgramm abgebrochen")
    except Exception as e:
        print(f"\nFehler: {e}")


def test_ma33_detection():
    print("\n" + "="*60)
    print("TEST: MA33 Detection")
    print("="*60)
    
    try:
        is_running = gui_utils.check_if_ma33_is_running()
        is_focused = gui_utils.check_if_ma33_is_in_focus()
        
        print("\n" + "="*60)
        print(f"MA33 läuft: {is_running}")
        print(f"MA33 im Fokus: {is_focused}")
        
        if is_running:
            print("MA33 erkannt")
        else:
            print("MA33 nicht gestartet")
        
        while True:
            time.sleep(2)
            os.system('cls' if os.name == 'nt' else 'clear')
            is_running = gui_utils.check_if_ma33_is_running()
            is_focused = gui_utils.check_if_ma33_is_in_focus()
            print("\n" + "="*60)
            print(f"MA33 lautet: {is_running}")
            print(f"MA33 im Fokus: {is_focused}")
    except KeyboardInterrupt:
        print("\nProgramm abgebrochen")
    except Exception as e:
        print(f"\nFehler: {e}")

def test_patient_input():
    print("\n" + "="*60)
    print("TEST: Patient Input")
    print("="*60)
    fill_in_patient.force_maico_focus()
    
    try:
        patients = fill_in_patient.load_patients()
        if patients:
            print(f"Teste mit Patient: {patients[0].get('firstname')} {patients[0].get('lastname')}")
            fill_in_patient.enter_patient(patients[0])
            print("✓ Patienten-Eingabe abgeschlossen")
        else:
            print("✗ Keine Patienten geladen")
    except Exception as e:
        print(f"✗ Fehler: {e}")


def test_hearing_test():
    print("\n" + "="*60)
    print("TEST: Hearing Test Sequence")
    print("="*60)
    print("⚠ ACHTUNG: MA33 muss laufen!")
    
    proceed = input("Fortfahren? (j/n): ").lower()
    if proceed != 'j':
        print("Test abgebrochen")
        return
    
    try:
        result = hearing_test_automation.execute_hearing_test_sequence()
        if result:
            print("✓ Hörtest-Sequenz erfolgreich gestartet")
        else:
            print("✗ Hörtest konnte nicht gestartet werden")
    except Exception as e:
        print(f"✗ Fehler: {e}")


def test_xml_reading():
    print("\n" + "="*60)
    print("TEST: XML Reading")
    print("="*60)
    
    try:
        xml_files = list(paths_dir.SAVED_TESTS_DIR.glob("*.xml"))
        
        if not xml_files:
            print("⚠ Keine XML-Dateien gefunden")
            return
        
        print(f"Gefundene XML-Dateien: {len(xml_files)}")
        
        latest_xml = max(xml_files, key=lambda x: x.stat().st_mtime)
        print(f"Teste mit: {latest_xml.name}")
        
        patient_data = test_evaluator.read_patient_xml(latest_xml)
        
        print("\nPatient Info:")
        print(f"  ID: {patient_data['patient_info']['id']}")
        print(f"  Name: {patient_data['patient_info']['name']}")
        print(f"  Geburtsdatum: {patient_data['patient_info']['birthdate']}")
        
        print("\nRechtes Ohr:")
        print(f"  {patient_data['right_ear']}")
        
        print("\nLinkes Ohr:")
        print(f"  {patient_data['left_ear']}")
        
        print("\n✓ XML erfolgreich ausgelesen")
    except Exception as e:
        print(f"✗ Fehler: {e}")


def test_evaluation_logic():
    print("\n" + "="*60)
    print("TEST: Evaluation Logic")
    print("="*60)
    
    try:
        with open(paths_dir.THRESHOLDS_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
    except:
        print("✗ Config-Datei nicht gefunden")
        return
    
    test_cases = [
        {
            'name': 'Normales Gehör',
            'data': {500: 10, 1000: 15, 2000: 10, 4000: 15}
        },
        {
            'name': 'Leichter Hochtonverlust',
            'data': {500: 10, 1000: 15, 2000: 20, 3000: 30, 4000: 35, 6000: 30, 8000: 35}
        },
        {
            'name': 'Deutlicher Hörverlust',
            'data': {500: 25, 1000: 30, 2000: 40, 4000: 50}
        },
    ]
    
    for test_case in test_cases:
        print(f"\nSzenario: {test_case['name']}")
        result = test_evaluator.evaluate_ears(test_case['data'], config)
        print(f"  Farbe: {result['color']}")
        print(f"  Hochton-Warnung: {result['high_freq_warning']}")


def test_filename_generation():
    print("\n" + "="*60)
    print("TEST: Filename Generation")
    print("="*60)
    
    try:
        patient_data = generate_file_name.get_patient_data()
        filename = generate_file_name.create_filename_from_patient(patient_data)
        print(f"✓ Generierter Dateiname: {filename}")
    except Exception as e:
        print(f"✗ Fehler: {e}")
def test_archive():
    print("\n" + "="*60)
    print("TEST: Archive")
    print("="*60)
    try:
        patient_manager.move_to_test_archive()
    except Exception as e:
        print(f"✗ Fehler: {e}")

def run_full_workflow():
    print("\n" + "="*60)
    print("FULL WORKFLOW")
    print("="*60)
    print("⚠ Dies führt den kompletten Programmablauf aus!")
    
    proceed = input("Wirklich starten? (j/n): ").lower()
    if proceed != 'j':
        print("Workflow abgebrochen")
        return
    
    try:
        import main
        main.main()
        print("✓ Workflow abgeschlossen")
    except Exception as e:
        print(f"✗ Fehler: {e}")
    return None


def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║                    HÖRZELLEN PLAYGROUND                        ║
║                                                                ║
║  Testumgebung für einzelne Module und Funktionen               ║
║  Bearbeite TEST_CONFIG um Tests zu aktivieren/deaktivieren     ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    active_tests = [key for key, value in TEST_CONFIG.items() if value]
    
    if not active_tests:
        print("⚠ Keine Tests aktiviert!")
        print("   Bearbeite TEST_CONFIG am Anfang der Datei")
        return
    
    print(f"Aktive Tests: {len(active_tests)}")
    print("-" * 60)
    
    test_functions = {
        "test_qr_code_validation": test_qr_code_validation,
        "test_qr_code_creation": test_qr_code_creation,
        "test_patient_download": test_patient_download,
        "test_patient_json_load": test_patient_json_load,
        "test_start_gui": test_start_gui,
        "test_result_gui": test_result_gui,
        "test_result_gui_with_diagrams": test_result_gui_with_diagrams,
        "test_pdf_generation": test_pdf_generation,
        "test_patient_removal": test_patient_removal,
        "test_maico_detection": test_maico_detection,
        "test_ma33_detection": test_ma33_detection,
        "test_patient_input": test_patient_input,
        "test_hearing_test": test_hearing_test,
        "test_xml_reading": test_xml_reading,
        "test_evaluation_logic": test_evaluation_logic,
        "test_filename_generation": test_filename_generation,
        "run_full_workflow": run_full_workflow,
        "test_test_in_progress_gui": test_test_in_progress_gui,
        "check_directories": paths_dir.ensure_directories_exist,
        "move_to_archive": test_archive   
    }
    
    for test_name in active_tests:
        if test_name in test_functions:
            try:
                test_functions[test_name]()
            except KeyboardInterrupt:
                print("\n⚠ Test durch Benutzer abgebrochen")
                break
            except Exception as e:
                print(f"✗ Unerwarteter Fehler: {e}")
    
    print("\n" + "="*60)
    print("PLAYGROUND BEENDET")
    print("="*60)


if __name__ == "__main__":
    main()
