#Acknowledgement: 
# Portions of this UI code were developed with assistance from ChatGPT

#  ui_helpers.py  -- minimal Rich-based UI helpers

import os
import sys
import time
import random
import subprocess
from typing import Optional, List

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

console = Console()

def clear_screen() -> None:
    if os.name == "nt":
        subprocess.run("cls", shell=True)
    else:
        subprocess.run("clear", shell=True)

def move_cursor_home() -> None:
    sys.stdout.write("\033[H")
    sys.stdout.flush()

def hide_cursor() -> None:
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def show_cursor() -> None:
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

def make_layout() -> Layout:
    layout = Layout()
    layout.split(
        Layout(name="header", size=3),
        Layout(name="body", size=3),
        Layout(name="footer", ratio=1),
    )
    return layout


def render_header(round_number: int, current_player: str, next_player: Optional[str] = None) -> Panel:
    text = Text()
    text.append(f" ROUND {round_number} ", style="bold yellow")
    text.append(" | ")
    text.append(f"Current: {current_player} ", style="bold green")
    if next_player is not None:
        text.append(" | ")
        text.append(f"Next: {next_player}", style="bold cyan")
    return Panel(text, title="EINS", border_style="magenta")


def render_body(top_card: Optional[str]) -> Panel:
    text = Text(f"Top Card: {top_card}", style="bold yellow")
    return Panel(text, title="Game State", border_style="cyan")


def render_footer(hand: List[str], selected_index: int, cols: int = 2) -> Panel:
    t = Text("Your Hand:\n", style="bold white")

    if not hand:
        t.append("(no cards)\n", style="dim")
    else:
        rows = []
        for i in range(0, len(hand), cols):
            rows.append(hand[i:i + cols])

        for r, row in enumerate(rows):
            for c, card in enumerate(row):
                idx = r * cols + c
                if idx == selected_index:
                    t.append(f"> {card:<15}", style="bold underline green")
                else:
                    t.append(f"  {card:<15}", style="white")
            t.append("\n")

    t.append("\n↑/↓ to move, ENTER to play, D to draw, Q to quit", style="cyan")
    return Panel(t, border_style="white")

def shred_ui(duration: float = 1.0, steps: int = 10) -> None:
    hide_cursor()
    try:
        height = console.size.height
        width = console.size.width
        for _ in range(steps):
            move_cursor_home()
            for _ in range(height):
                line = "".join(random.choice("0123456789ABCDEF ") for _ in range(width))
                sys.stdout.write(line + "\n")
            sys.stdout.flush()
            time.sleep(duration / steps)
        clear_screen()
    finally:
        show_cursor()


def render_announcement_panel(message: str) -> Panel:
    return Panel(
        Text(message, justify="center", style="bold magenta"),
        title="SERVER ANNOUNCEMENT",
        border_style="yellow",
        padding=(1, 2),
    )

def render_game_state(round_number: int,
                      current_player: str,
                      next_player: Optional[str],
                      hand: List[str],
                      discard_top: Optional[str]) -> None:
    """
    One-shot render of the game state (not used in main loop, but available).
    """
    layout = make_layout()
    layout["header"].update(render_header(round_number, current_player, next_player))
    layout["body"].update(render_body(discard_top))
    layout["footer"].update(render_footer(hand, selected_index=0))
    console.print(layout)

def render_suit_selector(selected_index: int = 0) -> Panel:
    suits = ["STEEL", "NICKLE", "IRON", "EUROPIUM"]
    t = Text("Choose a Suit:\n\n", style="bold white")

    for i, suit in enumerate(suits):
        if i == selected_index:
            t.append(f"> {suit}\n", style="bold underline green")
        else:
            t.append(f"  {suit}\n", style="white")

    t.append("\n↑/↓ to move, ENTER to select", style="cyan")
    return Panel(t, border_style="magenta", title="WILD CARD")