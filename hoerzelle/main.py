from core import fill_in_patient
from core import hearing_test_automation

def main():
    fill_in_patient.run_automation()
    hearing_test_automation.runner()

if __name__ == "__main__":
    main()