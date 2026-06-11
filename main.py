import customtkinter as ctk
from tkinter import messagebox, filedialog
import cv2
import os
from deepface import DeepFace
from PIL import Image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class FaceApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("Facial recognition")
        self.geometry("800x500")

        # Layout Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar (Branding Removed) ---
        self.sidebar = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # --- Main View ---
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.grid(row=0, column=1, padx=30, pady=30, sticky="nsew")
        self.main_view.columnconfigure(0, weight=1)

        self.header = ctk.CTkLabel(self.main_view, text="Facial recognition System",
                                   font=ctk.CTkFont(size=26, weight="bold"))
        self.header.pack(pady=(0, 60))

        # Action Buttons
        self.btn_library = ctk.CTkButton(self.main_view, text="📂 Photo Library Analysis",
                                         command=self.open_library, height=60, width=380,
                                         font=ctk.CTkFont(size=16, weight="bold"))
        self.btn_library.pack(pady=15)

        self.btn_webcam = ctk.CTkButton(self.main_view, text="🎥 webcam",
                                        command=self.live_webcam, height=60, width=380,
                                        fg_color="#4CAF50", hover_color="#43A047",
                                        font=ctk.CTkFont(size=16, weight="bold"))
        self.btn_webcam.pack(pady=15)

        self.status = ctk.CTkLabel(self.main_view, text="System Ready", font=ctk.CTkFont(size=12))
        self.status.pack(side="bottom", pady=20)

    def open_library(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.webp")]
        )
        if file_path:
            self.analyze_image_window(file_path)

    def analyze_image_window(self, path):
        try:
            # Emotion-only analysis
            analysis = DeepFace.analyze(img_path=path, actions=['emotion'], enforce_detection=False)
            res = analysis[0]

            result_win = ctk.CTkToplevel(self)
            result_win.title("Analysis Result")
            result_win.geometry("400x500")
            result_win.after(10, lambda: result_win.focus_force())

            img = Image.open(path)
            img.thumbnail((300, 300))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(250, 250))

            ctk.CTkLabel(result_win, image=ctk_img, text="").pack(pady=20)

            data = f"Detected Emotion:\n{res['dominant_emotion'].upper()}"
            ctk.CTkLabel(result_win, text=data, font=ctk.CTkFont(size=22, weight="bold")).pack()
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {e}")

    def live_webcam(self):
        cap = cv2.VideoCapture(0)
        current_emotion = "Initializing..."
        counter = 0

        while True:
            ret, frame = cap.read()
            if not ret: break

            # Standard detection for box rendering
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            # Analyze emotion every 20 frames
            if counter % 20 == 0 and len(faces) > 0:
                try:
                    results = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                    current_emotion = results[0]['dominant_emotion'].upper()
                except:
                    pass

            for (x, y, w, h) in faces:
                # Color theme matches the UI (blue/cyan)
                box_color = (255, 150, 80)  # BGR Format

                cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)

                # Header tag for emotion
                cv2.rectangle(frame, (x, y - 35), (x + w, y), box_color, -1)
                cv2.putText(frame, current_emotion, (x + 5, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            cv2.imshow('Facial recognition - Live', frame)
            counter += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    app = FaceApp()
    app.mainloop()
