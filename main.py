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

        # Editor with Tkinter Text widget
        self.text_area = Text(self, width=50, height=20, font=("Arial", 12))
        self.text_area.pack(padx=5, pady=5, fill="both", expand=True)
        self.text_area.bind("<Button-3>", self.show_formatting_menu)
        
        # Configure base formatting tags
        self.text_area.tag_configure("bold", font=("Arial", 12, "bold"))
        self.text_area.tag_configure("italic", font=("Arial", 12, "italic"))
        self.text_area.tag_configure("underline", font=("Arial", 12), underline=True)
        self.text_area.tag_configure("highlight", background="#FFFF99")

        # Footer Frame
        self.footer_frame = ctk.CTkFrame(self)
        self.footer_frame.pack(side="bottom", fill="x")

        # Creator Label (left)
        self.creator_label = ctk.CTkLabel(self.footer_frame, text="Created by Ashish Mishra", anchor="w")
        self.creator_label.pack(side="left", padx=5)

        # Status Label (right)
        self.status_label = ctk.CTkLabel(self.footer_frame, text="Words: 0 | Characters: 0", anchor="e")
        self.status_label.pack(side="right", padx=5)

        # Shortcuts
        self.bind("<Control-s>", lambda event: self.save_note())
        self.bind("<Control-f>", lambda event: self.search_text())
        self.bind("<Control-e>", lambda event: self.export_as_pdf())
        self.bind("<Control-b>", lambda event: self.toggle_format("bold"))
        self.bind("<Control-i>", lambda event: self.toggle_format("italic"))
        self.bind("<Control-u>", lambda event: self.toggle_format("underline"))
        self.bind("<KeyRelease>", lambda event: self.update_word_count())

        # Autosave
        self.start_autosave()

    def show_formatting_menu(self, event):
        try:
            if self.text_area.tag_ranges("sel"):
                format_menu = Menu(self, tearoff=0)
                format_menu.add_command(label="Bold (Ctrl+B)", command=lambda: self.toggle_format("bold"))
                format_menu.add_command(label="Italic (Ctrl+I)", command=lambda: self.toggle_format("italic"))
                format_menu.add_command(label="Underline (Ctrl+U)", command=lambda: self.toggle_format("underline"))
                format_menu.add_command(label="Change Font Size", command=self.change_font_size)
                format_menu.add_command(label="Align Left", command=lambda: self.align_text("left"))
                format_menu.add_command(label="Align Center", command=lambda: self.align_text("center"))
                format_menu.add_command(label="Align Right", command=lambda: self.align_text("right"))
                format_menu.tk_popup(event.x_root, event.y_root)
        except:
            pass

    def toggle_format(self, style):
        try:
            if self.text_area.tag_ranges("sel"):
                start = "sel.first"
                end = "sel.last"
                current_tags = self.text_area.tag_names(start)
                
                # Get current font size and styles
                size = 12
                styles = set()
                for tag in current_tags:
                    if tag.startswith("size_"):
                        size = int(tag.split("_")[1])
                    elif tag == "bold":
                        styles.add("bold")
                    elif tag == "italic":
                        styles.add("italic")
                    elif tag == "underline":
                        styles.add("underline")

                # Toggle the selected style
                if style in styles:
                    styles.remove(style)
                    self.text_area.tag_remove(style, start, end)
                else:
                    styles.add(style)
                    self.text_area.tag_add(style, start, end)

                # Remove any previous combined format tags
                for tag in current_tags:
                    if tag.startswith("format_"):
                        self.text_area.tag_remove(tag, start, end)

                # Apply combined formatting if there are styles
                if styles:
                    font_style = "normal"
                    underline = "underline" in styles
                    
                    if "bold" in styles and "italic" in styles:
                        font_style = "bold italic"
                    elif "bold" in styles:
                        font_style = "bold"
                    elif "italic" in styles:
                        font_style = "italic"

                    # Configure and apply the combined tag
                    combined_tag = f"format_{'_'.join(sorted(styles))}_{size}"
                    self.text_area.tag_configure(
                        combined_tag,
                        font=("Arial", size, font_style),
                        underline=underline
                    )
                    self.text_area.tag_add(combined_tag, start, end)

                # Update size tag if no styles remain
                if not styles and size != 12:
                    size_tag = f"size_{size}"
                    self.text_area.tag_configure(size_tag, font=("Arial", size))
                    self.text_area.tag_add(size_tag, start, end)

        except Exception as e:
            print(f"Error in toggle_format: {e}")

    def change_font_size(self):
        size = simpledialog.askinteger("Font Size", "Enter new font size:", minvalue=8, maxvalue=72)
        if size and self.text_area.tag_ranges("sel"):
            try:
                start = "sel.first"
                end = "sel.last"
                current_tags = self.text_area.tag_names(start)
                
                # Get current styles
                styles = set()
                for tag in ["bold", "italic", "underline"]:
                    if tag in current_tags:
                        styles.add(tag)
                
                # Remove existing size and format tags
                for tag in current_tags:
                    if tag.startswith("size_") or tag.startswith("format_"):
                        self.text_area.tag_remove(tag, start, end)
                
                # Apply new formatting with size
                if styles:
                    font_style = "normal"
                    underline = "underline" in styles
                    if "bold" in styles and "italic" in styles:
                        font_style = "bold italic"
                    elif "bold" in styles:
                        font_style = "bold"
                    elif "italic" in styles:
                        font_style = "italic"
                    
                    combined_tag = f"format_{'_'.join(sorted(styles))}_{size}"
                    self.text_area.tag_configure(
                        combined_tag,
                        font=("Arial", size, font_style),
                        underline=underline
                    )
                    self.text_area.tag_add(combined_tag, start, end)
                    
                    # Reapply individual style tags
                    for s in styles:
                        self.text_area.tag_add(s, start, end)
                else:
                    size_tag = f"size_{size}"
                    self.text_area.tag_configure(size_tag, font=("Arial", size))
                    self.text_area.tag_add(size_tag, start, end)

            except:
                pass

    def align_text(self, alignment):
        try:
            if self.text_area.tag_ranges("sel"):
                tag_name = f"align_{alignment}"
                self.text_area.tag_configure(tag_name, justify=alignment)
                self.text_area.tag_add(tag_name, "sel.first", "sel.last")
        except:
            pass

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
        bg = "#2B2B2B" if self.current_theme == "Dark" else "white"
        fg = "white" if self.current_theme == "Dark" else "black"
        self.text_area.configure(bg=bg, fg=fg)

    def show_about(self):
        CTkMessagebox(
            title="About", 
            message="This NoteMaker is created by Ashish Mishra, 1st year, B.Tech CSE MANIT, BHOPAL",
            icon="info"
        )

    def pin_note(self):
        self.attributes('-topmost', True)
        CTkMessagebox(title="Pin Note", message="Note pinned on top!", icon="info")

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
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(f"autosave_{timestamp}.txt", "w") as file:
                    file.write(content)
            threading.Event().wait(self.autosave_interval)

    def start_autosave(self):
        autosave_thread = threading.Thread(target=self.autosave, daemon=True)
        autosave_thread.start()

    def update_word_count(self):
        content = self.text_area.get("1.0", "end-1c")
        words = len(content.split())
        chars = len(content)
        self.status_label.configure(text=f"Words: {words} | Characters: {chars}")

if __name__ == "__main__":
    app = NotesApp()
    app.mainloop()