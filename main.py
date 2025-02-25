import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from tkinter import filedialog, simpledialog, Menu, Text
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

        # Here, we have initialized the menu bar.
        self.menu_bar = Menu(self)
        self.config(menu=self.menu_bar)

        # This is File menu option and its contents
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New Note", command=self.new_note)
        self.file_menu.add_command(label="Open Note", command=self.load_note)
        self.file_menu.add_command(label="Save Note", command=self.save_note)
        self.file_menu.add_command(label="Export as PDF", command=self.export_as_pdf)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit)

        # This is Edit menu option and its contents
        self.edit_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Search", command=self.search_text)
        self.edit_menu.add_command(label="Replace", command=self.replace_text)

        # This is View menu option where u can change theme to dark
        self.view_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Toggle Theme", command=self.toggle_theme)

        # Here, you get into help section presenting creator info
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)

        # This is major text editting area
        self.text_area = Text(self, width=50, height=20, font=("Arial", 12))
        self.text_area.pack(padx=5, pady=5, fill="both", expand=True)
        self.text_area.bind("<Button-3>", self.show_formatting_menu)
        
        # These are basic options for word formatting
        self.text_area.tag_configure("bold", font=("Arial", 12, "bold"))
        self.text_area.tag_configure("italic", font=("Arial", 12, "italic"))
        self.text_area.tag_configure("underline", font=("Arial", 12, "normal"), underline=True)
        self.text_area.tag_configure("highlight", background="#FFFF99")

        # This is for initializing footer
        self.footer_frame = ctk.CTkFrame(self)
        self.footer_frame.pack(side="bottom", fill="x")

        # This represents creator section
        self.creator_label = ctk.CTkLabel(self.footer_frame, text="Created by Ashish Mishra", anchor="w")
        self.creator_label.pack(side="left", padx=5)

        # This displays word & character count
        self.status_label = ctk.CTkLabel(self.footer_frame, text="Words: 0 | Characters: 0", anchor="e")
        self.status_label.pack(side="right", padx=5)

        # Creation of shortcut keys
        self.bind("<Control-s>", lambda event: self.save_note())
        self.bind("<Control-f>", lambda event: self.search_text())
        self.bind("<Control-e>", lambda event: self.export_as_pdf())
        self.bind("<Control-b>", lambda event: self.apply_format("bold"))
        self.bind("<Control-i>", lambda event: self.apply_format("italic"))
        self.bind("<Control-u>", lambda event: self.apply_format("underline"))
        self.bind("<KeyRelease>", lambda event: self.update_word_count())

        # Autosave Option Enabled
        self.start_autosave()

    # This gives toggle to word formatting options
    def show_formatting_menu(self, event):
        try:
            if self.text_area.tag_ranges("sel"):
                format_menu = Menu(self, tearoff=0)
                format_menu.add_command(label="Bold (Ctrl+B)", command=lambda: self.apply_format("bold"))
                format_menu.add_command(label="Italic (Ctrl+I)", command=lambda: self.apply_format("italic"))
                format_menu.add_command(label="Underline (Ctrl+U)", command=lambda: self.apply_format("underline"))
                format_menu.add_command(label="Change Font Size", command=self.change_font_size)
                format_menu.add_command(label="Align Left", command=lambda: self.align_text("left"))
                format_menu.add_command(label="Align Center", command=lambda: self.align_text("center"))
                format_menu.add_command(label="Align Right", command=lambda: self.align_text("right"))
                format_menu.tk_popup(event.x_root, event.y_root)
        except:
            pass


    # This applies formatting to the text
    def apply_format(self, style):
        try:
            if self.text_area.tag_ranges("sel"):
                start = self.text_area.index("sel.first")
                end = self.text_area.index("sel.last")
                current_tags = self.text_area.tag_names(start)

                # Check if style is already applied
                if style in current_tags:
                    self.text_area.tag_remove(style, start, end)
                else:
                    self.text_area.tag_add(style, start, end)

                # Preserve the content
                content = self.text_area.get("1.0", "end-1c")
                self.text_area.delete("1.0", "end")
                self.text_area.insert("1.0", content)
                
                # Reapply all current tags to maintain other formatting
                for tag in current_tags:
                    if tag in ["bold", "italic", "underline"] and tag != style:
                        self.text_area.tag_add(tag, start, end)

        except Exception as e:
            print(f"Error in apply_format: {e}")


    # This creates font change.
    def change_font_size(self):
        size = simpledialog.askinteger("Font Size", "Enter new font size:", minvalue=8, maxvalue=72)
        if size and self.text_area.tag_ranges("sel"):
            try:
                start = self.text_area.index("sel.first")
                end = self.text_area.index("sel.last")
                current_tags = self.text_area.tag_names(start)
                
                # Get current styles
                styles = set()
                for tag in ["bold", "italic", "underline"]:
                    if tag in current_tags:
                        styles.add(tag)
                
                # Remove existing size tags
                for tag in current_tags:
                    if tag.startswith("size_"):
                        self.text_area.tag_remove(tag, start, end)
                
                # Apply new size tag
                size_tag = f"size_{size}"
                font_config = ["Arial", size]
                if "bold" in styles and "italic" in styles:
                    font_config.append("bold italic")
                elif "bold" in styles:
                    font_config.append("bold")
                elif "italic" in styles:
                    font_config.append("italic")
                else:
                    font_config.append("normal")
                
                self.text_area.tag_configure(size_tag, font=tuple(font_config), underline="underline" in styles)
                self.text_area.tag_add(size_tag, start, end)
                
                # Reapply style tags
                for style in styles:
                    self.text_area.tag_add(style, start, end)

            except Exception as e:
                print(f"Error in change_font_size: {e}")


    # This helps to allign text
    def align_text(self, alignment):
        try:
            if self.text_area.tag_ranges("sel"):
                tag_name = f"align_{alignment}"
                self.text_area.tag_configure(tag_name, justify=alignment)
                self.text_area.tag_add(tag_name, "sel.first", "sel.last")
        except:
            pass


    # This clears the text area.
    def new_note(self):
        self.text_area.delete("1.0", "end")


    # This saves the note made 
    def save_note(self):
        content = self.text_area.get("1.0", "end-1c")
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(content)
            CTkMessagebox(title="Success", message="Note saved!", icon="check")


    # This opens pre-existing files
    def load_note(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.text_area.delete("1.0", "end")
                self.text_area.insert("1.0", content)
            self.update_word_count()


    # This is to save made note as pdf
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


    # This changes theme of the application
    def toggle_theme(self):
        self.current_theme = "Dark" if self.current_theme == "Light" else "Light"
        ctk.set_appearance_mode(self.current_theme)
        bg = "#2B2B2B" if self.current_theme == "Dark" else "white"
        fg = "white" if self.current_theme == "Dark" else "black"
        self.text_area.configure(bg=bg, fg=fg)


    # This gives description about the creator
    def show_about(self):
        CTkMessagebox(
            title="About", 
            message="This NoteMaker is created by Ashish Mishra, B.Tech CSE MANIT, BHOPAL",
            icon="info"
        )


    # This is to search text
    def search_text(self):
        search_term = simpledialog.askstring("Search", "Enter text to search:")
        if search_term:
            start = "1.0"
            self.text_area.tag_remove("highlight", "1.0", "end")
            while True:
                start = self.text_area.search(search_term, start, stopindex="end")
                if not start:
                    break
                end = f"{start}+{len(search_term)}c"
                self.text_area.tag_add("highlight", start, end)
                start = end


    # This is to search & replace text 
    def replace_text(self):
        search_term = simpledialog.askstring("Replace", "Enter text to search:")
        if search_term:
            replace_term = simpledialog.askstring("Replace", "Enter replacement text:")
            content = self.text_area.get("1.0", "end-1c")
            new_content = content.replace(search_term, replace_term)
            self.text_area.delete("1.0", "end")
            self.text_area.insert("1.0", new_content)
            CTkMessagebox(title="Success", message="Text replaced!", icon="check")


    # This autosaves the file if exists already
    def autosave(self):
        while True:
            content = self.text_area.get("1.0", "end-1c")
            if content.strip():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(f"autosave_{timestamp}.txt", "w") as file:
                    file.write(content)
            threading.Event().wait(self.autosave_interval)

    def start_autosave(self):
        autosave_thread = threading.Thread(target=self.autosave, daemon=True)
        autosave_thread.start()


    # This updates word count & charater as written
    def update_word_count(self):
        content = self.text_area.get("1.0", "end-1c")
        words = len(content.split())
        chars = len(content)
        self.status_label.configure(text=f"Words: {words} | Characters: {chars}")

if __name__ == "__main__":
    app = NotesApp()
    app.mainloop()