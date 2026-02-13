from pathlib import Path
import json
import xml.etree.ElementTree as ET

BASE_DIR = Path(".")
THRESHOLDS_FILE = BASE_DIR / "data" / "evaluation_config.json"
TEST_RESULTS_PATH = BASE_DIR / "data" / "saved_tests"

with open(THRESHOLDS_FILE, "r", encoding="utf-8") as file:
    threshold_json = json.load(file)

def get_text_safe(element, tag):
    found = element.find(tag)
    return found.text if found is not None else None

def read_in_xml(test_results_path):
    results = []
    
    xml_files = list(test_results_path.glob("*.xml"))
    
    if not xml_files:
        print(f"Keine XML-Dateien in {test_results_path} gefunden!")
        return results
    
    for xml_file in xml_files:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            patient_info = {
                'id': get_text_safe(root, 'idpatient'),
                'name': f"{get_text_safe(root, 'prenom')} {get_text_safe(root, 'nom')}" 
                    if root.find('prenom') is not None and root.find('nom') is not None 
                    else None,
                'birthdate': get_text_safe(root, 'datedenaissance'),
                'sex': get_text_safe(root, 'sexe'),
                'exam_date': get_text_safe(root, 'dateexamen')
            }
            
            right_ear = {}
            left_ear = {}
            
            audio = root.find('audio')
            if audio is not None:
                for test in audio.findall('test'):
                    ear = test.get('ear')
                    
                    for result in test.findall('result'):
                        freq = result.get('frequency')
                        volume = result.get('volume')
                        
                        
                        if volume and volume.strip():
                            db = float(volume)
                            
                            if ear == 'right':
                                right_ear[freq] = db
                            elif ear == 'left':
                                left_ear[freq] = db
            
            results.append({
                'filename': xml_file.name,
                'patient_info': patient_info,
                'right_ear': right_ear,
                'left_ear': left_ear
            })
            
        except Exception as e:
            print(f"Fehler beim Parsen von {xml_file.name}: {e}")
            continue
    
    return results

def evaluate_ears(ear_data, config):
    override = config['override_thresholds']
    pta4 = config['pta4_thresholds']
    special = config['special_thresholds']
    warning = config['additional_warning_flag']
    
    pta4_frequencies = [500, 1000, 2000, 4000]
    high_frequencies = [3000, 4000, 6000, 8000]
    
    red_count = 0
    yellow_count = 0
    high_freq_yellow_count = 0
    
    for freq, db in ear_data.items():
        freq_int = int(freq)
        
        if db >= 40:
            red_count += 1
        elif db >= 25:
            yellow_count += 1
        
        if freq_int in high_frequencies and db >= 25:
            high_freq_yellow_count += 1
    
    if red_count >= override['min_red_count']:
        return {'color': 'red', 'high_freq_warning': high_freq_yellow_count >= warning['high_frequency_max_yellow_count']}
    
    for db in ear_data.values():
        if db >= override['min_yellow_db_any']:
            color = 'yellow'
            break
    else:
        pta4_values = [ear_data.get(str(f), 0) for f in pta4_frequencies if str(f) in ear_data]
        
        if not pta4_values:
            return {'color': 'green', 'high_freq_warning': False}
        
        pta4_avg = sum(pta4_values) / len(pta4_values)
        
        if pta4_avg < pta4['green_max']:
            color = 'green'
            if yellow_count + red_count >= special['make_yellow_even_if_green_max_count']:
                color = 'yellow'
        elif pta4_avg < pta4['yellow_max']:
            color = 'yellow'
            if red_count >= special['make_red_even_if_yellow_max_count']:
                color = 'red'
        else:
            color = 'red'
    
    high_freq_warning = high_freq_yellow_count >= warning['high_frequency_max_yellow_count']
    
    return {'color': color, 'high_freq_warning': high_freq_warning}

def evaluate_patient(patient_data, config):
    left_result = evaluate_ears(patient_data['left_ear'], config)
    right_result = evaluate_ears(patient_data['right_ear'], config)
    
    return {
        'left': left_result,
        'right': right_result
    }