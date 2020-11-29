import pygame

import gui, states, events, configscreen


def handleInput(world, event):
  invalid = False
  if event == events.btnSelectOn or event == events.btnStartOn:
    moveForward(world)

  elif event == events.btnLeftOn or event == events.btnRightOn:
    changeFocusedElm(world)

  elif event == events.btnEscapeOn:
    world.running = False

  else:
    invalid = True

  if event%10 == 1 and not invalid:
    world.sounds['uiaction'].play(0)


def changeFocusedElm(world):
  if world.focused == "intro.play":
    world.focused = "intro.settings"
  else:
    world.focused = "intro.play"


def moveForward(world):
  if world.focused == "intro.play":
    world.state = states.Setup
  else:
    configscreen.enter(world)


def draw( world ):
  r = world.worldsurf_rect
  world.worldsurf.fill( world.bg_color )

  logo_rect = world.logo.get_rect()
  logo_rect.centerx = r.centerx
  logo_rect.top = 50
  world.worldsurf.blit( world.logo, logo_rect )

  gclogo_rect = world.gclogo.get_rect()
  gclogo_rect.bottom = r.bottom - 20
  gclogo_rect.centerx = r.centerx
  world.worldsurf.blit( world.gclogo, gclogo_rect )

  gui.button(world, "SETTINGS", r.centerx-160, r.bottom-210, 160, 51,
    world.focused == "intro.settings"
  )
  gui.button(world, "PLAY", r.centerx+40, r.bottom-210, 120, 51,
    world.focused == "intro.play"
  )

  txty = r.height - gclogo_rect.height - 40
  if world.moment >= world.textBlinkLastTime + 0.7:
    btnName = "START" if pygame.joystick.get_count() > 0 else "Enter"
    actName = " to begin" if world.focused == "intro.play" else " for settings"
    gui.textSurface("Press " + btnName + actName,
      world.scores_font, ( 200, 200, 200 ),
      ( r.centerx, txty ),
      world.worldsurf
    )
    if world.moment >= world.textBlinkLastTime + 2:
      world.textBlinkLastTime = world.moment
