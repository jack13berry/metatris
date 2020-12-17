import pygame.event
import states

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


buttonNames = [
  "Up", "Right", "Down", "Left",
  "Rotate CW", "Rotate CCW",
  "Start", "Select"
]

mappedKeyNames = {
  "Up": "Default",
  "Right": "Default",
  "Down": "Default",
  "Left": "Default",
  "Rotate CW": "Default",
  "Rotate CCW": "Default",
  "Start": "Default",
  "Select": "Default"
}

mappedBtnNames = {
  "Up": "Default",
  "Right": "Default",
  "Down": "Default",
  "Left": "Default",
  "Rotate CW": "Default",
  "Rotate CCW": "Default",
  "Start": "Default",
  "Select": "Default"
}


buttonVarNames = {
  "Up": "btnUp",
  "Right": "btnRight",
  "Down": "btnDown",
  "Left": "btnLeft",
  "Rotate CW": "btnRotateCw",
  "Rotate CCW": "btnRotateCcw",
  "Start": "btnStart",
  "Select": "btnSelect"
}


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

  key.add("off" +str(pygame.K_RETURN),  btnStartOff)
  key.add("on" +str(pygame.K_RETURN),   btnStartOn)

  key.add("off" +str(pygame.K_SPACE),   btnSelectOff)
  key.add("on" +str(pygame.K_SPACE),    btnSelectOn)

  btn.add("off1",                       btnRotateCwOff)
  btn.add("on1",                        btnRotateCwOn)

  btn.add("off2",                       btnRotateCcwOff)
  btn.add("on2",                        btnRotateCcwOn)

  btn.add("off9",                       btnSelectOff)
  btn.add("on9",                        btnSelectOn)


def readAll(world):
  rawList = pygame.event.get()

  if len(rawList) == 1:
    # print("SINGLEEVT:", world.state, world.state in [states.KeyRemapping, states.BtnRemapping])
    if world.state in [states.KeyRemapping, states.BtnRemapping]:
      # print("RAWINP @%d: %s" % (world.state, rawList))
      return rawList
    else:
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
      # print("axisUnv: %d %s" %(e.axis, e.value))
      if axisConsumed == e.value:
        # print("axisSkipped: %d %s" %(e.axis, e.value))
        continue
      if e.axis == 4:
        print("axis4:  %s" % (e.value))
        if e.value < -1:
          lst.append( btnUpOn )
          world.lastAxisDown = btnUpOn
        elif e.value > 0:
          lst.append( btnDownOn )
          world.lastAxisDown = btnDownOn
        elif e.value < 0:
          if world.lastAxisDown is not None:
            lst.append( world.lastAxisDown-1 )
            world.lastAxisDown = None

        axisConsumed = e.value

      elif e.axis == 0:
        # print("axis0:  %s" % (e.value))
        if e.value < -1:
          lst.append( btnLeftOn )
          world.lastAxisDown = btnLeftOn
        elif e.value > 0:
          lst.append( btnRightOn )
          world.lastAxisDown = btnRightOn
        elif e.value < 0:
          if world.lastAxisDown is not None:
            lst.append( world.lastAxisDown-1 )
            world.lastAxisDown = None

        axisConsumed = e.value

      else:
        print("axisN: %d %s" % (e.axis, e.value))

    else:
      if world.state in [states.KeyRemapping, states.BtnRemapping]:
        lst.append( e )
      else:
        lst.append( map(world, e) )

  return lst


def map(world, event):
  if event.type not in world.eventMap:
    # print("UnknownEvent:", event.type)
    return None

  group = world.eventMap[event.type]
  # print("EventGroup:", group)

  # if hasattr(event, "button"):
  #   print("C: %d" % event.button)
  # elif hasattr(event, "key"):
  #   print("K: %d" % event.key)

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


def exitRemapConfig(world):
  world.state = states.ConfigLvl2
  world.shouldRedraw = True


def startRemapping(world, device):
  if device == "btn":
    world.mappingBtnDown = None
    world.mappingAxsDown = None
    world.state = states.BtnRemapping
    # print("ENTERED::BTN for '%s' @%d" % (world.remapActTarget, world.state))
  else:
    world.mappingKeyDown = None
    world.state = states.KeyRemapping
    # print("ENTERED::KEY for '%s' @%d" % (world.remapActTarget, world.state))


def handleKeyRemapInput(world, event):
  if event.type != pygame.KEYDOWN and event.type != pygame.KEYUP:
    return

  # enter/right released
  if event.type == pygame.KEYUP and world.mappingKeyDown == None:
    # print("K:initial key release")
    return

  if event.key == pygame.K_ESCAPE:
    # print("K:escape key")
    return exitRemapConfig(world)

  if event.type == pygame.KEYDOWN:
    # print("K:keydown, setting mappingKeyDown to '%s'" % event.key)
    world.mappingKeyDown = event.key

  elif event.type == pygame.KEYUP:
    # print("K:keyup, mappingKey %s" % event.key)
    theMap = world.eventMap[pygame.KEYDOWN]
    mappedKeyNames[world.remapActTarget] = keyTitleFor(event)
    theAct = buttonVarNames[world.remapActTarget]
    names = globals()
    theMap.add("off"+str(event.key), names[theAct+"Off"])
    theMap.add("on"+str(event.key), names[theAct+"On"])
    # print("Remap '%s' ==> '%s'." % ("on"+str(event.key), names[theAct+"On"]))
    exitRemapConfig(world)


def handleBtnRemapInput(world, event):
  # print("BtnRemapEvt:", event)
  if event.type != pygame.JOYBUTTONDOWN and \
      event.type != pygame.JOYBUTTONUP and event.type != pygame.JOYAXISMOTION:

    if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
      if event.key == pygame.K_ESCAPE:
        exitRemapConfig(world)

    return

  # select/start released
  if event.type == pygame.JOYBUTTONUP and world.mappingBtnDown == None:
    # print("K:initial btn release")
    return

  if event.type == pygame.JOYBUTTONDOWN:
    # print("K:keydown, setting mappingKeyDown to '%s'" % event.key)
    world.mappingBtnDown = event.button

  elif event.type == pygame.JOYBUTTONUP:
    # print("K:keyup, mappingKey %s" % event.button)
    theMap = world.eventMap[pygame.JOYBUTTONDOWN]
    mappedBtnNames[world.remapActTarget] = "Btn<%d>" % (event.button)
    theAct = buttonVarNames[world.remapActTarget]
    names = globals()
    theMap.add("off"+str(event.button), names[theAct+"Off"])
    theMap.add("on"+str(event.button), names[theAct+"On"])
    # print("Remap '%s' ==> '%s'." % ("on"+str(event.button), names[theAct+"On"]))
    exitRemapConfig(world)

  elif event.type == pygame.JOYAXISMOTION:
    mappedBtnNames[world.remapActTarget] = "Jx<%d>" % event.button


def keyTitleFor(event):
  # print("Title for:", event)
  try:
    keynm = pygame.key.name(event.key)
  except:
    keynm = "K<%d>" % (event.key)

  return keynm[0].upper() + keynm[1:]
