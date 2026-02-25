import tkinter as tk
from tkinter import font

class PatientStartScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Start GUI")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")

        self.title_font = font.Font(family="Helvetica", size=23, weight="bold")
        self.button_font = font.Font(family="Helvetica", size=40, weight="bold")

        self.main_frame = tk.Frame(self.root, bg="black")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.label = tk.Label(
            self.main_frame,
            text="Willkommen in der Hörzelle!\n\n"
                 "Der Test beginnt, sobald Sie auf Start klicken.\n"
                 "Stellen Sie sicher, dass Sie angenehm sitzen.\n\n"
                 "Setzen Sie die Kopfhörer auf und nehmen Sie den Taster.\n"
                 "Bitte drücken Sie nicht auf Gefühl, sondern nur, wenn Sie explizit einen Ton hören.\n\n"
                 "Die rote Köpfhörerseite ist für das rechte Ohr. Der Test startet rechts.\n\n"
                 "Dauer: ca. 10 Minuten. Viel Erfolg!",
            font=self.title_font,
            foreground="white",
            background="black",
            justify="center",
            pady=40
        )
        self.label.pack()

        self.start_button = tk.Button(
            self.main_frame, 
            text="START",
            command=self.root.destroy,
            foreground="black",
            background="#00FFFF", 
            activebackground="#001FCC",
            font=self.button_font,
            padx=120,
            pady=40,
            borderwidth=0,
            cursor="hand2"
        )
        self.start_button.pack()

        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def run(self):
        self.root.mainloop()
        return True