import math, pygame.event
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

keyBack = 1000
keyA = 1001
keyB = 1002
keyC = 1003
keyD = 1004
keyE = 1005
keyF = 1006
keyG = 1007
keyH = 1008
keyI = 1009
keyJ = 1010
keyK = 1011
keyL = 1012
keyM = 1013
keyN = 1014
keyO = 1015
keyP = 1016
keyQ = 1017
keyR = 1018
keyS = 1019
keyT = 1020
keyU = 1021
keyV = 1022
keyW = 1023
keyX = 1024
keyY = 1025
keyZ = 1026
key0 = 1027
key1 = 1028
key2 = 1029
key3 = 1030
key4 = 1031
key5 = 1032
key6 = 1033
key7 = 1034
key8 = 1035
key9 = 1036
keyPeriod = 1037
keyShift = 1038


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


class ControllerButton():
  def __init__(group):
    group.known = {}

  def add(group, btnCode, eventCode):
    group.known[btnCode] = eventCode

  def map(group, world, event):
    #JOYBUTTONDOWN:on, JOYBUTTONUP:off
    dir = "off" if event.type == pygame.JOYBUTTONUP else "on"
    return group.known.get(dir+str(event.button), None)


def init(world):
  m = world.eventMap = {}
  key = m[pygame.KEYDOWN] = m[pygame.KEYUP] = KeyboardKey()
  btn = m[pygame.JOYBUTTONDOWN] = m[pygame.JOYBUTTONUP] = ControllerButton()

  axs = world.axisStateMap = {
    "01": btnUpOn,
    "10": btnLeftOn,
    "02": btnDownOn,
    "20": btnRightOn,
    "00001": btnUpOn,
    "11110": btnLeftOn,
    "00002": btnDownOn,
    "22220": btnRightOn
  }

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

  btn.add("off0",                       btnRotateCwOff)
  btn.add("on0",                        btnRotateCwOn)

  btn.add("off2",                       btnRotateCwOff)
  btn.add("on2",                        btnRotateCwOn)

  btn.add("off1",                       btnRotateCcwOff)
  btn.add("on1",                        btnRotateCcwOn)

  btn.add("off8",                       btnSelectOff)
  btn.add("on8",                        btnSelectOn)

  btn.add("off9",                       btnStartOff)
  btn.add("on9",                        btnStartOn)

  key.add("on" + str(pygame.K_BACKSPACE), keyBack)
  key.add("on" + str(pygame.K_a), keyA)
  key.add("on" + str(pygame.K_b), keyB)
  key.add("on" + str(pygame.K_c), keyC)
  key.add("on" + str(pygame.K_d), keyD)
  key.add("on" + str(pygame.K_e), keyE)
  key.add("on" + str(pygame.K_f), keyF)
  key.add("on" + str(pygame.K_g), keyG)
  key.add("on" + str(pygame.K_h), keyH)
  key.add("on" + str(pygame.K_i), keyI)
  key.add("on" + str(pygame.K_j), keyJ)
  key.add("on" + str(pygame.K_k), keyK)
  key.add("on" + str(pygame.K_l), keyL)
  key.add("on" + str(pygame.K_m), keyM)
  key.add("on" + str(pygame.K_n), keyN)
  key.add("on" + str(pygame.K_o), keyO)
  key.add("on" + str(pygame.K_p), keyP)
  key.add("on" + str(pygame.K_q), keyQ)
  key.add("on" + str(pygame.K_r), keyR)
  key.add("on" + str(pygame.K_s), keyS)
  key.add("on" + str(pygame.K_t), keyT)
  key.add("on" + str(pygame.K_u), keyU)
  key.add("on" + str(pygame.K_v), keyV)
  key.add("on" + str(pygame.K_w), keyW)
  key.add("on" + str(pygame.K_x), keyX)
  key.add("on" + str(pygame.K_y), keyY)
  key.add("on" + str(pygame.K_z), keyZ)
  key.add("on" + str(pygame.K_0), key0)
  key.add("on" + str(pygame.K_1), key1)
  key.add("on" + str(pygame.K_2), key2)
  key.add("on" + str(pygame.K_3), key3)
  key.add("on" + str(pygame.K_4), key4)
  key.add("on" + str(pygame.K_5), key5)
  key.add("on" + str(pygame.K_6), key6)
  key.add("on" + str(pygame.K_7), key7)
  key.add("on" + str(pygame.K_8), key8)
  key.add("on" + str(pygame.K_9), key9)
  key.add("on" + str(pygame.K_PERIOD), keyPeriod)
  key.add("on" + str(pygame.K_LSHIFT), keyShift)

  setupControllers(world)


