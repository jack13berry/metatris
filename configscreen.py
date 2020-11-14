import pygame, states
from settings import all as settings

import gui

def handleInput(world, event):
  valid = False
  if event.type == pygame.KEYDOWN:
    valid = True
    if event.key == pygame.K_SPACE:
      fwd(world)

    elif event.key == pygame.K_LEFT:
      left(world)

    elif event.key == pygame.K_RIGHT:
      right(world)

    elif event.key == pygame.K_UP:
      up(world)

    elif event.key == pygame.K_DOWN:
      down(world)

    elif event.key == pygame.K_ESCAPE:
      bwd(world)

    else:
      print("UNEXPECTED KEY:", event.key)
      valid = False

  elif event.type == pygame.JOYBUTTONDOWN:
    valid = True
    if event.button == world.JOY_START:
      fwd(world)
    elif event.button == pygame.JOY_LEFT:
      left(world)
    elif event.button == pygame.JOY_RIGHT:
      right(world)
    elif event.button == pygame.JOY_UP:
      up(world)
    elif event.button == pygame.JOY_DOWN:
      down(world)
    else:
      print("UNEXPECTED BUTTON:", event.button)
      valid = False

  if valid:
    world.sounds['uiaction'].play(0)


def fwd(world):
  if world.state < states.ConfigLvl2:
    return right(world)

  world.shouldRedraw = True


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

  if world.state == states.ConfigLvl2:
    return

  world.state += 1
  if world.state <= states.ConfigLvl1:
    world.configOptX = 0

  elif world.state == states.ConfigLvl2:
    pass #world.configOptX = 0


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


  world.shouldRedraw = True


def draw( world ):
  if not world.shouldRedraw:
    return

  r = world.worldsurf_rect
  world.worldsurf.fill( world.bg_color )

  drawCategories(world)
  drawSettings(world)
  if world.state >= states.ConfigLvl1:
    drawValues(world)

  world.shouldRedraw = False


def drawCategories(world):
  x, y, w, h = 0, 0, int(world.worldsurf_rect.width/4), 60

  for sx in range(0, len(settings)):
    y = gui.verticalTab(world, settings[sx].title, x, y, w, h,
      world.configCatX == sx
    )


def drawSettings(world):
  rect = world.worldsurf_rect
  x, y = int(rect.width/4) + 15, 0
  w, h = int(rect.width/4), 60
  g = settings[world.configCatX]

  clr1 = (120,200,50)
  pygame.draw.rect(world.worldsurf, clr1, [(x-11, 0), (4, rect.height)])
  for ox, opt in enumerate(g.opts):
    y = gui.verticalTab(world, opt.title, x, y, w, h,
      world.configOptX == ox,
      (81, 155, 214), (120,200,50)
    )


def drawValues(world):
  rect = world.worldsurf_rect
  x, y = int(rect.width/2) + 15, 0
  w, h = int(rect.width/4), 60
  g = settings[world.configCatX]
  o = g.opts[world.configOptX]

  pygame.draw.rect(world.worldsurf, (81, 155, 214), [(x, 0), (4, rect.height)])
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
