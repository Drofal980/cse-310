import tkinter as tk
from talk_ideas_db import TalkIdeasDB


class App(tk.Tk):
    """
    Root application that manages navigation and shared DB instance.
    Ensures MongoDB connection closes on exit.
    """
    def __init__(self):
        super().__init__()
        self.title("Church Talk Ideas")
        self.geometry("600x600")

        self.db = None  # Will hold TalkIdeasDB after login

        # Handle window close event
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}

        # Import pages here to avoid circular imports
        from login_page import LoginPage
        from dashboard_page import DashboardPage

        for page in (LoginPage, DashboardPage):
            frame = page(parent=container, controller=self)
            self.frames[page.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def show_frame(self, name: str):
        frame = self.frames[name]
        frame.tkraise()

    def set_db(self, db: TalkIdeasDB):
        self.db = db

    # -------------------------------------------------
    # Graceful shutdown
    # -------------------------------------------------
    def on_close(self):
        """
        Called when the user closes the window.
        Ensures MongoDB connection is closed cleanly.
        """
        if self.db:
            try:
                self.db.close()
            except Exception:  #pylint: disable=broad-except
                pass  # Avoid blocking shutdown

        self.destroy()


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app = App()
    app.mainloop()
