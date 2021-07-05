import pygame, states, events
from settings import all as settings

import gui

def handleInput(world, event):
  if event == events.btnStartOn:
    fwd(world)

  elif event == events.btnLeftOff:
    left(world)

  elif event == events.btnRightOff:
    right(world)

  elif event == events.btnUpOff:
    up(world)

  elif event == events.btnDownOff:
    down(world)

  elif event == events.btnSelectOn or event == events.btnEscapeOn:
    bwd(world)

  if event%10 == 0:
    world.sounds['uiaction'].play(0)
  world.shouldRedraw = True


def fwd(world):
  return right(world)


def bwd(world):
  if world.state >= states.Config:
    return left(world)

  world.shouldRedraw = True
  world.state = states.Intro


def left(world):
  if world.state == states.Config:
    world.state = states.Intro
    return

  world.state -= 1
  if world.state == states.Config:
    world.configOptX = -1

  world.shouldRedraw = True


def right(world):
  # print("CNF: %d.%d @%d" % (world.configCatX, world.configOptX, world.state))
  if world.state == states.ConfigLvl2:
    if world.configCatX == 3: #controls
      if world.configOptX == 1:
        events.startRemapping(world, "btn")
      else:
        events.startRemapping(world, "key")

      world.shouldRedraw = True

    return

  world.state += 1
  if world.state <= states.ConfigLvl1:
    world.configOptX = 0

  world.shouldRedraw = True


def up(world):
  if world.state == states.Config:
    world.configCatX -= 1
    if world.configCatX < 0:
      world.configCatX = len(settings) - 1
  elif world.state == states.ConfigLvl1:
    world.configOptX -= 1
    if world.configOptX < 0:
      world.configOptX = len(settings[world.configCatX].opts) - 1
  elif world.state == states.ConfigLvl2:
    opt = settings[world.configCatX].opts[world.configOptX]
    if hasattr(opt, "up"):
      opt.up(world)

  # print("CNF: %d.%d @%d" % (world.configCatX, world.configOptX, world.state))
  world.shouldRedraw = True


def down(world):
  if world.state == states.Config:
    world.configCatX += 1
    if world.configCatX >= len(settings):
      world.configCatX = 0
  elif world.state == states.ConfigLvl1:
    world.configOptX += 1
    if world.configOptX >= len(settings[world.configCatX].opts):
      world.configOptX = 0
  elif world.state == states.ConfigLvl2:
    opt = settings[world.configCatX].opts[world.configOptX]
    if hasattr(opt, "down"):
      opt.down(world)


  # print("CNF: %d.%d @%d" % (world.configCatX, world.configOptX, world.state))
  world.shouldRedraw = True


def draw( world ):
  if not world.shouldRedraw:
    return

  world.worldsurf.fill( world.bg_color )

  r = world.worldsurf_rect
  cw = int(r.width/4)+8

  if world.state == states.Config:
    pygame.draw.rect( world.worldsurf,
      (242,133,40), [(0, r.height-10), (cw-1, 10)])
  elif world.state == states.ConfigLvl1:
    drawValues(world)
    pygame.draw.rect( world.worldsurf,
      (242,133,40), [(cw, r.height-10), (cw-1, 10)])
  else:
    drawValues(world)
    pygame.draw.rect( world.worldsurf,
      (242,133,40), [(2*cw+4, r.height-10), (2*cw, 10)])

  drawCategories(world)
  drawSettings(world)

  world.shouldRedraw = False


def drawCategories(world):
  x, y, w, h = 0, 0, int(world.worldsurf_rect.width/4), 60
  if world.state == states.Config:
    clrFocused = (120,200,50)
    clrBlurred = (60,140,10)
    clrFocusedText = (26,26,26)
    clrBlurredText = (60,140,10)
  else:
    clrFocused = (70,150,0)
    clrBlurred = (30,110,0)
    clrFocusedText = (26,26,26)
    clrBlurredText = (40,120,0)

  for sx in range(0, len(settings)):
    y = gui.verticalTab(world, settings[sx].title, x, y, w, h,
      world.configCatX == sx,
      clrFocused, clrBlurred, clrFocusedText, clrBlurredText
    )


def drawSettings(world):
  rect = world.worldsurf_rect
  x, y = int(rect.width/4) + 15, 0
  w, h = int(rect.width/4), 60
  g = settings[world.configCatX]

  if world.state == states.Config:
    clrBorder = (120,200,50)
  else:
    clrBorder = (70,150,0)

  if world.state == states.ConfigLvl1:
    clrFocused = (11, 165, 204)
    clrBlurred = (40,100,160)
    clrFocusedText = (20,30,70)
    clrBlurredText = (8, 81, 135)
  else:
    clrFocused = (51, 125, 184)
    clrBlurred = (30,80,120)
    clrFocusedText = (0, 20, 90)
    clrBlurredText = (20,60,100)

  pygame.draw.rect(world.worldsurf, clrBorder, [(x-11, 0), (4, rect.height)])
  for ox, opt in enumerate(g.opts):
    y = gui.verticalTab(world, opt.title, x, y, w, h,
      world.configOptX == ox,
      clrFocused, clrBlurred, clrFocusedText, clrBlurredText
    )


def drawValues(world):
  rect = world.worldsurf_rect
  x, y = int(rect.width/2) + 15, 0
  w, h = int(rect.width/4), 60
  g = settings[world.configCatX]
  o = g.opts[world.configOptX]

  if world.state == states.ConfigLvl1:
    clrBorder = (11, 165, 204)
  else:
    clrBorder = (51, 125, 184)

  pygame.draw.rect(world.worldsurf, clrBorder, [(x, 0), (4, rect.height)])
  o.draw(world)


def enter(world):
  world.state = states.Config
  world.configCatX = 0
  world.configOptX = -1
  world.shouldRedraw = True

  # for ox, opt in enumerate(g.opts):
  #   y = gui.verticalTab(world, opt.title, x, y, w, h,
  #     world.configOptX == ox
  #   )
