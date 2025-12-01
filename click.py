import pyautogui
import win32gui
import win32process
import psutil
from pynput import mouse
import time

class CoordinateLogger:
    def __init__(self):
        self.ma33_window = None
        self.window_pos = None
        self.clicks = []
        
    def find_ma33_window(self):
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    process = psutil.Process(pid)
                    if process.name().lower() == 'ma33.exe':
                        windows.append(hwnd)
                except:
                    pass
            return True
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        
        if windows:
            self.ma33_window = windows[0]
            rect = win32gui.GetWindowRect(self.ma33_window)
            self.window_pos = {
                'x': rect[0],
                'y': rect[1],
                'width': rect[2] - rect[0],
                'height': rect[3] - rect[1]
            }
            return True
        return False
    
    def on_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            absolute_coords = (x, y)
            
            if self.window_pos:
                relative_x = x - self.window_pos['x']
                relative_y = y - self.window_pos['y']
                relative_coords = (relative_x, relative_y)
                
                click_info = {
                    'absolute': absolute_coords,
                    'relative': relative_coords,
                    'window': self.window_pos
                }
                
                self.clicks.append(click_info)
                
                print(f"\nClick #{len(self.clicks)}")
                print(f"  Absolute: ({x}, {y})")
                print(f"  Relative to MA33 window: ({relative_x}, {relative_y})")
                print(f"  Window position: ({self.window_pos['x']}, {self.window_pos['y']})")
                print(f"  Window size: {self.window_pos['width']}x{self.window_pos['height']}")
            else:
                print(f"\nClick: ({x}, {y}) - MA33 window not found!")
    
    def run(self):
        print("=" * 60)
        print("CLICK COORDINATE LOGGER FOR MA33")
        print("=" * 60)
        
        print("\nSearching for ma33.exe window...")
        
        if self.find_ma33_window() and self.window_pos:
            print(f"Found MA33 window!")
            print(f"  Position: ({self.window_pos['x']}, {self.window_pos['y']})")
            print(f"  Size: {self.window_pos['width']}x{self.window_pos['height']}")
        else:
            print("WARNING: MA33 window not found!")
            print("Logging absolute coordinates only...")
        
        print("\n" + "-" * 60)
        print("Click on buttons in MA33 to log their coordinates")
        print("Press Ctrl+C to finish and show summary")
        print("-" * 60 + "\n")
        
        with mouse.Listener(on_click=self.on_click) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                pass
        
        self.show_summary()
    
    def show_summary(self):
        print("\n\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        if not self.clicks:
            print("No clicks recorded!")
            return
        
        print(f"\nTotal clicks: {len(self.clicks)}")
        print("\nCode to use in automation:")
        print("-" * 60)
        
        for i, click in enumerate(self.clicks, 1):
            rel = click['relative']
            print(f"\n# Click {i}")
            print(f"window_x, window_y, _, _ = win32gui.GetWindowRect(ma33_window)")
            print(f"pyautogui.click(window_x + {rel[0]}, window_y + {rel[1]})")
        
        print("\n" + "=" * 60)

if __name__ == '__main__':
    try:
        logger = CoordinateLogger()
        logger.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()