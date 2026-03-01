from pathlib import Path

BASE_DIR = Path(__file__).parent

DATA_DIR = BASE_DIR / "data"
QR_CODE_DIR = DATA_DIR / "qr_codes"
SAVED_PATIENTS_DIR = DATA_DIR / "saved_patients"
SAVED_TESTS_DIR = DATA_DIR / "saved_tests"
XML_PORT = DATA_DIR / "xml_port"
IMAGES_DIR = BASE_DIR / "images"
#LOG_DIR = BASE_DIR / "logs"
ARCHIVE_DIR = DATA_DIR / "archive"

JSON_FILE = SAVED_PATIENTS_DIR / "patients.json"
THRESHOLDS_FILE = DATA_DIR / "evaluation_config.json"
IN_XML = XML_PORT / "in.xml"
OUT_XML = XML_PORT / "out.xml"

def ensure_directories_exist():
    directories = [
        ARCHIVE_DIR,
        DATA_DIR,
        QR_CODE_DIR,
        SAVED_PATIENTS_DIR,
        SAVED_TESTS_DIR,
        XML_PORT,
        IMAGES_DIR,
        #LOG_DIR
    ]
    for directory in directories:
        if not directory.exists():
            print(f"Erstelle Verzeichnis: {directory}")
            directory.mkdir(parents=True, exist_ok=True)

    return None

def get_latest_test_xml():
    xml_files = list(SAVED_TESTS_DIR.glob("*.xml"))
    if not xml_files:
        raise FileNotFoundError(f"Keine XML-Dateien in {SAVED_TESTS_DIR}")
    return max(xml_files, key=lambda x: x.stat().st_mtime)

def get_all_test_xmls():
    return list(SAVED_TESTS_DIR.glob("*.xml"))
