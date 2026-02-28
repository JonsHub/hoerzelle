import tkinter as tk
import paths_dir
import matplotlib
import matplotlib.pyplot as plt
import io
from matplotlib.patches import Polygon
from tkinter import font as tkfont
from PIL import Image, ImageTk

matplotlib.use('Agg')
class EvaluationGUI:
    def __init__(self, left_result, right_result, high_freq_warning_left=False, high_freq_warning_right=False, patient_data=None):
        self.root = tk.Tk()
        self.root.title("Hearing Test Evaluation")
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.state('zoomed')
        
        self.left_result = left_result
        self.right_result = right_result
        self.high_freq_warning_left = high_freq_warning_left
        self.high_freq_warning_right = high_freq_warning_right
        self.patient_data = patient_data
        
        self.images_dir = paths_dir.IMAGES_DIR
        self.traffic_light_images = {
            "red": tk.PhotoImage(file=self.images_dir / "ampel_rot.png"),
            "yellow": tk.PhotoImage(file=self.images_dir / "ampel_gelb.png"),
            "green": tk.PhotoImage(file=self.images_dir / "ampel_grün.png"),
        }
        
        self.title_font = tkfont.Font(family="Franklin Gothic Medium", size=22)
        self.label_font = tkfont.Font(family="Segoe UI", size=15)
        self.warning_font = tkfont.Font(family="Verdana", size=12)
        self.info_font = tkfont.Font(family="Segoe UI", size=13)
        self.button_font = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        
        self.diagram_images = {}
        
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
        title.pack(pady=(0, 20))
        
        ears_frame = tk.Frame(main_frame, bg="black")
        ears_frame.pack()
        
        left_frame = tk.Frame(ears_frame, bg="black")
        left_frame.pack(side=tk.LEFT, padx=25)
        
        left_label = tk.Label(
            left_frame,
            text="LINKES OHR",
            font=self.label_font,
            fg="white",
            bg="black"
        )
        left_label.pack(pady=(0, 8), padx=15)
        
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
            left_warning.pack(pady=(8, 0))
        
        right_frame = tk.Frame(ears_frame, bg="black")
        right_frame.pack(side=tk.LEFT, padx=25)
        
        right_label = tk.Label(
            right_frame,
            text="RECHTES OHR",
            font=self.label_font,
            fg="white",
            bg="black"
        )
        right_label.pack(pady=(0, 8), padx=15)
        
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
            right_warning.pack(pady=(8, 0))
        
        recommendation = self.get_recommendation()
        rec_label = tk.Label(
            main_frame,
            text=recommendation,
            font=self.info_font,
            fg="white",
            bg="black",
            wraplength=600,
            justify=tk.CENTER
        )
        rec_label.pack(pady=(30, 20))
        
        button_frame = tk.Frame(main_frame, bg="black")
        button_frame.pack(pady=(15, 0))
        
        details_button = tk.Button(
            button_frame,
            text="DETAILS",
            command=self.show_details_screen,
            foreground="black",
            background="#00FFFF",
            activebackground="#001FCC",
            font=self.button_font,
            width=15,
            height=2
        )
        details_button.pack(side=tk.LEFT, padx=15)
        
        exit_button = tk.Button(
            button_frame,
            text="BEENDEN",
            command=self.confirm_exit,
            foreground="black",
            background="#00FFFF",
            activebackground="#001FCC",
            font=self.button_font,
            width=15,
            height=2
        )
        exit_button.pack(side=tk.LEFT, padx=15)
    
    def create_audiogram_image_for_tk(self, ear_data, ear_side):
        frequencies = [125, 250, 500, 1000, 2000, 3000, 4000, 6000, 8000]
        frequency_labels = ['125', '250', '500', '1K', '2K', '3K', '4K', '6K', '8K']
        
        threshold_values = []
        for freq in frequencies:
            if freq in ear_data:
                threshold_values.append(ear_data[freq])
            else:
                threshold_values.append(None)
        
        fig, ax = plt.subplots(figsize=(7, 5))
        
        ax.set_xlim(0, len(frequencies) - 1)
        ax.set_ylim(-10, 120)
        ax.invert_yaxis()
        
        ax.set_xticks(range(len(frequencies)))
        ax.set_xticklabels(frequency_labels, fontsize=9)
        ax.set_xlabel('Frequenz (Hz)', fontsize=10, fontweight='bold')
        
        ax.set_yticks(range(-10, 121, 10))
        ax.set_ylabel('Hörschwelle (Dezibel)', fontsize=10, fontweight='bold')
        
        ax.grid(True, alpha=0.3, linewidth=0.5)
        ax.set_facecolor('#f5f5f5')
        
        green_zone = Polygon([(0, -10), (len(frequencies)-1, -10), 
                              (len(frequencies)-1, 25), (0, 25)], 
                             facecolor='lightgreen', alpha=0.3, edgecolor='none')
        ax.add_patch(green_zone)
        
        yellow_zone = Polygon([(0, 25), (len(frequencies)-1, 25), 
                               (len(frequencies)-1, 40), (0, 40)], 
                              facecolor='yellow', alpha=0.3, edgecolor='none')
        ax.add_patch(yellow_zone)
        
        red_zone = Polygon([(0, 40), (len(frequencies)-1, 40), 
                            (len(frequencies)-1, 120), (0, 120)], 
                           facecolor='lightcoral', alpha=0.3, edgecolor='none')
        ax.add_patch(red_zone)
        
        valid_indices = []
        valid_values = []
        for i, val in enumerate(threshold_values):
            if val is not None:
                valid_indices.append(i)
                valid_values.append(val)
        
        if valid_indices:
            marker_style = 'o' if ear_side == 'right' else 'x'
            marker_color = 'red' if ear_side == 'right' else 'blue'
            marker_size = 10
            
            ax.plot(valid_indices, valid_values, 
                    marker=marker_style, 
                    color=marker_color,
                    linewidth=2, 
                    markersize=marker_size,
                    label=f'{ear_side.capitalize()} Ohr')
                        
        plt.tight_layout()
        
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        
        image = Image.open(buffer)
        photo = ImageTk.PhotoImage(image)
        
        plt.close()
        buffer.close()
        
        return photo
    
    def show_details_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        container = tk.Frame(self.root, bg="black")
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        details_frame = tk.Frame(container, bg="black")
        details_frame.pack(padx=30)
        
        title = tk.Label(
            details_frame,
            text="DETAILLIERTE INFORMATIONEN",
            font=self.title_font,
            fg="#00FFFF",
            bg="black"
        )
        title.pack(pady=(0, 25))
        
        if self.high_freq_warning_left or self.high_freq_warning_right:
            ht_title = tk.Label(
                details_frame,
                text="Was bedeutet Hochtonverlust?",
                font=tkfont.Font(family="Arial", size=14, weight="bold"),
                fg="white",
                bg="black"
            )
            ht_title.pack(pady=(0, 10))
            
            ht_text = tk.Label(
                details_frame,
                text="Hochtonverlust bedeutet, dass hohe Töne schlechter gehört werden.\n\n"
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
            ht_text.pack(pady=(0, 20))
        
        worst_result = "red" if (self.left_result == "red" or self.right_result == "red") else \
                       "yellow" if (self.left_result == "yellow" or self.right_result == "yellow") else "green"
        
        if worst_result == "red":
            advice_title = "Empfehlung: HNO-Arzt aufsuchen"
            advice_text = ("Bei roten Ampelwerten liegt eine deutliche Hörminderung vor.\n"
                          "Bitte vereinbaren Sie zeitnah einen Termin bei einem HNO-Arzt.")
            advice_color = "#FF4444"
        elif worst_result == "yellow":
            advice_title = "Empfehlung: HNO-Kontrolle"
            advice_text = ("Bei gelben Ampelwerten liegt eine leichte Auffälligkeit vor.\n"
                          "Wir empfehlen eine HNO-ärztliche Kontrolle.")
            advice_color = "#FFD700"
        else:
            advice_title = "Ihr Hörvermögen liegt im Normalbereich"
            advice_text = ("Ihre Hörschwellen sind unauffällig.\n"
                          "Regelmäßige Kontrollen (alle 1-2 Jahre) werden empfohlen.")
            advice_color = "#00FF00"
        
        advice_title_label = tk.Label(
            details_frame,
            text=advice_title,
            font=tkfont.Font(family="Arial", size=14, weight="bold"),
            fg=advice_color,
            bg="black"
        )
        advice_title_label.pack(pady=(15, 10))
        
        advice_text_label = tk.Label(
            details_frame,
            text=advice_text,
            font=self.info_font,
            fg="white",
            bg="black",
            justify=tk.CENTER
        )
        advice_text_label.pack(pady=(0, 25))
        
        button_frame = tk.Frame(details_frame, bg="black")
        button_frame.pack(pady=(10, 15))
        
        if self.patient_data:
            diagram_button = tk.Button(
                button_frame,
                text="Ergebnisse anzeigen",
                command=self.show_diagrams_screen,
                foreground="black",
                background="#FFD700",
                activebackground="#FFA500",
                font=self.button_font,
                width=20,
                height=2
            )
            diagram_button.pack(side=tk.LEFT, padx=15)
        
        back_button = tk.Button(
            button_frame,
            text="ZURÜCK",
            command=self.show_main_screen,
            foreground="black",
            background="#00FFFF",
            activebackground="#001FCC",
            font=self.button_font,
            width=15,
            height=2
        )
        back_button.pack(side=tk.LEFT, padx=15)
        
        exit_button = tk.Button(
            button_frame,
            text="BEENDEN",
            command=self.confirm_exit,
            foreground="black",
            background="#00FFFF",
            activebackground="#001FCC",
            font=self.button_font,
            width=15,
            height=2
        )
        exit_button.pack(side=tk.LEFT, padx=15)
    
    def show_diagrams_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        diagram_window = tk.Frame(self.root, bg="white")
        diagram_window.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        title = tk.Label(
            diagram_window,
            text="TESTERGEBNISSE - AUDIOGRAMME",
            font=self.title_font,
            fg="#000000",
            bg="white"
        )
        title.pack(pady=(10, 15))
        
        diagrams_frame = tk.Frame(diagram_window, bg="white")
        diagrams_frame.pack(pady=(0, 15))
        
        left_container = tk.Frame(diagrams_frame, bg="white")
        left_container.pack(side=tk.LEFT, padx=15)
        
        left_label_title = tk.Label(
            left_container,
            text="Linkes Ohr",
            font=tkfont.Font(family="Arial", size=14, weight="bold"),
            fg="#000000",
            bg="white"
        )
        left_label_title.pack(pady=(0, 5))
        
        left_diagram_label = tk.Label(left_container, bg="white")
        left_diagram_label.pack()
        
        right_container = tk.Frame(diagrams_frame, bg="white")
        right_container.pack(side=tk.LEFT, padx=15)
        
        right_label_title = tk.Label(
            right_container,
            text="Rechtes Ohr",
            font=tkfont.Font(family="Arial", size=14, weight="bold"),
            fg="#000000",
            bg="white"
        )
        right_label_title.pack(pady=(0, 5))
        
        right_diagram_label = tk.Label(right_container, bg="white")
        right_diagram_label.pack()
        
        try:
            left_photo = self.create_audiogram_image_for_tk(
                self.patient_data['left_ear'] if self.patient_data else {}, 'left'
            )
            self.diagram_images['left'] = left_photo
            left_diagram_label.config(image=left_photo)
        except Exception as e:
            print(f"Error creating left diagram: {e}")
            error_label = tk.Label(
                left_container,
                text="Diagramm konnte nicht\ngeladen werden",
                font=self.info_font,
                fg="red",
                bg="white"
            )
            error_label.pack()
        
        try:
            right_photo = self.create_audiogram_image_for_tk(
                self.patient_data['right_ear'] if self.patient_data else {}, 'right'
            )
            self.diagram_images['right'] = right_photo
            right_diagram_label.config(image=right_photo)
        except Exception as e:
            print(f"Error creating right diagram: {e}")
            error_label = tk.Label(
                right_container,
                text="Diagramm konnte nicht\ngeladen werden",
                font=self.info_font,
                fg="red",
                bg="white"
            )
            error_label.pack()
        
        button_frame = tk.Frame(diagram_window, bg="white")
        button_frame.pack(pady=(15, 10))
        
        back_button = tk.Button(
            button_frame,
            text="ZURÜCK",
            command=self.show_details_screen,
            foreground="white",
            background="#333333",
            activebackground="#555555",
            font=self.button_font,
            width=15,
            height=2
        )
        back_button.pack()
        
    def confirm_exit(self):
        confirm_window = tk.Toplevel(self.root)
        confirm_window.configure(bg="black")
        confirm_window.overrideredirect(True)
        
        window_width = 450
        window_height = 220
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        confirm_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        confirm_frame = tk.Frame(confirm_window, bg="black", highlightbackground="white", highlightthickness=2)
        confirm_frame.pack(expand=True, fill=tk.BOTH, padx=2, pady=2)
        
        inner_frame = tk.Frame(confirm_frame, bg="black")
        inner_frame.pack(expand=True, fill=tk.BOTH, padx=15, pady=15)
        
        question_label = tk.Label(
            inner_frame,
            text="Möchten Sie wirklich beenden?",
            font=tkfont.Font(family="Segoe UI", size=14),
            fg="white",
            bg="black"
        )
        question_label.pack(pady=(20, 25))
        
        button_frame = tk.Frame(inner_frame, bg="black")
        button_frame.pack()
        
        no_button = tk.Button(
            button_frame,
            text="ABBRECHEN",
            command=confirm_window.destroy,
            foreground="black",
            background="#00FFFF",
            activebackground="#001FCC",
            font=self.button_font,
            width=12,
            height=2
        )
        no_button.pack(side=tk.LEFT, padx=12)
        
        yes_button = tk.Button(
            button_frame,
            text="BEENDEN",
            command=self.root.destroy,
            foreground="white",
            background="#FF4444",
            activebackground="#CC0000",
            font=self.button_font,
            width=12,
            height=2
        )
        yes_button.pack(side=tk.LEFT, padx=12)
    
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
