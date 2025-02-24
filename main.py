import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from tkinter import filedialog
import os
import zipfile
from datetime import datetime

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class NotesApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Notes App")
        self.geometry("800x500")
        self.minsize(600, 400)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.header.grid_columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self.header, text="Notes App", font=("Arial", 20, "bold"))
        self.title_label.grid(row=0, column=0, padx=10, pady=10)

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self.header, textvariable=self.search_var, placeholder_text="Search notes...")
        self.search_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.search_notes)

        # Left: Note list
        self.note_frame = ctk.CTkScrollableFrame(self, width=200, label_text="Saved Notes")
        self.note_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ns")
        self.notes = {}
        self.active_note = None

        # Right: Editor frame
        self.editor_frame = ctk.CTkFrame(self)
        self.editor_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.editor_frame.grid_columnconfigure(0, weight=1)
        self.editor_frame.grid_rowconfigure(3, weight=1)

        # Title entry and category
        self.title_var = ctk.StringVar(value="Untitled")
        self.title_entry = ctk.CTkEntry(self.editor_frame, textvariable=self.title_var, placeholder_text="Note Title")
        self.title_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.category_var = ctk.StringVar(value="General")
        self.category_menu = ctk.CTkOptionMenu(self.editor_frame, values=["General", "Work", "Personal", "Ideas", "Code"],
                                               variable=self.category_var, command=self.update_category_color)
        self.category_menu.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        # Buttons row
        self.top_button_frame = ctk.CTkFrame(self.editor_frame)
        self.top_button_frame.grid(row=1, column=0, columnspan=2, pady=5)

        self.new_button = ctk.CTkButton(self.top_button_frame, text="New Note (Ctrl+N)", command=self.new_note)
        self.new_button.grid(row=0, column=0, padx=5)

        self.export_button = ctk.CTkButton(self.top_button_frame, text="Export All", command=self.export_all_notes)
        self.export_button.grid(row=0, column=1, padx=5)

        # Text area
        self.text_area = ctk.CTkTextbox(self.editor_frame, width=400, height=300, wrap="word")
        self.text_area.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        self.text_area.bind("<KeyRelease>", self.autosave_note)

        # Word count
        self.stats_label = ctk.CTkLabel(self.editor_frame, text="Words: 0 | Chars: 0")
        self.stats_label.grid(row=4, column=0, columnspan=2, padx=5, pady=2)

        # Buttons
        self.button_frame = ctk.CTkFrame(self.editor_frame)
        self.button_frame.grid(row=5, column=0, columnspan=2, pady=5)

        self.save_button = ctk.CTkButton(self.button_frame, text="Save As (Ctrl+S)", command=self.save_note_manual)
        self.save_button.grid(row=0, column=0, padx=5)

        self.load_button = ctk.CTkButton(self.button_frame, text="Load", command=self.load_note)
        self.load_button.grid(row=0, column=1, padx=5)

        self.clear_button = ctk.CTkButton(self.button_frame, text="Clear", command=self.clear_text)
        self.clear_button.grid(row=0, column=2, padx=5)

        self.delete_all_button = ctk.CTkButton(self.button_frame, text="Delete All", command=self.delete_all_notes, fg_color="red")
        self.delete_all_button.grid(row=0, column=3, padx=5)

        # Autosave directory
        self.notes_dir = os.path.join(os.getcwd(), "autosaved_notes")
        os.makedirs(self.notes_dir, exist_ok=True)
        self.current_autosave_file = None

        # Keyboard shortcuts
        self.bind("<Control-s>", lambda e: self.save_note_manual())
        self.bind("<Control-n>", lambda e: self.new_note())

        self.load_note_list()

    def update_category_color(self, category):
        colors = {"General": "#1f6aa5", "Work": "#d83a34", "Personal": "#2fa572", "Ideas": "#f9a62b", "Code": "#9b59b6"}
        self.text_area.configure(border_color=colors.get(category, "#1f6aa5"))

    def update_stats(self):
        text = self.text_area.get("1.0", "end-1c")
        words = len(text.split()) if text.strip() else 0
        chars = len(text)
        self.stats_label.configure(text=f"Words: {words} | Chars: {chars}")

    def new_note(self):
        self.clear_text()
        self.current_autosave_file = None
        self.title_var.set("Untitled")
        self.category_var.set("General")
        self.update_category_color("General")
        self.active_note = None
        self.update_note_list()

    def autosave_note(self, event=None):
        content = self.text_area.get("1.0", "end-1c")
        if not content.strip():
            return
        self.update_stats()
        title = self.title_var.get().replace(" ", "_") or "Untitled"
        category = self.category_var.get()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not self.current_autosave_file:
            self.current_autosave_file = os.path.join(self.notes_dir, f"{title}_{timestamp}_{category}.txt")
        with open(self.current_autosave_file, "w") as file:
            file.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {category}\n{content}")
        self.notes[os.path.basename(self.current_autosave_file)] = content
        self.update_note_list()

    def save_note_manual(self):
        category = self.category_var.get()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"[{timestamp}] {category}\n{self.text_area.get('1.0', 'end-1c')}"
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")],
                                                 initialfile=self.title_var.get())
        if file_path:
            with open(file_path, "w") as file:
                file.write(content)
            note_name = os.path.basename(file_path)
            self.notes[note_name] = content
            self.update_note_list()
            CTkMessagebox(title="Success", message="Note saved manually!", icon="check")

    def load_note(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.text_area.delete("1.0", "end")
                self.text_area.insert("1.0", content)
                self.title_var.set(os.path.splitext(os.path.basename(file_path))[0])
                self.current_autosave_file = None
                self.update_stats()

    def clear_text(self):
        response = CTkMessagebox(title="Confirm", message="Clear the text?", icon="question", option_1="Yes", option_2="No")
        if response.get() == "Yes":
            self.text_area.delete("1.0", "end")
            self.current_autosave_file = None
            self.update_stats()

    def load_note_list(self):
        for widget in self.note_frame.winfo_children():
            widget.destroy()
        # Load autosaved notes
        for file in os.listdir(self.notes_dir):
            if file.endswith(".txt") and file not in self.notes:
                with open(os.path.join(self.notes_dir, file), "r") as f:
                    self.notes[file] = f.read()
        # Display notes
        row = 0
        for note_name in sorted(self.notes.keys()):
            fg_color = "gray" if note_name == self.active_note else None
            btn = ctk.CTkButton(self.note_frame, text=note_name, command=lambda n=note_name: self.display_note(n), anchor="w",
                                fg_color=fg_color)
            btn.grid(row=row, column=0, padx=5, pady=2, sticky="ew")
            del_btn = ctk.CTkButton(self.note_frame, text="X", width=30, command=lambda n=note_name: self.delete_note(n), fg_color="red")
            del_btn.grid(row=row, column=1, padx=5, pady=2)
            row += 1

    def display_note(self, note_name):
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", self.notes[note_name])
        self.current_autosave_file = os.path.join(self.notes_dir, note_name) if note_name in os.listdir(self.notes_dir) else None
        self.active_note = note_name
        title = "_".join(note_name.split("_")[:-2]) if "_" in note_name else note_name.replace(".txt", "")
        self.title_var.set(title)
        category = note_name.split("_")[-1].replace(".txt", "") if "_" in note_name else "General"
        self.category_var.set(category)
        self.update_category_color(category)
        self.update_stats()
        self.update_note_list()

    def delete_note(self, note_name):
        response = CTkMessagebox(title="Delete?", message=f"Delete {note_name}?", icon="warning", option_1="Yes", option_2="No")
        if response.get() == "Yes":
            file_path = os.path.join(self.notes_dir, note_name)
            if os.path.exists(file_path):
                os.remove(file_path)
            del self.notes[note_name]
            if self.active_note == note_name:
                self.active_note = None
                self.clear_text()
            self.update_note_list()

    def delete_all_notes(self):
        response = CTkMessagebox(title="Delete All?", message="Delete all notes?", icon="warning", option_1="Yes", option_2="No")
        if response.get() == "Yes":
            for note_name in list(self.notes.keys()):
                file_path = os.path.join(self.notes_dir, note_name)
                if os.path.exists(file_path):
                    os.remove(file_path)
            self.notes.clear()
            self.active_note = None
            self.update_note_list()
            self.clear_text()

    def export_all_notes(self):
        if not self.notes:
            CTkMessagebox(title="Error", message="No notes to export!", icon="cancel")
            return
        export_path = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("ZIP Files", "*.zip")],
                                                  initialfile=f"notes_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        if export_path:
            with zipfile.ZipFile(export_path, "w") as zipf:
                for note_name, content in self.notes.items():
                    zipf.writestr(note_name, content)
            CTkMessagebox(title="Success", message="Notes exported successfully!", icon="check")

    def search_notes(self, event=None):
        query = self.search_var.get().lower()
        for widget in self.note_frame.winfo_children():
            widget.destroy()
        row = 0
        for note_name, content in sorted(self.notes.items()):
            if query in note_name.lower() or query in content.lower():
                fg_color = "gray" if note_name == self.active_note else None
                btn = ctk.CTkButton(self.note_frame, text=note_name, command=lambda n=note_name: self.display_note(n), anchor="w",
                                    fg_color=fg_color)
                btn.grid(row=row, column=0, padx=5, pady=2, sticky="ew")
                del_btn = ctk.CTkButton(self.note_frame, text="X", width=30, command=lambda n=note_name: self.delete_note(n), fg_color="red")
                del_btn.grid(row=row, column=1, padx=5, pady=2)
                row += 1

if __name__ == "__main__":
    app = NotesApp()
    app.mainloop()