#!/usr/bin/env python3
"""Records asciiverse/evilhack.cast, EvilHack's catalog preview, at 100x30
(hub/RECORDING.md): a new Valkyrie, then about PLAY_SECONDS (default 30)
of play by a simple adventurer, then the game is saved.

The adventurer reads the map with its colours (tmux capture -e: doors are
brown) and walks, by the shortest known way, to the stairs down if it can
see them, else to the nearest door or corridor it hasn't stood on. It
attacks any monster next to it except its pet (the monster beside it at
the start, by letter and colour) and descends when on the stairs (it
remembers where they were, since the hero hides them). --More-- gets
Enter, any other question Esc. The hero is found by the terminal cursor, which NetHack keeps
on the hero. A fresh HOME keeps your own playground out. Games are random:
run it a few times and keep a take with fights or stairs, under 60 s.
Usage, from the repo root after asciiverse/build.sh and stage.sh:
    python3 asciiverse/record-preview.py
DEBUG=<file> logs every step and writes the last screen to <file>."""
import os, random, subprocess, tempfile, time

s = "evilhack-preview"
secs = float(os.environ.get("PLAY_SECONDS", 30))
home = tempfile.mkdtemp()

def screen():
    return subprocess.run(["tmux", "capture-pane", "-p", "-t", s],
                          capture_output=True, text=True).stdout.split("\n")
def cursor():
    out = subprocess.run(["tmux", "display", "-p", "-t", s,
                          "#{cursor_x} #{cursor_y}"],
                         capture_output=True, text=True).stdout.split()
    return int(out[0]), int(out[1])
def key(k, wait):
    subprocess.run(["tmux", "send-keys", "-t", s, k]); time.sleep(wait)

subprocess.run(["tmux", "kill-session", "-t", s], stderr=subprocess.DEVNULL)
subprocess.run(["tmux", "new-session", "-d", "-s", s, "-x", "100", "-y", "30",
    f"HOME={home} USER=Freya TERM=xterm-256color COLORTERM=truecolor "
    "LANG=C.UTF-8 asciinema rec --overwrite -q -i 2 --window-size 100x30 "
    "--capture-env TERM,COLORTERM,LANG -c './stage/evilhack -p Valkyrie' "
    "asciiverse/evilhack.cast"])
time.sleep(2.5)
key("y", 1.2)                     # pick the rest for me
key("y", 2.5)                     # is this ok? yes: the intro
key("Enter", 1.5)

DIRS = {(-1,0):"h", (1,0):"l", (0,-1):"k", (0,1):"j",
        (-1,-1):"y", (1,-1):"u", (-1,1):"b", (1,1):"n"}
DOOR = "94"                       # doors are drawn brown (38;5;94)
WALK = set(".#<>{_%$)[!?/=\"*(`^")

def grid():
    """the map rows as [(char, fg colour)], from tmux's coloured capture"""
    raw = subprocess.run(["tmux", "capture-pane", "-p", "-e", "-t", s],
                         capture_output=True, text=True).stdout.split("\n")
    g = []
    for line in raw[:22]:
        row, fg, i = [], "", 0
        while i < len(line):
            if line[i] == "\x1b":
                j = line.index("m", i)
                codes = line[i+2:j].split(";")
                while codes:
                    c = codes.pop(0)
                    if c in ("", "0", "39"): fg = ""
                    elif c == "38" and len(codes) >= 2: fg = codes[1]; codes = codes[2:]
                    elif c.isdigit() and (30 <= int(c) <= 37 or 90 <= int(c) <= 97): fg = c
                i = j + 1; continue
            row.append((line[i], fg)); i += 1
        g.append(row)
    return g

def cell(g, x, y):
    return g[y][x] if 0 <= y < len(g) and 0 <= x < len(g[y]) else (" ", "")
