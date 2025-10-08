import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import glob
from pathlib import Path

class CountdownSlideshow:
    def __init__(self, waiting_time):
        self.window = tk.Tk()
        self.window.attributes('-fullscreen', True, '-topmost', True)
        self.window.config(bg='black')
        
        # Create a label that will display the images
        self.label = ttk.Label(self.window)
        self.label.pack(expand=True, fill='both')
        
        self.current_time = waiting_time
        self.current_image = None
        self.slideshow_running = True
        
        # Get the directory where countdown images are stored
        self.image_dir = Path("slideshow")  # Adjust path as needed

        self.window.bind('<Escape>', lambda e: self.stop())
        self.window.protocol("MW_DELETE_WINDOW", self.stop)
        
    def get_image_for_time(self, time_value):
        """Try to find an image for the given time value."""
        # Try both PNG and JPG formats
        for ext in ['.png', '.jpg']:
            image_path = self.image_dir / f"{time_value}{ext}"
            if image_path.exists():
                return str(image_path)
        return None
        
    def update_display(self):
        if not self.slideshow_running or self.current_time < 0:
            #self.window.quit()
            self.stop()
            return
            
        # Try to get image for current time
        image_path = self.get_image_for_time(self.current_time)
        
        if image_path:
            try:
                # Load and resize image to fit screen
                image = Image.open(image_path)
                screen_width = self.window.winfo_screenwidth()
                screen_height = self.window.winfo_screenheight()
                image = image.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(image)
                self.label.configure(image=photo)
                self.label.image = photo  # Keep a reference
                self.current_image = image_path
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")
        
        self.current_time -= 1
        self.window.after(1000, self.update_display)  # Update every second
        
    def start(self):
        """Start the slideshow"""
        self.update_display()
        self.window.mainloop()
        
    def stop(self):
        """Stop the slideshow"""
        self.slideshow_running = False
        
        self.window.after(100, self.destroy_window)

    def destroy_window(self):
        try:
            self.window.destroy()
            self.window.quit()
        except:
            pass

def start_countdown_slideshow(waiting_time):
    slideshow = CountdownSlideshow(waiting_time)
    slideshow.start()

if __name__ == "__main__":
    # For testing
    from program import WAITING_TIME
    start_countdown_slideshow(WAITING_TIME) 