import xml.etree.ElementTree as ET

def get_text_safe(element, tag):
    found = element.find(tag)
    return found.text if found is not None else None

def read_patient_xml(xml_path):
    tree = ET.parse(xml_path)
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
                freq = int(result.get('frequency', 0))
                volume = result.get('volume', '')                
                if volume and volume.strip():
                    db = float(volume)
                    
                    if ear == 'right':
                        right_ear[freq] = db
                    elif ear == 'left':
                        left_ear[freq] = db
    
    return {
        'patient_info': patient_info,
        'right_ear': right_ear,
        'left_ear': left_ear
    }
    
def evaluate_ears(ear_data, config):
    """
    Evaluates the results of a hearing test for one ear.

    :param ear_data: A dictionary containing the hearing test results for one ear.
    :param config: A dictionary containing the thresholds and special rules for the evaluation.

    :return: A dictionary containing the color and high frequency warning for the evaluated ear.
    :rtype: dict
    """

    if not ear_data:
        return {'color': 'green', 'high_freq_warning': False}
    
    override = config['override_thresholds']
    pta4_thresholds = config['pta4_thresholds']
    special = config['special_thresholds']
    warning = config['additional_warning_flag']
    
    pta4_frequencies = [500, 1000, 2000, 4000]
    high_frequencies = [3000, 4000, 6000, 8000]
    
    red_count = 0
    yellow_count = 0
    high_freq_yellow_count = 0
    
    for freq, db in ear_data.items():
        if db >= 40:
            red_count += 1
        elif db >= 25:
            yellow_count += 1
        
        if freq in high_frequencies and db >= 25:
            high_freq_yellow_count += 1
    
    if red_count >= override['min_red_count']:
        return {
            'color': 'red',
            'high_freq_warning': high_freq_yellow_count >= warning['high_frequency_max_yellow_count']
        }
    
    for db in ear_data.values():
        if db >= override['min_yellow_db_any']:
            return {
                'color': 'yellow',
                'high_freq_warning': high_freq_yellow_count >= warning['high_frequency_max_yellow_count']
            }
    
    pta4_values = [ear_data.get(f, None) for f in pta4_frequencies]
    pta4_values = [v for v in pta4_values if v is not None]
    
    if not pta4_values:
        return {'color': 'green', 'high_freq_warning': False}
    
    pta4_average = sum(pta4_values) / len(pta4_values)
    
    if pta4_average < pta4_thresholds['green_max']:
        color = 'green'
        if (yellow_count + red_count) >= special['make_yellow_even_if_green_max_count']:
            color = 'yellow'
    elif pta4_average < pta4_thresholds['yellow_max']:
        color = 'yellow'
        if red_count >= special['make_red_even_if_yellow_max_count']:
            color = 'red'
    else:
        color = 'red'
    
    high_freq_warning = high_freq_yellow_count >= warning['high_frequency_max_yellow_count']
    
    return {'color': color, 'high_freq_warning': high_freq_warning}

def evaluate_patient(patient_data, config):
    """
    Evaluates the results of a hearing test for both ears.

    :param patient_data: A dictionary containing the hearing test results for both ears.
    :param config: A dictionary containing the thresholds and special rules for the evaluation.

    :return: A dictionary containing the evaluation results for both ears.
    :rtype: dict
    """
    left_result = evaluate_ears(patient_data['left_ear'], config)
    right_result = evaluate_ears(patient_data['right_ear'], config)
    
    return {
        'left': left_result,
        'right': right_result
    }