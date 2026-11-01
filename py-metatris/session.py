"""Study sessions: timed stages played in order, each after instruction screens.

A profile lists its stages in `session_stages` and gives each stage
`<stage>_time` (seconds), `<stage>_seeds` and `<stage>_instructions`.
Further screens before a stage go in `<stage>_instructions_2`, `_3`, ...;
the participant pages through them with START. A "|" in the text starts a new paragraph.
The profile's aids (bar, leading outline, prescriptive outline) are shown only
in the stages listed in `aid_stages`.
"""
import re

import pygame

import gui, logger, states, events, paths

AIDS = ("bar", "hint_context", "hint_zoid")
INPUT_DELAY = 2  # seconds before an instruction screen accepts a press
RESTART_DELAY = 2.5  # seconds a game over is shown before the next game starts
LIGHT, DIM, ACCENT = (230, 230, 230), (170, 170, 170), (120, 200, 50)
TEXT_SIZES = (.042, .038, .034, .030, .026)  # fractions of screen height, tried largest first
LINE_SPACING = 1.3
_fonts = {}


def names(text):
  return [name.strip() for name in text.split(",") if name.strip()]


def init(world):
  world.stages = names(world.session_stages)
  world.stage_index = 0
  world.stage_first_game = 0
  world.stage_aids = {aid: getattr(world, aid) for aid in AIDS}
  if world.stages:
    apply(world, world.stages[0])


def apply(world, stage):
  world.game_type = stage
  world.time_limit = float(world.config[stage + "_time"])
  if stage + "_seeds" in world.config:
    world.fixed_seeds = True
    world.random_seeds = [int(seed) for seed in names(world.config[stage + "_seeds"])]
  world.seed_order = range(len(world.random_seeds))
  if world.permute_seeds:
    world.seed_order = world.seed_shuffler.sample(world.seed_order, len(world.seed_order))
  aided = stage in names(world.aid_stages)
  for aid, value in world.stage_aids.items():
    setattr(world, aid, value and aided)
  world.hint_toggle = world.hint_zoid


def begin(world):
  """Start playing from the intro screen."""
  if world.stages:
    show_instructions(world)
  else:
    world.state = states.Setup


def show_instructions(world):
  if not complete(world):
    apply(world, world.stages[world.stage_index])
  world.instruction_page = 0
  world.state = states.Instructions
  world.instructions_shown_at = world.moment


def pages(world, stage):
  """The instruction screens shown before `stage`, in order."""
  keys = [stage + "_instructions"]
  while "%s_instructions_%d" % (stage, len(keys) + 1) in world.config:
    keys.append("%s_instructions_%d" % (stage, len(keys) + 1))
  return [world.config.get(key, "") for key in keys]


def complete(world):
  return world.stage_index >= len(world.stages)


def start_stage(world):
  stage = world.stages[world.stage_index]
  world.blockStartTime = None
  world.time_limit_reached = False
  world.stage_first_game = world.game_number
  logger.game_event(world, "STAGE", "BEGIN", stage)
  world.state = states.Setup


def end_stage(world):
  logger.game_event(world, "STAGE", "END", world.stages[world.stage_index])
  world.stage_index += 1
  show_instructions(world)


def handleInput(world, event):
  if event == events.btnEscapeOn:
    if complete(world):
      world.running = False
    else:
      world.state = states.Intro
    return
  if event != events.btnStartOn or world.moment < world.instructions_shown_at + INPUT_DELAY:
    return
  if complete(world):
    # The researcher sets up the next participant; main.py reopens the config picker.
    world.restart = True
    world.running = False
  elif world.instruction_page + 1 < len(pages(world, world.stages[world.stage_index])):
    world.instruction_page += 1
    world.instructions_shown_at = world.moment
  else:
    start_stage(world)


def wrap(text, font, width):
  lines, line = [], ""
  for word in text.split():
    candidate = (line + " " + word).strip()
    if line and font.size(candidate)[0] > width:
      lines.append(line)
      line = word
    else:
      line = candidate
  return lines + [line] if line else lines


def font(size):
  if size not in _fonts:
    _fonts[size] = pygame.font.Font(
      paths.resource("media", "fonts", "Montserrat", "Montserrat-Medium.ttf"), size)
  return _fonts[size]


def sentences(paragraph):
  return re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", paragraph.strip())


def layout(text, r):
  """Wrap `text` with each sentence on a new line, in the largest size that fits.

  Returns the font, line height and a list of (line, color, y offset) rows.
  """
  for fraction in TEXT_SIZES:
    face = font(max(12, int(r.height * fraction)))
    line_height = int(face.get_linesize() * LINE_SPACING)
    width = min(r.width * .75, face.size("x")[0] * 50)
    rows, y = [], 0
    for paragraph in text.split("|"):
      for sentence in sentences(paragraph):
        color = ACCENT if sentence.startswith("Press Start") else LIGHT
        for line in wrap(sentence, face, width):
          rows.append((line, color, y))
          y += line_height
        y += line_height * .6
      y += line_height * .6
    height = y - line_height * 1.2
    if height <= r.height * .7:
      break
  return face, line_height, rows, height


def draw_text(world, text, center_y, centered=False):
  """Draw `text` as a left-aligned block centered on the screen, or with each line centered."""
  r = world.worldsurf_rect
  face, line_height, rows, height = layout(text, r)
  left = r.centerx - max(face.size(line)[0] for line, _, _ in rows) // 2
  top = center_y - height // 2
  for line, color, y in rows:
    if centered:
      gui.textSurface(line, face, color, (r.centerx, int(top + y)), world.worldsurf, "midtop")
    else:
      gui.textSurface(line, face, color, (left, int(top + y)), world.worldsurf, "topleft")
  return face


def draw(world):
  r = world.worldsurf_rect
  world.worldsurf.fill(world.bg_color)
  ready = world.moment >= world.instructions_shown_at + INPUT_DELAY

  if complete(world):
    gui.textSurface("Session complete", font(int(r.height * .07)), LIGHT,
                    (r.centerx, int(r.height * .3)), world.worldsurf)
    draw_text(world, "Thank you! Please let the researcher know you have finished.",
              int(r.height * .5), centered=True)
    if ready:
      gui.textSurface("Researcher: START (Enter) for the next participant, Esc to close",
                      world.scores_font, DIM, (r.centerx, int(r.height * .88)), world.worldsurf)
    return

  screens = pages(world, world.stages[world.stage_index])
  face = draw_text(world, screens[world.instruction_page], int(r.height * .44))

  # The last screen's own text says to press START.
  if ready and world.instruction_page + 1 < len(screens):
    gui.textSurface("Press Start to continue", face, DIM,
                    (r.centerx, int(r.height * .9)), world.worldsurf)
