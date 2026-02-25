import cv2
import json
import hashlib
import paths_dir
import patient_manager

SALT = "blackberry pancake bake"

def generate_hash(user_id):
    payload = f"{user_id}{SALT}"
    return hashlib.sha256(payload.encode()).hexdigest()

def check_qr_code():
    if not paths_dir.JSON_FILE.exists():
        print(f"Error: JSON file not found at {paths_dir.JSON_FILE}. Calling patient_manager to download patients.")
        patient_manager.get_all_patients()
        
    with open(paths_dir.JSON_FILE, "r") as file:
        patients = json.load(file)
    
    valid_hashes = {}
    for patient in patients:
        user_id = patient.get("id")
        if user_id is None:
            continue
        hash_value = generate_hash(user_id)
        valid_hashes[hash_value] = user_id 
    
    cv2.namedWindow('QR Code Validation', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('QR Code Validation', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 900)
    cap.set(cv2.CAP_PROP_FPS, 30)
    detector = cv2.QRCodeDetector()
    
    while True:
        camera_return, image = cap.read()
        if not camera_return:
            print("Failed to capture image from camera.")
            break
        
        
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l_channel)
        enhanced = cv2.merge((cl, a_channel, b_channel))
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        data_qr, bbox, _ = detector.detectAndDecode(enhanced)
        if data_qr:
            print(f"QR Code detected: {data_qr}")
            
            if data_qr in valid_hashes:
                patient_id = valid_hashes[data_qr]
                print(f"QR Code is VALID for patient ID: {patient_id}")
                
                if bbox is not None:
                    if bbox is not None:
                        bbox = bbox.astype(int)
                        cv2.polylines(image, [bbox], True, (0, 255, 0), 3)
                        cv2.putText(image, f"VALID: {patient_id}", 
                                (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                                1, (0, 255, 0), 2)
            else:
                print("QR Code is INVALID")
                if bbox is not None:
                    bbox = bbox.astype(int)
                    cv2.polylines(image, [bbox], True, (0, 0, 255), 3)
                    cv2.putText(image, "INVALID", 
                                (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                                1, (0, 0, 255), 2)
            cv2.imshow("QR Code Scanner", image)
            cv2.waitKey(2000)
            break
        
        cv2.imshow("QR Code Scanner", image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("Exiting QR Code scanner.")
            break
    
    cap.release()
    cv2.destroyAllWindows()
    return True