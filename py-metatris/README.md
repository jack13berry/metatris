# Metatris Frontend

This repository contains the game source and builds single-file executables
with Python, dependencies, graphics, sounds, boards, controllers, and study
profiles included.

## Portable executables

Copy the executable for your OS to a writable folder and run it. Python and an
installer are not needed on the destination device:

- Windows x64: `dist/windows-x86_64/metatris.exe`
- Linux x64: `dist/linux-x86_64/metatris`

On first launch, the executable creates `configs/` beside itself with the bundled
profiles. Add or edit config files there; later launches preserve your changes.
Saved games go in `data/` beside the executable, regardless of the working folder
used to launch it. If the executable's folder is read-only, configs and data use
the user's application-data directory instead. `METATRIS_HOME` can explicitly
choose a writable location for both.
If sound cannot initialize, the game runs silently. On Linux, a downloaded file
may need `chmod +x metatris` before its first launch.

Run `metatris.exe --self-test` on Windows or `./metatris --self-test` on Linux to
verify the bundled profiles, controls, aids, timers, assets, and saved-data
formats. The checks use temporary logs and disable network uploads.

Each OS and CPU architecture needs its own executable. The supplied Linux build
uses an Ubuntu 20.04 environment for compatibility with glibc 2.31 and newer
desktop distributions. The Windows build targets Windows 10/11 x64. GUI/audio
drivers and a physical controller still depend on the destination device.

## Selecting configurations

Run `python main.py` from this directory. The startup picker lists the profiles
in `configs/` by name: `normal`, `lagging`, `leading` and `prescriptive` first,
then any others. `default` is not listed, and `normal` is selected initially. Use Up/Down and
Enter, or the controller D-pad and A/Start. B/Esc exits the picker.

The picker and the game open fullscreen (`fullscreen = True` in `default.config`).
Run with `-F false` for a window, for example `python main.py -F false`.
A `configs/default.config` created by an earlier version keeps its old
`fullscreen = False`; delete it so the new default is copied on the next launch.

Every selection starts with `configs/default.config` and applies the selected
file on top. A new profile needs only the settings it changes:

```ini
starting_level = 2
game_type = higher_speed
```

Save it as `configs/higher_speed.config`; it appears on the next launch.
Comments beginning with `#`, quoted strings, and inline comments are supported.
Running `python main.py -c default` uses the default file without other overrides.

To select a profile directly and skip the picker, run `python main.py -c normal`.
Each launch uses one profile.

## Home screen and save files

After a profile is chosen, the home screen shows a participant ID field and a
PLAY button. Type the ID on the keyboard (letters, digits, `-`, `_`, `.`, `@`;
Backspace deletes), or paste it with Ctrl+V (Cmd+V on macOS, or Shift+Insert);
surrounding spaces are removed and characters not allowed in an ID are left out.
Then press Enter or the controller's START. PLAY does
nothing until an ID is typed. Starting the session saves its files in
`data/<ID>_<YYYY-MM-DD>_<HH-MM-SS>/`, timestamped when PLAY is pressed, and the
ID is recorded as `SID` in every log. The ID cannot be changed once the session
has started. `-id` on the command line fills in the ID in advance.

## Single-session study profiles

Each profile is one participant's whole session for one condition (45 minutes
of play). It runs four timed stages in order, and each stage begins with its
instruction screens: four before practice (the game, scoring, controls, and the
session), one before each later stage. The participant moves on with START (or
Enter); other buttons do nothing. Presses are ignored for the first 2 seconds of
each screen, so a button still held from the previous stage does not skip the
instructions. Esc on an instruction screen returns to the home screen.

| Stage | Duration | Seeds | Display |
| --- | --- | --- | --- |
| Practice | 1 minute | 1101–1120 | Normal |
| Baseline | 6 minutes | 2101–2120 | Normal |
| Playing | 28 minutes | 3101–3200 | The profile's aid |
| Test | 10 minutes | 4101–4140 | Normal |

| Config | Aid during the playing stage |
| --- | --- |
| `normal` | None; board frame stays a fixed color |
| `lagging` | Performance bar on the right; board frame changes color with the bar |
| `leading` | Piece outline appears only over the recommended column and rotation |
| `prescriptive` | Piece outline at the recommended spot from the start of each descent |

After the last stage, a "Session complete" screen asks the participant to tell
the researcher. The researcher then presses START (or Enter) to open the config
picker for the next participant, with the last profile selected (or, when `-c`
named a profile, the home screen of that profile), or Esc to close the game.
Pressing Esc during play returns to the home screen (Space and the
controller's Select button do nothing during a game); pressing PLAY again
restarts the current stage with a fresh clock.

All study profiles start at level 0, show the classic score/lines/level and next
piece, and allow unlimited games within a stage. Optional aids are off, except
the profile's aid during the playing stage. Both hint profiles use
`score_506_dellacherie` with overhang recommendations disabled.

The stage settings live in each profile: `session_stages` lists the stages in
order and `aid_stages` names the stages that show the aid. Each stage has
`<stage>_time` in seconds, `<stage>_seeds`, and `<stage>_instructions`, which is
the text on its instruction screen and can be edited without rebuilding. Further
screens before the same stage go in `<stage>_instructions_2`, `_3`, and so on.
A `|` in the text starts a new paragraph. Instruction text cannot contain `#`. The seed lists are the same for every
profile and every participant. Games cycle through a stage's list from its
start. A profile without `session_stages`, such as `default`, starts play
directly and uses `time_limit`.

A stage's clock begins when its first game starts and includes time between
games. The time left in the stage is shown in the bottom right corner during
play. START on the controller (or Enter or P) pauses and resumes a game; the
board is hidden and the stage clock stops while paused. If the pieces reach the top, "GAME OVER" shows for 2.5 seconds
and a new game starts by itself with the stage's next seed, until time runs out.
When time runs out, the current game ends and the next instruction screen
appears.

Saved config snapshots, history, event/state logs, episode/game summaries,
piece score logs, and performance data include `config_name` (the profile).
`game_type` is the stage name, and `STAGE` `BEGIN`/`END` events mark stage
edges. The TSV log version is 3.3; piece score TSVs now have a header and
config/game/episode identifiers alongside the score.

Version 3.3 corrects hole counts, pit depths, column transitions, and column
diversity used by the placement controller and Meta feedback. Earlier saved
sessions retain their original metrics; raw board snapshots can be analyzed
independently. Column diversity counts distinct cell-difference patterns between
adjacent columns.

The default controller mapping is A = clockwise, B = counterclockwise.

To run the configuration and game integration checks with Python 3.11 or later,
use `python -m unittest discover -s tests -v`. Tests use SDL's headless drivers
and temporary logs, with network uploads disabled.

## Building executables

Use Python 3.11 x64 on the OS you want to target. From this directory:

```sh
python -m pip install -r requirements-build.txt
python build.py
```

The executable is written to `dist/<os>-<architecture>/`; `--output-dir` can set
a different destination. On Windows, `install.bat` and `build.bat` run the same
commands. For broad Linux compatibility, build inside the oldest distribution
you intend to support. Build-time packages are pinned in the requirements files.
User settings, saved game data, and upload credentials are excluded from bundles.

The home screen no longer offers sign-in, registration, settings or performance
screens, so saved data is not uploaded. Gameplay requires no network account.
