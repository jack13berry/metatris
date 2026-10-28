"""Study sessions: timed stages played in order, each after an instruction screen.

A profile lists its stages in `session_stages` and gives each stage
`<stage>_time` (seconds), `<stage>_seeds` and `<stage>_instructions`.
The profile's aids (bar, leading outline, prescriptive outline) are shown only
in the stages listed in `aid_stages`.
"""
import gui, logger, states, events

AIDS = ("bar", "hint_context", "hint_zoid")
INPUT_DELAY = 2  # seconds before an instruction screen accepts a press
RESTART_DELAY = 2.5  # seconds a game over is shown before the next game starts
CONTROLS = ("Left / Right: move", "Down: drop faster", "A / B or J / K: rotate")


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
  world.state = states.Instructions
  world.instructions_shown_at = world.moment


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
  if complete(world) or world.moment < world.instructions_shown_at + INPUT_DELAY:
    return
  if event == events.anyPress or event in (events.btnUpOn, events.btnDownOn,
                                           events.btnLeftOn, events.btnRightOn):
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


def draw(world):
  r = world.worldsurf_rect
  world.worldsurf.fill(world.bg_color)
  font = world.scores_font
  light, dim = (230, 230, 230), (170, 170, 170)
  y = int(r.height * .15)

  if 0 < world.stage_index < len(world.stages):
    finished = world.stages[world.stage_index - 1].capitalize()
    gui.textSurface(finished + " complete", font, dim, (r.centerx, y), world.worldsurf)
  y += int(r.height * .1)

  if complete(world):
    gui.textSurface("Session complete", world.end_font, light, (r.centerx, y), world.worldsurf)
    y += int(r.height * .1)
    for line in wrap("Thank you! Please let the researcher know you have finished.",
                     font, r.width * .7):
      gui.textSurface(line, font, light, (r.centerx, y), world.worldsurf)
      y += font.get_linesize()
    return

  stage = world.stages[world.stage_index]
  minutes = world.time_limit / 60
  duration = ("%g minute" % minutes) + ("" if minutes == 1 else "s")
  gui.textSurface(stage.capitalize(), world.end_font, light, (r.centerx, y), world.worldsurf)
  y += int(r.height * .07)
  gui.textSurface("Stage %d of %d  -  %s" % (world.stage_index + 1, len(world.stages), duration),
                  font, dim, (r.centerx, y), world.worldsurf)
  y += int(r.height * .1)

  for line in wrap(world.config.get(stage + "_instructions", ""), font, r.width * .7):
    gui.textSurface(line, font, light, (r.centerx, y), world.worldsurf)
    y += font.get_linesize()
  y += font.get_linesize()
  for line in CONTROLS:
    gui.textSurface(line, font, dim, (r.centerx, y), world.worldsurf)
    y += font.get_linesize()

  if world.moment >= world.instructions_shown_at + INPUT_DELAY:
    gui.textSurface("Press any button to start", font, (120, 200, 50),
                    (r.centerx, int(r.height * .85)), world.worldsurf)
