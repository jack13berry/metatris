# Based on the work by John K. Lindstedt

from twisted.internet import reactor
from twisted.internet.task import LoopingCall

import os
import sys
import copy
import csv
import random
import time
import json
import datetime
import platform
import random
import tkinter
import tkinter.simpledialog

import pygame, numpy


from zoid import Zoid

from simulator import TetrisSimulator

import states, logger, cnf, drawer, inputhandler

try:
  #from pyfixation import VelocityFP
  #print("Pyfixation success.")
  from pyviewx.client import iViewXClient, Dispatcher
  # print("Pyview client success")
  from pyviewx.pygame import Calibrator
  # print("Pyview pygame support success.")
  from pyviewx.pygame import Validator
  # print("Pyview validator support success.")
  import numpy as np
  # print("numpy success")
  eyetrackerSupport = True
except ImportError:
  # print("Warning: Eyetracker not supported on this machine.")
  eyetrackerSupport = False


sep = os.path.sep
get_time = time.time if platform.system() == 'Windows' else time.process_time

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

  if eyetrackerSupport:
    gaze_buffer = []
    gaze_buffer2 = []
    d = Dispatcher()

  #initializes the game object with most needed resources at startup
  def __init__( self, args ):
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
    self.starttime = get_time()

    # Collect argument values
    self.args = args

    self.session = self.args.logfile

    # Collect config values
    self.config_names = self.args.config_names
    if self.config_names == "default":
      self.config_names = ["default"]

    #junk configuration fetch for use in setting up log files and others.
    self.config_ix = -1
    cnf.load(self, self.config_names[0])

    ## Input init

    #...# provide a function for setting game controls here.

    #initialize joystick
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
      self.joystick1 = pygame.joystick.Joystick(0)
      self.joystick1.init()
    if pygame.joystick.get_count() > 1:
      self.joystick2 = pygame.joystick.Joystick(1)
      self.joystick2.init()

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
    self.score = 0
    self.newscore = 0
    self.high_score = 0
    self.prev_tetris = 0

    self.drop_score = 0

    self.game_number = 0
    self.episode_number = 0

    self.seeds_used = []

    self.game_scores = []

    self.game_start_time = get_time()

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
    self.lines_to_clear = []

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

    if self.args.eyetracker and eyetrackerSupport:
      self.i_x_avg = 0
      self.i_y_avg = 0
      self.i_x_conf = None
      self.i_y_conf = None
      self.prev_x_avg = 0
      self.prev_y_avg = 0

      self.i_x_avg2 = 0
      self.i_y_avg2 = 0
      self.i_x_conf2 = None
      self.i_y_conf2 = None
      self.prev_x_avg2 = 0
      self.prev_y_avg2 = 0
      if self.gameover_fixcross == True:
        self.implement_gameover_fixcross = True
        self.gameover_fixation = False
        self.gameover_fixcross_frames_count = 0
        self.gameover_fixcross_frames_miss = 0



      else:
        self.implement_gameover_fixcross = False
    else:
      ##set to true only for debugging.
      self.implement_gameover_fixcross = False


    # Gets screen information
    self.screeninfo = pygame.display.Info()

    # Remove modes that are double the width of another mode
    # which indicates a dual monitor resolution
    modes = pygame.display.list_modes()
    print(modes)
    for mode in modes:
      tmp = mode[0] / 2
      for m in modes:
        if tmp == m[0]:
          modes.remove( mode )
          break

    # Initialize image graphics

    self.logo = pygame.image.load( "media" + sep + "logo.png" )
    self.rpi_tag = pygame.image.load( "media" + sep + "std-rpilogo.gif" )
    self.cwl_tag = pygame.image.load( "media" + sep + "cogworks.gif" )

    gameicon = pygame.image.load( "media" + sep + "game-changer.ico" )
    pygame.display.set_icon(gameicon)

    if self.fullscreen:
      self.screen = pygame.display.set_mode( ( 0, 0 ), pygame.FULLSCREEN )
    else:
      #self.screen = pygame.display.set_mode( modes[1], 0 )
      self.screen = pygame.display.set_mode( (800,600), 0 )
      pygame.display.set_caption("Game Changer")


    self.worldsurf = self.screen.copy()
    self.worldsurf_rect = self.worldsurf.get_rect()

    self.side = int( self.worldsurf_rect.height / (self.game_ht + 4.0) )
    self.border = int( self.side / 6.0 )
    self.border_thickness = int(round(self.side/4))

    # Fonts (intro: 36; scores: 48; end: 68; pause: 102)
    # ratios divided by default HEIGHT: .04, .053, .075, .113
    self.intro_font = pygame.font.Font( "freesansbold.ttf", int(.04 * self.worldsurf_rect.height) )
    self.scores_font = pygame.font.Font( "freesansbold.ttf", int(.033 * self.worldsurf_rect.height) )
    self.end_font = pygame.font.Font( "freesansbold.ttf", int(.055 * self.worldsurf_rect.height) )
    self.pause_font = pygame.font.Font( "freesansbold.ttf", int(.083 * self.worldsurf_rect.height) )


    # Colors
    self.NES_colors = Zoid.NES_colors
    self.STANDARD_colors = Zoid.STANDARD_colors

    self.block_color_type = Zoid.all_color_types
    self.blocks = []
    #generate blocks for all levels
    for l in range( 0, 10 ):
      blocks = []
      #and all block-types...
      if self.color_mode == "STANDARD":
        for b in range( 0, len(self.STANDARD_colors)):
          blocks.append( drawer.generate_block( self, self.side, l, b ) )
      else:
        for b in range( 0, 3 ):
          blocks.append( drawer.generate_block( self, self.side, l, b ) )
      self.blocks.append( blocks )

    self.gray_block = drawer.generate_block( self, self.side, 0, 0 )

    self.end_text_color = ( 210, 210, 210 )
    self.message_box_color = ( 20, 20, 20 )
    self.mask_color = ( 100, 100, 100 )

    self.ghost_alpha = 100

    self.next_alpha = 255
    if self.next_dim:
      self.next_alpha = self.next_dim_alpha



    # Surface definitions

    self.gamesurf = pygame.Surface( ( self.game_wd * self.side, self.game_ht * self.side ) )
    self.gamesurf_rect = self.gamesurf.get_rect()
    self.gamesurf_rect.center = self.worldsurf_rect.center

    self.gamesurf_msg_rect = self.gamesurf_rect.copy()
    self.gamesurf_msg_rect.height = self.gamesurf_rect.height / 2
    self.gamesurf_msg_rect.center = self.gamesurf_rect.center

    if self.score_align == "right":
      self.score_offset = self.gamesurf_rect.right + 3 * self.side
    elif self.score_align == "left":
      self.score_offset = 2 * self.side

    self.next_offset = self.gamesurf_rect.right + 3 * self.side


    self.next_size = 5 if self.pentix_zoids else 4

    self.nextsurf = pygame.Surface( ( (self.next_size + .5) * self.side, (self.next_size + .5) * self.side ) )
    self.nextsurf_rect = self.nextsurf.get_rect()
    self.nextsurf_rect.top = self.gamesurf_rect.top
    self.nextsurf_rect.left = self.next_offset

    self.gamesurf_border_rect = self.gamesurf_rect.copy()
    self.gamesurf_border_rect.width += self.border_thickness
    self.gamesurf_border_rect.height += self.border_thickness
    self.gamesurf_border_rect.left = self.gamesurf_rect.left - self.border_thickness / 2
    self.gamesurf_border_rect.top = self.gamesurf_rect.top - self.border_thickness / 2

    self.nextsurf_border_rect = self.nextsurf_rect.copy()
    self.nextsurf_border_rect.width += self.border_thickness
    self.nextsurf_border_rect.height += self.border_thickness
    self.nextsurf_border_rect.left = self.nextsurf_rect.left - self.border_thickness / 2
    self.nextsurf_border_rect.top = self.nextsurf_rect.top - self.border_thickness / 2

    if self.far_next:
      self.nextsurf_rect.left = self.worldsurf_rect.width - self.nextsurf_border_rect.width - self.border_thickness / 2
      self.nextsurf_border_rect.left = self.worldsurf_rect.width - self.nextsurf_border_rect.width - self.border_thickness

    if self.keep_zoid:
      self.keptsurf = self.nextsurf.copy()
      self.keptsurf_rect = self.keptsurf.get_rect()
      self.keptsurf_rect.top = self.gamesurf_rect.top
      self.keptsurf_rect.left = self.gamesurf_rect.left - self.keptsurf_rect.width - (4 * self.border_thickness)

      self.keptsurf_border_rect = self.keptsurf_rect.copy()
      self.keptsurf_border_rect.width += self.border_thickness
      self.keptsurf_border_rect.height += self.border_thickness
      self.keptsurf_border_rect.left = self.keptsurf_rect.left - self.border_thickness / 2
      self.keptsurf_border_rect.top = self.keptsurf_rect.top - self.border_thickness / 2

    if self.args.eyetracker and eyetrackerSupport:
      self.spotsurf = pygame.Surface( (self.worldsurf_rect.width * 2, self.worldsurf_rect.height * 2), flags = pygame.SRCALPHA)
      self.spotsurf_rect = self.spotsurf.get_rect()
      self.spotsurf_rect.center = (self.worldsurf_rect.width, self.worldsurf_rect.height)
      self.spotsurf.fill( self.spot_color + tuple([self.spot_alpha]) )
      center = (self.spotsurf_rect.width / 2, self.spotsurf_rect.height / 2)
      if self.spot_gradient:
        for i in range(0, self.spot_radius):
          j = self.spot_radius - i
          alpha = int(float(j) / float(self.spot_radius) * float(self.spot_alpha))
          pygame.draw.circle( self.spotsurf, self.spot_color + tuple([alpha]), center, j, 0)
      else:
        pygame.draw.circle( self.spotsurf, self.spot_color + tuple([0]), center, self.spot_radius, 0)



    # Text labels
    midtopy = self.worldsurf_rect.height / 2
    lineheight = 50
    self.high_lab_left = ( self.score_offset, midtopy - 2*lineheight )
    self.zoids_lab_left = ( self.score_offset, midtopy - lineheight )
    self.score_lab_left = ( self.score_offset, midtopy )
    self.lines_lab_left = ( self.score_offset, midtopy + lineheight )
    self.level_lab_left = ( self.score_offset, midtopy + 2*lineheight )
    self.newscore_lab_left = ( self.score_offset, midtopy + 3*lineheight )
    self.metascore_lab_left = ( self.score_offset, midtopy + 4*lineheight )

    self.label_offset = int(280.0 / 1440.0 * self.worldsurf_rect.width)
    self.high_left = ( self.score_offset + self.label_offset, self.high_lab_left[1] )
    self.zoids_left = ( self.score_offset + self.label_offset, self.zoids_lab_left[1] )
    self.score_left = ( self.score_offset + self.label_offset, self.score_lab_left[1] )
    self.lines_left = ( self.score_offset + self.label_offset, self.lines_lab_left[1] )
    self.level_left = ( self.score_offset + self.label_offset, self.level_lab_left[1] )
    self.newscore_left = ( self.score_offset + self.label_offset, self.newscore_lab_left[1] )
    self.metascore_left = ( self.score_offset + self.label_offset, self.metascore_lab_left[1] )


    # Animation
    self.gameover_anim_tick = 0
    self.gameover_tick_max = self.game_ht * 2
    self.gameover_board = [[0] * self.game_wd] * self.game_ht

    self.tetris_flash_tick = 0 #currently dependent on framerate
    self.tetris_flash_colors = [self.bg_color, ( 100, 100, 100 )]

    self.title_blink_timer = 0

    ## Sound
    self.setupSounds()

    ## Eyetracking

    # sampling and fixations
    self.fix = None
    self.samp = None
    if self.args.eyetracker and eyetrackerSupport:
      self.client = iViewXClient( self.args.eyetracker, 4444 )
      self.client.addDispatcher( self.d )
      #self.fp = VelocityFP()
      self.calibrator = Calibrator( self.client, self.screen, reactor = reactor ) #escape = True?

    self.eye_x = None
    self.eye_y = None


    ## Board statistics
    self.print_stats = self.args.boardstats
    #self.boardstats = TetrisBoardStats( self.board, self.curr_zoid.type, self.next_zoid.type )

    self.sim = TetrisSimulator(board = self.board, curr = self.curr_zoid.type, next = self.next_zoid.type, controller = self.get_controller(),
          overhangs = self.sim_overhangs, force_legal = self.sim_force_legal)
    self.update_stats()

    self.features_set = sorted(self.features.keys())
    self.fixed_header = self.fixed_header + self.features_set

    #behavior tracking: latencies and sequences
    self.evt_sequence = []
    self.ep_starttime = get_time()

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


  def setupSounds(self):
    #pygame.mixer.music.load( "media" + sep + "title.wav" )
    pygame.mixer.set_num_channels( 24 )
    pygame.mixer.music.set_volume( self.music_vol )
    # pygame.mixer.music.play( -1 )

    # Sound effects
    self.sounds = {}
    for sound in [ 'rotate','trans','clear1','clear4','crash','levelup',
      'thud','pause','slam','keep','solved1']:
      self.sounds[sound] = pygame.mixer.Sound(
        sep.join(['media', 'sounds', 'default', sound]) + ".wav"
      )
      self.sounds[sound].set_volume( self.sfx_vol )

    self.soundrand = random.Random()
    self.soundrand.seed(get_time())


  def get_controller( self ):
    f = open("controllers" + sep + self.controller + ".control")
    lines = f.readlines()
    f.close()
    return json.loads(lines[0].strip())


  def set_var( self, name, default, type ):
    #set hard defaults first
    vars(self)[name] = default

    msg = "D"
    #set config values, if exist
    if name in self.config:
      val = []
      if type == 'float' or type == 'int':
        val = eval(type)(self.config[name])
      elif type == 'bool':
        entry = self.config[name].lower()
        val = ( entry == 'true') or (entry == 't') or (entry == 'yes') or (entry == 'y')
      elif type == 'string':
        val = self.config[name]
      elif type == 'int_list' or 'color':
        list = self.config[name].split(",")
        for i in list:
          val.append(int(i.strip()))
        if type == 'color':
          val = tuple(val)

      vars(self)[name] = val

      if val != default:
        msg = "C"

    #set command line overrides, if exist
    if name in vars(self.args):
      if vars(self.args)[name] != None:
        vars(self)[name] = vars(self.args)[name]
        msg = "A"

    print(msg + ": " + name + " = " + str(vars(self)[name]))
    self.configs_to_write += [name]


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


  ###

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
    lat = int(1000 * (get_time() - self.ep_starttime))
    self.evt_sequence.append([token,lat])
    if self.initial_lat == 0:
      self.initial_lat = lat
    if drop and self.drop_lat == 0:
      self.drop_lat = lat
    if kp:
      self.latencies.append(lat)





  ####
  #  Game Logic
  ####

  #main game logic refresh, handles animations and logic updates
  def process_game_logic( self ):
    #lc counter and are counter start at zero and automatically count backward
    if self.state == states.Play:
      for i in range( 0, self.ticks_per_frame ):
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

  ###

  # For debugging purposes; produces random player behavior
  def random_behavior( self ):
    if self.timer % 7 == 0:
      self.curr_zoid.down( self.interval_toggle )
    if self.timer % 35 == 0:
      self.curr_zoid.rotate( random.randint( -1, 1 ) )
    if self.timer % 25 == 0:
      self.curr_zoid.translate( random.randint( -1, 1 ) )
  ###

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
      pygame.mixer.music.stop()
      pygame.mixer.music.load( "media" + sep + "%s_fast.wav" % self.song )
      pygame.mixer.music.play( -1 )
      logger.game_event(self,  "DANGER", "BEGIN" )
    #if we've cleared out of danger mode...
    elif not topfull and self.danger_mode:
      self.danger_mode = False
      pygame.mixer.music.stop()
      pygame.mixer.music.load( "media" + sep + "%s.wav" % self.song )
      pygame.mixer.music.play( -1 )
      logger.game_event(self,  "DANGER", "END" )
  ###

  #Stamps the current zoid onto the board representation.
  def place_zoid( self ):
    self.zoids_placed += 1
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
  ###

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
  ###

  #get a new zoid for the piece queue
  def get_next_zoid( self ):
    zoid = None
    if self.seven_bag_switch:
      zoid = self.get_seven_bag()
    else:
      zoid = self.get_random_zoid()
    return zoid

  ###


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
  ###

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
    self.ep_starttime = get_time()

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

  #end a trial
  def end_trial( self ):
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

  #startup and reset procedures
  def setup( self ):

    #check for additional configs
    self.config_ix += 1

    ## preserve continues count from initial config
    cur_continues = self.continues
    self.config = {}
    cnf.load(self, (self.config_names[self.config_ix%len(self.config_names)]))
    self.continues = cur_continues
    #new board
    self.initialize_board()

    #increment game number
    self.game_number += 1

    if self.fixed_seeds:
      # print(self.seed_order)
      # print(self.random_seeds)
      seed = self.random_seeds[self.seed_order[(self.game_number-1)%len(self.random_seeds)]]
      # print(seed)
    else:
      seed = int(get_time() * 10000000000000.0)

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
    self.ep_starttime = get_time()

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
    self.zoids_placed = 0
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

    self.needs_new_zoid = False
    self.are_counter = 0
    self.lc_counter = 0

    self.gameover_anim_tick = 0

    self.episode_number = 0

    self.game_start_time = get_time()

    self.gameover_params = {
      'size' : self.gameover_fixcross_size,
      'width' : self.gameover_fixcross_width,
      'frames' : self.gameover_fixcross_frames,
      'tolerance' : self.gameover_fixcross_tolerance,
      'frames_tolerance' : self.gameover_fixcross_frames_tolerance,
      'hit_color' : self.gameover_fixcross_color,
      'timeout' : self.gameover_fixcross_timeout,
      'miss_color' : self.border_color,
      'bg_color' : self.message_box_color,
      'val_accuracy' : self.validation_accuracy,
      'automated' : self.automated_revalidation
    }

    #restart the normal music
    pygame.mixer.music.load( "media" + sep + "%s.wav" % self.song )
    pygame.mixer.music.play( -1 )
    self.danger_mode = False

    logger.game_event(self,  "GAME", "BEGIN", self.game_number )

  def fixcross ( self, lc ,log = None, results = None ):
    evt_recal = False
    if self.args.eyetracker and eyetrackerSupport:
      event_log = self.validator.log
      validation_results = str(self.validator.validationResults)
      if len(event_log) > 1:
        if "RECALIBRATE" in event_log:
          evt_recal = True
        event_log = str(event_log)

      logger.game_event(self, "VALIDATION", event_log, validation_results)

    if event_log == "RECALIBRATE" or evt_recal == True:

      logger.game_event(self, "RECALIBRATION", "START")
      self.state = states.Calibrate
      self.recalibrate()

    else:
      self.state = states.Gameover
      self.input_continue()

  def recalibrate( self ) :
    self.calibrator._reset()
    self.calibrator.start(self.runrecalibrate, recalibrate = True, points = self.calibration_points, auto = int(self.calibration_auto ))

  def runrecalibrate( self, lc, results = None ):
    if self.args.eyetracker and eyetrackerSupport:
      logger.game_event(self, "RECALIBRATION", "COMPLETE", self.calibrator.calibrationResults)

    self.state = states.Gameover
    self.input_continue()


  def process_eyetracker(self):
    if not (self.args.eyetracker and eyetrackerSupport):
      return

    if len( World.gaze_buffer ) > 1:
      #get avg position
      xs = []
      ys = []
      for i in World.gaze_buffer:
        xs += [i[0]]
        ys += [i[1]]

      self.prev_x_avg = self.i_x_avg
      self.prev_y_avg = self.i_y_avg
      self.i_x_avg = int( sum(xs) / len( World.gaze_buffer ) )
      self.i_y_avg = int( sum(ys) / len( World.gaze_buffer ) )

      #handle eye-based events
      if self.eye_mask:
        prev = self.mask_toggle
        if self.i_x_avg > int((self.gamesurf_rect.width + self.gamesurf_rect.left + self.nextsurf_rect.left) / 2) and self.i_y_avg < int((self.nextsurf_rect.top + self.nextsurf_rect.height + self.score_lab_left[1]) / 2):
          self.mask_toggle = True
        else:
          self.mask_toggle = False
        if self.mask_toggle != prev:
          logger.game_event(self, "MASK_TOGGLE", self.mask_toggle)


      #HOOK FOR MISDIRECTION / LOOKAWAY EVENTS
      # when in board, normal. when leave board, subtly alter accumulation.
      ## will need crossover detection for event onset
      ## will need board mutator function
      ## could use some helper "in-bounds" or collision functions.

      self.i_x_conf = 0 if int(self.i_x_avg)<=0 else sum(map((lambda a, b: pow(a + b, 2)), xs, [-self.i_x_avg] * len(xs))) / int(self.i_x_avg)#len(xs)
      self.i_y_conf = 0 if int(self.i_y_avg)<=0 else sum(map((lambda a, b: pow(a + b, 2)), ys, [-self.i_y_avg] * len(ys))) / int(self.i_y_avg)#len(ys)


    #for second eye when both are captured
    if len( World.gaze_buffer2 ) > 1:
      xs2 = []
      ys2 = []
      for i in World.gaze_buffer2:
        xs2 += [i[0]]
        ys2 += [i[1]]

      self.prev_x_avg2 = self.i_x_avg2
      self.prev_y_avg2 = self.i_y_avg2
      self.i_x_avg2 = int( sum(xs2) / len( World.gaze_buffer2 ) )
      self.i_y_avg2 = int( sum(ys2) / len( World.gaze_buffer2 ) )

      self.i_x_conf2 = 0 if int(self.i_x_avg2)<=0 else sum(map((lambda a, b: abs(a + b)), xs2, [-self.i_x_avg2] * len(xs2))) / int(self.i_x_avg2)
      self.i_y_conf2 = 0 if int(self.i_y_avg2)<=0 else sum(map((lambda a, b: abs(a + b)), ys2, [-self.i_y_avg2] * len(ys2))) / int(self.i_y_avg2)


  #Twisted event loop refresh logic
  def refresh( self ):
    if self.state != states.Calibrate and self.state != states.GameoverFixation:
      inputhandler.handle(self)
      self.process_eyetracker()
      self.process_game_logic()
      drawer.drawTheWorld(self)

    if self.state == states.Play:
      logger.world(self)


  #Twisted event loop setup
  def start( self, lc, results=None ):
    self.state = states.Intro
    if self.args.eyetracker and eyetrackerSupport:
      logger.game_event(self, "CALIBRATION", "Complete", str(self.calibrator.calibrationResults))

    self.lc = LoopingCall( self.refresh )
    #pygame.mixer.music.play( -1 )
    cleanupD = self.lc.start( 1.0 / self.fps )
    cleanupD.addCallbacks( self.quit )


  #Twisted event loop teardown procedures
  def quit( self, lc ):
    if self.game_number > 0 and not self.state == states.Gameover:
      logger.gameresults(self, complete=False)
    self.criterion_score()
    logger.close_files(self)
    reactor.stop()
  ###

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
      #NOTE: the following won't end the program here:
      #quit(), sys.exit(), raise ..., return error
      #...because 'deferred' will just catch it and ignore it
      os.abort()

  #Begin the reactor
  def run( self ):
    #coop.coiterate(self.process_pygame_events()).addErrback(error_handler)
    if self.args.eyetracker and eyetrackerSupport:
      self.state = states.Calibrate
      reactor.listenUDP( 5555, self.client )
      logger.game_event(self, "CALIBRATION", "Start")
      self.calibrator.start( self.start , points = self.calibration_points, auto = int(self.calibration_auto))
    else:
      self.start( None )

    reactor.run()
  ###


  """
  inResponse =
  [timestamp, eyetype (l, r, b), sx = (lx, rx), sy = (ly, rx), dx = (diam l and r), dy = (diam, l and r),,
   eye3d X (l, r), eye3d Y (l, r), eye3d Z (l, r)]

  [smi_ts, smi_eyes,
   smi_samp_x_l, smi_samp_x_r,
   smi_samp_y_l, smi_samp_y_r,
   smi_diam_x_l, smi_diam_x_r,
   smi_diam_y_l, smi_diam_y_r,
   smi_eye_x_l, smi_eye_x_r,
   smi_eye_y_l, smi_eye_y_r,
   smi_eye_z_l, smi_eye_z_r]
  """
  #Eyetracker information support
  if eyetrackerSupport:
    @d.listen( 'ET_SPL' )
    def iViewXEvent( self, inResponse ):
      self.inResponse = inResponse
      if not self.unifile.closed:
        logger.eye_sample(self)
      global x, y, x2, y2
      if self.state < 0:
        return

      try:
        t = int( inResponse[0] )
        x = float( inResponse[2] )
        y = float( inResponse[4] )
        x2 = float( inResponse[3] )
        y2 = float( inResponse[5] )

        ex = np.mean( ( float( inResponse[10] ), float( inResponse[11] ) ) )
        ey = np.mean( ( float( inResponse[12] ), float( inResponse[13] ) ) )
        ez = np.mean( ( float( inResponse[14] ), float( inResponse[15] ) ) )
        dia = int( inResponse[6] ) > 0 and int( inResponse[7] ) > 0 and int( inResponse[8] ) > 0 and int( inResponse[9] ) > 0

        #if good sample, add
        if x != 0 and y != 0:
          World.gaze_buffer.insert( 0, ( x, y ) )
          if len( World.gaze_buffer ) > self.gaze_window:
            World.gaze_buffer.pop()

        if x2 != 0 and y2 != 0:
          World.gaze_buffer2.insert( 0, ( x2, y2 ) )
          if len( World.gaze_buffer2 ) > self.gaze_window:
            World.gaze_buffer2.pop()
        self.fix, self.samp = None, None
        #self.fix, self.samp = self.fp.processData( t, dia, x, y, ex, ey, ez )
      except(IndexError):
        print("IndexError caught-- AOI error on eyetracking machine?")
        logger.game_event(self, "ERROR", "AOI INDEX")
