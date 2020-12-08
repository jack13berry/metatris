# Based on the work by John K. Lindstedt

import os, sys, copy, csv, random, time, json, datetime, platform, random

import pygame, numpy

from zoid import Zoid

from simulator import TetrisSimulator

import states, events, logger, cnf, drawer, inputhandler, timing

sep = os.path.sep

zoid_col_offset = {
  "O":[4],
  "L":[3,3,3,4],
  "J":[3,3,3,4],
  "S":[3,4],
  "Z":[3,4],
  "T":[3,3,3,4],
  "I":[3,5]
}

class World( object ):

  #initializes the game object with most needed resources at startup
  def __init__( self, args ):
    # Time Now
    self.moment = time.perf_counter()

    self.focused = "intro.play"

    ## Constants

    self.roll_avg = []
    self.metascore = 0
    self.metaticks = 0

    self.LOG_VERSION = 3.1

    #token names for latency logging
    self.evt_token_names = [
      "kr-rt-cc", #RL
      "kr-rt-cw", #RR
      "kp-tr-l",  #TL
      "kp-tr-r",  #TR
      "kp-dwn",   #DN
      "sy-rt-cc", #SRL
      "sy-rt-cw", #SRR
      "sy-tr-l",  #STL
      "sy-tr-r",  #STR
      "sy-dn-u",  #UD
      "sy-dn-s"   #SD
    ]

    # Get time
    self.startTime = self.moment
    self.curFrm = 0

    # Collect argument values
    self.args = args

    self.session = self.args.logfile

    self.config = {}
    self.configs_to_write = []
    self.rawConfDicts = {}
    for configName in ["default", "user"]:
      cnf.read(self, configName)

    cnf.setAll(self)
    events.init(self)

    self.timing = getattr(timing, self.timingSetup)
    self.levelTimes = self.timing.levels
    self.dasWaitTime = self.timing.dasWaitTime
    self.dasRepeatTime = self.timing.dasRepeatTime

    ## Input init

    #...# provide a function for setting game controls here.
    pygame.init()
    # print("pygame init[92]: %s" % pygame.joystick.get_init())
    # print("Controller Count: %d" % pygame.joystick.get_count())

    self.lastAxisDown = None
    self.contobj = None
    contid = pygame.joystick.get_count()
    self.numberOfControllers = contid
    while contid > 0:
      contid -= 1
      contobj = pygame.joystick.Joystick(contid)
      setattr(self, ("joystick%d" % contid), contobj)

      print("Recognized Controller %d:")
      print("            id: '%s'" % contobj.get_instance_id())
      print("          guid: '%s'" % contobj.get_guid())
      print("          name: '%s'" % contobj.get_name())
      print("    powerlevel: '%s'" % contobj.get_power_level())
      print("       numaxes: '%s'" % contobj.get_numaxes())
      print("      numballs: '%s'" % contobj.get_numballs())
      print("    numbuttons: '%s'" % contobj.get_numbuttons())
      print("       numhats: '%s'" % contobj.get_numhats())

      print("\n")
      print("           pre: '%s'" % (contobj.get_init()))
      contobj.init()
      print("          post: '%s'" % (contobj.get_init()))

    #initialize joystick
    # pygame.joystick.init()
    # if pygame.joystick.get_count() > 0:
    #   self.joystick1 = pygame.joystick.Joystick(0)
    #   self.joystick1.init()
    # if pygame.joystick.get_count() > 1:
    #   self.joystick2 = pygame.joystick.Joystick(1)
    #   self.joystick2.init()

    ## Drawing init
    # modifier for command keys
    self.modifier = pygame.KMOD_CTRL
    if platform.system() == 'Darwin':
      self.modifier = pygame.KMOD_META
    #joystick constants for original controllers
    if self.joystick_type == "NES_RETRO-USB":
      #Removed by CJB 2019.12.07
      #self.JOY_UP = 7
      #self.JOY_DOWN = 5
      #self.JOY_LEFT = 4
      #self.JOY_RIGHT = 6
      #self.JOY_B = 0
      #self.JOY_A = 1
      #self.JOY_START = 3
      #self.JOY_SELECT = 2
      #self.joyaxis_enabled = False

      #self.buttons = ["B", "A", "SELECT", "START", "LEFT", "DOWN", "RIGHT", "UP"]
      self.JOY_UP = 7
      self.JOY_DOWN = 7
      self.JOY_LEFT = 7
      self.JOY_RIGHT = 7
      self.JOY_B = 0
      self.JOY_A = 1
      self.JOY_START = 9
      self.JOY_SELECT = 8
      self.last_lr_pressed = ""
      self.last_ud_pressed = ""
      self.joyaxis_enabled = True

      self.buttons = ["B", "A", "N/A", "N/A", "N/A", "N/A", "N/A", "JOY", "SELECT", "START"]

    elif self.joystick_type == "NES_TOMEE-CONVERTED":
      #joystick constants for TOMEE NES Retro Classic Controller USB, 2009. X007SJRFP
      self.JOY_UP = 7
      self.JOY_DOWN = 7
      self.JOY_LEFT = 7
      self.JOY_RIGHT = 7
      self.JOY_B = 0
      self.JOY_A = 1
      self.JOY_START = 9
      self.JOY_SELECT = 8
      self.last_lr_pressed = ""
      self.last_ud_pressed = ""
      self.joyaxis_enabled = True

      self.buttons = ["B", "A", "N/A", "N/A", "N/A", "N/A", "N/A", "JOY", "SELECT", "START"]


    logger.init(self)

    #Start graphing up here on the open file
    #self.start_animate(self.scorefile_path + ".incomplete")

    cnf.write(self)


    ## Derivative variable setting after settling game definitions
    self.ticks_per_frame = int(round(self.tps / self.fps))

    self.zoids = []
    if self.tetris_zoids:
      self.zoids += Zoid.set_tetris
    if self.pentix_zoids:
      self.zoids += Zoid.set_pentix
    if self.tiny_zoids:
      self.zoids += Zoid.set_tiny

    ## Gameplay variables
    self.state = states.Intro

    #universal frame timer
    self.timer = 0

    #pygame.key.set_repeat( self.das_delay, self.das_repeat )
    self.das_timer = 0
    self.das_held = 0

    # Scoring and leveling
    self.level = self.starting_level
    self.lines_cleared = 0
    self.lines_to_clear = []

    self.score = 0
    self.newscore = 0
    self.high_score = 0
    self.prev_tetris = 0

    self.drop_score = 0

    self.game_number = 0
    self.episode_number = 0

    self.seeds_used = []

    self.game_scores = []

    self.gameStartTime = self.moment

    # Starting board
    self.initialize_board()

    # Determine Fixed or Random Seeds
    self.fixed_seeds = True if 'random_seeds' in self.config else False

    # seven-bag of zoids
    self.seven_bag = random.sample( range( 0, len(self.zoids) ), len(self.zoids) )

    # Zoid variables -- DUMMIES, REAL ZOID SEQUENCE BEGINS IN SETUP.
    # This is only for the simulator initialization later in the __init__
    self.zoidrand = random.Random()
    self.seed_shuffler = random.Random()
    self.seed_shuffler.seed(self.shuffle_seed)

    # Set seed order for use later-- lasts beyond config resets!
      ## WARNING: MUST USE SAME LIST OF SEEDS, ELSE EXPLOSION.
    self.seed_order = range(0,len(self.random_seeds))
    if self.permute_seeds:
      self.seed_order = self.seed_shuffler.sample(self.seed_order, len(self.seed_order))

    self.curr_zoid = []
    self.next_zoid = []
    self.curr_zoid = Zoid( self.zoids[self.get_next_zoid()], self )
    self.next_zoid = Zoid( self.zoids[self.get_next_zoid()], self )

    self.zoid_buff = []

    self.danger_mode = False

    self.needs_new_zoid = False

    self.are_counter = 0
    self.lc_counter = 0

    # current interval (gravity)
    self.interval = [self.intervals[self.level], self.drop_interval] #[levelintvl, dropintvl]
    self.interval_toggle = 0

    # for mask mode
    self.mask_toggle = False

    # for kept zoid mode
    self.kept_zoid = None
    self.swapped = False

    # for zoid slamming
    self.zoid_slammed = False

    # for auto-solving
    self.solved = False
    self.solved_col = None
    self.solved_rot = None
    self.solved_row = None

    self.hint_toggle = self.hint_zoid
    self.hints = 0

    # for grace period
    self.grace_timer = 0

    #for After-Action Review
    self.AAR_timer = 0
    self.AAR_conflicts = 0

    #controller agreement
    self.agree = None

    # Gets screen information
    self.screeninfo = pygame.display.Info()


    # Remove modes that are double the width of another mode
    # which indicates a dual monitor resolution
    modes = pygame.display.list_modes()
    # print(modes)
    for mode in modes:
      tmp = mode[0] / 2
      for m in modes:
        if tmp == m[0]:
          modes.remove( mode )
          break

    # Initialize image graphics

    self.logo = pygame.image.load( "media" + sep + "logo.png" )
    self.logo = pygame.transform.scale(self.logo, (400, 300))
    self.gclogo = pygame.image.load( "media" + sep + "gclogo.png" )
    self.gclogo = pygame.transform.scale(self.gclogo, (368, 72))

    self.scorebarsrc = pygame.image.load( "media" + sep + "scorebar.png" )

    gameicon = pygame.image.load( "media" + sep + "metatris.ico" )
    pygame.display.set_icon(gameicon)


    drawer.setupOSWindow(self)
    drawer.setupColors(self)

    # Fonts (intro: 36; scores: 48; end: 68; pause: 102)
    # ratios divided by default HEIGHT: .04, .053, .075, .113
    fontPath = sep.join(["media", "fonts", "Montserrat", "Montserrat-Medium.ttf"])
    fontBPath = sep.join(["media", "fonts", "Montserrat", "Montserrat-Black.ttf"])
    self.intro_font = pygame.font.Font( fontPath, int(.04 * self.worldsurf_rect.height) )
    self.instantScoreFont = pygame.font.Font( fontPath, int(.040 * self.worldsurf_rect.height) )
    self.inBoardScoreFont = pygame.font.Font( fontBPath, int(.10 * self.worldsurf_rect.height) )
    self.scores_font = pygame.font.Font( fontPath, int(.033 * self.worldsurf_rect.height) )
    self.end_font = pygame.font.Font( fontPath, int(.055 * self.worldsurf_rect.height) )
    self.pause_font = pygame.font.Font( fontPath, int(.083 * self.worldsurf_rect.height) )

    drawer.setupLayout(self)

    ## Sound
    self.setupSounds()

    ## Board statistics
    self.print_stats = self.args.boardstats
    #self.boardstats = TetrisBoardStats( self.board, self.curr_zoid.type, self.next_zoid.type )

    self.sim = TetrisSimulator(
      board = self.board,               curr = self.curr_zoid.type,
      next = self.next_zoid.type,       controller = self.get_controller(),
      overhangs = self.sim_overhangs,   force_legal = self.sim_force_legal
    )
    self.update_stats()

    self.features_set = sorted(self.features.keys())
    self.fixed_header = self.fixed_header + self.features_set

    #behavior tracking: latencies and sequences
    self.evt_sequence = []
    self.epStartTime = self.moment

    self.drop_lat = 0
    self.initial_lat = 0
    self.latencies = [0]

    self.rots = 0
    self.trans = 0
    self.min_rots = 0
    self.min_trans = 0
    self.u_drops = 0
    self.s_drops = 0

    self.tetrises_game = 0
    self.tetrises_level = 0
    self.reset_lvl_tetrises = False

    self.avg_latency = 0
    self.prop_drop = 0.0

    if self.fixed_log:
      logger.universal_header(self)

    logger.game_event(self, "LOG_VERSION", self.LOG_VERSION)
    logger.game_event(self,  "BOARD_INIT" )

    #Initialization complete! Log the history file and get started:
    logger.history(self)


  def setup( self ):
    self.initialize_board()

    #increment game number
    self.game_number += 1

    if self.fixed_seeds:
      # print(self.seed_order)
      # print(self.random_seeds)
      seed = self.random_seeds[self.seed_order[(self.game_number-1)%len(self.random_seeds)]]
      # print(seed)
    else:
      seed = int(self.moment * 10000000000000.0)

    self.zoidrand = random.Random()
    self.zoidrand.seed(seed)
    self.seeds_used += [str(seed)]
    logger.game_event(self, "SEED", data1 = self.game_number, data2 = seed)

    #new bag and next zoids - INACCURATE. BAD.
    if self.seven_bag_switch:
       self.seven_bag = self.zoidrand.sample( range( 0, len(self.zoids) ), len(self.zoids) )

    self.curr_zoid = None
    self.next_zoid = None

    self.curr_zoid = Zoid( self.zoids[self.get_next_zoid()], self )
    self.next_zoid = Zoid( self.zoids[self.get_next_zoid()], self )

    # for auto-solving
    self.solved = False
    self.solved_col = None
    self.solved_rot = None
    self.solved_row = None

    # for hints
    self.hint_toggle = self.hint_zoid
    self.hints = 0

    #for After-Action Review
    self.AAR_timer = 0
    self.AAR_conflicts = 0

    #controller agreement
    self.agree = None


    self.zoid_buff = [self.curr_zoid.type]

    self.kept_zoid = None
    self.swapped = False

    #episode behavior information
    self.evt_sequence = []
    self.epStartTime = self.moment

    self.drop_lat = 0
    self.initial_lat = 0
    self.latencies = [0]

    self.rots = 0
    self.trans = 0
    self.min_rots = 0
    self.min_trans = 0
    self.u_drops = 0
    self.s_drops = 0

    self.tetrises_game = 0
    self.tetrises_level = 0
    self.reset_lvl_tetrises = False

    self.avg_latency = 0
    self.prop_drop = 0.0

    #reset score
    self.level = self.starting_level
    self.lines_cleared = 0
    self.score = 0
    self.newscore = 0
    self.metascore = 0
    self.metaticks = 0
    self.prev_tetris = 0
    self.drop_score = 0

    self.interval = [self.intervals[self.level], self.drop_interval]
    self.interval_toggle = 0

    #update the board stats object with reset values
    self.sim.set_board( self.board )
    self.sim.set_zoids( self.curr_zoid.type, self.next_zoid.type )
    self.update_stats()

    #reset ticks
    self.timer = 0
    self.das_timer = 0
    self.das_held = 0

    self.isDropping = False
    self.currentDasKey = 0
    self.dasLastTime = 0
    self.dasInitTime = 0
    self.pieceDownLastTime = self.moment
    self.pieceDropLastTime = self.moment
    self.lastNewPieceTime = 0
    # self.setTimeIntervals()

    self.needs_new_zoid = False
    self.are_counter = 0
    self.lc_counter = 0

    self.gameover_anim_tick = 0

    self.episode_number = 0

    self.gameStartTime = self.moment

    #restart the normal music
    pygame.mixer.music.load( "media" + sep + "music" + sep + self.song )
    pygame.mixer.music.play( -1 )
    self.danger_mode = False

    logger.game_event(self,  "GAME", "BEGIN", self.game_number )
    # print("Game starts at", self.moment, "with wait time", self.pieceDownInterval)


  def setupSounds(self):
    #pygame.mixer.music.load( "media" + sep + "title.mp3" )
    pygame.mixer.set_num_channels( 24 )
    pygame.mixer.music.set_volume( self.music_vol )
    # pygame.mixer.music.play( -1 )

    # Sound effects
    self.sounds = {}
    for sound in ['rotate','trans','clear1','clear4','crash','levelup',
      'thud','pause','slam','keep','solved1', 'uiaction']:
      self.sounds[sound] = pygame.mixer.Sound(
        sep.join(['media', 'sounds', 'default', sound]) + ".wav"
      )
      self.sounds[sound].set_volume( self.sfx_vol )

    # self.soundrand = random.Random()
    # self.soundrand.seed(self.moment)


  def updateVolumes(self):
    # print("Volume was: ", pygame.mixer.music.get_volume(), self.sfx_vol)
    pygame.mixer.music.set_volume( self.music_vol )
    # print("Volume is : ", pygame.mixer.music.get_volume(), self.sfx_vol)
    for s in self.sounds:
      # print("SFX was: ", self.sounds[s].get_volume(), self.sfx_vol )
      self.sounds[s].set_volume( self.sfx_vol )
      # print("SFX is : ", self.sounds[s].get_volume(), self.sfx_vol )


  def get_controller( self ):
    f = open("controllers" + sep + self.controller + ".control")
    lines = f.readlines()
    f.close()
    return json.loads(lines[0].strip())


  def min_path (self, zoid, col, rot):
    #calculate rotations
    rots = 0
    if int(rot) != 0:
      rots = 2 if rot == 2 else 1

    #calculate translations
    trans = abs(zoid_col_offset[zoid][int(rot)] - int(col))

    return rots, trans


  #initializes a board based on arguments
  def initialize_board( self ):
    f = open("boards" + sep + self.boardname + ".board")
    lines = ""
    for l in f.readlines():
      lines += l.strip()
    f.close()
    fileboard = json.loads(lines.strip())

    if len(fileboard) != self.game_ht or len(fileboard[0]) != self.game_wd:
      print("Error: Read board from file with mismatched dimensions. Loading empty.")
      self.board = []
      self.new_board = None
      for r in range( 0, self.game_ht ):
        row = []
        for c in range( 0, self.game_wd ):
          row.append( 0 )
        self.board.append( row )
    else:
      self.board = fileboard
      self.new_board = None


  #initializes the feedback messages for printing to the screen.
  def initialize_feedback( self ):
    #"height",
    #"avgheight",
    #"pits",
    #"roughness",
    #"ridge_len",
    #"ridge_len_sqr",
    #"tetris_available",
    #"tetris_progress",
    #"filled_rows_covered",
    #"tetrises_covered",
    #"good_pos_curr",
    #"good_pos_next",
    #"good_pos_any",
    self.height_left = ()


  #pauses game
  def input_pause( self ):
    if self.pause_enabled:
      if self.state == states.Play:
        self.state = states.Pause
        logger.game_event(self, "PAUSED")
        pygame.mixer.music.pause()
      elif self.state == states.Pause:
        self.state = states.Play
        logger.game_event(self, "UNPAUSED")
        pygame.mixer.music.unpause()
      self.sounds["pause"].play()


  #moves zoid left
  def input_trans_left( self ):
    self.add_latency("TL", kp = True)
    if self.timer >= 0:
      self.curr_zoid.left()


  #moves zoid right
  def input_trans_right( self ):
    self.add_latency("TR", kp = True)
    if self.timer >= 0:
      self.curr_zoid.right()


  def input_trans_stop( self, direction ):
    if direction == self.das_held or not self.das_reversible:
      self.das_timer = 0
      self.das_held = 0
    if direction == -1:
      self.add_latency("TL")
    elif direction == 1:
      self.add_latency("TR")


  #initiates a user drop
  def input_start_drop( self ):
    self.add_latency("DN", kp = True, drop = True)
    self.interval_toggle = 1


  #terminates a user drop
  def input_stop_drop( self ):
    self.add_latency("DN")
    self.interval_toggle = 0


  def input_clockwise( self ):
    self.add_latency("RR", kp = True)
    self.curr_zoid.rotate( 1 )


  def input_counterclockwise( self ):
    self.add_latency("RL", kp = True)
    self.curr_zoid.rotate( -1 )


  #rotates zoid clockwise, or counterclockwise if shift is held (for single-button rotation)
  def input_rotate_single( self ):
    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
      self.add_latency("RL", kp = True)
      self.curr_zoid.rotate( -1 )
    else:
      self.add_latency("RR", kp = True)
      self.curr_zoid.rotate( 1 )


  def input_swap( self ):
    if self.keep_zoid and self.lc_counter < 0 and self.are_counter < 0:
      self.swap_kept_zoid()


  def input_undo( self ):
    if self.lc_counter < 0 and self.are_counter < 0 and self.undo:
      self.curr_zoid.init_pos()
      logger.game_event(self, "ZOID","UNDO")


  def input_place( self ):
    if self.lc_counter < 0 and self.are_counter < 0:
      if not self.gravity:
        self.curr_zoid.place()


  def input_slam( self ):
    if self.lc_counter < 0 and self.are_counter < 0:
      if self.zoid_slam:
        self.curr_zoid.to_bottom(move=True)
        self.zoid_slammed = True
        self.skip_timer()

  def input_mask_toggle( self, on ):
    if self.next_mask and self.lc_counter < 0 and self.are_counter < 0:
      self.mask_toggle = on
      logger.game_event(self, "MASK_TOGGLE", on)


  def input_continue( self ):
    if self.continues != 0 and self.gameover_anim_tick > self.gameover_tick_max:
      self.state = states.Setup


  def input_solve( self ):
    if self.solve_button and self.are_counter < 0 and self.lc_counter < 0:
      self.solve()


  def input_end_AAR( self ):
    self.state = states.Play
    self.AAR_timer = 0
    logger.game_event(self, "AAR", "END", "SELF")


  #creates a screenshot of the current game.
  def do_screenshot( self ):
    if not os.path.exists( self.logname + sep + "screenshots" ):
      os.mkdir( self.logname + sep + 'screenshots' )
    d = datetime.datetime.now().timetuple()
    filename = self.logname + sep + "screenshots" + sep + "Gm" + str(self.game_number) + "_Ep" + str(self.episode_number) + "_%d-%d-%d_%d-%d-%d.jpeg" % ( d[0], d[1], d[2], d[3], d[4], d[5] )
    pygame.image.save( self.worldsurf, filename )
    logger.game_event(self, "SCREENSHOT")

  def skip_timer( self ):
    if self.level < len(self.intervals):
      self.timer = self.intervals[self.level]
    else:
      self.timer = self.intervals[-1]

  def add_latency( self, token, kp = False, drop = False ):
    lat = int(1000 * (self.moment - self.epStartTime))
    self.evt_sequence.append([token,lat])
    if self.initial_lat == 0:
      self.initial_lat = lat
    if drop and self.drop_lat == 0:
      self.drop_lat = lat
    if kp:
      self.latencies.append(lat)


  # For debugging purposes; produces random player behavior
  def random_behavior( self ):
    if self.timer % 7 == 0:
      self.curr_zoid.down( self.interval_toggle )
    if self.timer % 35 == 0:
      self.curr_zoid.rotate( random.randint( -1, 1 ) )
    if self.timer % 25 == 0:
      self.curr_zoid.translate( random.randint( -1, 1 ) )


  #Checks if the top 5 lines are occupied (engage in danger mode warning music)
  def check_top( self , board ):
    topfull = False
    #top 5 lines occupied?
    for i in board[0:5]:
      if i != [0] * self.game_wd:
        topfull = True
    #if we've just changed to danger mode...
    if topfull and not self.danger_mode:
      self.danger_mode = True
      # pygame.mixer.music.stop()
      # pygame.mixer.music.load( "media" + sep + "%s_fast.wav" % self.song )
      # pygame.mixer.music.play( -1 )
      # logger.game_event(self,  "DANGER", "BEGIN" )
    #if we've cleared out of danger mode...
    elif not topfull and self.danger_mode:
      self.danger_mode = False
      # pygame.mixer.music.stop()
      # pygame.mixer.music.load( "media" + sep + "%s.wav" % self.song )
      # pygame.mixer.music.play( -1 )
      # logger.game_event(self,  "DANGER", "END" )


  #Stamps the current zoid onto the board representation.
  def place_zoid( self ):
    do_place = True
    if self.n_back:
      if len(self.zoid_buff) <= self.nback_n:
        do_place = False
      elif self.zoid_buff[-1] != self.zoid_buff[-(1+self.nback_n)]:
        do_place = False
    if self.ax_cpt:
      if len(self.zoid_buff) < 2:
        do_place = True
      if self.zoid_buff[-1] == self.ax_target and self.zoid_buff[-2] == self.ax_cue:
        do_place = False

    if do_place:
      x = self.curr_zoid.col
      y = self.game_ht - self.curr_zoid.row
      ix = x
      iy = y
      for i in self.curr_zoid.get_shape():
        for j in i:
          if j != 0 and iy >= 0:
            self.board[iy][ix] = j
          ix += 1
        ix = x
        iy += 1

      self.score += self.drop_score
      self.drop_score = 0

      if self.curr_zoid.overboard( self.board ):
        self.game_over()

    if self.zoid_slammed:
      self.sounds['slam'].play( 0 )
      logger.game_event(self, "ZOID", "SLAMMED")
      self.zoid_slammed = False
    elif self.solved and not (self.hint_zoid or self.hint_button):
      self.sounds['solved1'].play( 0 )
      logger.game_event(self, "ZOID", "SOLVED")

    else:
      self.sounds['thud'].play( 0 )

    logger.game_event(self,  "PLACED", self.curr_zoid.type, [self.curr_zoid.rot, self.curr_zoid.get_col(), self.curr_zoid.get_row()])


  def solve( self , move = True):
    self.curr_zoid
    c = self.sim.predict(self.board, self.curr_zoid.type)
    self.sim.set_zoids(self.curr_zoid.type, self.next_zoid.type)
    self.solved_col, self.solved_rot, self.solved_row = self.curr_zoid.place_pos(c[0],c[1],c[2]+1, move = move)
    if move:
      self.skip_timer()
    self.solved = True


  def swap_kept_zoid( self ):
    if not self.needs_new_zoid and not self.swapped:
      if self.kept_zoid == None:
        self.kept_zoid = self.curr_zoid
        self.new_zoid()
        logger.game_event(self,  "ZOID_SWAP", self.kept_zoid.type)
      else:
        temp = self.curr_zoid
        self.curr_zoid = self.kept_zoid
        self.kept_zoid = temp
        self.curr_zoid.init_pos()
        logger.game_event(self,  "ZOID_SWAP", self.kept_zoid.type, self.curr_zoid.type  )

      self.curr_zoid.refresh_floor()
      self.swapped = True
      self.drop_score = 0
      self.sounds['keep'].play( 0 )

  # 7-bag randomization without doubles
  def get_seven_bag( self ):
    if len( self.seven_bag ) == 0:
      logger.game_event(self,  "7-BAG", "refresh" )
      self.seven_bag = self.zoidrand.sample( range( 0, len(self.zoids) ), len(self.zoids) )
      if self.zoids[self.seven_bag[-1]] == self.curr_zoid.type:
        self.seven_bag.reverse()
    return self.seven_bag.pop()
  ###

  #randomized, but with a slight same-piece failsafe
  def get_random_zoid( self ):

    #generate random, but with dummy value 7? [in the specs, but what good is it?]
    z_id = self.zoidrand.randint( 0, len(self.zoids) )

    #then repeat/dummy check, and reroll *once*
    if not self.curr_zoid or z_id == len(self.zoids):
      return self.zoidrand.randint( 0, len(self.zoids)-1 )
    elif self.zoids[z_id] == self.curr_zoid.type and self.state != states.Setup:
      return self.zoidrand.randint( 0, len(self.zoids)-1 )

    return z_id


  #get a new zoid for the piece queue
  def get_next_zoid( self ):
    zoid = None
    if self.seven_bag_switch:
      zoid = self.get_seven_bag()
    else:
      zoid = self.get_random_zoid()
    return zoid


  #Rotate next-zoid into curr-zoid and get a new zoid.
  def new_zoid( self ):
    self.curr_zoid = self.next_zoid
    self.curr_zoid.refresh_floor()

    self.zoid_buff.append(self.curr_zoid.type)

    self.next_zoid = Zoid( self.zoids[self.get_next_zoid()], self )

    self.sim.set_zoids( self.curr_zoid.type, self.next_zoid.type )
    #self.update_stats()

    if self.curr_zoid.collide( self.curr_zoid.col, self.curr_zoid.row, self.curr_zoid.rot, self.board ):
      self.game_over()

    logger.game_event(self,  "ZOID", "NEW", self.curr_zoid.type )


  #Perform line clearing duties and award points
  def clear_lines( self ):
    self.lines_to_clear = []
    #find all filled lines
    for i in range( 0, len( self.board ) ):
      filled = True
      for j in self.board[i]:
        filled = filled and j != 0
      if filled:
        self.lines_to_clear.append( i )
    #clear them
    self.lines_to_clear.reverse()
    numcleared = len( self.lines_to_clear )

    if numcleared > 0:

      self.new_board = copy.copy( self.board )
      for i in self.lines_to_clear:
        del( self.new_board[i] )
      for i in range( 0, numcleared ):
        self.new_board.insert( 0, [0] * self.game_wd )
        self.check_top( self.new_board )

      if numcleared == 1:
        self.score += self.scoring[0] * ( self.level + 1 )
        self.sounds['clear1'].play( 0 )
      elif numcleared == 2:
        self.score += self.scoring[1] * ( self.level + 1 )
        self.sounds['clear1'].play( 0 )
      elif numcleared == 3:
        self.score += self.scoring[2] * ( self.level + 1 )
        self.sounds['clear1'].play( 0 )
      elif numcleared == 4:
        self.score += self.scoring[3] * ( self.level + 1 )
        self.tetris_flash_tick = 10
        self.sounds['clear4'].play( 0 )
        self.tetrises_game += 1
        self.tetrises_level += 1
      elif numcleared == 5:
        self.score += self.scoring[4] * ( self.level + 1 )
        self.tetris_flash_tick = 15
        self.sounds['clear1'].play( 0 )
        self.sounds['clear4'].play( 0 )

      self.lines_cleared += numcleared

      self.check_lvlup()

      self.lc_counter = self.lc_delay

      self.sim.set_board( self.new_board )

      if numcleared != 0:
        logger.game_event(self, "Clear", numcleared)

    else:
      self.check_top( self.board )
      self.sim.set_board( self.board )

    if self.score > self.high_score:
      self.high_score = self.score


  #check to see if player leveled up from line clears
  def check_lvlup( self ):
    prev = self.level
    self.level = int( self.lines_cleared / self.lines_per_lvl ) + self.starting_level

    if self.level != prev:
      self.reset_lvl_tetrises = True
      self.sounds['levelup'].play( 0 )
      logger.game_event(self,  "LEVELUP", self.level)

    if self.level < len( self.intervals ):
      self.interval[0] = self.intervals[self.level]


  def update_evts( self ):
    if self.u_drops + self.s_drops != 0:
      self.prop_drop = self.u_drops * 1.0 / ((self.u_drops + self.s_drops) * 1.0)
    else:
      self.prop_drop = 0.0

    latency_diffs = numpy.diff(self.latencies)
    if len(latency_diffs) != 0:
      self.avg_latency = sum(latency_diffs) / (len(latency_diffs) * 1.0)
    else:
      self.avg_latency = 0

    self.min_rots, self.min_trans = self.min_path(self.curr_zoid.type, self.curr_zoid.get_col(), self.curr_zoid.rot)


  def reset_evts( self ):
    self.evt_sequence = []
    self.epStartTime = self.moment

    if self.reset_lvl_tetrises:
      self.tetrises_level = 0
      self.reset_lvl_tetrises = False
    self.drop_lat = 0
    self.initial_lat = 0
    self.latencies = [0]

    self.rots = 0
    self.trans = 0
    self.min_rots = 0
    self.min_trans = 0
    self.u_drops = 0
    self.s_drops = 0


  #check to see if an after-action review is needed
  def check_AAR( self ):
    AAR_agree = self.controller_agree()
    if not AAR_agree:
      self.AAR_conflicts += 1
    if self.AAR_conflicts == self.AAR_max_conflicts:
      logger.game_event(self, "AAR", "BEGIN")
      self.AAR_conflicts = 0
      self.state = states.Aar
      self.AAR_timer = self.AAR_dur
      if self.AAR_dur_scaling:
        self.AAR_timer = self.interval[0]


  def controller_agree( self ):
    return self.solved_rot == self.curr_zoid.rot and self.solved_col == self.curr_zoid.col and self.solved_row == self.curr_zoid.row


  def endEpisode( self ):
    if self.solved:
      self.agree = self.controller_agree()
      logger.game_event(self,  "CONTROLLER", "AGREE?", self.agree)
    if self.AAR and self.state != states.Gameover:
      self.check_AAR()
    self.place_zoid()
    self.clear_lines()
    self.sim.set_board( self.board)
    self.needs_new_zoid = True
    self.swapped = False

    self.update_evts()

    logger.episode(self)

    if self.hint_toggle: #if the hint toggle is still being held
      if self.hint_limit >= 0 or not self.hint_release:
        self.hint_toggle = False

    logger.game_event(self,  "EPISODE", "END", self.episode_number )
    if self.episode_number == self.max_eps - 1:
      self.game_over()
      logger.game_event(self,  "EPISODE_LIMIT_REACHED" )


  #game over detected, change state
  def game_over( self ):
    logger.game_event(self,  "GAME", "END", self.game_number )
    logger.gameresults(self, complete = True)
    self.continues -= 1
    self.state = states.Gameover
    if self.episode_number == self.max_eps - 1:
      self.sounds['pause'].play()
    else:
      self.sounds['crash'].play()
    pygame.mixer.music.stop()


  #push piece down based on timer
  def down_tick( self ):
    if self.gravity or self.interval_toggle == 1:
      if self.timer >= self.interval[self.interval_toggle]:
        self.timer = 0
        self.curr_zoid.down( self.interval_toggle )


  #def das_tick
  def das_tick( self ):
    if not self.das_chargeable:
      self.das_timer += 1
    if self.das_timer >= self.das_delay and (self.das_timer - self.das_delay) % self.das_repeat == 0:
      if self.das_held == -1:
        self.curr_zoid.left()
      elif self.das_held == 1:
        self.curr_zoid.right()


  #update the on-line board statistics
  def update_stats( self ):
    self.features = self.sim.report_board_features()
    if self.print_stats:
      print(self.features)

  def update_stats_move( self, col, rot, row):
    self.features = self.sim.report_move_features(col, rot, row, printout = self.print_stats)
    if self.print_stats:
      print(self.features)


  def quit( self ):
    if self.game_number > 0 and not self.state == states.Gameover:
      logger.gameresults(self, complete=False)
    self.criterion_score()
    logger.close_files(self)
    # reactor.stop()
    self.running = False


  def criterion_score( self ):
    x = self.game_scores
    x.sort()
    if len(x) > 4:
      x = x[-4:]
    if len(x) > 0:
      print("\nCriterion score: " + str(sum(x) / len(x)) + "\n")
      print("High score: " + str(x[-1]) + "\n")
      print("Meta score: " + "{:0.3f}".format(self.metascore) + "\n")


  def error_handler(error):
    self.running = False


  def process_game_logic( self ):
    #lc counter and are counter start at zero and automatically count backward
    if self.state == states.Play:
      #for i in range( 0, self.ticks_per_frame ):
      self.lc_counter -= 1
      self.are_counter -= 1

      if not self.solved:
        if self.auto_solve:
          self.solve()
        else:
          self.solve(move = False)

      #enable "charging" of translation repeats regardless of zoid release
      if self.das_held != 0 and self.das_chargeable:
        self.das_timer += 1

      #if lineclear animation counter is positive, animate to clear lines in 20 frames.
      if self.lc_counter > 0:
        c = int( float(self.lc_delay - self.lc_counter) / float(self.lc_delay) * float(self.game_wd) / 2)
        for r in self.lines_to_clear:
          self.board[r][c] = 0
          self.board[r][-(c+1)] = 0

      #otherwise, enter delay period until equilibrium
      elif self.lc_counter < 1:
        if self.lc_counter == 0:
          self.board = self.new_board
          self.new_board = None
        if self.are_counter < 1:
          if self.are_counter == 0:
            self.solved = False
            self.new_zoid()
            self.needs_new_zoid = False
            self.episode_number += 1
            logger.game_event(self,  "EPISODE", "BEGIN", self.episode_number )
            self.reset_evts()
            if self.ep_screenshots:
              self.do_screenshot()
          #if ARE counter is currently out of service
          elif self.are_counter < 0:
            #and a new zoid is needed
            if self.needs_new_zoid:
              self.are_counter = self.are_delay
            self.timer += 1
            self.down_tick()

            if self.das_held != 0:
              self.das_tick()

      #else:
        """
        self.timer -= 1
        delay = -1 * self.are_delay
        if self.line_cleared:
          delay = -1 * ( self.are_delay + self.lc_delay )
        if self.timer < delay:
          self.timer = 0
          self.line_cleared = False
        """

    elif self.state == states.Setup:
       self.setup()
       self.state += 1

    elif self.state == states.Aar:
      if self.AAR_timer == 0:
        self.state = states.Play
        logger.game_event(self, "AAR", "END")
      self.AAR_timer -= 1


  def logControllerStates(self, event):
    evtname = pygame.event.event_name(event.type)
    self.eventLogCounter += 1
    lc = self.eventLogCounter
    if evtname.lower() == "joyaxismotion":
      print("%d: axisMotion <%s|%s>"  % (lc, event.axis, event.value))

    elif evtname.lower() == "joyballmotion":
      print("%d: ballMotion <%s|%s>"  % (lc, event.ball, event.rel))

    elif evtname.lower() == "joyhatmotion":
      print("%d: hatMotion <%s|%s>"   % (lc, event.hat, event.value))

    elif evtname.lower() == "joybuttondown":
      print("%d: btnPress <%s>"    % (lc, event.button))

    elif evtname.lower() == "joybuttonup":
      print("%d: btnRelease <%s>"  % (lc, event.button))

    else:
      print("%d: irrelevant: <%s>" % (lc, evtname))


    # print("====== EVENT [%d]: %s ========" % (self.eventLogCounter, evtname))
    # for i in range(0, self.numberOfControllers):
    #   contobj = getattr(self, "joystick%d"%i)

    #   print("  controller: %d" % i )
    #   astr = "        axes: "
    #   for ax in range(0, contobj.get_numaxes()):
    #     astr += "[%d]%d " % (ax, contobj.get_axis(ax))
    #   print(astr)

    #   bstr = "       balls: "
    #   for bx in range(0, contobj.get_numballs()):
    #     bstr += "[%d]%d " % (bx, contobj.get_ball(bx))
    #   print(bstr)

    #   bstr = "     buttons: "
    #   for bx in range(0, contobj.get_numbuttons()):
    #     bstr += "[%d]%d " % (bx, contobj.get_button(bx))
    #   print(bstr)

    #   hstr = "        hats: "
    #   for hx in range(0, contobj.get_numhats()):
    #     hstr += "[%d]%d " % (hx, contobj.get_hat(hx))
    #   print(hstr)


  def run( self ):
    self.running = True
    self.state = states.Intro
    resizeEvent = False

    self.moment = time.perf_counter()

    self.textBlinkLastTime = self.moment
    self.gameStartTime = self.moment
    self.frmStartTime = self.moment

    self.curFrm = 0
    self.eventLogCounter = 0
    while self.running:
      self.moment = time.perf_counter()
      curFrm = int( (self.moment - self.gameStartTime) * self.timing.fps )
      self.frmChanged = (curFrm != self.curFrm)
      if self.frmChanged:
        self.curFrm = curFrm
        self.frmStartTime = self.moment

      for event in events.readAll(self):

        if event == events.reqQuit:
          return self.quit()

        if event is None:
          continue

        # self.logControllerStates(event)
        print("E:", event)

        if event == events.reqWinResize:
          resizeEvent = self.lastResize

        elif event == events.reqScreenShot:
          self.do_screenshot()

        else:
          stateHandler = inputhandler.HANDLERS.get(self.state, False)
          if stateHandler:
            stateHandler(self, event)

      if resizeEvent:
        drawer.setupOSWindow(self, resizeEvent.w, resizeEvent.h)
        drawer.setupLayout(self)
        resizeEvent = False
        self.shouldRedraw = True

      if self.frmChanged:
        self.process_game_logic()
        drawer.drawTheWorld(self)
        if self.state == states.Play:
          logger.worldState(self)

    self.quit()
