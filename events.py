import pygame.event

btnLeftOff      = 110
btnLeftOn       = 111
btnRightOff     = 120
btnRightOn      = 121
btnUpOff        = 130
btnUpOn         = 131
btnDownOff      = 140
btnDownOn       = 141

btnRotateCwOff  = 210
btnRotateCwOn   = 211
btnRotateCcwOff = 220
btnRotateCcwOn  = 221

btnSelectOff    = 310
btnSelectOn     = 311
btnStartOff     = 320
btnStartOn      = 321
btnEscapeOff    = 330
btnEscapeOn     = 331

reqScreenShot   = 901
reqWinResize    = 971
reqPause        = 990
reqResume       = 991
reqPauseResume  = 992
reqQuit         = 999


def init(world):
  m = world.eventMap = {}
  key = m[pygame.KEYDOWN] = m[pygame.KEYUP] = KeyboardKey()
  btn = m[pygame.JOYBUTTONDOWN] = m[pygame.JOYBUTTONUP] = ControllerButton()

  key.add("off"+str(pygame.K_LEFT),     btnLeftOff)
  key.add("on" +str(pygame.K_LEFT),     btnLeftOn)

  key.add("off"+str(pygame.K_RIGHT),    btnRightOff)
  key.add("on" +str(pygame.K_RIGHT),    btnRightOn)

  key.add("off"+str(pygame.K_UP),       btnUpOff)
  key.add("on" +str(pygame.K_UP),       btnUpOn)

  key.add("off"+str(pygame.K_DOWN),     btnDownOff)
  key.add("on" +str(pygame.K_DOWN),     btnDownOn)

  key.add("on" +str(pygame.K_ESCAPE),   btnEscapeOn)
  key.add("on" +str(pygame.K_i),        reqScreenShot)

  key.add("off"+str(pygame.K_j),        btnRotateCwOff)
  key.add("on" +str(pygame.K_j),        btnRotateCwOn)

  key.add("off"+str(pygame.K_k),        btnRotateCcwOff)
  key.add("on" +str(pygame.K_k),        btnRotateCcwOn)

  key.add("on" +str(pygame.K_p),        reqPauseResume)

  key.add("on" +str(pygame.K_RETURN),   btnStartOn)
  key.add("on" +str(pygame.K_SPACE),    btnSelectOn)

  btn.add("off1",                       btnRotateCcwOff)
  btn.add("on1",                        btnRotateCcwOn)

  btn.add("off2",                       btnRotateCwOff)
  btn.add("on2",                        btnRotateCwOn)


def readAll(world):
  rawList = pygame.event.get()
  if len(rawList) == 1:
    return [ map(world, rawList[0]) ]

  lst = []
  axisConsumed = None
  for e in rawList:

    if e.type == pygame.QUIT:
      lst.append( reqQuit )

    elif e.type == pygame.VIDEORESIZE:
      lst.append( reqWinResize )
      world.lastResize = e

    elif e.type == pygame.JOYAXISMOTION:
      if axisConsumed == e.value:
        continue
      if e.axis == 4:
        if e.value < -1:
          lst.append( btnUpOn )
          world.lastAxisDown = btnUpOn
        elif e.value > 0:
          lst.append( btnDownOn )
          world.lastAxisDown = btnDownOn
        elif e.value < 0:
          if world.lastAxisDown is not None:
            lst.append( world.lastAxisDown+1 )
            world.lastAxisDown = None

        axisConsumed = e.value

      elif e.axis == 0:
        if e.value < -1:
          lst.append( btnLeftOn )
          world.lastAxisDown = btnLeftOn
        elif e.value > 0:
          lst.append( btnRightOn )
          world.lastAxisDown = btnRightOn
        elif e.value < 0:
          if world.lastAxisDown is not None:
            lst.append( world.lastAxisDown+1 )
            world.lastAxisDown = None

        axisConsumed = e.value

    else:
      lst.append( map(world, e) )

  return lst


def map(world, event):
  if event.type not in world.eventMap:
    print("UnknownEvent:", event.type)
    return None

  group = world.eventMap[event.type]
  # print("MatchedGroup:", group)
  return group.map(world, event)


class ControllerButton():
  def __init__(group):
    group.known = {}

  def add(group, btnCode, eventCode):
    group.known[btnCode] = eventCode

  def map(group, world, event):
    #JOYBUTTONDOWN:on, JOYBUTTONUP:off
    dir = "off" if event.type == pygame.JOYBUTTONUP else "on"
    return group.known.get(dir+str(event.button), None)


class KeyboardKey():
  def __init__(group):
    group.known = {}

  def add(group, keyCode, eventCode):
    # print("AddKeyCode:", keyCode, eventCode)
    group.known[keyCode] = eventCode

  def map(group, world, event):
    #KEYDOWN:on, KEYUP:off
    dir = "off" if event.type == pygame.KEYUP else "on"
    return group.known.get(dir+str(event.key), None)
