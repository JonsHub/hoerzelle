import json
import hashlib
import qrcode
from pathlib import Path

BASE_DIR = Path(".")
JSON_FILE = BASE_DIR / "data" / "patients.json"
QR_DIR = BASE_DIR / "data" / "qr_codes"

SALT = "blackberry pancake bake"

def generate_hash(user_id):
    payload = f"{user_id}{SALT}"
    return hashlib.sha256(payload.encode()).hexdigest()

def create_qr_code():
    QR_DIR.mkdir(parents=True, exist_ok=True)
    if not JSON_FILE.exists():
        print(f"JSON file not found: {JSON_FILE}")
        return
    
    try:
        with open(JSON_FILE, "r") as file:
            patients = json.load(file)
        for patient in patients:
            user_id = patient.get("id")
            if user_id is None:
                print(f"Patient record missing 'id': {patient}")
                continue
            
            hash_value = generate_hash(user_id)
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(hash_value)
            qr.make(fit=True)
            img = qr.make_image(fill="black", back_color="white")
            with open(QR_DIR / f"{user_id}.png", "wb") as f:
                img.save(f)
                print(f"QR code created for user_id: {user_id}")
    except Exception as e:
        print(f"Error processing JSON file: {e}")
    return True