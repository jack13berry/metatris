import pygame

import cnf
import gui
import paths

STUDY_ORDER = ("normal", "lagging", "leading", "prescriptive")
CANVAS = (800, 600)


def picker_names():
  """Configs to offer: study profiles in study order, then any others.
  default is hidden unless it is the only config."""
  names = cnf.available_configs()
  if "default" not in names:
    raise ValueError("configs/default.config is required")
  names = [name for name in names if name != "default"] or ["default"]
  return sorted(names, key=lambda name: STUDY_ORDER.index(name) if name in STUDY_ORDER
                else len(STUDY_ORDER))


class ConfigPicker:
  rows_per_page = 8

  def __init__(self, initial=None):
    self.names = picker_names()
    self.index = self.names.index(initial) if initial in self.names else 0
    self.axis_states = {}
    self.row_rects = []
    self.offset = (0, 0)  # where the picker canvas sits on the screen

  def move(self, direction):
    self.index = (self.index + direction) % len(self.names)

  def handle_event(self, event):
    if event.type == pygame.QUIT:
      return False
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        return False
      if event.key == pygame.K_RETURN:
        return self.names[self.index]
      if event.key == pygame.K_UP:
        self.move(-1)
      elif event.key == pygame.K_DOWN:
        self.move(1)
      elif event.key == pygame.K_PAGEUP:
        self.move(-self.rows_per_page)
      elif event.key == pygame.K_PAGEDOWN:
        self.move(self.rows_per_page)
    elif event.type == pygame.JOYBUTTONDOWN:
      if event.button in (1, 9):  # A or Start on the supported NES controllers.
        return self.names[self.index]
      if event.button in (0, 2, 8):
        return False
    elif event.type == pygame.JOYHATMOTION:
      if event.value[1]:
        self.move(-event.value[1])
    elif event.type == pygame.JOYAXISMOTION and event.axis in (1, 4):
      direction = -1 if event.value < -0.4 else (1 if event.value > 0.4 else 0)
      key = (event.joy, event.axis)
      if direction and direction != self.axis_states.get(key, 0):
        self.move(direction)
      self.axis_states[key] = direction
    elif event.type == pygame.MOUSEBUTTONDOWN:
      pos = (event.pos[0] - self.offset[0], event.pos[1] - self.offset[1])
      for index, rect in self.row_rects:
        if event.button == 1 and rect.collidepoint(pos):
          self.index = index
          return self.names[index]
    elif event.type == pygame.MOUSEWHEEL:
      self.move(-event.y)
    return None

  def draw(self, screen, title_font, font):
    screen.fill((26, 26, 26))
    gui.textSurface("Select a configuration", title_font, (240, 240, 240),
                    (400, 55), screen)
    gui.textSurface("Choose the participant's condition.", font,
                    (190, 190, 190), (400, 100), screen)
    first = (self.index // self.rows_per_page) * self.rows_per_page
    self.row_rects = []
    for row, index in enumerate(range(first, min(first + self.rows_per_page, len(self.names)))):
      rect = pygame.Rect(100, 135 + row * 43, 600, 39)
      self.row_rects.append((index, rect))
      color = (230, 230, 230)
      if index == self.index:
        pygame.draw.rect(screen, (120, 200, 50), rect, border_radius=4)
        color = (26, 26, 26)
      label = self.names[index]
      while font.size(label)[0] > rect.width - 30:
        label = label[:-4] + "..."
      gui.textSurface(label, font, color, rect.center, screen)
    gui.textSurface("%d / %d" % (self.index + 1, len(self.names)), font,
                    (190, 190, 190), (400, 505), screen)
    gui.textSurface("Up / Down: choose     Enter / A / Start: confirm", font,
                    (210, 210, 210), (400, 545), screen)
    gui.textSurface("Esc / B: exit", font, (190, 190, 190), (400, 578), screen)


def choose(initial=None, fullscreen=False):
  picker = ConfigPicker(initial)
  if fullscreen:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
  else:
    screen = pygame.display.set_mode(CANVAS)
  canvas = pygame.Surface(CANVAS)
  picker.offset = ((screen.get_width() - CANVAS[0]) // 2, (screen.get_height() - CANVAS[1]) // 2)
  pygame.display.set_caption("Metatris - Configuration")
  font_path = paths.resource("media", "fonts", "Montserrat", "Montserrat-Medium.ttf")
  title_font = pygame.font.Font(font_path, 30)
  font = pygame.font.Font(font_path, 18)
  controllers = [pygame.joystick.Joystick(index) for index in range(pygame.joystick.get_count())]
  for controller in controllers:
    controller.init()
  clock = pygame.time.Clock()
  while True:
    for event in pygame.event.get():
      result = picker.handle_event(event)
      if result is not None:
        return result or None
    picker.draw(canvas, title_font, font)
    screen.fill((26, 26, 26))
    screen.blit(canvas, picker.offset)
    pygame.display.flip()
    clock.tick(60)
