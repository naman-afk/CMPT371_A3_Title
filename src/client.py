# client.py  -- client talk to server, handle input and updates UI
# connect to server & receive thread
# handle user input
# call UI function
# send JSON msg back

import socket
import threading
import time
import sys
import os

from state import GState
from protocol import parse_msg, mk_draw, mk_play
from ui_helpers import (
    make_layout,
    render_body,
    render_header,
    render_footer,
    render_suit_selector
)
from rich.live import Live
from rich.text import Text


#cross-platform key
WINDOWS = os.name == "nt"
if WINDOWS:
    import msvcrt
else:
    import tty
    import termios
    import select

# grap one key w/out blocking

def read_key():
    if WINDOWS:
        if not msvcrt.kbhit():
            return None
        ch=msvcrt.getwch()

        if ch=="\r":
            return "ENTER"

        if ch.lower() in ["d", "q"]:
            return ch.upper()

        if ch.isdigit():
            return ch

        if ch=="\xe0":
            arrow = msvcrt.getwch()
            return {
                "H": "UP",
                "P": "DOWN",
                "K": "LEFT",
                "M": "RIGHT",
            }.get(arrow, None)

        return None

    # linux / mac users
    else:
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if not dr:
            return None

        ch = sys.stdin.read(1)

        if ch == "\n":
            return "ENTER"

        if ch.lower() in ["d", "q"]:
            return ch.upper()

        if ch.isdigit():
            return ch

        if ch == "\x1b":
            seq = sys.stdin.read(2)
            return {
                "[A": "UP",
                "[B": "DOWN",
                "[C": "RIGHT",
                "[D": "LEFT",
            }.get(seq, None)

        return None

#gloabal game state
g = GState()

#connect + recv trhead

def connect_to_srv(host="127.0.0.1", port=12345):
    socky = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socky.connect((host, port))
    print("[client] connected to EINS")
    return socky


def rcv_loop(socky):
    # wait till server sends something
    buf = ""
    while True:
        try:
            chunk = socky.recv(1024).decode()
            if not chunk:
                print("Server closed connection")
                break

            buf += chunk

            # server sends one JSON per line
            while "\n" in buf:
                raw, buf = buf.split("\n", 1)
                raw = raw.strip()
                if not raw:
                    continue

                msg = parse_msg(raw)
                if not msg:
                    print("Invalid message from server:", raw)
                    continue

                handle_msg(msg)

        except Exception as e:
            print("Error rcv from server:", e)
            break

# handle incoming msgs -> update GState
def handle_msg(msg):
    t = msg.get("type")

    if t == "Start":
        g.pid = msg["player_id"]
        g.hand = msg["cards"]
        g.top = msg["top_card"]
        g.cur = msg["current_turn"]
        g.turn = 0
        g.my_turn = (g.cur == g.pid)

    elif t == "Your_Turn":
        g.my_turn = True
        g.turn = msg["turn"]
        g.cur = g.pid

    elif t == "Other_Turn":
        g.my_turn = False
        g.cur = msg["player_turn"]

    elif t == "INVALID":
        g.my_turn = True

    elif t == "Card_Draw":
        g.hand.append(msg["card"])

    elif t == "Update":
        pass

    elif t == "State":
        g.hand = msg["your_hand"]
        g.top = msg["top_card"]
        g.cur = msg["current_turn"]
        g.turn = msg["turn"]

    elif t == "Winner":
        if msg["player"] == g.pid:
            g.pending_announcement= "🔥 YOU WIN! Certified EINS Menace."
        else:
            g.pending_announcement=f"DEFEAT 💀"

    elif t == "DISCONNECT":
        g.pending_announcement="PLAYER DISCONNECTED"

    else:
        print("[client] unknown msg", msg)

# find wild card (-1 or -2)
def is_wild(card: str) -> bool:
    parts = card.split()

    #when: "IRON -1" or "EUROPIUM -2"
    if parts[-1] in ["-1", "-2"]:
        return True

    #when: "IRON CARD" or "EUROPIUM DRAW4"
    if parts[-1] in ["CARD", "DRAW4"]:
        return True

    return False

# for wildcard pick suite UI
def choose_suit_in_layout(live, layout):
    suits = ["STEEL", "NICKLE", "IRON", "EUROPIUM"]
    selected = 0

    while True:
        layout["footer"].update(render_suit_selector(selected))
        time.sleep(0.05)

        key = read_key()
        if key is None:
            continue

        if key == "UP":
            selected = (selected - 1) % 4
        elif key == "DOWN":
            selected = (selected + 1) % 4
        elif key == "ENTER":
            return suits[selected]


def main():
    socky = connect_to_srv()
    socky.sendall(b"CONNECT\n")

    #recv thread
    th = threading.Thread(target=rcv_loop, args=(socky,), daemon=True)
    th.start()

    layout = make_layout()
    #raw mode for linux/mac
    if not WINDOWS:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)

    try:
        with Live(layout, screen=True, refresh_per_second=1) as live:
            while True:
                #update UI
                cur_label = "You" if g.my_turn else f"Player {g.cur}"
                layout["header"].update(render_header(g.turn, cur_label))
                layout["body"].update(render_body(g.top))
                layout["footer"].update(render_footer(g.hand, g.selected))

                live.update(layout)
                
                #only announcement for WIN/DISCONNECT
                if getattr(g, "pending_announcement", None):
                    if g.pending_announcement.strip():

                        msg = g.pending_announcement

                        # create a simple centered text message
                        t = Text(f"\n{msg}\n", style="bold magenta", justify="center")

                        # reuse wildcard-style footer container
                        footer_panel = render_suit_selector(0)
                        footer_panel.renderable = t  # replace its content

                        layout["footer"].update(footer_panel)
                        live.update(layout)

                        time.sleep(1.5)
                        os._exit(0)

                    g.pending_announcement = None
                    continue

                #read key
                key = read_key()
                if key is None:
                    time.sleep(0.05)
                    continue

                #quit
                if key == "Q":
                    show_announcement("QUIT", live, layout)
                    os._exit(0)

                #draw
                if key == "D" and g.my_turn:
                    socky.sendall((mk_draw() + "\n").encode())
                    g.my_turn = False
                    continue

                #move 
                if key == "UP":
                    g.selected = max(0, g.selected - 1)
                    continue

                if key == "DOWN":
                    if g.hand:
                        g.selected = min(len(g.hand) - 1, g.selected + 1)
                    continue

                # ENTER to play selected card
                if key == "ENTER" and g.my_turn:
                    if 0 <= g.selected < len(g.hand):
                        card = g.hand[g.selected]
                        
                        if is_wild(card):
                            suit = choose_suit_in_layout(live, layout)
                        else:
                            suit=None
                        
                        socky.sendall((mk_play(card, suit) + "\n").encode())
                        g.my_turn = False
                    continue

                # no. key
                if key.isdigit() and g.my_turn:
                    idx = int(key) - 1
                    if 0 <= idx < len(g.hand):
                        card = g.hand[idx]
                    
                        if is_wild(card):
                            suit = choose_suit_in_layout(live, layout)
                        else:
                            suit=None

                        socky.sendall((mk_play(card, suit) + "\n").encode())
                        g.my_turn = False
                    continue

    finally:
        if not WINDOWS:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


if __name__ == "__main__":
    main()
