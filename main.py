import pyttsx3
import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfReader
import threading
import os

class LecteurLivre(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry("800x600")
        self.title("IA: Lecteur de Livres")
        self.configure(bg="#f0f0f0")

        # Attributes
        self.all_pages_marquee = []
        self.page_actuelle = 0
        self.choix_du_livre = tk.StringVar()
        self.text = ""
        self.is_reading = False
        self.is_paused = False
        self.voice_speed = 150

        # UI Components
        self.create_widgets()

        # Text-to-speech engine
        self.alicia = pyttsx3.init()
        self.tts_thread = threading.Thread(target=self.run_tts, daemon=True)

    def create_widgets(self):
        # Header Label
        header_label = tk.Label(self, text="Lecteur de Livres", fg="#333", font=("Arial", 24, "bold"), bg="#f0f0f0")
        header_label.pack(pady=20)

        # File Selection Frame
        file_frame = tk.Frame(self, bg="#f0f0f0")
        file_frame.pack(pady=10)

        browse_button = tk.Button(file_frame, text="Parcourir", command=self.livre_choisie,
                                  relief=tk.RAISED, fg="#fff", bg="#4CAF50", font=("Arial", 12),
                                  width=15, height=2, borderwidth=2)
        browse_button.grid(row=0, column=0, padx=10)

        self.btn_lecture = tk.Button(file_frame, text="Commencer la lecture", command=self.lecture_du_livre,
                                     relief=tk.RAISED, fg="#fff", bg="#2196F3", font=("Arial", 12),
                                     width=20, height=2, borderwidth=2, state=tk.DISABLED)
        self.btn_lecture.grid(row=0, column=1, padx=10)

        # New Pause/Resume button
        self.btn_pause_resume = tk.Button(file_frame, text="Pause/Reprendre la lecture", command=self.pause_resume_lecture,
                                          relief=tk.RAISED, fg="#fff", bg="#FF9800", font=("Arial", 12),
                                          width=25, height=2, borderwidth=2, state=tk.DISABLED)
        self.btn_pause_resume.grid(row=0, column=2, padx=10)

        # File Details Label
        self.file_details_label = tk.Label(self, text="", fg="#555", font=("Arial", 10), bg="#f0f0f0")
        self.file_details_label.pack()

        # Voice Speed Label
        speed_label = tk.Label(self, text="Vitesse de la voix:", fg="#333", font=("Arial", 12), bg="#f0f0f0")
        speed_label.pack(pady=10)

        self.speed_label = tk.Label(self, text=str(self.voice_speed), fg="#333", font=("Arial", 12), bg="#f0f0f0")
        self.speed_label.pack()

        # Text Display
        text_display_frame = tk.Frame(self, bg="#f0f0f0")
        text_display_frame.pack(pady=10)

        self.text_display = tk.Text(text_display_frame, wrap=tk.WORD, width=60, height=10, bg="#fff", fg="#333",
                                    font=("Arial", 12), borderwidth=2, relief=tk.SOLID)
        self.text_display.pack()

    def livre_choisie(self):
        try:
            chemin_livre = filedialog.askopenfilename(filetypes=[("Fichiers PDF", "*.pdf")])
            self.choix_du_livre.set(chemin_livre)

            if chemin_livre:
                self.btn_lecture.config(state=tk.NORMAL)
                self.btn_pause_resume.config(state=tk.DISABLED)
                self.file_details_label.config(text=f"Fichier choisi : {os.path.basename(chemin_livre)}")
        except Exception as e:
            self.afficher_erreur(f"Erreur lors de la sélection du fichier : {e}")

    def run_tts(self):
        while True:
            if self.is_reading and not self.is_paused:
                self.alicia.say(self.text)
                self.alicia.runAndWait()

    def lecture_du_livre(self, page_index=0):
        threading.Thread(target=self.read_pages, args=(page_index,), daemon=True).start()

    def read_pages(self, page_index=0):
        try:
            chemin_livre = self.choix_du_livre.get()
            if chemin_livre:
                livre = open(chemin_livre, 'rb')
                lecture = PdfReader(livre)
                self.is_reading = True
                self.is_paused = False
                self.alicia.setProperty('rate', self.voice_speed)

                for i in range(page_index, len(lecture.pages)):
                    if not self.is_reading or self.is_paused:
                        break

                    page = lecture.pages[i]
                    self.text = page.extract_text()
                    self.page_actuelle += 1

                    self.text_display.delete(1.0, tk.END)
                    self.text_display.insert(tk.END, self.text)

                    self.alicia.say(self.text)
                    self.alicia.runAndWait()

                    self.after(1000)  # Sleep for 1 second between pages

                self.is_reading = False
                self.file_details_label.config(
                    text="J'ai terminé la lecture du livre. Si vous avez d'autres tâches à effectuer ou si vous souhaitez "
                         "me confier d'autres livres, je suis prêt à les prendre en charge.")
                self.btn_lecture.config(state=tk.DISABLED)
                self.btn_pause_resume.config(state=tk.DISABLED)

        except Exception as e:
            self.afficher_erreur(f"Une erreur s'est produite lors de la lecture du livre : {e}")

    def pause_resume_lecture(self):
        if self.is_reading:
            self.is_paused = not self.is_paused
            if self.is_paused:
                self.btn_pause_resume.config(text="Reprendre la lecture")
            else:
                self.btn_pause_resume.config(text="Pause la lecture")
                threading.Thread(target=self.read_pages, args=(self.page_actuelle,), daemon=True).start()


    def marquer_page(self):
        try:
            page_marques = self.page_actuelle + 1
            self.all_pages_marquee.append(page_marques)
            print("Page Marquée : ", page_marques)
        except Exception as e:
            self.afficher_erreur(f"Erreur lors du marquage de la page : {e}")

    def marquer_page_thread(self):
        threading.Thread(target=self.marquer_page).start()

    def afficher_erreur(self, message):
        print(message)

if __name__ == "__main__":
    application = LecteurLivre()
    application.tts_thread.start()
    application.mainloop()
