import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from tkinter import filedialog, font, simpledialog
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import threading

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class NotesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Notes App")
        self.geometry("900x600")

        self.notes = {}
        self.autosave_interval = 60

        self.current_theme = "Light"

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")

        self.note_listbox = ctk.CTkTextbox(self.sidebar, width=200, height=400)
        self.note_listbox.pack(padx=5, pady=5, fill="both", expand=True)

        self.add_note_btn = ctk.CTkButton(self.sidebar, text="New Note", command=self.new_note)
        self.add_note_btn.pack(pady=5)

        self.delete_note_btn = ctk.CTkButton(self.sidebar, text="Delete Note", command=self.delete_note)
        self.delete_note_btn.pack(pady=5)

        self.pin_note_btn = ctk.CTkButton(self.sidebar, text="Pin Note", command=self.pin_note)
        self.pin_note_btn.pack(pady=5)

        # Editor
        self.editor_frame = ctk.CTkFrame(self)
        self.editor_frame.pack(side="right", fill="both", expand=True)

        self.text_area = ctk.CTkTextbox(self.editor_frame, width=400, height=300)
        self.text_area.pack(padx=5, pady=5, fill="both", expand=True)

        # Bottom bar
        self.bottom_frame = ctk.CTkFrame(self.editor_frame)
        self.bottom_frame.pack(fill="x")

        self.save_btn = ctk.CTkButton(self.bottom_frame, text="Save", command=self.save_note)
        self.save_btn.pack(side="left", padx=5, pady=5)

        self.load_btn = ctk.CTkButton(self.bottom_frame, text="Load", command=self.load_note)
        self.load_btn.pack(side="left", padx=5, pady=5)

        self.export_pdf_btn = ctk.CTkButton(self.bottom_frame, text="Export PDF", command=self.export_as_pdf)
        self.export_pdf_btn.pack(side="left", padx=5, pady=5)

        self.search_entry = ctk.CTkEntry(self.bottom_frame, placeholder_text="Search...")
        self.search_entry.pack(side="left", padx=5)

        self.search_btn = ctk.CTkButton(self.bottom_frame, text="Find", command=self.search_text)
        self.search_btn.pack(side="left", padx=5)

        self.theme_btn = ctk.CTkButton(self.bottom_frame, text="Toggle Theme", command=self.toggle_theme)
        self.theme_btn.pack(side="right", padx=5)

        self.word_count_label = ctk.CTkLabel(self.bottom_frame, text="Words: 0 | Characters: 0")
        self.word_count_label.pack(side="right", padx=5)

        # Shortcuts
        self.bind("<Control-s>", lambda event: self.save_note())
        self.bind("<Control-f>", lambda event: self.search_text())
        self.bind("<Control-e>", lambda event: self.export_as_pdf())
        self.bind("<KeyRelease>", lambda event: self.update_word_count())

        # Autosave
        self.start_autosave()

    def new_note(self):
        note_name = simpledialog.askstring("New Note", "Enter note name:")
        if note_name:
            self.notes[note_name] = {"content": "", "pinned": False}
            self.update_notes_list()

    def delete_note(self):
        note_name = simpledialog.askstring("Delete Note", "Enter note name to delete:")
        if note_name in self.notes:
            del self.notes[note_name]
            self.update_notes_list()

    def pin_note(self):
        note_name = simpledialog.askstring("Pin Note", "Enter note name to pin:")
        if note_name in self.notes:
            self.notes[note_name]["pinned"] = not self.notes[note_name]["pinned"]
            self.update_notes_list()

    def save_note(self):
        content = self.text_area.get("1.0", "end-1c")
        if not content.strip():
            CTkMessagebox(title="Error", message="Note is empty!", icon="cancel")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(content)
            CTkMessagebox(title="Success", message="Note saved!", icon="check")

    def load_note(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.text_area.delete("1.0", "end")
                self.text_area.insert("1.0", content)
            self.update_word_count()

    def export_as_pdf(self):
        content = self.text_area.get("1.0", "end-1c")
        if not content.strip():
            CTkMessagebox(title="Error", message="Note is empty!", icon="cancel")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            text_object = c.beginText(40, height - 40)
            text_object.setFont("Helvetica", 12)

            for line in content.split('\n'):
                text_object.textLine(line)

            c.drawText(text_object)
            c.save()
            CTkMessagebox(title="Success", message="PDF exported!", icon="check")

    def search_text(self):
        search_term = self.search_entry.get()
        self.text_area.tag_remove("highlight", "1.0", "end")
        if search_term:
            start = "1.0"
            while True:
                start = self.text_area.search(search_term, start, stopindex="end")
                if not start:
                    break
                end = f"{start}+{len(search_term)}c"
                self.text_area.tag_add("highlight", start, end)
                self.text_area.tag_config("highlight", background="yellow")
                start = end

    def toggle_theme(self):
        self.current_theme = "Dark" if self.current_theme == "Light" else "Light"
        ctk.set_appearance_mode(self.current_theme)

    def autosave(self):
        while True:
            self.save_note()
            threading.Event().wait(self.autosave_interval)

    def start_autosave(self):
        autosave_thread = threading.Thread(target=self.autosave, daemon=True)
        autosave_thread.start()

    def update_notes_list(self):
        self.note_listbox.delete("1.0", "end")
        pinned_notes = [n for n in self.notes if self.notes[n]["pinned"]]
        regular_notes = [n for n in self.notes if not self.notes[n]["pinned"]]
        for note in pinned_notes + regular_notes:
            pin_symbol = "📌 " if self.notes[note]["pinned"] else ""
            self.note_listbox.insert("end", pin_symbol + note + "\n")

    def update_word_count(self):
        content = self.text_area.get("1.0", "end-1c")
        words = len(content.split())
        chars = len(content)
        self.word_count_label.configure(text=f"Words: {words} | Characters: {chars}")

if __name__ == "__main__":
    app = NotesApp()
    app.mainloop()
