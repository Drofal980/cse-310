import os
from cryptography.fernet import Fernet

KEY_FILE = "session.key"
SESSION_FILE = "session.enc"


def _get_fernet():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return Fernet(key)


def save_session(username: str, host: str):
    f = _get_fernet()
    data = f"{username}||{host}".encode("utf-8")
    token = f.encrypt(data)
    with open(SESSION_FILE, "wb") as f_out:
        f_out.write(token)


def load_session():
    if not os.path.exists(SESSION_FILE):
        return {}
    f = _get_fernet()
    with open(SESSION_FILE, "rb") as f_in:
        token = f_in.read()
    try:
        data = f.decrypt(token).decode("utf-8")
        username, host = data.split("||", 1)
        return {"username": username, "host": host}
    except Exception: #pylint: disable=broad-except
        return {}
