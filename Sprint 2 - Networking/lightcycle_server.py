#!/usr/bin/env python3
import socket
import threading
import json
import time
import random

from collections import deque

HOST = '127.0.0.1'
PORT = 1982
TICK_RATE = 6  # ticks per second
ROWS, COLS = 20, 40
START_LENGTH = 4

DIR_VECTORS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1)
}
OPPOSITE = {"UP":"DOWN","DOWN":"UP","LEFT":"RIGHT","RIGHT":"LEFT"}
PERPENDICULAR = {
    "UP": {"LEFT","RIGHT"},
    "DOWN": {"LEFT","RIGHT"},
    "LEFT": {"UP","DOWN"},
    "RIGHT": {"UP","DOWN"}
}

lock = threading.Lock()

class Player:
    _id_counter = 1
    def __init__(self, name):
        self.id = Player._id_counter; Player._id_counter += 1
        self.name = name
        self.alive = True
        self.dir = random.choice(list(DIR_VECTORS.keys()))
        self.next_dir = self.dir
        self.color = random.randint(1,7)
        self.trail = deque()  # store (r,c,dir) for each segment
        self.head = None
        self.init_position()

    def init_position(self):
        # place randomly with room for start length
        r = random.randint(1, ROWS-2)
        c = random.randint(1, COLS-2)
        dr, dc = DIR_VECTORS[self.dir]
        # build initial trail behind head
        self.trail.clear()
        for i in range(START_LENGTH):
            rr = (r - dr*i) % ROWS
            cc = (c - dc*i) % COLS
            self.trail.appendleft([rr, cc, self.dir])
        self.head = list(self.trail[-1])

    def to_dict(self):
        return {"id":self.id,"name":self.name,"alive":self.alive,"head":self.head,"trail":list(self.trail),"color":self.color}

class GameServer:
    def __init__(self, host, port):
        self.addr = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.addr)
        self.sock.listen(5)
        self.clients = {}  # conn -> player
        self.players = {}  # player.id -> player
        self.running = True
        self.powerup = self.random_empty_cell()
        self.tick = 0

    def random_empty_cell(self):
        while True:
            r = random.randrange(ROWS)
            c = random.randrange(COLS)
            if not any((p for p in self.players.values() if any(seg[0]==r and seg[1]==c for seg in p.trail))):
                return [r,c]

    def start(self):
        print(f"Server listening on {self.addr}")
        threading.Thread(target=self.accept_loop, daemon=True).start()
        self.game_loop()

    def accept_loop(self):
        while self.running:
            conn, addr = self.sock.accept()
            print("Connection from", addr)
            threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()

    def handle_client(self, conn):
        player = None
        buf = ""
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                buf += data.decode()
                while "\n" in buf:
                    line, buf = buf.split("\n",1)
                    try:
                        msg = json.loads(line)
                    except:
                        continue
                    if msg.get("type") == "join":
                        name = msg.get("name","Player")
                        with lock:
                            player = Player(name)
                            self.clients[conn] = player
                            self.players[player.id] = player
                        # send ack
                        conn.sendall((json.dumps({"type":"join_ack","id":player.id})+"\n").encode())
                    elif msg.get("type") == "input" and player:
                        d = msg.get("dir")
                        if d in DIR_VECTORS and d != OPPOSITE.get(player.dir):
                            # queue next_dir to be applied on next tick
                            with lock:
                                player.next_dir = d
        except Exception as e:
            print("Client handler error:", e)
        finally:
            print("Client disconnected")
            with lock:
                if conn in self.clients:
                    p = self.clients.pop(conn)
                    if p.id in self.players:
                        del self.players[p.id]
            try:
                conn.close()
            except:
                pass

    def broadcast_state(self):
        state = {"type":"state","tick":self.tick,"players":[p.to_dict() for p in self.players.values()],"powerup":self.powerup,"grid_size":[ROWS,COLS]}
        data = (json.dumps(state)+"\n").encode()
        dead_conns = []
        for conn in list(self.clients.keys()):
            try:
                conn.sendall(data)
            except:
                dead_conns.append(conn)
        for c in dead_conns:
            with lock:
                if c in self.clients:
                    p = self.clients.pop(c)
                    if p.id in self.players:
                        del self.players[p.id]
                    try: c.close()
                    except: pass

    def cell_occupied(self, r, c):
        # return (player_id, dir) if occupied by any trail segment
        for p in self.players.values():
            for seg in p.trail:
                if seg[0]==r and seg[1]==c:
                    return (p.id, seg[2])
        return None

    def game_loop(self):
        interval = 1.0 / TICK_RATE
        while self.running:
            start = time.time()
            with lock:
                self.tick += 1
                # advance players
                for p in self.players.values():
                    if not p.alive:
                        continue
                    # apply queued direction
                    p.dir = p.next_dir
                    dr, dc = DIR_VECTORS[p.dir]
                    nr = (p.head[0] + dr) % ROWS
                    nc = (p.head[1] + dc) % COLS
                    occ = self.cell_occupied(nr, nc)
                    if occ:
                        occ_pid, occ_dir = occ
                        # if occupied by another player's trail and perpendicular -> eliminated
                        if occ_pid != p.id and p.dir in PERPENDICULAR.get(occ_dir, set()):
                            p.alive = False
                            continue
                        # if colliding with any trail otherwise, eliminate as well
                        if occ_pid != p.id:
                            p.alive = False
                            continue
                        # if colliding with own trail -> eliminate
                        if occ_pid == p.id:
                            p.alive = False
                            continue
                    # move head
                    p.head = [nr, nc]
                    p.trail.append([nr, nc, p.dir])
                    # keep length: by default length is len(trail) but we want to maintain growth only when powerup collected
                    # We'll store desired length as len(trail) but to keep start length, we trim if longer than current length
                    # For simplicity, we keep trail length equal to current length (we'll track length via deque size)
                    # If powerup collected, we don't pop tail this tick (effectively +1)
                    if [nr,nc] == self.powerup:
                        # extend by 1: do not pop tail this tick
                        self.powerup = self.random_empty_cell()
                    else:
                        # pop tail to maintain length
                        if len(p.trail) > START_LENGTH:
                            p.trail.popleft()
                        else:
                            # keep at least START_LENGTH
                            while len(p.trail) > START_LENGTH:
                                p.trail.popleft()
                # remove dead players' trails (optional: keep trails for others to hit)
                # Here we keep trails so others can collide with them.
            # broadcast
            self.broadcast_state()
            elapsed = time.time() - start
            to_sleep = interval - elapsed
            if to_sleep > 0:
                time.sleep(to_sleep)

if __name__ == "__main__":
    server = GameServer(HOST, PORT)
    try:
        server.start()
    except KeyboardInterrupt:
        print("Shutting down server")
        server.running = False
        server.sock.close()
