import window_config
import generate_file_name
import gui_utils
import time
import pyautogui

def execute_hearing_test_sequence():
    
    gui_utils.wait_until_ma33_starts()
    pyautogui.press("space")
    
    if not gui_utils.check_if_ma33_is_in_focus():
        return False
    
    print("\n" + "=" * 60)
    print("START HEARING TEST")
    print("=" * 60)

    time.sleep(2)
    
    print("\nStep 1: Clicking Autotest button...")
    if not gui_utils.click_button_relative_to_ma33_window('autotest'):
        print("FAILED")
        return False
    time.sleep(2)
    
    print("\nStep 2: Clicking Play button...")
    if not gui_utils.click_button_relative_to_ma33_window('play'):
        print("FAILED")
        return False
    
    print("\n" + "=" * 60)
    print("SUCCESS: Hearing test started!")
    print("Test is now running...")
    print("=" * 60)
    
    return True
def test_waiting():
    print("Waiting for test to start...")
    gui_utils.wait_for_instruction_window_to_appear(window_config.WINDOW_TITLES['test_start'])
    gui_utils.wait_for_audio_and_window_to_close(window_config.WINDOW_TITLES['test_start'], audio_duration=12)

    print("\n" + "="*40)
    print("--- TEST IS NOW RUNNING ---")
    
    print("Program pauses until the 'test_end' window appears...")
    print("="*40)

    gui_utils.wait_for_instruction_window_to_appear(window_config.WINDOW_TITLES['test_end'])
    gui_utils.wait_for_audio_and_window_to_close(window_config.WINDOW_TITLES['test_end'], audio_duration=7)
    print("Ready to save test!")
    
    # TODO: Schalte Bildschirm irgendwie aus
    # TODO: Vielleicht kündige Ohrwechsel an
    # TODO: Schalte Bildschirm wieder an

def finish_and_save_test():
    print("\n" + "=" * 60)
    print("FINISH AND SAVE TEST")
    print("=" * 60)

    while not gui_utils.check_if_ma33_is_in_focus():
        print("ERROR: MA33 not in focus")
        time.sleep(0.5)   
    gui_utils.wait_until_ma33_starts()
    
    print("\nClicking Drucken button...")
    if not gui_utils.click_button_relative_to_ma33_window('drucken'):
        print("FAILED")
        return False
    
    print("\nPrint dialog opened, clicking OK...")
    if not gui_utils.click_in_print_dialog('ok'):
        print("FAILED")
        return False
    
    time.sleep(1.5)
    
    print("Access Folder")
    pyautogui.hotkey("ctrl", "l")
    time.sleep(0.5)
    pyautogui.write("", interval=0.05) #TODO: add maico path
    pyautogui.press("enter")
    for i in range(7):
        pyautogui.press("tab")
        time.sleep(0.3)
    
    print("\nEntering test name")
    patient_data = generate_file_name.get_patient_data()
    
    if isinstance(patient_data, list) and len(patient_data) > 0:
        current_patient = patient_data[0]
        time.sleep(1.5)
        generate_file_name.enter_filename(current_patient)
    
    time.sleep(1)
    
    print("\n3x TAB to navigate to save button...")
    for _ in range(3):
        pyautogui.press('tab')
        time.sleep(0.3)
    
    print("\nSPACE to save...")
    pyautogui.press('space')
    time.sleep(1)
    
    print("\nClicking Speichern und Beenden...")
    if not gui_utils.click_button_relative_to_ma33_window('speichern_beenden'):
        print("FAILED")
        return False
    
    time.sleep(1)
    
    print("\nClicking Ja (Messwerte übernehmen)...")
    if not gui_utils.click_button_relative_to_ma33_window('ja_uebernehmen'):
        print("FAILED")
        return False
    
    print("\n" + "=" * 60)
    print("SUCCESS: Test saved and finished!")
    print("=" * 60)
    
    return True

def runner():
    execute_hearing_test_sequence()
    test_waiting()
    time.sleep(1.5)
    finish_and_save_test()
    return True