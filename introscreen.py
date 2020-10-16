import pygame

import gui

#draw the introduction screen
def draw( world ):
  r = world.worldsurf_rect
  world.worldsurf.fill( ( 39, 39, 39 ) )

  logo_rect = world.logo.get_rect()
  logo_rect.centerx = r.centerx
  logo_rect.top = 50
  world.worldsurf.blit( world.logo, logo_rect )

  gclogo_rect = world.gclogo.get_rect()
  gclogo_rect.bottom = r.bottom - 20
  gclogo_rect.centerx = r.centerx
  world.worldsurf.blit( world.gclogo, gclogo_rect )

  gui.button(world, "SETTINGS", r.centerx-160, r.bottom-210, 160, 44)
  gui.button(world, "PLAY", r.centerx+40, r.bottom-210, 120, 44)

  world.title_blink_timer += 1
  if world.title_blink_timer <= world.fps:
    btnName = "START" if pygame.joystick.get_count() > 0 else "SPACE BAR"
    gui.textSurface("Press " + btnName +" to begin",
      world.scores_font, ( 200, 200, 200 ),
      ( r.centerx, r.height - r.height / 5 ),
      world.worldsurf
    )

  if world.title_blink_timer > world.fps * 2:
    world.title_blink_timer = 0
