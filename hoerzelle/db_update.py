import time
import patient_manager

from datetime import datetime, timedelta

POLL_INTERVAL_MINUTES = 60
last_update = None

def should_update_patients():
    global last_update
    if last_update is None:
        return True
    elapsed = datetime.now() - last_update
    return elapsed > timedelta(minutes=POLL_INTERVAL_MINUTES)

def update_patients_if_needed():
    if should_update_patients():
        patient_manager.get_all_patients()
        last_update = datetime.now()
        print(f"Patient list updated at {last_update}")

def main():
    while True:
        update_patients_if_needed()
        time.sleep(60)

if __name__ == "__main__":
    main()