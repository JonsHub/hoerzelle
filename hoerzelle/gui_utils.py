import psutil
import pyperclip
import win32gui
import win32process
import time
import pyautogui
import tkinter as tk
import window_config
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

def get_patient_id():
    time.sleep(0.1)
    pyautogui.doubleClick()
    time.sleep(0.05)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.1)
    patienten_id = pyperclip.paste().strip()
    return patienten_id
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
    
    if button_name not in window_config.BUTTON_COORDINATES:
        print(f"ERROR: Unknown button '{button_name}'")
        return False
    
    window_x, window_y, _, _ = win32gui.GetWindowRect(window_handle)
    relative_x, relative_y = window_config.BUTTON_COORDINATES[button_name]
    
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
    return True

class TestBlackScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Testvorgang")
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="black")
        self.label = tk.Label(
            self.root, 
            text="Testvorgang läuft...", 
            font=("Arial", 49), 
            foreground="white", 
            background="black"
        )
        self.label.pack(fill=tk.BOTH, expand=True)
        self._running = True
        self.root.bind("<Key-q>", lambda e: self.terminate_gui())

    def terminate_gui(self):
        self._running = False
        self.root.destroy()

    def check_and_close(self):
        if check_if_instruction_window_exists(window_config.WINDOW_TITLES['test_end']):
            self._running = False
            self.root.destroy()
        else:
            self.root.after(500, self.check_and_close)

    def run(self):
        self.root.after(500, self.check_and_close)
        self.root.mainloop()