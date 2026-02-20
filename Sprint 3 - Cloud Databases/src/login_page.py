import tkinter as tk
from tkinter import messagebox
from secure_session import save_session, load_session
from talk_ideas_db import TalkIdeasDB


class LoginPage(tk.Frame):
    """
    Login screen for the app.
    Handles:
    - Username/password/host input
    - Password masking toggle
    - Encrypted session persistence
    - MongoDB connection
    """
    CONN_ERR_HEADER = "Connection Error"
    CONN_ERR_MSG = "Failed to connect to MongoDB. Check your credentials and host."

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Login to Talk Ideas", font=("Arial", 18)).pack(pady=20)

        session = load_session()

        form = tk.Frame(self)
        form.pack(pady=10)

        tk.Label(form, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(form, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        tk.Label(form, text="Host:").grid(row=2, column=0, padx=5, pady=5)

        self.username_entry = tk.Entry(form)
        self.password_entry = tk.Entry(form, show="*")
        self.host_entry = tk.Entry(form)

        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        self.host_entry.grid(row=2, column=1, padx=5, pady=5)

        self.username_entry.insert(0, session.get("username", ""))
        self.host_entry.insert(0, session.get("host", "localhost:27017"))

        # Password toggle
        self.show_password = tk.BooleanVar()
        tk.Checkbutton(
            form,
            text="Show Password",
            variable=self.show_password,
            command=self.toggle_password
        ).grid(row=1, column=2, padx=5)

        tk.Button(self, text="Connect", command=self.connect).pack(pady=20)

    def toggle_password(self):
        self.password_entry.config(show="" if self.show_password.get() else "*")

    def connect(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        host = self.host_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Username and password required")
            return

        uri = f"mongodb+srv://{username}:{password}@{host}"

        try:
            db = TalkIdeasDB(uri)
            self.controller.set_db(db)

            save_session(username, host)

            # Test connection by listing databases
            if db.ping():
                messagebox.showinfo("Success", "Connected successfully!")
                self.controller.show_frame("DashboardPage")
            else:
                messagebox.showerror(self.CONN_ERR_HEADER, self.CONN_ERR_MSG)
        
        except ConnectionError:
            messagebox.showerror(self.CONN_ERR_HEADER, self.CONN_ERR_MSG)

        except Exception as e:  #pylint: disable=broad-except
            messagebox.showerror(self.CONN_ERR_HEADER, str(e))
