import pygame
import states, events, logger
import introscreen, configscreen, perfscreen


def aarStateHandler(world, event):
  if event==events.btnDownOff or (event==events.btnUpOff and world.inverted):
    world.input_stop_drop()
  elif event == events.btnLeftOff:
    world.input_trans_stop(-1)
  elif event == events.btnRightOff:
    world.input_trans_stop(1)
  elif event == events.btnSelectOff and world.AAR_worldpaced:
    world.input_end_AAR()


def playStateHandler(world, event):
  # ***LOG to be MOVED TO events.py:
  # if event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:
  #   dir = "PRESS" if event.type == pygame.KEYDOWN else "RELEASE"
  #   logger.game_event(world,  "KEYPRESS", dir, pygame.key.name(event.key))
  # elif event.type == pygame.JOYBUTTONUP or event.type == pygame.JOYBUTTONDOWN:
  #   dir = "PRESS" if event.type == pygame.JOYBUTTONDOWN else "RELEASE"
  #   logger.game_event(world,  "KEYPRESS", dir, world.buttons[event.button] )

  if event == events.btnSelectOn or event == events.btnEscapeOn:
    world.state = states.Intro

  # elif event == events.btnSelectOn:
  #   world.input_slam()
  #   world.input_place()

  elif event == events.reqPause or event == events.reqPauseResume:
    world.input_pause()

  elif event == events.btnStartOn:
    world.input_pause()

  elif event == events.btnLeftOn:
    world.input_trans_left()
    world.das_held = -1
  elif event == events.btnLeftOff:
    world.input_trans_stop(-1)

  elif event == events.btnRightOn:
    world.input_trans_right()
    world.das_held = 1
  elif event == events.btnRightOff:
    world.input_trans_stop(1)

  elif event == events.btnDownOn:
    if world.inverted:
      world.input_rotate_single()
    else:
      world.input_start_drop()

  elif event == events.btnDownOff:
    if world.inverted:
      if pygame.KMOD_SHIFT:
        world.add_latency("RL")
      else:
        world.add_latency("RR")
    else:
      world.input_stop_drop()

  elif event == events.btnUpOn:
    if world.inverted:
      world.input_start_drop()
    else:
      world.input_rotate_single()
  elif event == events.btnUpOff:
    if world.inverted:
      world.input_stop_drop()
    else:
      if pygame.KMOD_SHIFT:
        world.add_latency("RL")
      else:
        world.add_latency("RR")

  elif event == events.btnRotateCwOn:
    world.input_clockwise()
    world.add_latency("RR")

  elif event == events.btnRotateCcwOn:
    world.add_latency("RL")
    world.input_counterclockwise()

  # if event.type == pygame.KEYDOWN:
  #   elif event.key == pygame.K_r:
  #     world.input_undo()

  #   elif event.key == pygame.K_e:
  #     world.input_swap()

  #   elif event.key == pygame.K_q:
  #     world.input_mask_toggle(True)

  #   #solver
  #   elif event.key == pygame.K_m:
  #     world.input_solve()

  #   elif event.key == pygame.K_n:
  #     if world.solve_button:
  #       world.auto_solve = True

  #   #hints
  #   elif event.key == pygame.K_h:
  #     #if hints aren't continuous, and the button is allowed
  #     if world.hint_button and not world.hint_zoid and (world.hints != world.hint_limit):
  #       world.hints += 1
  #       world.hint_toggle = True

  # elif event.type == pygame.KEYUP:
  #   elif event.key == pygame.K_q:
  #     world.input_mask_toggle(False)
  #   #solver
  #   elif event.key == pygame.K_n:
  #     if world.solve_button:
  #       world.auto_solve = False
  #   #hints
  #   elif event.key == pygame.K_h:
  #     #if hints aren't continuous, and the button is allowed
  #     if world.hint_button and not world.hint_zoid and world.hint_release:
  #       world.hint_toggle = False

  # elif event.type == pygame.JOYBUTTONUP:
  #   if not world.two_player or event.joy == 1:
  #     if event.button == world.JOY_SELECT:
  #       world.input_mask_toggle(False)


def pauseStateHandler(world, event):
  if event == events.reqResume or event == events.reqPauseResume:
    world.input_pause()
  elif event == events.btnStartOn:
    world.input_pause()
  elif event == events.btnSelectOn or event == events.btnEscapeOn:
    world.state = states.Intro


def gameoverStateHandler(world, event):
  if event == events.btnSelectOn or event == events.btnEscapeOn:
    world.state = states.Intro

  elif event == events.btnStartOn:
    if world.episode_number != world.max_eps-1:
      world.input_continue()


HANDLERS = {
  states.Intro:        introscreen.handleInput,
  states.Perf:         perfscreen.handleInput,
  states.Aar:          aarStateHandler,
  states.Play:         playStateHandler,
  states.Pause:        pauseStateHandler,
  states.Gameover:     gameoverStateHandler,
  states.Config:       configscreen.handleInput,
  states.ConfigLvl1:   configscreen.handleInput,
  states.ConfigLvl2:   configscreen.handleInput,
  states.KeyRemapping: events.handleKeyRemapInput,
  states.BtnRemapping: events.handleBtnRemapInput,
}