# rawInpX = 0
def readAll(world):
  rawList = []
  axisMotionIndex = -1
  ex = 0
  for e in pygame.event.get():
    if e.type == pygame.MOUSEMOTION:
      continue

    if e.type == pygame.JOYAXISMOTION:
      if axisMotionIndex == -1:
        axisMotionIndex = ex
      else:
        rawList[axisMotionIndex] = e
        continue

    rawList.append(e)
    ex += 1

  if len(rawList) == 0:
    return rawList

  # print("EVTS:", len(rawList))

  if world.state in [states.KeyRemapping, states.BtnRemapping]:
    # global rawInpX
    # rawInpX += 1
    # if rawList[0].type == pygame.KEYDOWN:
      # print("Controller %1d %17s %s" % (0, " ", axisToButton(world, 0)))
    # else:
    #   print("\n\n\nRAWINP @%0.4d: %d" % (rawInpX, len(rawList)))
    return rawList

  lst = []
  for e in rawList:
    if e.type == pygame.QUIT:
      lst.append( reqQuit )

    elif e.type == pygame.VIDEORESIZE:
      lst.append( reqWinResize )
      world.lastResize = e

    elif e.type == pygame.JOYAXISMOTION:
      axisState = axisToButton(world, e.joy)
      if axisState != "":
        if world.jaxPrevious != None:
          # print("AxisEvent: '%s' is off" % world.jaxPrevious )
          lst.append( world.axisStateMap.get(world.jaxPrevious)-1 )
          world.jaxPrevious = None

        if axisState != world.jaxNatural:
          newevt = world.axisStateMap.get(axisState)
          if newevt:
            lst.append( newevt )
            world.jaxPrevious = axisState
            # print("AxisEvent: '%s' is on" % axisState )
          # else:
          #   print("AxisEvent: '%s' was ignored" % axisState)

    else:
      newevt = map(world, e)
      if newevt:
        lst.append( newevt )

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


def exitRemapConfig(world):
  world.state = states.ConfigLvl2
  world.shouldRedraw = True


def startRemapping(world, device):
  if device == "btn":
    world.mappingBtnDown = None
    world.axisToMap = None
    world.jaxNatural = axisToButton(world, 0)
    # print("JAXNATURAL:", world.jaxNatural)
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
  if not hasattr(event, 'type'):
    return

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
    # mappedBtnNames[world.remapActTarget] = "Jx<%d>" % event.button
    axisState = axisToButton(world, event.joy)
    if axisState == "":
      return

    if world.axisToMap == None:
      if axisState != world.jaxNatural:
        world.axisToMap = axisState
      return

    if axisState == world.jaxNatural:
      axisState = world.axisToMap
      world.axisToMap = None
      theAct = buttonVarNames[world.remapActTarget]
      mappedBtnNames[world.remapActTarget] = "X<%s>" % (axisState)
      names = globals()
      world.axisStateMap[axisState] = globals()[theAct+"On"]
      # print("Remap '%s' ==> '%s'." % (axisState, names[theAct+"On"]))
      exitRemapConfig(world)

    else:
      print("Confusing controller")


def keyTitleFor(event):
  # print("Title for:", event)
  try:
    keynm = pygame.key.name(event.key)
  except:
    keynm = "K<%d>" % (event.key)

  return keynm[0].upper() + keynm[1:]


def axisToButtonForStandardController(world, event):
  xx = math.floor(event.value*4) # >0.5 is on and <0.5 is off
  if event.axis == 0:
    if xx > 2:
      btn = "onE"
      world.jaxX = 1
    elif xx < -2:
      btn = "onW"
      world.jaxX = -1
    elif world.jaxX == 1:
      world.jaxX = 0
      btn = "offE"
    elif world.jaxX == -1:
      world.jaxX = 0
      btn = "offW"
    else:
      btn = ""
  elif event.axis == 1:
    if xx > 2:
      btn = "onS"
      world.jaxY = 1
    elif xx < -2:
      btn = "onN"
      world.jaxY = -1
    elif world.jaxY == 1:
      world.jaxY = 0
      btn = "offS"
    elif world.jaxY == -1:
      world.jaxY = 0
      btn = "offN"
    else:
      btn = ""
  else:
    btn = ""

  print("%d.%d -- %2.10f ===> %s" % (
    event.axis, xx, event.value, btn
  ))
  return btn


def axisToButton(world, cx = 0):
  # xx = math.floor(event.value*2) # int(round((event.value+1)/2.0 * 50))
  # col1 = "  Axis.%d: %12.10f --> %2d" % ( event.axis, event.value, xx )
  # print("%30s %s" % ( col1, axisReport(world, event.joy) ))
  j = getattr(world, 'joystick%d'%(cx))
  nax = j.get_numaxes()
  axes = ''
  for x in range(0, nax):
    # axes += '%d' % (math.floor(j.get_axis(x)*2)+4)
    xval = j.get_axis(x)
    axes += '1' if xval < -0.4 else ( '0' if xval < 0.4 else '2')

  return axes


def axisReport(world, cx):
  j = getattr(world, 'joystick%d'%(cx))
  nax = j.get_numaxes()
  axes = []
  for x in range(0, nax):
    xval = j.get_axis(x)
    # xx = math.floor(xval*2)+4
    xx = 1 if xval < -0.4 else ( 0 if xval < 0.4 else 2)
    axes.append( '%24s' % ('%d: %12.10f --> %2d' % (x, xval, xx)) )
    # axes.append('%d'%xx)

  return ''.join(axes)


def setupControllers(world):
  contid = pygame.joystick.get_count()
  world.numberOfControllers = contid
  while contid > 0:
    contid -= 1
    contobj = pygame.joystick.Joystick(contid)
    setattr(world, ("joystick%d" % contid), contobj)
    # global axisToButton
    # if contobj.get_numaxes() > 2:
    #   axisToButton = axisToButtonForWeirdController
    #   world.jaxNatural = ""

    # else:
    #   world.jaxX = 0
    #   world.jaxY = 0
    #   axisToButton = axisToButtonForWeirdController
    #   world.jaxNatural = axisToButton(world, 0)
    #   # axisToButton = axisToButtonForStandardController

    # print("Controller %1d %17s %s" % (contid, " ", axisReport(world, contid)))

    contobj.init()

  if world.numberOfControllers > 0:
    world.jaxPrevious = None
    world.jaxNatural = axisToButton(world)
