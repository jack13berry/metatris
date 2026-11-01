import pygame

import gui, states, events, session

MAX_ID_LENGTH = 24


def handleInput(world, event):
  if event == events.btnStartOn:
    world.sounds['uiaction'].play(0)
    moveForward(world)

  elif event == events.btnEscapeOn:
    world.running = False

  elif event == events.keyPaste:
    if not world.session_started:
      paste(world, read_clipboard())

  elif event == events.keyBack:
    if not world.session_started:
      world.participant_id = world.participant_id[:-1]
      world.intro_message = ""

  elif events.keyTextStart <= event < events.keyTextStart + len(events.textCharacters):
    if not world.session_started and len(world.participant_id) < MAX_ID_LENGTH:
      world.participant_id += events.textCharacters[event - events.keyTextStart]
      world.intro_message = ""


def read_clipboard():
  """The clipboard's text, or "" when it has none or cannot be read."""
  try:
    if not pygame.scrap.get_init():
      pygame.scrap.init()
    for kind in ("text/plain;charset=utf-8", pygame.SCRAP_TEXT):
      data = pygame.scrap.get(kind)
      if data:
        # Windows may return UTF-16; ID characters are ASCII, so dropping zero bytes is safe.
        return data.replace(b"\0", b"").decode("utf-8", "ignore")
  except pygame.error:
    pass
  return ""


def paste(world, text):
  text = text.strip()
  allowed = "".join(char for char in text if char in events.textCharacters)
  room = MAX_ID_LENGTH - len(world.participant_id)
  world.participant_id += allowed[:room]
  if not text:
    world.intro_message = "The clipboard has no text to paste"
  elif allowed != text or len(allowed) > room:
    world.intro_message = "Some pasted characters were left out"
  else:
    world.intro_message = ""


def moveForward(world):
  """PLAY: name the save files after the participant ID, then start or resume the session."""
  if not world.participant_id:
    world.intro_message = "Type the participant ID first"
    return
  if not world.session_started:
    world.start_session_logs(world.participant_id)
  session.begin(world)


def draw( world ):
  r = world.worldsurf_rect
  world.worldsurf.fill( world.bg_color )

  logo_rect = world.logo.get_rect()
  logo_rect.centerx = r.centerx+10
  logo_rect.top = 20
  world.worldsurf.blit( world.logo, logo_rect )

  gclogo_rect = world.gclogo.get_rect()
  gclogo_rect.bottom = r.bottom - 20
  gclogo_rect.centerx = r.centerx
  world.worldsurf.blit( world.gclogo, gclogo_rect )

  gui.simpleText(world, "Participant ID", r.centerx, 345, color=(200, 200, 200))
  shown = world.participant_id
  if not world.session_started and world.moment % 1 < .5:
    shown += "|"  # blinking cursor while the ID can be typed
  gui.textInput(world, shown, r.centerx - 150, 365, 300, 36)

  gui.button(world, "PLAY", r.centerx - 50, 425, 100, 46, focused=True)

  if world.intro_message:
    gui.simpleText(world, world.intro_message, r.centerx, 494, color=(230, 80, 80))
  else:
    prompt = ("Press Enter or START to continue the session" if world.session_started
              else "Type the ID, then press Enter")
    gui.simpleText(world, prompt, r.centerx, 494, color=(200, 200, 200))
