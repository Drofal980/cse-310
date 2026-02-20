import tkinter as tk
from tkinter import messagebox, simpledialog
from note_editor import NoteEditorModal


class DashboardPage(tk.Frame):
    """
    Dashboard for the app
    Shows:
    - List of talk topic collections
    - Notes for the selected topic
    Allows:
    - Add topic (creates a new MongoDB collection)
    - Delete topic (drops the collection)
    - Add note
    - Edit note
    - Delete note
    """


    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_topic = None
        self.topics = []

        self.SELECT_TOPIC_ERROR = "Select a topic first"

        tk.Label(self, text="Talk Topics Dashboard", font=("Arial", 18)).pack(pady=10)

        # -----------------------------
        # Topic List
        # -----------------------------
        tk.Label(self, text="Your Talk Topics:", font=("Arial", 12)).pack()

        self.topic_list = tk.Listbox(self, width=60, height=8)
        self.topic_list.pack(pady=5)

        # Bind ONLY the topic list to load notes
        self.topic_list.bind("<<ListboxSelect>>", self.load_notes)

        # -----------------------------
        # Notes List
        # -----------------------------
        tk.Label(self, text="Notes for Selected Topic:", font=("Arial", 12)).pack(pady=5)

        self.notes_list = tk.Listbox(self, width=70, height=10)
        self.notes_list.pack(pady=5)

        # -----------------------------
        # Buttons
        # -----------------------------
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Topic", width=12,
                  command=self.add_topic).grid(row=0, column=0, padx=5)

        tk.Button(btn_frame, text="Delete Topic", width=12,
                  command=self.delete_topic).grid(row=0, column=1, padx=5)

        tk.Button(btn_frame, text="Add Note", width=12,
                  command=self.add_note).grid(row=0, column=2, padx=5)

        tk.Button(btn_frame, text="Edit Note", width=12,
                  command=self.edit_note).grid(row=0, column=3, padx=5)

        tk.Button(btn_frame, text="Delete Note", width=12,
                  command=self.delete_note).grid(row=0, column=4, padx=5)

        tk.Button(self, text="Refresh", width=12,
                  command=self.refresh).pack(pady=10)
        
        # Initial load of topics
        self.refresh()

    # -------------------------------------------------
    # Refresh topic list
    # -------------------------------------------------
    def refresh(self):
        self.topic_list.delete(0, tk.END)
        self.notes_list.delete(0, tk.END)
        self.selected_topic = None

        db = self.controller.db
        if not db:
            return

        self.topics = db.list_topics()

        for name in self.topics:
            self.topic_list.insert(tk.END, name)

    # -------------------------------------------------
    # Add Topic (Create Collection)
    # -------------------------------------------------
    def add_topic(self):
        db = self.controller.db

        topic_name = simpledialog.askstring(
            "New Topic",
            "Enter a name for the new talk topic:"
        )

        if not topic_name:
            return

        topic_name = topic_name.strip()

        if topic_name in db.list_topics():
            messagebox.showerror("Error", "A topic with that name already exists.")
            return

        try:
            db.create_topic(topic_name)
            messagebox.showinfo("Success", f"Created new topic: {topic_name}")
            self.refresh()

        except Exception as e: #pylint: disable=broad-except
            messagebox.showerror("Error", str(e))

    # -------------------------------------------------
    # Delete Topic (Drop Collection)
    # -------------------------------------------------
    def delete_topic(self):
        if not self.selected_topic:
            messagebox.showerror("Error", self.SELECT_TOPIC_ERROR)
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the topic '{self.selected_topic}'?\n"
            "This will permanently delete all notes in this topic."
        )

        if not confirm:
            return

        try:
            self.controller.db.delete_topic(self.selected_topic)
            messagebox.showinfo("Deleted", f"Topic '{self.selected_topic}' deleted.")
            self.refresh()

        except Exception as e:  #pylint: disable=broad-except
            messagebox.showerror("Error", str(e))

    # -------------------------------------------------
    # Load notes for selected topic
    # -------------------------------------------------
    def load_notes(self, event=None):
        # Only respond if the TOPIC listbox triggered the event
        if event and event.widget is not self.topic_list:
            return

        self.notes_list.delete(0, tk.END)

        idx = self.topic_list.curselection()
        if not idx:
            return

        topic_name = self.topics[idx[0]]
        self.selected_topic = topic_name

        doc = self.controller.db.get_topic_doc(topic_name)
        if not doc or "notes" not in doc:
            return

        for note in doc["notes"]:
            self.notes_list.insert(tk.END, note)



    # -------------------------------------------------
    # Add Note
    # -------------------------------------------------
    def add_note(self):
        if not self.selected_topic:
            messagebox.showerror("Error", self.SELECT_TOPIC_ERROR)
            return

        NoteEditorModal(
            parent=self,
            db=self.controller.db,
            topic_name=self.selected_topic,
            mode="add"
        )
        self.refresh()

    # -------------------------------------------------
    # Edit Note
    # -------------------------------------------------
    def edit_note(self):
        if not self.selected_topic:
            messagebox.showerror("Error", self.SELECT_TOPIC_ERROR)
            return

        doc = self.controller.db.get_topic_doc(self.selected_topic)
        notes = doc.get("notes", [])

        if not notes:
            messagebox.showinfo("No Notes", "This topic has no notes to edit.")
            return

        # Create popup window
        win = tk.Toplevel(self)
        win.title("Select Note to Edit")
        win.geometry("500x300")
        win.grab_set()

        tk.Label(win, text="Select a note to edit:", font=("Arial", 12)).pack(pady=10)

        listbox = tk.Listbox(win, width=60, height=10)
        listbox.pack(pady=5)

        for note in notes:
            listbox.insert(tk.END, note)

        def confirm_edit():
            idx = listbox.curselection()
            if not idx:
                messagebox.showerror("Error", "Select a note to edit")
                return
            note_index = idx[0]
            current_text = notes[note_index]
            win.destroy()

            NoteEditorModal(
                parent=self,
                db=self.controller.db,
                topic_name=self.selected_topic,
                mode="edit",
                note_index=note_index,
                text=current_text
            )
            self.refresh()

        tk.Button(win, text="Edit Selected Note", command=confirm_edit).pack(pady=10)


    # -------------------------------------------------
    # Delete Note
    # -------------------------------------------------
    def delete_note(self):
        if not self.selected_topic:
            messagebox.showerror("Error", self.SELECT_TOPIC_ERROR)
            return

        doc = self.controller.db.get_topic_doc(self.selected_topic)
        notes = doc.get("notes", [])

        if not notes:
            messagebox.showinfo("No Notes", "This topic has no notes to delete.")
            return

        # Create popup window
        win = tk.Toplevel(self)
        win.title("Select Note to Delete")
        win.geometry("500x300")
        win.grab_set()

        tk.Label(win, text="Select a note to delete:", font=("Arial", 12)).pack(pady=10)

        listbox = tk.Listbox(win, width=60, height=10)
        listbox.pack(pady=5)

        for note in notes:
            listbox.insert(tk.END, note)

        def confirm_delete():
            idx = listbox.curselection()
            if not idx:
                messagebox.showerror("Error", "Select a note to delete")
                return
            note_index = idx[0]
            confirm = messagebox.askyesno("Confirm Delete", "Delete this note?")
            if confirm:
                self.controller.db.delete_note(self.selected_topic, note_index)
                self.refresh()
            win.destroy()

        tk.Button(win, text="Delete Selected Note", command=confirm_delete).pack(pady=10)

