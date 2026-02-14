import fill_in_patient
import hearing_test_automation
import qr_code_validate
import test_evaluator
import json
import test_start_gui
import paths
from test_result_gui import EvaluationGUI
def main():
    try:
        is_valid = qr_code_validate.check_qr_code()
    except Exception as exception:
        print(f"Error validating QR code: {exception}")
        return
    if not is_valid:
        return
    
    start_screen = test_start_gui.PatientStartScreen()
    start_screen.run()
    fill_in_patient.run_automation()
    hearing_test_automation.runner()
    
    with open(paths.THRESHOLDS_FILE, "r", encoding="utf-8") as file:
        config = json.load(file)
    
    
    xml_files = list(paths.SAVED_TESTS_DIR.glob("*.xml"))
    
    if not xml_files:
        print("No XML files found in SAVED_TESTS_DIR.")
        return
    xml_path = max(xml_files, key=lambda x: x.stat().st_mtime)
    patient_data = test_evaluator.read_patient_xml(xml_path)
    
    results = test_evaluator.evaluate_patient(patient_data, config)
        
    gui = EvaluationGUI(
        left_result=results['left']['color'],
        right_result=results['right']['color'],
        high_freq_warning_left=results['left']['high_freq_warning'],
        high_freq_warning_right=results['right']['high_freq_warning']
    )
    gui.run()
    
    
def test_export():
    from hearing_test_automation import archive_xml
    archive_xml() #TODO: fix folder logic test if test works and moves xml to correct folder
if __name__ == "__main__":
    test_export()