#!/usr/bin/env python3
import socket
import threading
import json
import curses
import time

HOST = '127.0.0.1'
PORT = 1982

DIR_KEYS = {
    curses.KEY_UP: "UP",
    curses.KEY_DOWN: "DOWN",
    curses.KEY_LEFT: "LEFT",
    curses.KEY_RIGHT: "RIGHT",
    ord('w'): "UP",
    ord('s'): "DOWN",
    ord('a'): "LEFT",
    ord('d'): "RIGHT"
}

class Client:
    def __init__(self, host, port, name="Player"):
        self.addr = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = name
        self.running = True
        self.state = None
        self.buf = ""
        self.id = None

    def connect(self):
        self.sock.connect(self.addr)
        self.send({"type":"join","name":self.name})
        threading.Thread(target=self.recv_loop, daemon=True).start()

    def send(self, msg):
        try:
            self.sock.sendall((json.dumps(msg)+"\n").encode())
        except:
            self.running = False

    def recv_loop(self):
        while self.running:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break
                self.buf += data.decode()
                while "\n" in self.buf:
                    line, self.buf = self.buf.split("\n",1)
                    try:
                        msg = json.loads(line)
                    except:
                        continue
                    if msg.get("type") == "join_ack":
                        self.id = msg.get("id")
                    elif msg.get("type") == "state":
                        self.state = msg
            except:
                break
        self.running = False

    def init_colors(self):
        # Returns True if colors are available
        if not curses.has_colors():
            return False
        curses.start_color()
        curses.use_default_colors()
        # Map server color ids 1..7 to curses colors
        # 1 red, 2 green, 3 yellow, 4 blue, 5 magenta, 6 cyan, 7 white
        mapping = {
            1: curses.COLOR_RED,
            2: curses.COLOR_GREEN,
            3: curses.COLOR_YELLOW,
            4: curses.COLOR_BLUE,
            5: curses.COLOR_MAGENTA,
            6: curses.COLOR_CYAN,
            7: curses.COLOR_WHITE
        }
        for cid, color in mapping.items():
            try:
                curses.init_pair(cid, color, -1)
            except:
                # ignore if terminal can't init a pair
                pass
        return True

    def run_curses(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(50)
        has_colors = self.init_colors()
        name = self.name
        while self.running:
            ch = stdscr.getch()
            if ch == ord('q'):
                self.running = False
                break
            if ch in DIR_KEYS:
                self.send({"type":"input","dir":DIR_KEYS[ch]})
            stdscr.erase()
            if not self.state:
                stdscr.addstr(0,0,"Waiting for game state...")
                stdscr.refresh()
                time.sleep(0.05)
                continue
            rows, cols = self.state.get("grid_size", [20,40])
            power = self.state.get("powerup",[0,0])
            players = self.state.get("players",[])
            # draw border
            try:
                for r in range(rows+2):
                    stdscr.addstr(r, 0, "|")
                    stdscr.addstr(r, cols+1, "|")
                for c in range(cols+2):
                    stdscr.addstr(0, c, "-")
                    stdscr.addstr(rows+1, c, "-")
            except curses.error:
                pass
            # draw powerup
            pr, pc = power
            try:
                stdscr.addstr(1+pr, 1+pc, "*")
            except curses.error:
                pass
            # draw players and trails
            for p in players:
                pid = p.get("id")
                color_id = p.get("color", 7)
                alive = p.get("alive", True)
                head_char = "@" if alive else "X"
                # draw trail segments
                for seg in p.get("trail", []):
                    sr, sc, _ = seg
                    try:
                        if has_colors:
                            attr = curses.color_pair(color_id)
                            stdscr.addstr(1+sr, 1+sc, ".", attr)
                        else:
                            stdscr.addstr(1+sr, 1+sc, ".")
                    except curses.error:
                        pass
                # draw head
                hr, hc = p.get("head", [0,0])
                try:
                    if has_colors:
                        attr = curses.color_pair(color_id) | curses.A_BOLD
                        stdscr.addstr(1+hr, 1+hc, head_char, attr)
                    else:
                        stdscr.addstr(1+hr, 1+hc, head_char)
                except curses.error:
                    pass
            stdscr.addstr(rows+3, 0, f"Name: {name}  (q to quit)")
            stdscr.refresh()
            time.sleep(0.05)
        try:
            self.sock.close()
        except:
            pass

if __name__ == "__main__":
    import sys
    name = sys.argv[1] if len(sys.argv)>1 else "Player"
    client = Client(HOST, PORT, name)
    try:
        client.connect()
    except Exception as e:
        print("Could not connect:", e)
        sys.exit(1)
    curses.wrapper(client.run_curses)
