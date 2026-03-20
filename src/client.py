# client.py  -- client talk to server
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
    render_game_state,
    show_announcement,
    clear_screen,
    make_layout,
    render_body,
    render_header,
    render_footer,
)
from rich.live import Live

# Cross-platform keypress
WINDOWS = os.name == "nt"
if WINDOWS:
    import msvcrt
else:
    import tty
    import termios
    import select

# -----------------------------
# Cross-platform key reader
# -----------------------------

def read_key():
    """Return 'UP', 'DOWN', 'LEFT', 'RIGHT', 'ENTER', 'D', 'Q', or a digit, or None."""
    if WINDOWS:
        if not msvcrt.kbhit():
            return None
        ch = msvcrt.getwch()

        if ch == "\r":
            return "ENTER"

        if ch.lower() in ["d", "q"]:
            return ch.upper()

        if ch.isdigit():
            return ch

        if ch == "\xe0":  # Windows arrow prefix
            arrow = msvcrt.getwch()
            return {
                "H": "UP",
                "P": "DOWN",
                "K": "LEFT",
                "M": "RIGHT",
            }.get(arrow, None)

        return None

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

        if ch == "\x1b":  # ESC
            seq = sys.stdin.read(2)
            return {
                "[A": "UP",
                "[B": "DOWN",
                "[C": "RIGHT",
                "[D": "LEFT",
            }.get(seq, None)

        return None


g = GState()

# -----------------------------
# Networking helpers
# -----------------------------

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


# -----------------------------
# Message handler
# -----------------------------

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
        show_announcement("YOUR TURN")

    elif t == "Other_Turn":
        g.my_turn = False
        g.cur = msg["player_turn"]

    elif t == "INVALID":
        show_announcement("INVALID MOVE")
        g.my_turn = True

    elif t == "Card_Draw":
        card = msg["card"]
        g.hand.append(card)
        show_announcement(f"DREW {card}")

    elif t == "Update":
        if msg["event"] == "Play":
            show_announcement(f"PLAYER {msg['player']} PLAYED {msg['card']}")
        else:
            show_announcement(f"PLAYER {msg['player']} DREW")

    elif t == "State":
        g.hand = msg["your_hand"]
        g.top = msg["top_card"]
        g.cur = msg["current_turn"]
        g.turn = msg["turn"]

    elif t == "Winner":
        if msg["player"] == g.pid:
            show_announcement("YOU WIN")
        else:
            show_announcement(f"PLAYER {msg['player']} WINS")
        os._exit(0)

    elif t == "DISCONNECT":
        show_announcement("PLAYER DISCONNECTED")
        os._exit(0)

    else:
        print("[client] unknown msg", msg)


# -----------------------------
# Main loop
# -----------------------------

def main():
    socky = connect_to_srv()
    socky.sendall(b"CONNECT\n")

    th = threading.Thread(target=rcv_loop, args=(socky,), daemon=True)
    th.start()

    layout = make_layout()

    if not WINDOWS:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)

    try:
        with Live(layout, screen=True, refresh_per_second=20):
            while True:
                # Update UI panels
                cur_label = "You" if g.my_turn else f"Player {g.cur}"
                layout["header"].update(render_header(g.turn, cur_label))
                layout["body"].update(render_body(g.top))
                layout["footer"].update(render_footer(g.hand, g.selected))

                key = read_key()
                if key is None:
                    time.sleep(0.05)
                    continue

                # Quit
                if key == "Q":
                    show_announcement("QUIT")
                    os._exit(0)

                # Draw
                if key == "D" and g.my_turn:
                    socky.sendall((mk_draw() + "\n").encode())
                    g.my_turn = False
                    continue

                # Move selection
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
                        suit = None
                        # TODO: if card is wild, prompt for suit
                        socky.sendall((mk_play(card, suit) + "\n").encode())
                        g.my_turn = False
                    continue

                # Number keys (quick play)
                if key.isdigit() and g.my_turn:
                    idx = int(key) - 1
                    if 0 <= idx < len(g.hand):
                        card = g.hand[idx]
                        suit = None
                        socky.sendall((mk_play(card, suit) + "\n").encode())
                        g.my_turn = False
                    continue

    finally:
        if not WINDOWS:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


if __name__ == "__main__":
    main()
