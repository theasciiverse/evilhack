# EvilHack (Asciiverse packaging)

EvilHack by k21971 (Keith Simpson), a hard NetHack 3.6 variant, packaged
for the Asciiverse catalog. The game's source is unchanged: everything
is build configuration under `asciiverse/`, listed in PATCHES.md. Keep it
that way; anything that must change in the source should be small and
offered upstream.

- Branch `asciiverse` on upstream's release tag (now `v0.9.3`);
  `upstream` is github.com/k21971/EvilHack, which is active: rebase onto
  new release tags.
- Build: `sh asciiverse/build.sh` (needs bison, flex, ncursesw; the
  parser sources in sys/share are stale), then `sh asciiverse/stage.sh`;
  run `stage/evilhack`. Our hints file goes through upstream's setup.sh.
- Playground per player: the start script makes
  `${XDG_DATA_HOME:-~/.local/share}/evilhack`, links nhdat, symbols,
  license, sysconf and serverseed into it and sets NETHACKDIR. No
  VAR_PLAYGROUND, no setgid. The system packages use the same script.
- `asciiverse/sysconf` follows upstream's `sys/unix/sysconf`; when
  upstream changes theirs, carry the game settings over.
- Quitting needs the whole word "yes". No dumplog for games under 100
  turns (upstream: "scummed games").
- Preview: `python3 asciiverse/record-preview.py` (tmux, asciinema 3);
  run it a few times and keep a take with kills and stairs, under 60 s.
  `DEBUG=<file>` logs steps and the last screen.
