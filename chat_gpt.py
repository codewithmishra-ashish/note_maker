import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from tkinter import filedialog, font, simpledialog, Menu
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

        # Menu Bar
        self.menu_bar = Menu(self)
        self.config(menu=self.menu_bar)

        # File Menu
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New Note", command=self.new_note)
        self.file_menu.add_command(label="Open Note", command=self.load_note)
        self.file_menu.add_command(label="Save Note", command=self.save_note)
        self.file_menu.add_command(label="Export as PDF", command=self.export_as_pdf)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit)

        # Edit Menu
        self.edit_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Search", command=self.search_text)
        self.edit_menu.add_command(label="Replace", command=self.replace_text)
        self.edit_menu.add_command(label="Pin Note", command=self.pin_note)

        # View Menu
        self.view_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)

        # Help Menu
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)

        # Editor
        self.text_area = ctk.CTkTextbox(self, width=400, height=300)
        self.text_area.pack(padx=5, pady=5, fill="both", expand=True)
        self.text_area.bind("<ButtonRelease-1>", self.show_formatting_menu)

        # Status Bar
        self.status_bar = ctk.CTkLabel(self, text="Words: 0 | Characters: 0", anchor="e")
        self.status_bar.pack(side="bottom", fill="x")

        # Shortcuts
        self.bind("<Control-s>", lambda event: self.save_note())
        self.bind("<Control-f>", lambda event: self.search_text())
        self.bind("<Control-e>", lambda event: self.export_as_pdf())
        self.bind("<KeyRelease>", lambda event: self.update_word_count())

        # Autosave
        self.start_autosave()

    def show_formatting_menu(self, event):
        try:
            selected_text = self.text_area.get(ctk.SEL_FIRST, ctk.SEL_LAST)
            if selected_text:
                format_menu = Menu(self, tearoff=0)
                format_menu.add_command(label="Bold", command=lambda: self.apply_tag("bold"))
                format_menu.add_command(label="Italic", command=lambda: self.apply_tag("italic"))
                format_menu.add_command(label="Underline", command=lambda: self.apply_tag("underline"))
                format_menu.add_command(label="Change Font Size", command=self.change_font_size)
                format_menu.add_command(label="Align Left", command=lambda: self.align_text("left"))
                format_menu.add_command(label="Align Center", command=lambda: self.align_text("center"))
                format_menu.add_command(label="Align Right", command=lambda: self.align_text("right"))
                format_menu.tk_popup(event.x_root, event.y_root)
        except:
            pass

    def apply_tag(self, tag):
        if tag == "bold":
            self.text_area.tag_add("bold", ctk.SEL_FIRST, ctk.SEL_LAST)
            self.text_area.tag_config("bold", foreground="black", underline=0)
        elif tag == "italic":
            self.text_area.tag_add("italic", ctk.SEL_FIRST, ctk.SEL_LAST)
            self.text_area.tag_config("italic", foreground="gray")
        elif tag == "underline":
            self.text_area.tag_add("underline", ctk.SEL_FIRST, ctk.SEL_LAST)
            self.text_area.tag_config("underline", underline=1)

    def change_font_size(self):
        size = simpledialog.askinteger("Font Size", "Enter new font size:")
        if size:
            self.text_area.tag_add("size", ctk.SEL_FIRST, ctk.SEL_LAST)
            self.text_area.tag_config("size", offset=size // 2)

    def align_text(self, alignment):
        self.text_area.tag_add(alignment, ctk.SEL_FIRST, ctk.SEL_LAST)
        self.text_area.tag_config(alignment, justify=alignment)

    def new_note(self):
        self.text_area.delete("1.0", "end")

    def save_note(self):
        content = self.text_area.get("1.0", "end-1c")
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

    def toggle_theme(self):
        self.current_theme = "Dark" if self.current_theme == "Light" else "Light"
        ctk.set_appearance_mode(self.current_theme)

    def show_about(self):
        CTkMessagebox(title="About", message="Notes App\nCreated with customtkinter", icon="info")

    def pin_note(self):
        self.attributes('-topmost', True)
        CTkMessagebox(title="Pin Note", message="Note pinned on top!", icon="info")

    def search_text(self):
        search_term = simpledialog.askstring("Search", "Enter text to search:")
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

    def replace_text(self):
        search_term = simpledialog.askstring("Replace", "Enter text to search:")
        if search_term:
            replace_term = simpledialog.askstring("Replace", "Enter replacement text:")
            content = self.text_area.get("1.0", "end-1c")
            new_content = content.replace(search_term, replace_term)
            self.text_area.delete("1.0", "end")
            self.text_area.insert("1.0", new_content)
            CTkMessagebox(title="Success", message="Text replaced!", icon="check")

    def autosave(self):
        while True:
            content = self.text_area.get("1.0", "end-1c")
            if content.strip():
                self.save_note()
            threading.Event().wait(self.autosave_interval)

    def start_autosave(self):
        autosave_thread = threading.Thread(target=self.autosave, daemon=True)
        autosave_thread.start()

    def update_word_count(self):
        content = self.text_area.get("1.0", "end-1c")
        words = len(content.split())
        chars = len(content)
        self.status_bar.configure(text=f"Words: {words} | Characters: {chars}")

if __name__ == "__main__":
    app = NotesApp()
    app.mainloop()
