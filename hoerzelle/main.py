import fill_in_patient
import hearing_test_automation
import qr_code_validate

def main():
    try:
        is_valid = qr_code_validate.check_qr_code()
    except KeyboardInterrupt:
        print("Program interrupted by user. Exiting.")
        return
    except Exception as exception:
        print(f"Error during QR code validation: {exception}. Exiting.")
        return
    if is_valid:
        print("QR Code validation successful. Starting automation...")
        try:
            fill_in_patient.run_automation()
            hearing_test_automation.runner()
        except KeyboardInterrupt:
            print("Program interrupted by user. Exiting.")
            return
        except Exception as exception:
            print(f"Error during automation: {exception}. Exiting.")
            return

if __name__ == "__main__":
    main()