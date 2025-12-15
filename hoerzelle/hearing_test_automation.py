import psutil
import time
import pyautogui
import win32gui
import generate_file_name
import win32process

BUTTON_COORDINATES = {
    'autotest': (633, 74),
    'play': (593, 761),
    'drucken': (885, 885),
    'speichern_beenden': (1030, 891),
    'ja_uebernehmen': (551, 547),
}

PRINT_DIALOG_COORDINATES = {
    'ok': (42, 236),
}

WINDOW_TITLES = {
    'test_start': 'Testeinführung',
    'test_end': 'Test beendet'
}

def check_if_ma33_is_in_focus() -> bool:
    while True:
        try:
            foreground_window = win32gui.GetForegroundWindow()
            _, process_id = win32process.GetWindowThreadProcessId(foreground_window)
            process = psutil.Process(process_id)
            if process.name().lower() == 'ma33.exe':
                return True
        except Exception:
            pass
        print("Waiting for MA33 to be in focus...", end="\r")
        time.sleep(0.5)

def check_if_ma33_is_running() -> bool:
    for process in psutil.process_iter(['name']):
        try:
            if process.info['name'].lower() == 'ma33.exe':
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def find_print_dialog_window():
    def enum_callback(handle_window, window_handles):
        if win32gui.IsWindowVisible(handle_window):
            window_title = win32gui.GetWindowText(handle_window)
            if 'druck' in window_title.lower() or 'print' in window_title.lower():
                window_handles.append(handle_window)
        return True
    
    window_handles = []
    win32gui.EnumWindows(enum_callback, window_handles)
    
    return window_handles[0] if window_handles else None

def click_in_print_dialog(button_name: str) -> bool:
    window_handle = find_print_dialog_window()
    
    if not window_handle:
        print(f"ERROR: Print dialog window not found")
        return False
    
    if button_name not in PRINT_DIALOG_COORDINATES:
        print(f"ERROR: Unknown button '{button_name}'")
        return False
    
    window_x, window_y, _, _ = win32gui.GetWindowRect(window_handle)
    relative_x, relative_y = PRINT_DIALOG_COORDINATES[button_name]
    
    absolute_x = window_x + relative_x
    absolute_y = window_y + relative_y
    
    print(f"Clicking {button_name} in print dialog: window({window_x},{window_y}) + relative({relative_x},{relative_y}) = absolute({absolute_x},{absolute_y})")
    
    pyautogui.click(absolute_x, absolute_y)
    return True

def find_ma33_window_handle():
    def enum_callback(handle_window, window_handles):
        if win32gui.IsWindowVisible(handle_window):
            window_title = win32gui.GetWindowText(handle_window)
            if 'ma33' in window_title.lower():
                window_handles.append(handle_window)
        return True
    
    window_handles = []
    win32gui.EnumWindows(enum_callback, window_handles)
    
    return window_handles[0] if window_handles else None

def check_if_instruction_window_exists(window_title: str) -> bool:
    window_handle = win32gui.FindWindow(None, window_title)
    return window_handle != 0 and window_handle is not None

def wait_for_instruction_window_to_appear(window_title: str):
    print(f"Waiting for window: '{window_title}'")
    
    while not check_if_instruction_window_exists(window_title):
        print(f"  Still waiting...", end="\r")
        time.sleep(0.5)
    
    print(f"\n  FOUND: '{window_title}'!")
    time.sleep(1)

def wait_for_audio_and_window_to_close(window_title: str, audio_duration: int):
    print(f"Window '{window_title}' is visible. Waiting {audio_duration}s for audio instructions...")
    time.sleep(audio_duration)
    print(f"  Audio instructions finished ({audio_duration}s).")

    print(f"Waiting for window to close: '{window_title}'")
    while check_if_instruction_window_exists(window_title): 
        print(f"  Window still open...", end="\r")
        time.sleep(0.5)
    
    print(f"\n  CLOSED: '{window_title}'!")

def click_button_relative_to_ma33_window(button_name: str) -> bool:
    window_handle = find_ma33_window_handle()
    
    if not window_handle:
        print(f"ERROR: MA33 window not found")
        return False
    
    if button_name not in BUTTON_COORDINATES:
        print(f"ERROR: Unknown button '{button_name}'")
        return False
    
    window_x, window_y, _, _ = win32gui.GetWindowRect(window_handle)
    relative_x, relative_y = BUTTON_COORDINATES[button_name]
    
    absolute_x = window_x + relative_x
    absolute_y = window_y + relative_y
    
    print(f"Clicking {button_name}: window({window_x},{window_y}) + relative({relative_x},{relative_y}) = absolute({absolute_x},{absolute_y})")
    
    pyautogui.click(absolute_x, absolute_y)
    return True

def wait_until_ma33_starts():
    print("Waiting for ma33.exe to start...")
    
    while not check_if_ma33_is_running():
        time.sleep(1)
    
    print("ma33.exe detected!")
    time.sleep(0.5)

def execute_hearing_test_sequence():
    
    wait_until_ma33_starts()
    pyautogui.press("space")
    
    if not check_if_ma33_is_in_focus():
        return False
    
    print("\n" + "=" * 60)
    print("START HEARING TEST")
    print("=" * 60)

    time.sleep(2)
    
    print("\nStep 1: Clicking Autotest button...")
    if not click_button_relative_to_ma33_window('autotest'):
        print("FAILED")
        return False
    time.sleep(2)
    
    print("\nStep 2: Clicking Play button...")
    if not click_button_relative_to_ma33_window('play'):
        print("FAILED")
        return False
    
    print("\n" + "=" * 60)
    print("SUCCESS: Hearing test started!")
    print("Test is now running...")
    print("=" * 60)
    

    return True
def test_waiting():
    print("Waiting for test to start...")
    wait_for_instruction_window_to_appear(WINDOW_TITLES['test_start'])
    wait_for_audio_and_window_to_close(WINDOW_TITLES['test_start'], audio_duration=12)

    print("\n" + "="*40)
    print("--- TEST IS NOW RUNNING ---")
    
    print("Program pauses until the 'test_end' window appears...")
    print("="*40)

    wait_for_instruction_window_to_appear(WINDOW_TITLES['test_end'])
    wait_for_audio_and_window_to_close(WINDOW_TITLES['test_end'], audio_duration=7)
    print("Ready to save test!")
    
    # TODO: Schalte Bildschirm irgendwie aus
    # TODO: Vielleicht kündige Ohrwechsel an
    # TODO: Schalte Bildschirm wieder an

def finish_and_save_test():
    print("\n" + "=" * 60)
    print("FINISH AND SAVE TEST")
    print("=" * 60)

    while not check_if_ma33_is_in_focus():
        print("ERROR: MA33 not in focus")
        time.sleep(0.5)   
    wait_until_ma33_starts()
    
    print("\nClicking Drucken button...")
    if not click_button_relative_to_ma33_window('drucken'):
        print("FAILED")
        return False
    
    print("\nPrint dialog opened, clicking OK...")
    if not click_in_print_dialog('ok'):
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
    if not click_button_relative_to_ma33_window('speichern_beenden'):
        print("FAILED")
        return False
    
    time.sleep(1)
    
    print("\nClicking Ja (Messwerte übernehmen)...")
    if not click_button_relative_to_ma33_window('ja_uebernehmen'):
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