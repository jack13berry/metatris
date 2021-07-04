import pygame, states, events
from settings import all as settings

import gui

def handleInput(world, event):
  if event == events.btnEscapeOn:
    bwd(world)

  if event%10 == 0:
    world.sounds['uiaction'].play(0)
  # world.shouldRedraw = True


def bwd(world):
  if world.state >= states.Config:
    return left(world)

  world.shouldRedraw = True
  world.state = states.Intro


def draw( world ):
  if not world.shouldRedraw:
    return

  r = world.worldsurf_rect
  world.worldsurf.fill(world.bg_color)

  perfdata = world.getperf()
  print("perfdata")
  print(perfdata)
  for i in range(0,len(perfdata)):
    gui.simpleText(world, perfdata[i], r.centerx, (i+1)*30+200)
  world.shouldRedraw = False

def enter(world):
  world.state = states.Perf
  world.configCatX = 0
  world.configOptX = -1
  world.shouldRedraw = True


