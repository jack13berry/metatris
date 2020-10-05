import pygame
import logger

def start( world ):
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      done = True

    #Universal controls

    #escape clause
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
      world.lc.stop()

    #screenshot clause
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
      world.do_screenshot()

    #eyetracker keys (number line)
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_5 and world.args.eyetracker:
      world.eye_conf_borders = not world.eye_conf_borders
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_6 and world.args.eyetracker:
      world.spotlight = not world.spotlight
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_7 and world.args.eyetracker:
      world.draw_samps = not world.draw_samps
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_8 and world.args.eyetracker:
      world.draw_avg = not world.draw_avg
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_9 and world.args.eyetracker:
      world.draw_err = not world.draw_err
    elif event.type == pygame.KEYDOWN and event.key == pygame.K_0 and world.args.eyetracker:
      world.draw_fixation = not world.draw_fixation

    #Intro state controls
    if world.state == world.STATE_INTRO:
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
          world.state += 1

      #joystick controls
      elif event.type == pygame.JOYBUTTONDOWN:
        if event.button == world.JOY_START :
          world.state += 1

    #After-Action Review controls
    elif world.state == world.STATE_AAR:
      if event.type == pygame.KEYUP:
        if event.key == pygame.K_DOWN or event.key == pygame.K_s:
          world.input_stop_drop()
        elif event.key == pygame.K_UP or event.key == pygame.K_w and world.inverted:
          world.input_stop_drop()
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
          world.input_trans_stop(-1)
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
          world.input_trans_stop(1)
        elif event.key == pygame.K_SPACE and world.AAR_worldpaced:
          world.input_end_AAR()
      elif event.type == pygame.JOYBUTTONDOWN:
        if event.button == world.JOY_START and world.AAR_worldpaced:
          world.input_end_AAR()
      elif event.type == pygame.JOYBUTTONUP:
        if not world.two_player or event.joy == 0:
          if event.button == world.JOY_DOWN:
            world.input_stop_drop()
          elif event.button == world.JOY_UP and world.inverted:
            world.input_stop_drop()
          elif event.button == world.JOY_LEFT:
            world.input_trans_stop(-1)
          elif event.button == world.JOY_RIGHT:
            world.input_trans_stop(1)

    #Gameplay state controls
    elif world.state == world.STATE_PLAY:
      if event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:
        dir = "PRESS" if event.type == pygame.KEYDOWN else "RELEASE"
        logger.game_event(world,  "KEYPRESS", dir, pygame.key.name(event.key))
      elif event.type == pygame.JOYBUTTONUP or event.type == pygame.JOYBUTTONDOWN:
        dir = "PRESS" if event.type == pygame.JOYBUTTONDOWN else "RELEASE"
        logger.game_event(world,  "KEYPRESS", dir, world.buttons[event.button] )

      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT or event.key == pygame.K_a:
          world.input_trans_left()
          world.das_held = -1
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
          world.input_trans_right()
          world.das_held = 1

        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
          if world.inverted:
            world.input_rotate_single()
          else:
            world.input_start_drop()
        elif event.key == pygame.K_UP or event.key == pygame.K_w:
          if world.inverted:
            world.input_start_drop()
          else:
            world.input_rotate_single()

        elif event.key == pygame.K_j:
          world.input_clockwise()
        elif event.key == pygame.K_k:
          world.input_counterclockwise()

        elif event.key == pygame.K_r:
          world.input_undo()

        elif event.key == pygame.K_SPACE:
          world.input_slam()
          world.input_place()

        elif event.key == pygame.K_e:
          world.input_swap()

        elif event.key == pygame.K_q:
          world.input_mask_toggle(True)

        #pause clause
        elif event.key == pygame.K_p:
          world.input_pause()

        #solver
        elif event.key == pygame.K_m:
          world.input_solve()

        elif event.key == pygame.K_n:
          if world.solve_button:
            world.auto_solve = True

        #hints
        elif event.key == pygame.K_h:
          #if hints aren't continuous, and the button is allowed
          if world.hint_button and not world.hint_zoid and (world.hints != world.hint_limit):
            world.hints += 1
            world.hint_toggle = True

      elif event.type == pygame.KEYUP:
        if event.key == pygame.K_DOWN or event.key == pygame.K_s:
          world.input_stop_drop()
        elif event.key == pygame.K_UP or event.key == pygame.K_w and world.inverted:
          world.input_stop_drop()
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
          world.input_trans_stop(-1)
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
          world.input_trans_stop(1)
        elif event.key == pygame.K_q:
          world.input_mask_toggle(False)

        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
          if world.inverted:
            if pygame.KMOD_SHIFT:
              world.add_latency("RL")
            else:
              world.add_latency("RR")

        elif event.key == pygame.K_UP or event.key == pygame.K_w:
          if not world.inverted:
            if pygame.KMOD_SHIFT:
              world.add_latency("RL")
            else:
              world.add_latency("RR")

        elif event.key == pygame.K_j:
          world.add_latency("RR")
        elif event.key == pygame.K_k:
          world.add_latency("RL")

        #solver
        elif event.key == pygame.K_n:
          if world.solve_button:
            world.auto_solve = False

        #hints
        elif event.key == pygame.K_h:
          #if hints aren't continuous, and the button is allowed
          if world.hint_button and not world.hint_zoid and world.hint_release:
            world.hint_toggle = False

      elif event.type == pygame.JOYAXISMOTION:
        if (not world.two_player or event.joy == 0) and world.joyaxis_enabled:

          pressed = ""
          released = ""

          #key is pressed
          if event.axis == 0:
            if round(event.value) == 1.0:
              pressed = "RIGHT"
              released = world.last_ud_pressed
              world.last_ud_pressed = ""
            elif round(event.value) == -1.0:
              pressed = "LEFT"
              released = world.last_ud_pressed
              world.last_ud_pressed = ""
            elif round(event.value) == 0.0:
              released = world.last_lr_pressed
              world.last_lr_pressed = ""
          elif event.axis == 1:
            if round(event.value) == 1.0:
              pressed = "DOWN"
              if not world.inverted:
                released = world.last_lr_pressed
                world.last_lr_pressed = ""
            elif round(event.value) == -1.0:
              pressed = "UP"
              if world.inverted:
                released = world.last_lr_pressed
                world.last_lr_pressed = ""
            elif round(event.value) == 0.0:
              released = world.last_ud_pressed
              world.last_ud_pressed = ""

          #resolve release event
          if released != "":
            if released == "DOWN":
              world.input_stop_drop()
            elif released == "UP" and world.inverted:
              world.input_stop_drop()
            elif released == "LEFT":
              world.input_trans_stop(-1)
            elif released == "RIGHT":
              world.input_trans_stop(1)

            logger.game_event(world,  "KEYPRESS", "RELEASE", released)
            #print("released", released)

          #resolve pressed
          if pressed != "":
            if pressed == "DOWN":
              world.last_ud_pressed = pressed
              if world.inverted:
                world.input_slam()
                world.input_undo()
              else:
                world.input_start_drop()
            elif pressed == "UP":
              world.last_ud_pressed = pressed
              if world.inverted:
                world.input_start_drop()
              else:
                world.input_slam()
                world.input_undo()
            elif pressed == "LEFT":
              world.last_lr_pressed = pressed
              world.input_trans_left()
              world.das_held = -1
            elif pressed == "RIGHT":
              world.last_lr_pressed = pressed
              world.input_trans_right()
              world.das_held = 1
            logger.game_event(world,  "KEYPRESS", "PRESS", pressed)
            #print("pressed", pressed)


      elif event.type == pygame.JOYBUTTONDOWN:
        #player 1
        if not world.two_player or event.joy == 0:
          if event.button == world.JOY_LEFT:
            world.input_trans_left()
            world.das_held = -1
          elif event.button == world.JOY_RIGHT:
            world.input_trans_right()
            world.das_held = 1
          elif event.button == world.JOY_DOWN:
            if world.inverted:
              world.input_slam()
              world.input_undo()
            else:
              world.input_start_drop()
          elif event.button == world.JOY_UP:
            if world.inverted:
              world.input_start_drop()
            else:
              world.input_slam()
              world.input_undo()

        #player 2
        if not world.two_player or event.joy == 1:
          if event.button == world.JOY_B:
            world.input_counterclockwise()
          elif event.button == world.JOY_A:
            world.input_clockwise()
          elif event.button == world.JOY_SELECT:
            world.input_mask_toggle(True)
            world.input_place()
            world.input_swap()

        #both players
        if event.button == world.JOY_START:
          if world.pause_enabled:
            world.input_pause()
          else:
            world.input_place()


      elif event.type == pygame.JOYBUTTONUP:
        if not world.two_player or event.joy == 0:
          if event.button == world.JOY_DOWN:
            world.input_stop_drop()
          elif event.button == world.JOY_UP and world.inverted:
            world.input_stop_drop()
          elif event.button == world.JOY_LEFT:
            world.input_trans_stop(-1)
          elif event.button == world.JOY_RIGHT:
            world.input_trans_stop(1)
          elif event.button == world.JOY_A:
            world.add_latency("RR")
          elif event.button == world.JOY_B:
            world.add_latency("RL")

        if not world.two_player or event.joy == 1:
          if event.button == world.JOY_SELECT:
            world.input_mask_toggle(False)

    elif world.state == world.STATE_PAUSE:
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_p:
          world.input_pause()
      if event.type == pygame.JOYBUTTONDOWN:
        if event.button == world.JOY_START:
          world.input_pause()


    #Gameover state controls
    elif world.state == world.STATE_GAMEOVER:
      if world.implement_gameover_fixcross != True or world.episode_number == world.max_eps - 1:
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_SPACE:
            world.input_continue()
        if event.type == pygame.JOYBUTTONDOWN:
          if event.button == world.JOY_START:
            world.input_continue()
      elif world.implement_gameover_fixcross == True and world.episode_number != world.max_eps - 1:
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_SPACE:
            logger.game_event(world, "GAMEOVER_FIXCROSS", "START")
            world.state = world.STATE_GAMEOVER_FIXATION
            #world.gameover_params['bg_color'] = world.mask_color
            world.validator = Validator( world.client, world.screen, reactor = reactor, escape = True, params = world.gameover_params)
            world.validator.start(world.fixcross)
            # world.input_continue()
        if event.type == pygame.JOYBUTTONDOWN:
          if event.button == world.JOY_START:
            logger.game_event(world, "GAMEOVER_FIXCROSS", "START")
            world.state = world.STATE_GAMEOVER_FIXATION
            #world.gameover_params['bg_color'] = world.mask_color
            world.validator = Validator( world.client, world.screen, reactor = reactor, escape = True, params = world.gameover_params)
            world.validator.start(world.fixcross)
            # world.input_continue()
