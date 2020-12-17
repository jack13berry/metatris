import pygame

import states, gui, mond


def handleInput(world, event):
  world.sounds['uiaction'].play(0)


authCode = ""
clrTxt = ( 255, 224, 63 )
clrBad = ( 255, 63, 63 )
prevMondState = ""

def draw( world ):
  world.state = states.Intro
  world.shouldRedraw = True
  return

  global authCode, skipx, prevMondState

  mondstate = mond.status()

  if authCode == "":
    authCode = " ".join( list(mond.authDigits()) )

  r = world.worldsurf_rect
  world.worldsurf.fill( world.bg_color )

  logo_rect = world.minilogo.get_rect()
  logo_rect.right = r.right - 20
  logo_rect.bottom = r.bottom - 15
  world.worldsurf.blit( world.minilogo, logo_rect )

  gclogo_rect = world.gclogo.get_rect()
  gclogo_rect.bottom = r.bottom - 20
  gclogo_rect.left = 20
  world.worldsurf.blit( world.gclogo, gclogo_rect )


  if mondstate == "authorized":
    world.state = states.Intro
    world.shouldRedraw = True

  elif mondstate == "rejected":
    gui.textSurface("REJECTED", world.authDigitFont, clrBad,
      ( r.centerx, r.centery ), world.worldsurf
    )

    gui.textSurface("Login not approved. :(",
      world.authInfoFont, clrTxt, ( r.centerx, r.centery + 90 ),
      world.worldsurf
    )

  else:
    gui.textSurface("Please confirm the connection from the",
      world.authInfoFont, clrTxt, ( r.centerx, 130 ), world.worldsurf )

    gui.textSurface("browser tab that opened.",
      world.authInfoFont, clrTxt, ( r.centerx, 160 ), world.worldsurf )

    gui.textSurface(authCode,
      world.authDigitFont, ( 200, 200, 200 ),
      ( r.centerx, r.centery ),
      world.worldsurf
    )

    gui.textSurface("Make sure the numbers match!",
      world.authInfoFont, clrTxt, ( r.centerx, r.centery + 90 ), world.worldsurf )
