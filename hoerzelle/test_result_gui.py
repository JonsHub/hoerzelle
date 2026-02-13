import tkinter as tk
from tkinter import font as tkfont
from pathlib import Path

class EvaluationGUI:
    def __init__(self, left_result, right_result, high_freq_warning_left=False, high_freq_warning_right=False):
        self.root = tk.Tk()
        self.root.title("Hearing Test Evaluation")
        self.root.configure(bg="black")
        self.root.attributes('-fullscreen', True)
        
        self.left_result = left_result
        self.right_result = right_result
        self.high_freq_warning_left = high_freq_warning_left
        self.high_freq_warning_right = high_freq_warning_right
        
        self.images_dir = Path("images")
        self.traffic_light_images = {
            "red": tk.PhotoImage(file=self.images_dir / "ampel_rot.png"),
            "yellow": tk.PhotoImage(file=self.images_dir / "ampel_gelb.png"),
            "green": tk.PhotoImage(file=self.images_dir / "ampel_grün.png"),
        }
        
        self.title_font = tkfont.Font(family="Franklin Gothic Medium", size=38)
        self.label_font = tkfont.Font(family="Segoe UI", size=20)
        self.warning_font = tkfont.Font(family="Verdana", size=16)
        self.info_font = tkfont.Font(family="Segoe UI", size=18)
        
        self.show_main_screen()
        
    def show_main_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        container = tk.Frame(self.root, bg="black")
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        main_frame = tk.Frame(container, bg="black")
        main_frame.pack()
        
        title = tk.Label(
            main_frame,
            text="HÖRTEST ERGEBNIS",
            font=self.title_font,
            fg="#00FFFF",
            bg="black"
        )
        title.pack(pady=(0, 30))
        
        ears_frame = tk.Frame(main_frame, bg="black")
        ears_frame.pack()
        
        left_frame = tk.Frame(ears_frame, bg="black")
        left_frame.pack(side=tk.LEFT, padx=30)
        
        left_label = tk.Label(
            left_frame,
            text="LINKES OHR",
            font=self.label_font,
            fg="white",
            bg="black"
        )
        left_label.pack(pady=(0, 10), padx=20)
        
        left_image = tk.Label(
            left_frame,
            image=self.traffic_light_images[self.left_result],
            bg="black"
        )
        left_image.pack()
        
        if self.high_freq_warning_left:
            left_warning = tk.Label(
                left_frame,
                text="⚠ Hochtonverlust erkannt",
                font=self.warning_font,
                fg="#FFD700", 
                bg="black"
            )
            left_warning.pack(pady=(10, 0))
        
        right_frame = tk.Frame(ears_frame, bg="black")
        right_frame.pack(side=tk.LEFT, padx=30)
        
        right_label = tk.Label(
            right_frame,
            text="RECHTES OHR",
            font=self.label_font,
            fg="white",
            bg="black"
        )
        right_label.pack(pady=(0, 10), padx=20)
        
        right_image = tk.Label(
            right_frame,
            image=self.traffic_light_images[self.right_result],
            bg="black"
        )
        right_image.pack()
        
        if self.high_freq_warning_right:
            right_warning = tk.Label(
                right_frame,
                text="⚠ Hochtonverlust erkannt",
                font=self.warning_font,
                fg="#FFD700", 
                bg="black"
            )
            right_warning.pack(pady=(10, 0))
        
        recommendation = self.get_recommendation()
        rec_label = tk.Label(
            main_frame,
            text=recommendation,
            font=self.info_font,
            fg="white",
            bg="black",
            wraplength=700,
            justify=tk.CENTER
        )
        rec_label.pack(pady=(40, 30))
        
        button_frame = tk.Frame(main_frame, bg="black")
        button_frame.pack(pady=(20, 0))
        
        details_button = tk.Button(
            button_frame,
            text="DETAILS ANZEIGEN",
            command=self.show_details_screen,
            foreground="black",
            background="#00FFFF",
            activebackground="#001FCC",
            font=self.label_font,
            width=20,
            height=2
        )
        details_button.pack(side=tk.LEFT, padx=30)
        
        exit_button = tk.Button(
            button_frame,
            text="BEENDEN",
            command=self.confirm_exit,
            foreground="black",
            background="#00FFFF",
            activebackground="#001FCC",
            font=self.label_font,
            width=20,
            height=2
        )
        exit_button.pack(side=tk.LEFT, padx=30)
    
    def show_details_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        container = tk.Frame(self.root, bg="black")
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        details_frame = tk.Frame(container, bg="black")
        details_frame.pack(padx=40)
        
        title = tk.Label(
            details_frame,
            text="DETAILLIERTE INFORMATIONEN",
            font=self.title_font,
            fg="#00FFFF",
            bg="black"
        )
        title.pack(pady=(0, 40))
        
        if self.high_freq_warning_left or self.high_freq_warning_right:
            ht_title = tk.Label(
                details_frame,
                text="Was bedeutet Hochtonverlust?",
                font=tkfont.Font(family="Arial", size=18, weight="bold"),
                fg="white",
                bg="black"
            )
            ht_title.pack(pady=(0, 15))
            
            ht_text = tk.Label(
                details_frame,
                text="Hochtonverlust bedeutet, dass hohe Töne schlechter gehört werden als tiefe Töne.\n\n"
                     "Betroffene Alltagssituationen:\n"
                     "• Vogelgezwitscher und Naturgeräusche\n"
                     "• Kinderstimmen und hohe Frauenstimmen\n"
                     "• Zischlaute in Gesprächen (S, F, Sch...)\n"
                     "• Telefonate und TV-Dialoge\n\n"
                     "Häufige Ursachen:\n"
                     "• Altersbedingte Veränderungen im Innenohr\n"
                     "• Lärmbelastung (Beruf, Musik, etc.)\n"
                     "• Genetische Faktoren",
                font=self.info_font,
                fg="white",
                bg="black",
                justify=tk.LEFT
            )
            ht_text.pack(pady=(0, 30))
        
        worst_result = "red" if (self.left_result == "red" or self.right_result == "red") else \
                       "yellow" if (self.left_result == "yellow" or self.right_result == "yellow") else "green"
        
        if worst_result == "red":
            advice_title = "Empfehlung: HNO-Arzt aufsuchen"
            advice_text = ("Bei roten Ampelwerten liegt eine deutliche Hörminderung vor.\n"
                          "Bitte vereinbaren Sie zeitnah einen Termin bei einem HNO-Arzt\n"
                          "für eine ausführliche Untersuchung und Beratung.")
            advice_color = "#FF4444"
        elif worst_result == "yellow":
            advice_title = "Empfehlung: HNO-Kontrolle"
            advice_text = ("Bei gelben Ampelwerten liegt eine leichte Auffälligkeit vor.\n"
                          "Wir empfehlen eine HNO-ärztliche Kontrolle zur weiteren Abklärung.")
            advice_color = "#FFD700"
        else:
            advice_title = "Ihr Hörvermögen liegt im Normalbereich"
            advice_text = ("Ihre Hörschwellen sind unauffällig.\n"
                          "Regelmäßige Kontrollen (alle 1-2 Jahre) werden dennoch empfohlen.")
            advice_color = "#00FF00"
        
        advice_title_label = tk.Label(
            details_frame,
            text=advice_title,
            font=tkfont.Font(family="Arial", size=18, weight="bold"),
            fg=advice_color,
            bg="black"
        )
        advice_title_label.pack(pady=(20, 15))
        
        advice_text_label = tk.Label(
            details_frame,
            text=advice_text,
            font=self.info_font,
            fg="white",
            bg="black",
            justify=tk.CENTER
        )
        advice_text_label.pack(pady=(0, 40))
        
        button_frame = tk.Frame(details_frame, bg="black")
        button_frame.pack(pady=(20, 0))
        
        back_button = tk.Button(
            button_frame,
            text="ZURÜCK",
            command=self.show_main_screen,
            foreground="black",
            background="#00FFFF",
            activebackground="#001FCC",
            font=self.label_font,
            width=20,
            height=2
        )
        back_button.pack(side=tk.LEFT, padx=30)
        
        exit_button = tk.Button(
            button_frame,
            text="BEENDEN",
            command=self.confirm_exit,
            foreground="black",
            background="#00FFFF",
            activebackground="#001FCC",
            font=self.label_font,
            width=20,
            height=2
        )
        exit_button.pack(side=tk.LEFT, padx=30)
    def confirm_exit(self):
        confirm_window = tk.Toplevel(self.root)
        confirm_window.configure(bg="black")
        confirm_window.overrideredirect(True)
        
        window_width = 600
        window_height = 300
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        confirm_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        confirm_frame = tk.Frame(confirm_window, bg="black", highlightbackground="white", highlightthickness=2)
        confirm_frame.pack(expand=True, fill=tk.BOTH, padx=2, pady=2)
        
        inner_frame = tk.Frame(confirm_frame, bg="black")
        inner_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        question_label = tk.Label(
            inner_frame,
            text="Möchten Sie wirklich beenden?",
            font=tkfont.Font(family="Segoe UI", size=18),
            fg="white",
            bg="black"
        )
        question_label.pack(pady=(30, 40))
        
        button_frame = tk.Frame(inner_frame, bg="black")
        button_frame.pack()
        
        no_button = tk.Button(
            button_frame,
            text="ABBRECHEN",
            command=confirm_window.destroy,
            foreground="black",
            background="#00FFFF",
            activebackground="#001FCC",
            font=self.label_font,
            width=15,
            height=2
        )
        no_button.pack(side=tk.LEFT, padx=20)
        
        yes_button = tk.Button(
            button_frame,
            text="BEENDEN",
            command=self.root.destroy,
            foreground="white",
            background="#FF4444",
            activebackground="#CC0000",
            font=self.label_font,
            width=15,
            height=2
        )
        yes_button.pack(side=tk.LEFT, padx=20)
        
        no_button = tk.Button(
            button_frame,
            text="ABBRECHEN",
            command=confirm_window.destroy,
            foreground="black",
            background="#00FFFF",
            activebackground="#001FCC",
            font=self.label_font,
            width=15,
            height=2
        )
        no_button.pack(side=tk.LEFT, padx=15)
    
    def get_recommendation(self):
        worst = "red" if (self.left_result == "red" or self.right_result == "red") else \
                "yellow" if (self.left_result == "yellow" or self.right_result == "yellow") else "green"
        
        if worst == "red":
            return "Bitte vereinbaren Sie zeitnah einen Termin beim HNO-Arzt."
        elif worst == "yellow":
            return "Wir empfehlen eine HNO-ärztliche Kontrolle."
        else:
            return "Ihr Hörvermögen liegt im Normalbereich."
    
    def run(self):
        self.root.mainloop()
        return True
    
if __name__ == "__main__":
    gui = EvaluationGUI(
        left_result="yellow",
        right_result="red",
        high_freq_warning_left=False,
        high_freq_warning_right=True,
    )
    gui.run()

