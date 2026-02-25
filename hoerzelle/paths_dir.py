from pathlib import Path

BASE_DIR = Path(__file__).parent

#folders
DATA_DIR = BASE_DIR / "data"
QR_CODE_DIR = DATA_DIR / "qr_codes"
SAVED_PATIENTS_DIR = DATA_DIR / "saved_patients"
SAVED_TESTS_DIR = DATA_DIR / "saved_tests"
XML_PORT = DATA_DIR / "xml_port"
IMAGES_DIR = BASE_DIR / "images"
LOG_DIR = BASE_DIR / "logs"

#files
JSON_FILE = SAVED_PATIENTS_DIR / "patients.json"
THRESHOLDS_FILE = DATA_DIR / "evaluation_config.json"
IN_XML = DATA_DIR / XML_PORT / "in.xml"