import tkinter as tk
from tkinter import messagebox


class NoteEditorModal:
    """
    A modal window for adding or editing a note.
    Supports:
    - mode="add"
    - mode="edit"
    Uses topic_name instead of idea_id.
    """
    def __init__(self, parent, db, topic_name, mode="add", note_index=None, text=""):
        self.db = db
        self.topic_name = topic_name
        self.mode = mode
        self.note_index = note_index

        # Create modal window
        self.win = tk.Toplevel(parent)
        self.win.title("Note Editor")
        self.win.geometry("500x350")
        self.win.grab_set()  # Make modal

        # Title
        title = "Add Note" if mode == "add" else "Edit Note"
        tk.Label(self.win, text=title, font=("Arial", 14)).pack(pady=10)

        # Textbox
        self.textbox = tk.Text(self.win, width=60, height=12)
        self.textbox.pack(padx=10, pady=5)
        self.textbox.insert("1.0", text)

        # Save button
        tk.Button(self.win, text="Save", width=12, command=self.save).pack(pady=10)

    # -------------------------------------------------
    # Save note
    # -------------------------------------------------
    def save(self):
        content = self.textbox.get("1.0", tk.END).strip()

        if not content:
            messagebox.showerror("Error", "Note cannot be empty")
            return

        try:
            if self.mode == "add":
                self.db.add_note(self.topic_name, content)
            else:
                self.db.edit_note(self.topic_name, self.note_index, content)

            self.win.destroy()

        except Exception as e:  #pylint: disable=broad-except
            messagebox.showerror("Error", str(e))