import patient_save, patient_download

def patient_runner():
    patients_list = patient_download.download_patients()
    patient_save.save_patients(patients_list)
    return patients_list