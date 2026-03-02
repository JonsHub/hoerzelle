import fill_in_patient
import hearing_test_automation
import qr_code_validate
import test_evaluator
import patient_manager
import pdf_generator
import json
import test_start_gui
import paths_dir
import time
import maico_handler
from test_result_gui import EvaluationGUI

def main():
    paths_dir.ensure_directories_exist
    max_qr_attempts = 3
    attempt_count = 0
    current_patient_id = None
    
    while attempt_count < max_qr_attempts:
        try:
            is_valid, scanned_patient_id = qr_code_validate.check_qr_code()
            if is_valid and scanned_patient_id:
                current_patient_id = scanned_patient_id
                print(f"QR Code valid for patient ID: {current_patient_id}")
                break
            else:
                attempt_count += 1
                if attempt_count < max_qr_attempts:
                    print(f"Invalid QR. Attempt {attempt_count}/{max_qr_attempts}")
                    time.sleep(2)
        except Exception as exception:
            print(f"Error validating QR code: {exception}")
            attempt_count += 1
            time.sleep(2)
    
    if not current_patient_id:
        print("QR validation failed after max attempts. Exiting.")
        return False
    
    start_screen = test_start_gui.PatientStartScreen()
    start_screen.run()
    
    fill_in_patient.run_automation()
    
    hearing_test_automation.runner()
    
    with open(paths_dir.THRESHOLDS_FILE, "r", encoding="utf-8") as file:
        config = json.load(file)
    
    xml_files = list(paths_dir.SAVED_TESTS_DIR.glob("*.xml"))
    
    if not xml_files:
        print("No XML files found in SAVED_TESTS_DIR.")
        return False
    
    xml_path = max(xml_files, key=lambda x: x.stat().st_mtime)
    patient_data = test_evaluator.read_patient_xml(xml_path)
    
    results = test_evaluator.evaluate_patient(patient_data, config)
    
    try:
        pdf_path = pdf_generator.generate_report_for_patient(xml_path, config)
        print(f"PDF report generated: {pdf_path}")
    except Exception as e:
        print(f"Warning: Could not generate PDF: {e}")
    
    gui = EvaluationGUI(
        left_result=results['left']['color'],
        right_result=results['right']['color'],
        high_freq_warning_left=results['left']['high_freq_warning'],
        high_freq_warning_right=results['right']['high_freq_warning'],
        patient_data=patient_data
    )
    gui.run()
    
    try:
        hearing_test_automation.rename_xml_file()
    except Exception as exception:
        print(f"Error renaming XML file: {exception}")
    
    time.sleep(2)
        
    try:
        patient_manager.move_to_test_archive()
    except Exception as exception:
        print(f"Error moving patient to test archive: {exception}")
    
    try:
        patient_manager.remove_patient_from_json(current_patient_id)
        remaining = patient_manager.get_patient_count()
        print(f"Patient removed from queue. Remaining patients: {remaining}")
    except Exception as exception:
        print(f"Error removing patient from queue: {exception}")
    
    time.sleep(5)
    maico_handler.restart_maico()
    return True

def run_kiosk():
    while True:
        print("System ready. Waiting for patient to scan QR code...")
        success = main()
        if success:
            print("Patient processed successfully. Waiting for next patient...")
        else:
            print("Error processing patient. Restart in 5 seconds...")
            time.sleep(5)
            continue

if __name__ == "__main__":
    run_kiosk()