def is_door(c): return c[1] == DOOR and c[0] in "|-+."
def is_mon(c): return c[0].isalpha() or c[0] in "@&;:'"
def is_doorway(g, x, y):
    """a door, or a '.' set in a wall (a doorless or broken doorway)"""
    if is_door(cell(g, x, y)): return True
    if cell(g, x, y)[0] != ".": return False
    wall = lambda c: c[0] in "|-" and c[1] != DOOR
    return (wall(cell(g, x-1, y)) and wall(cell(g, x+1, y))) or \
           (wall(cell(g, x, y-1)) and wall(cell(g, x, y+1)))
def passable(c): return c[0] in WALK or is_door(c) or is_mon(c)

def step_towards(g, x, y, goal_fn):
    """first step of a shortest walk to the nearest cell goal_fn accepts"""
    from collections import deque
    seen = {(x, y): None}; q = deque([(x, y)])
    while q:
        cx, cy = q.popleft()
        if (cx, cy) != (x, y) and goal_fn(cx, cy):
            while seen[(cx, cy)] != (x, y): cx, cy = seen[(cx, cy)]
            return (cx - x, cy - y)
        for (dx, dy) in DIRS:
            nx, ny = cx + dx, cy + dy
            if (nx, ny) in seen or not passable(cell(g, nx, ny)): continue
            if dx and dy and (is_door(cell(g, cx, cy)) or is_door(cell(g, nx, ny))):
                continue                  # no diagonal moves through doors
            if ((cx, cy), (nx, ny)) in blocked: continue
            if is_mon(cell(g, nx, ny)) and (nx, ny) != (x+dx, y+dy): continue
            seen[(nx, ny)] = (cx, cy); q.append((nx, ny))
    return None

blocked = set()                   # steps that didn't move us (doorways)
tried = None
pet = None; stairs = None; visited = set(); end = time.time() + secs; log = []
while time.time() < end:
    rows = screen()
    top = rows[0]
    if "--More--" in "".join(rows):
        key("Enter", 0.4); continue
    if "?" in top and ("[" in top or "(yes)" in top):
        key("Escape", 0.4); continue          # any question: no
    x, y = cursor()
    if not (1 <= y <= 21):
        key("Escape", 0.4); continue          # a menu or text window
    g = grid()
    if tried and tried[0] == (x, y):  # the last step went nowhere
        blocked.add(tried)
    tried = None
    if pet is None:                           # the pet starts next to us
        pet = next((cell(g, x+dx, y+dy) for (dx, dy) in DIRS
                    if is_mon(cell(g, x+dx, y+dy))), ("?", "?"))
    visited.add((x, y))
    seen_stairs = [(cx, cy) for cy, r in enumerate(g) for cx, c in enumerate(r) if c[0] == ">"]
    if seen_stairs: stairs = seen_stairs[0]
    if (x, y) == stairs or "staircase down here" in top:
        key(">", 1.5); log.append("down")
        visited.clear(); blocked.clear(); stairs = None; pet = ("?", "?")
        continue
    foes = [(dx, dy) for (dx, dy) in DIRS
            if is_mon(cell(g, x+dx, y+dy)) and cell(g, x+dx, y+dy) != pet]
    if foes:
        dx, dy = foes[0]
        key(DIRS[(dx, dy)], 0.3); log.append("fight " + cell(g, x+dx, y+dy)[0]); continue
    d = step_towards(g, x, y, lambda cx, cy: cell(g, cx, cy)[0] == ">")
    if d is None:                             # explore: doors and corridors
        d = step_towards(g, x, y, lambda cx, cy: (cx, cy) not in visited and
                         (cell(g, cx, cy)[0] == "#" or is_doorway(g, cx, cy)))
    if d is None:
        d = random.choice(list(DIRS)); visited.clear()
    key(DIRS[d], 0.06)
    tried = ((x, y), (x + d[0], y + d[1]))
    if os.environ.get("DEBUG"): log.append(f"{x},{y}>{DIRS[d]}")

time.sleep(1.0)
if os.environ.get("DEBUG"):
    open(os.environ["DEBUG"], "w").write("\n".join(screen()))
key("Escape", 0.3)
key("S", 0.8); key("y", 3.0)      # save and quit
subprocess.run(["tmux", "kill-session", "-t", s], stderr=subprocess.DEVNULL)
print(" ".join(log))
