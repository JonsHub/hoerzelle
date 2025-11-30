import psutil
import time
import pyautogui
import win32gui
import win32process

BUTTON_COORDINATES = {
    'autotest': (633, 74),
    'play': (593, 761),
    'drucken': (885, 885),
    'save_dialog_ok': (913, 731),
    'speichern_beenden': (1030, 891),
    'ja_uebernehmen': (551, 547),
}

def check_if_ma33_is_running() -> bool:
    for process in psutil.process_iter(['name']):
        try:
            if process.info['name'].lower() == 'ma33.exe':
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def find_ma33_window_handle():
    def enum_callback(hwnd, window_handles):
        if win32gui.IsWindowVisible(hwnd):
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(process_id)
                if process.name().lower() == 'ma33.exe':
                    window_handles.append(hwnd)
            except:
                pass
        return True
    
    window_handles = []
    win32gui.EnumWindows(enum_callback, window_handles)
    
    return window_handles[0] if window_handles else None

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
    time.sleep(2)

def execute_hearing_test_sequence():
    print("\n" + "=" * 60)
    print("START HEARING TEST")
    print("=" * 60)
    
    wait_until_ma33_starts()
    
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

def finish_and_save_test():
    print("\n" + "=" * 60)
    print("FINISH AND SAVE TEST")
    print("=" * 60)
    
    print("\nStep 1: Clicking Drucken button...")
    if not click_button_relative_to_ma33_window('drucken'):
        print("FAILED")
        return False
    
    time.sleep(2)

    print("\nStep 2: Clicking OK in save dialog...")
    if not click_button_relative_to_ma33_window('save_dialog_ok'):
        print("FAILED")
        return False
    
    time.sleep(2)
    
    print("\nStep 2: Windows save dialog opened")
    print("Waiting for manual filename input...")
    input("Enter filename manually, then press Enter here to continue...")
    
    print("\nStep 3: 3x TAB to navigate to save button...")
    for i in range(3):
        pyautogui.press('tab')
        time.sleep(0.3)
    
    print("\nStep 4: SPACE to save...")
    pyautogui.press('space')
    time.sleep(2)
    
    print("\nStep 5: Clicking Speichern und Beenden...")
    if not click_button_relative_to_ma33_window('speichern_beenden'):
        print("FAILED")
        return False
    
    time.sleep(1)
    
    print("\nStep 6: Clicking Ja (Messwerte übernehmen)...")
    if not click_button_relative_to_ma33_window('ja_uebernehmen'):
        print("FAILED")
        return False
    
    print("\n" + "=" * 60)
    print("SUCCESS: Test saved and finished!")
    print("=" * 60)
    
    return True

def test_individual_button():
    print("\n" + "=" * 60)
    print("BUTTON TEST")
    print("=" * 60)
    
    print("\nAvailable buttons:")
    button_list = list(BUTTON_COORDINATES.keys())
    
    for index, button_name in enumerate(button_list, 1):
        coordinates = BUTTON_COORDINATES[button_name]
        print(f"{index}. {button_name} at relative position {coordinates}")
    
    choice = input("\nSelect button number: ")
    
    try:
        selected_button = button_list[int(choice) - 1]
        
        print(f"\nTesting: {selected_button}")
        print("Make sure ma33.exe window is visible!")
        input("Press Enter to click...")
        
        if click_button_relative_to_ma33_window(selected_button):
            print(f"\nSUCCESS")
        else:
            print(f"\nFAILED")
            
    except (ValueError, IndexError):
        print("Invalid selection")

def display_main_menu():
    print("\n" + "=" * 60)
    print("MA33 HEARING TEST AUTOMATION")
    print("=" * 60)
    
    print("\n1. Start hearing test (Autotest + Play)")
    print("2. Finish and save test (Drucken + Save + Beenden)")
    print("3. Test individual button")
    print("4. Exit")
    
    choice = input("\nSelect option: ")
    
    if choice == "1":
        execute_hearing_test_sequence()
    elif choice == "2":
        finish_and_save_test()
    elif choice == "3":
        test_individual_button()
    else:
        print("Exiting...")

if __name__ == '__main__':
    try:
        display_main_menu()
    except KeyboardInterrupt:
        print("\n\nAborted!")