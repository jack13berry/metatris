import cnf, gui, states

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
    currentX = opt.getCurrentX(world)
    y = world.worldsurf_rect.height//2 - currentX*30

    for (x, val) in enumerate(opt.set):
      txt = val[1]
      if x == currentX:
        txtcolor = (116, 176, 223)
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

  def infotext(opt, world, text):
    gui.infoText(world, text, y = int(world.worldsurf_rect.height*0.9))

  def draw(opt, world):
    opt.infotext(world, "Hit space key to edit")

dynamics = G("Dynamics")

dynamics.opts.append(Radio("starting_level", "Start Level",
  [ [a, "Level %02d"%a, ""] for a in range(0, 20) ]
))

dynamics.opts.append(Radio("timingSetup", "Timing", [
  ["NesNtsc", "NES NTSC", ""],
  ["NesPal", "NES PAL", ""]
]))

dynamics.opts.append(Radio("inverted", "Direction", [
  [False, "Normal", "Pieces fall down"],
  [True, "Upside Down", "Pieces fly up"]
]))

controls = G("Controls")

controls.opts.append(ControllerSetup("keyboard", "Keyboard"))
controls.opts.append(ControllerSetup("joystick", "Joystick"))

# profile = G("Theme")

# profile = G("Profile")

all = [
  dynamics,
  controls,
  # profile
]
