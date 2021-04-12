import cnf, gui, states, events

class O():
  pass


class G():
  def __init__(group, title):
    group.title = title
    group.opts = []


class Radio():
  def __init__(opt, target, title, set, default=0):
    opt.target = target
    opt.title = title
    opt.default = default
    opt.set = set
    opt.currentX = -1


  def getCurrentX(opt, world):
    if opt.currentX != -1:
      return opt.currentX

    current = getattr(world, opt.target)
    for (x, val) in enumerate(opt.set):
      if val[0] == current:
        opt.currentX = x
        return x


  def up(opt, world):
    if opt.currentX > 0:
      opt.currentX -= 1
    else:
      opt.currentX = len(opt.set) - 1

    cnf.updateUserConfig(world, opt.target, opt.set[opt.currentX][0])


  def down(opt, world):
    if opt.currentX < len(opt.set) - 1:
      opt.currentX += 1
    else:
      opt.currentX = 0

    cnf.updateUserConfig(world, opt.target, opt.set[opt.currentX][0])


  def draw(opt, world):
    opt.currentX = opt.getCurrentX(world)
    y = world.worldsurf_rect.height//2 - opt.currentX*30

    txtcolor = (116, 176, 223)
    for (x, val) in enumerate(opt.set):
      txt = val[1]
      if x == opt.currentX:
        rect = gui.infoText(world, txt, y=y, color=txtcolor)

        if world.state == states.ConfigLvl2:
          gui.button(world, txt, rect.left-30, y-15, rect.w+60, 30,
            focused=True, withTicks=False,
            clr1=txtcolor, clr2=(255, 255, 255)
          )
        else:
          gui.infoText(world, "▶", x=rect.left-20, y=y, color=txtcolor)
          gui.infoText(world, "◀", x=rect.right+20, y=y, color=txtcolor)

      else:
        gui.infoText(world, txt, y=y, color=(45, 73, 96))

      y += 30



class ControllerSetup():
  def __init__(opt, target, title):
    opt.target = target
    opt.title = title
    opt.set = []
    opt.currentX = (len(events.buttonNames)+1)//2

    if target == "keyboard":
      opt.namedMap = events.mappedKeyNames
      opt.actName = "key"
    else:
      opt.actName = "button"
      opt.namedMap = events.mappedBtnNames


  def infoText(opt, world, text):
    gui.infoText(world, text, y = int(world.worldsurf_rect.height*0.9))


  def up(opt, world):
    if opt.currentX > 0:
      opt.currentX -= 1
    else:
      opt.currentX = len(events.buttonNames) - 1


  def down(opt, world):
    if opt.currentX < len(events.buttonNames) - 1:
      opt.currentX += 1
    else:
      opt.currentX = 0


  def draw(opt, world):
    txtcolor = (116, 176, 223)
    midy = world.worldsurf_rect.height//2
    x = int(world.worldsurf_rect.width*0.75)

    if world.state == states.ConfigLvl1:
      opt.infoText(world, opt.title + " Mappings")

    elif world.state == states.ConfigLvl2:
      world.remapActTarget = events.buttonNames[opt.currentX]
      gui.infoText(world, "◀▶", x=x, y=midy-15, color=txtcolor)
      opt.infoText(world, "Enter to remap")

    else:
      gui.infoText(world, ("Press the %s for" % opt.actName),
        x=x, y=midy-20, color=txtcolor
      )
      gui.infoText(world, "'%s' action." % events.buttonNames[opt.currentX],
        x=x, y=midy+20, color=txtcolor
      )
      opt.infoText(world, "Esc to cancel")
      return


    y = midy - opt.currentX*30
    ix = 0
    for name in events.buttonNames:
      # selected = (world.state == states.ConfigLvl1) \
      #            and (opt.currentX == ix)

      gui.simpleText(world, name, x-12, y-15, color=txtcolor,
        alignment="midright")
      gui.simpleText(world, opt.namedMap[name], x+12, y-15, color=txtcolor,
        alignment="midleft")

      ix += 1
      y += 30


dynamics = G("Dynamics")

dynamics.opts.append(Radio("starting_level", "Starting Level",
  [ [a, "Level %02d"%a, ""] for a in range(0, 20) ]
))

dynamics.opts.append(Radio("boardname", "Starting Board", [
  [ "empty", "Empty" ], ["quarterfull", "Quarter Full"]
]))

dynamics.opts.append(Radio("inverted", "Direction", [
  [False, "Normal", "Pieces fall down"],
  [True, "Upside Down", "Pieces fly up"]
]))

dynamics.opts.append(Radio("timingSetup", "Timing", [
  ["NesNtsc", "NES NTSC", ""],
  ["NesPal", "NES PAL", ""]
]))



appearance = G("Appearance")

appearance.opts.append(Radio("ghost_zoid", "Ghost Piece", [
  [False, "Off", ""],
  [True, "On", ""]
]))

appearance.opts.append(Radio("color_mode", "Piece Colors", [
  ["STANDARD", "Standard", ""],
  ["REMIX", "Remix", ""]
]))

# appearance.opts.append(Radio("render_scores", "Show Scores", [
#   [False, "Only at the End", ""],
#   [True, "Always", ""]
# ]))

audio = G("Audio")

audio.opts.append(Radio("sfx_vol", "Effects Volume",
  [ [a/100, "%02d%%"%a, ""] for a in range(0, 101, 10) ]
))

audio.opts.append(Radio("music_vol", "Music Volume",
  [ [a/100, "%02d%%"%a, ""] for a in range(0, 101, 10) ]
))

controls = G("Controls")

controls.opts.append(ControllerSetup("keyboard", "Keyboard"))
controls.opts.append(ControllerSetup("controller", "Controller"))



all = [
  dynamics,
  appearance,
  audio,
  controls
]
