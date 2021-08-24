import pygame, states, events
from settings import all as settings

import gui

def handleInput(world, event):
  if event == events.btnSelectOn or event == events.btnEscapeOn:
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
  for i in range(0,len(perfdata)):
    separate_point = 15
    if(i<separate_point):
      if(i<5):
        gui.simpleText(world, perfdata[i], r.centerx - 350, (i + 1) * 30, alignment="midleft", color=(239,145,242))
      else:
        gui.simpleText(world, perfdata[i], r.centerx-350, (i+1)*30,alignment="midleft")
    else:
      gui.simpleText(world, perfdata[i], r.centerx - 50, (i-separate_point + 1) * 30, alignment="midleft")
  world.shouldRedraw = False

def enter(world):
  world.state = states.Perf
  world.configCatX = 0
  world.configOptX = -1
  world.shouldRedraw = True


