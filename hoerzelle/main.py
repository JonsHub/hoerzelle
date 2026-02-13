import fill_in_patient
import hearing_test_automation
import qr_code_validate
import test_start_gui
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

    try:
        fill_in_patient.run_automation()
        hearing_test_automation.runner()
        hearing_test_automation.archive_xml()
    except Exception as exception:
        print(f"Error during test execution: {exception}")
        return
        
if __name__ == "__main__":
    main()