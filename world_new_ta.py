"""
John K. Lindstedt

    To-dos:


        - Log Epistemic Action things, log Rotations, Translations, Etc.
        - Log Episode Duration
        - Program to split data files up by episode and game.

        - Eric Demaine (sp?) - ideal performer, complexity, etc.
        - t-spin, any-spin
        - grace period;
        - ideal performer and/or AI

        - Logging summaries:
          - sequencing
          - latency
          - PITS / DEEP PITS / OVERHANGS
          -


        squish the DROP / PAUSE bug
        little issue with charging AS something drops.

        -IMPLEMENT A POST-GAME EVENT LOGGING SYSTEM FOR THE MAIN LOG
        -ALSO LOG ALL CONFIG EVENTS
        -AND REDUCE THE WHOLE GODDAMN LOG SIZE
        -Add the command line hooks for various necessary items

        -reimplement the "header section" of the log file.
           -There's no reason not to have this, despite what was previously discussed


        -Implement first-person tetris

        -implement grace period
            -implied soft-drop when enabled
            -make SLAMS skip this timer

        -implement multiple look-aheads
            -need a rotating queue structure

        -implement history file logging (PySide needed -_-)

        -implement dialog box for inputting experiment information
            -Need to be hashed

        -Create package of VERSION 1;
            -For package bundling, move config files outside - referencing outside

        -Revamp the draw-cycle so we can hit 60 fps again
            - Implement lazy drawing? (changes only needed at PIECE-PLACED, LC-DELAY ANIMATION STEPS, ARE-DELAY start, NEW PIECE start)
        -Chug is still happening in strange spots, rather infrequently; need to make sure this isn't still from GC or key-repeat.

        - idea for a very subtle manipulation: change which direction the ONLY rotate key rotates the zoid
        - allow people to gain expertise, and see how it affects their treating of the L and J blocks, as well as tetris-candidate column selection
        -


        -implement Random-arrow-keybindings mode

        -files:
            --> .config file
            <-- History file
            <-- Log file
            <-- Eye file
            <-- Episode aggregate file?


        -implement arbitrary keybindings using vars(pygame_key)
        -implement random next box position per trial
        -implement extra option for next-mask uncovering DURING delay phase

        -implement swappable board-piece invisibility

        -implement ALL KINDS of lagtris
            -constant in all inputs
            -random in all game-events, but not PLAYER events
            -random, but about an average
            -some simulation of net-play lag...
            -reduced framerate, but with the same underlying game
            ?how do players deal with lag? What are their limits of "dealing"?

        -Random or NO auditory feedback (see how the auditory cues influence gameplay)

        -logging:
            -need two modes: verbose and compact
                -all session-constants can be logged separately in compact mode
                -all session-constants included in state logging in verbose mode (current default)
            -centroids
            -current Tetris Version / logging version
            -key releases
            -zoid randomizer seed

        -ssvep-ready flicker mode...
            - hz, categories

        -implement ACT-R interactivity (once I get Ryan's device)

        -implement "quiz" mode
            -instantaneous
            -two-step
            -build-up

        -implement playback mode

        -implement Bastard mode (rearrange board when looking away)
            -levels of disruption: whole, partial, single, (incremental), (stochastic)

        -implement CPTetris:
            -NBack or AX-CPT
                -only make piece valid (stamped and placed) when a "hit"
                -i.e., comes after a proper cue or is same as the nth-back piece...

        Game modes:
            Pentix vs Classic
            Upsidedown vs rightsideup
            Rational vs time pressured
            look ahead amount
            congruent controls?
            Invisible




    Upstream:
        -Get the logs into good format with robust information:
            -On-line fixation and ROI processing
            -On-line optimality metrics (both board and piece)
                -Piece metrics can include CHOSEN location among 'good' locations (ROIs for these?)
        -On-line sequence processing? (ROIs, actions, and sysevts)
        -EEG integration? (at least sending event tags)
        -Integrate PyCogWorks for RIN and such
        -Considerations for packaging this as a 'take-home' app for participants.



"""

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
#from boardstats import TetrisBoardStats
from simulator import TetrisSimulator

try:
    #from pyfixation import VelocityFP
    #print("Pyfixation success.")
    from pyviewx.client import iViewXClient, Dispatcher
    print("Pyview client success")
    from pyviewx.pygame import Calibrator
    print("Pyview pygame support success.")
    from pyviewx.pygame import Validator
    print("Pyview validator support success.")
    import numpy as np
    print("numpy success")
    eyetrackerSupport = True
except ImportError:
    print("Warning: Eyetracker not supported on this machine.")
    eyetrackerSupport = False

try:
    import pycogworks.crypto
    cryptoSupport = True
except ImportError:
    print("Warning: cryptography not supported on this machine.")
    cryptoSupport = False

get_time = time.time

sep = "/"
if platform.system() == 'Windows':
    get_time = time.process_time
    sep = "/"

class World( object ):

    if eyetrackerSupport:
        gaze_buffer = []
        gaze_buffer2 = []
        d = Dispatcher()


    #initializes the game object with most needed resources at startup
    def __init__( self, args ):



        ## Constants
        self.STATE_CALIBRATE = -1
        self.STATE_INTRO = 0
        self.STATE_SETUP = 1
        self.STATE_PLAY = 2
        self.STATE_PAUSE = 3
        self.STATE_GAMEOVER = 4
        self.STATE_GAMEOVER_FIXATION = 6

        self.roll_avg = []
        self.metascore = 0
        self.metaticks = 0

        #After Action Review state
        self.STATE_AAR = 5
        self.LOG_VERSION = 3.1

        #token names for latency logging
        self.evt_token_names = ["kr-rt-cc", #RL
                                "kr-rt-cw", #RR
                                "kp-tr-l",  #TL
                                "kp-tr-r",  #TR
                                "kp-dwn",   #DN
                                "sy-rt-cc", #SRL
                                "sy-rt-cw", #SRR
                                "sy-tr-l",  #STL
                                "sy-tr-r",  #STR
                                "sy-dn-u",  #UD
                                "sy-dn-s"]  #SD


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
        self.get_config(self.config_names[0])


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



        # Logging provisions
        self.init_logs()
        #Start graphing up here on the open file
        #self.start_animate(self.scorefile_path + ".incomplete")

        self.config_write()



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

        self.state = self.STATE_INTRO

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

        if self.fullscreen:
            self.screen = pygame.display.set_mode( ( 0, 0 ), pygame.FULLSCREEN )
        else:
            #self.screen = pygame.display.set_mode( modes[1], 0 )
            self.screen = pygame.display.set_mode( (800,600), 0 )
            pygame.display.set_caption("Meta-T")
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
                    blocks.append( self.generate_block( self.side, l, b ) )
            else:
                for b in range( 0, 3 ):
                    blocks.append( self.generate_block( self.side, l, b ) )
            self.blocks.append( blocks )

        self.gray_block = self.generate_block( self.side, 0, 0 )

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


        self.next_size = 4
        if self.pentix_zoids:
            self.next_size = 5
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

        self.score_lab_left = ( self.score_offset, self.worldsurf_rect.height / 2 )
        self.high_lab_left = ( self.score_offset, self.score_lab_left[1] - 50 )
        self.lines_lab_left = ( self.score_offset, self.score_lab_left[1] + 50 )
        self.level_lab_left = ( self.score_offset, self.lines_lab_left[1] + 50 )
        self.newscore_lab_left = ( self.score_offset, self.level_lab_left[1] + 50 )
        self.metascore_lab_left = ( self.score_offset, self.newscore_lab_left[1] + 50 )

        self.label_offset = int(280.0 / 1440.0 * self.worldsurf_rect.width)
        self.high_left = ( self.score_offset + self.label_offset, self.high_lab_left[1] )
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

        # Music
        #pygame.mixer.music.load( "media" + sep + "title.wav" )
        pygame.mixer.set_num_channels( 24 )
        pygame.mixer.music.set_volume( self.music_vol )
        # pygame.mixer.music.play( -1 )

        # Sound effects
        self.sounds = {}
        self.sounds['rotate'] = pygame.mixer.Sound( "media" + sep + "rotate.wav" )
        self.sounds['trans'] = pygame.mixer.Sound( "media" + sep + "movebeep.wav" )
        self.sounds['clear1'] = pygame.mixer.Sound( "media" + sep + "clear1.wav" )
        self.sounds['clear4'] = pygame.mixer.Sound( "media" + sep + "clear4.wav" )
        self.sounds['crash'] = pygame.mixer.Sound( "media" + sep + "crash.wav" )
        self.sounds['levelup'] = pygame.mixer.Sound( "media" + sep + "levelup.wav" )
        self.sounds['thud'] = pygame.mixer.Sound( "media" + sep + "thud.wav" )
        self.sounds['pause'] = pygame.mixer.Sound( "media" + sep + "pause.wav" )
        self.sounds['slam'] = pygame.mixer.Sound( "media" + sep + "slam.wav" )
        self.sounds['keep'] = pygame.mixer.Sound( "media" + sep + "keep.wav" )
        self.sounds['solved1'] = pygame.mixer.Sound( "media" + sep + "solved_blip.wav" )
        for s in self.sounds:
            self.sounds[s].set_volume( self.sfx_vol )
        self.soundrand = random.Random()
        self.soundrand.seed(get_time())

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

        ## Fixed-length log headers

        #line types:
        # events
        # states
        # ep summs
        # game summs
        # eyes


        self.uni_header = ["ts","event_type"]


        #game and up
        self.game_header = ["SID","ECID","session","game_type","game_number","episode_number","level","score","lines_cleared",
                        "completed","game_duration","avg_ep_duration","zoid_sequence"]
        #event slots
        self.event_header = ["evt_id","evt_data1","evt_data2"]

        #episode and up
        self.ep_header = ["curr_zoid","next_zoid","danger_mode",
                            "evt_sequence","rots","trans","path_length",
                            "min_rots","min_trans","min_path",
                            "min_rots_diff","min_trans_diff","min_path_diff",
                            "u_drops","s_drops","prop_u_drops",
                            "initial_lat","drop_lat","avg_lat",
                            "tetrises_game","tetrises_level",
                            "agree"]
        self.features_set = sorted(self.features.keys())

        #immediate only
        self.state_header = ["delaying","dropping","zoid_rot","zoid_col","zoid_row"]
        self.board_header = ["board_rep","zoid_rep","newscore","metascore","rollavg"]

        #eye and up
        self.eye_header = ["smi_ts","smi_eyes",
                        "smi_samp_x_l","smi_samp_x_r",
                        "smi_samp_y_l","smi_samp_y_r",
                        "smi_diam_x_l","smi_diam_x_r",
                        "smi_diam_y_l","smi_diam_y_r",
                        "smi_eye_x_l","smi_eye_x_r",
                        "smi_eye_y_l","smi_eye_y_r",
                        "smi_eye_z_l","smi_eye_z_r",
                        "fix_x","fix_y"]

        self.fixed_header = self.uni_header + self.game_header + self.event_header + self.ep_header + self.state_header + self.board_header
        if self.args.eyetracker:
            self.fixed_header = self.fixed_header + self.eye_header

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
            self.log_universal_header()

        self.log_game_event("LOG_VERSION", self.LOG_VERSION)
        self.log_game_event( "BOARD_INIT" )



        #Initialization complete! Log the history file and get started:
        self.log_history()



    ## File IO

    def get_config( self, name = "default" ):

        self.config = {}

        f = open("configs" + sep + name + ".config")
        lines = f.readlines()
        f.close()

        for l in lines:
            l = l.strip().split("#")
            if l[0] != '':
                line = l[0].split("=")
                key = line[0].strip()
                val = line[1].strip()
                self.config[key] = val

        self.configs_to_write = []

        ## Session variables
        #print(self.args)
        #print(self.config)

        #read once for value
        self.set_var('logdir', 'data', 'string')
        self.set_var('SID', 'Test', 'string')

        self.set_var('RIN', '000000000', 'string')

        self.set_var('ECID', 'NIL', 'string')

        if cryptoSupport:
            self.RIN = pycogworks.crypto.rin2id(self.RIN)[0]

        self.set_var('game_type', "standard", 'string')

        self.set_var('distance_from_screen', -1.0, 'float')

        self.set_var('fixed_log', True, 'bool')
        self.set_var('ep_log', True, 'bool')
        self.set_var('game_log', True, 'bool')


        self.set_var('continues', 0, 'int')

        self.set_var('time_limit', 3600, 'int') #defaults to 1 hour

        ## Game definitions

        # Manipulable variable setup

        self.set_var('music_vol', 0.5, 'float')
        self.set_var('sfx_vol', 1.0, 'float')
        self.set_var('song', "korobeiniki", 'string')

        self.set_var('fullscreen', False, 'bool')


        # Frames per second, updates per frame
        self.set_var('fps', 30 ,'int')
        self.set_var('tps', 60 ,'int')

        # render
        self.set_var('inverted', False ,'bool')

        # zoid set
        self.set_var('tetris_zoids', True ,'bool')
        self.set_var('pentix_zoids', False ,'bool')
        self.set_var('tiny_zoids', False ,'bool')

        # Held left-right repeat delays
        self.set_var('das_delay', 16, 'int')
        self.set_var('das_repeat', 6, 'int')
        #  in milliseconds based on 60 fps, 16 frames and 6 frames respectively...
        self.set_var('das_delay_ms', 266 ,'int')
        self.set_var('das_repeat_ms', 100 ,'int')


        # Zoid placement delay
        self.set_var('are_delay', 10 ,'int')

        # Line clear delay
        self.set_var('lc_delay', 20 ,'int')

        # Lines per level
        self.set_var('lines_per_lvl', 10 ,'int')

        # Game speed information
        self.set_var('intervals', [48, 43, 38, 33, 28, 23, 18, 13, 8, 6, 5, 5, 5, 4, 4, 4, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1] ,'int_list')
        self.set_var('drop_interval', 2 ,'int')

        self.set_var('gravity', True ,'bool')


        # Starting board information
        self.set_var('boardname', 'empty', 'string')

        self.set_var('game_ht', 20 ,'int')
        self.set_var('game_wd', 10 ,'int')

        # Invisible tetris
        self.set_var('visible_board', True ,'bool')
        self.set_var('visible_zoid', True ,'bool')
        self.set_var('board_echo_placed', True ,'bool')
        self.set_var('board_echo_lc', True ,'bool')

        # Number of next pieces to display (currently only 0 or 1)
        self.set_var('look_ahead', 1 ,'int')

        self.set_var('seven_bag_switch', False ,'bool')

        self.set_var('drop_bonus', True ,'bool')

        self.set_var('scoring', [40,100,300,1200,6000] ,'int_list')

        # manipulations
        self.set_var('undo', False ,'bool')

        self.set_var('far_next', False ,'bool')
        self.set_var('next_dim', True ,'bool')
        self.set_var('next_dim_alpha', 50 ,'int')

        self.set_var('next_mask', False ,'bool')
        self.set_var('board_mask', False, 'bool')

        self.set_var('eye_mask', False, 'bool')

        #modern game features
        self.set_var('ghost_zoid', False ,'bool')

        self.set_var('zoid_slam', False ,'bool')

        self.set_var('keep_zoid', False ,'bool')

        # allow rotations to "kick" away from wall and piece collisions
        self.set_var('wall_kicking', False ,'bool')


        #must include board states, placement summaries, and piece events once implemented
        self.set_var('feedback_mode', False ,'bool')

        #dimtris!
        self.set_var('dimtris', False, 'bool')
        self.set_var('dimtris_alphas', [255,225,200,175,150,125,100,75,50,25,0], 'int_list')

        #gridlines
        self.set_var('gridlines_x', False, 'bool')
        self.set_var('gridlines_y', False, 'bool')
        self.set_var('gridlines_color', (50,50,50), 'color')

        #draw fixations?
        self.set_var('draw_samps', False, 'bool')
        self.set_var('draw_avg', False, 'bool')
        self.set_var('draw_fixation', False, 'bool')
        self.set_var('draw_err', False, 'bool')
        self.set_var('gaze_window', 30, 'int')

        self.set_var('spotlight', False, 'bool')
        self.set_var('spot_radius', 350, 'int')
        self.set_var('spot_color', (50,50,50), 'color')
        self.set_var('spot_alpha', 255, 'int')
        self.set_var('spot_gradient', True, 'bool')

        #unimplemented
        self.set_var('grace_period', 0, 'int') #UNIMPLEMENTED
        self.set_var('grace_refresh', False, 'bool') #UNIMPLEMENTED
        ###

        self.set_var('bg_color', (0,0,0), 'color')
        self.set_var('border_color', (250,250,250), 'color')

        self.set_var('kept_bgc', ( 50, 50, 50 ), 'color')

        self.set_var('pause_enabled', True, 'bool')

        self.set_var('das_chargeable', True, 'bool')
        self.set_var('das_reversible', True, 'bool')

        self.set_var('two_player', False, 'bool')

        self.set_var('misdirection', False, 'bool') #UNIMPLEMENTED

        self.set_var('max_eps', -1, 'int')

        self.set_var('show_high_score', False, 'bool')

        self.set_var('starting_level', 0, 'int')


        self.set_var('ep_screenshots', False, 'bool')


        self.set_var('n_back', False, 'bool')
        self.set_var('nback_n', 2, 'int')

        self.set_var('ax_cpt', False, 'bool')
        self.set_var('ax_cue', 'O', 'string')
        self.set_var('ax_target', 'I', 'string')

#         self.set_var('fixed_seeds', False, 'bool')
        self.set_var('random_seeds', [int(self.starttime * 10000000000000.0)], 'int_list')
        self.set_var('permute_seeds', False, 'bool')
        self.set_var('shuffle_seed', int(self.starttime * 10000000000000.0), 'int')


        self.set_var('joystick_type', "NES_RETRO-USB", 'string')

        self.set_var('eye_conf_borders', False, 'bool')

        self.set_var('solve_button', False, 'bool')
        self.set_var('auto_solve', False, 'bool')

        self.set_var('hint_zoid', False, 'bool')
        self.set_var('hint_button', False, 'bool')
        self.set_var('hint_release', True, 'bool')
        self.set_var('hint_limit', -1, 'int')

        self.set_var('controller', "dellacherie", 'string')
        self.set_var('sim_overhangs', True, 'bool')
        self.set_var('sim_force_legal', True, 'bool')

        self.set_var('color_mode', "STANDARD", 'string')


        #tutoring system modes
            #NONE, CONSTANT, CONTEXT, CONFLICT

        #context-only hint zoids (i.e., correct rotation and column found)
        self.set_var('hint_context', False, 'bool')
        self.set_var('hint_context_col_tol', 0, 'int')

        #after-action review
        self.set_var('AAR', False, 'bool')
        self.set_var('AAR_max_conflicts', 1, 'int')
        self.set_var('AAR_dim', 50, 'int')
        self.set_var('AAR_dur', 20, 'int')
        self.set_var('AAR_dur_scaling', True, 'bool')
        self.set_var('AAR_curr_zoid_hl', True, 'bool')
        self.set_var('AAR_selfpaced', False, 'bool')

        self.set_var('score_align', 'left', 'string')

        self.set_var('gray_zoid', False, 'bool')
        self.set_var('gray_board', False, 'bool')
        self.set_var('gray_next', True, 'bool')
        self.set_var('gray_kept', False, 'bool')


        # Game Over Fixation Cross
        self.set_var('gameover_fixcross', False, 'bool')
        self.set_var('gameover_fixcross_size', 15, 'int')
        self.set_var('gameover_fixcross_width', 3, 'int')
        self.set_var('gameover_fixcross_frames', 30, 'int')
        self.set_var('gameover_fixcross_tolerance', 50, 'int')
        self.set_var('gameover_fixcross_frames_tolerance', 2, 'int')
        self.set_var('gameover_fixcross_color', (0,115,10), 'color')
        self.set_var('gameover_fixcross_timeout', 600, 'int')

        self.set_var('calibration_points', 5, 'int')
        self.set_var('calibration_auto', True, 'bool')
        self.set_var('validation_accuracy', 0.8, 'float')
        self.set_var('automated_revalidation', True, 'bool')

        self.set_var('episode_timeout', True, 'bool')

        return True

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

    #####
    # initialize log directory
    def init_logs( self ):


        if self.args.logfile:

            self.filename = self.SID + "_" + self.args.logfile
            self.logname = os.path.join( self.logdir, self.filename )

            if not os.path.exists( self.logdir ):
                os.makedirs( self.logdir )
            if not os.path.exists( self.logname):
                os.makedirs( self.logname)

            #open file
            self.histfile_path = self.logname + "/_hist_" + self.filename + ".hist"
            self.histfile = open( self.histfile_path, "w")

            self.configfile_path = self.logname + "/_config_" + self.filename + ".config"
            self.configfile = open( self.configfile_path, "w")

            self.unifile_path = self.logname + "/complete_" + self.filename + ".tsv"
            self.unifile = open( self.unifile_path + ".incomplete", "w")
            #self.uni_header()

            self.scorefile_path = self.logname + "/score_" + self.filename + ".tsv"
            self.scorefile = open( self.scorefile_path + ".incomplete", "w")

            if self.ep_log:
                self.epfile_path = self.logname + "/episodes_" + self.filename + ".tsv"
                self.epfile = open(   self.epfile_path + ".incomplete", "w" )

            if self.game_log:
                self.gamefile_path = self.logname + "/games_" + self.filename + ".tsv"
                self.gamefile = open (self.gamefile_path + ".incomplete", "w")

        else:
            self.logfile = sys.stdout

    def close_files( self ):

            self.log_game_event("seed_sequence", data1 = self.seeds_used )
            self.unifile.close()
            os.rename( self.unifile_path + ".incomplete", self.unifile_path)
            self.scorefile.close()
            os.rename( self.scorefile_path + ".incomplete", self.scorefile_path)

            if self.ep_log:
                self.epfile.close()
                os.rename( self.epfile_path + ".incomplete", self.epfile_path)

            if self.game_log:
                self.gamefile.close()
                os.rename( self.gamefile_path + ".incomplete", self.gamefile_path)

            self.configfile.write("\n#fixed values to recreate session's seed sequence\n")
            self.configfile.write("random_seeds = " + ",".join(self.seeds_used) + "\n")
            self.configfile.write("permute_seeds = False\n")
            self.configfile.write("fixed_seeds = True\n")
            self.configfile.close()
            """
            self.logfile.close()
            os.rename( self.logfile_path + ".incomplete", self.logfile_path)

            if self.args.eyetracker:
                self.eyefile.close()
                os.rename( self.eyefile_path + ".incomplete", self.eyefile_path)
            """

    def config_write( self ):
        for varname in self.configs_to_write:
            if type(vars(self)[varname]) is list or type(vars(self)[varname]) is tuple:
                out = []
                for i in vars(self)[varname]:
                    out += [str(i)]
                out = ",".join(out)
            else:
                out = str(vars(self)[varname])
            prepend = ""
            if varname in ['permute_seeds', 'random_seeds', 'fixed_seeds']:
                prepend = "#"
            self.configfile.write(prepend + varname + " = " + out + "\n")


    zoid_col_offset = {
        "O":[4],
        "L":[3,3,3,4],
        "J":[3,3,3,4],
        "S":[3,4],
        "Z":[3,4],
        "T":[3,3,3,4],
        "I":[3,5]
        }
    def min_path (self, zoid, col, rot):
        #calculate rotations
        rots = 0
        if int(rot) != 0:
            rots = 2 if rot == 2 else 1

        #calculate translations
        trans = abs(self.zoid_col_offset[zoid][int(rot)] - int(col))

        return rots, trans

    def log_universal_header( self ):
        head = "\t".join( map(str, self.fixed_header) ) + "\n"
        self.unifile.write( head )
        if self.ep_log:
            self.epfile.write( head )
        if self.game_log:
            self.gamefile.write( head )


    def log_universal( self, event_type, loglist, complete = False, evt_id = False, evt_data1 = False, evt_data2 = False, eyes = False, features = False):
        data = []
        def logit(val, key):
            data.append(val if key in loglist else "")

        #["ts","event_type"]
        data.append(get_time() - self.starttime)
        data.append(event_type)

        #["SID","session","game_number","game_type","episode_number","level","score","lines_cleared"
        #                "completed","game_duration","avg_ep_duration","zoid_sequence"]
        logit(self.SID, "SID")
        logit(self.ECID, "ECID")
        logit(self.session, "session")
        logit(self.game_type, "game_type")
        logit(self.game_number, "game_number")
        logit(self.episode_number, "episode_number")
        logit(self.level, "level")
        logit(self.score, "score")
        logit(self.lines_cleared, "lines_cleared")
        logit(complete, "completed")
        logit(get_time() - self.game_start_time, "game_duration")
        logit((get_time() - self.game_start_time) / (self.episode_number + 1), "avg_ep_duration")
        logit("'%s'" % json.dumps( self.zoid_buff ), "zoid_sequence")

        #["evt_id","evt_data1","evt_data2"]
        data.append(evt_id if evt_id else "")
        data.append(evt_data1 if evt_data1 else "")
        data.append(evt_data2 if evt_data2 else "")

        #["curr_zoid","next_zoid","danger_mode"
        #   "evt_sequence","rots","trans","path_length",
        #   "min_rots","min_trans","min_path",
        #  "min_rots_diff","min_trans_diff","min_path_diff",
        #   "u_drops","s_drops","prop_u_drops",
        #   "initial_lat","drop_lat","avg_lat",
        #   "tetrises_game","tetrises_level"]
        logit(self.curr_zoid.type, "curr_zoid")
        logit(self.next_zoid.type, "next_zoid")
        logit(self.danger_mode, "danger_mode")
        logit(json.dumps(self.evt_sequence), "evt_sequence")
        logit(self.rots, "rots")
        logit(self.trans, "trans")
        logit(self.rots + self.trans, "path_length")
        logit(self.min_rots, "min_rots")
        logit(self.min_trans, "min_trans")
        logit(self.min_rots + self.min_trans, "min_path")
        logit(self.rots - self.min_rots, "min_rots_diff")
        logit(self.trans - self.min_trans, "min_trans_diff")
        logit((self.rots - self.min_rots) + (self.trans - self.min_trans), "min_path_diff")
        logit(self.u_drops, "u_drops")
        logit(self.s_drops, "s_drops")
        logit(self.prop_drop, "prop_u_drops")
        logit(self.initial_lat, "initial_lat")
        logit(self.drop_lat, "drop_lat")
        logit(self.avg_latency, "avg_lat")
        logit(self.tetrises_game, "tetrises_game")
        logit(self.tetrises_level, "tetrises_level")
        logit(self.agree, "agree")

        #["delaying","dropping","zoid_rot","zoid_col","zoid_row"]
        logit(self.needs_new_zoid, "delaying")
        logit(self.interval_toggle, "dropping")
        logit(self.curr_zoid.rot, "zoid_rot")
        logit(self.curr_zoid.get_col(), "zoid_col")
        logit(self.curr_zoid.get_row(), "zoid_row")
        #logit(12345.0, "my_chris")



        #["board_rep","zoid_rep"]
        logit("'%s'" % json.dumps( self.board ), "board_rep")
        logit("'%s'" % json.dumps( self.zoid_in_board() ), "zoid_rep")



        #["smi_ts","smi_eyes",
        #  "smi_samp_x_l","smi_samp_x_r","smi_samp_y_l","smi_samp_y_r",
        #  "smi_diam_x_l","smi_diam_x_r","smi_diam_y_l","smi_diam_y_r",
        #  "smi_eye_x_l","smi_eye_x_r","smi_eye_y_l","smi_eye_y_r","smi_eye_z_l","smi_eye_z_r",
        #  "fix_x","fix_y"]

        #logit("CHRIS", "CHRIS")
        #Successfully adds a column after zoid_rep
        #data.append("CHRIS")

        if self.args.eyetracker:
            if eyes:
                for i in self.inResponse:
                    data.append(i)
                if self.fix:
                    data.append(self.fix[0])
                    data.append(self.fix[1])
                else:
                    data.append(None)
                    data.append(None)
            else:
                for i in range(0, 18):
                    data.append("")



        if features or (event_type == "GAME_EVENT" and evt_id == "KEYPRESS" and evt_data1 == "PRESS" and self.episode_number > 0):
           factor1  = 0.663025211
           factor2  = 0.213249645
           factor3  = 0.035625071
           factor4  = 0.03242133
           factor5  = 0.024535821
           factor6  = 0.015835537
           factor7  = 0.01085867
           factor8  = 0.002856802
           factor9  = 0.001980513
           factor10 = 0.001189963
           factor11 = 0.000694257
           factor12 = 0.000534684

           z_answer =  self.features["pattern_div"]*(0.064355*factor1 + 0.003902*factor2 + 0.002922*factor6 + 0.002172*factor10 + 0.000086528*factor11 + 0.000236992*factor12)
           z_answer += self.features["mean_ht"]*(0.193209*factor1 + 0.009624*factor2 + 0.000498*factor6 + 0.000686*factor8 + 0.00027*factor9 + 0.000147968*factor11 + 0.000074263*factor12)
           z_answer += self.features["max_ht"]*(0.149666*factor1 + 0.011828*factor2 + 0.004558*factor6 + 0.000899*factor8 + 0.000083232*factor11 + 0.000081648*factor12)
           z_answer += self.features["weighted_cells"]*(0.179315*factor1 + 0.010358*factor2 + 0.001098*factor8 + 0.000543*factor9 + 0.000207088*factor12)
           z_answer += self.features["min_ht"]*(0.207176*factor1 + 0.003856*factor2 + 0.00081*factor6 + 0.00103*factor10)
           z_answer += self.features["row_trans"]*(0.154613*factor1 + 0.012476*factor2 + 0.006403*factor6 + 0.000112*factor10 + 0.000329672*factor11)
           z_answer += self.features["pits"]*(0.222091*factor1 + 0.000163*factor9)
           z_answer += self.features["pit_rows"]*(0.224396*factor1)
           z_answer += self.features["landing_height"]*(0.153465*factor1 + 0.009769*factor2 + 0.000506*factor6 + 0.001861*factor7 + 0.000789*factor8 + 0.000363*factor9 + 0.000170528*factor11)
           z_answer += self.features["col_trans"]*(0.21254*factor1 + 0.000677047*factor12)
           z_answer += self.features["pit_depth"]*(0.211193*factor1 + 0.000346*factor10 + 0.000091592*factor11)
           z_answer += self.features["lumped_pits"]*(0.21209*factor1 + 0.000499023*factor12)
           z_answer += self.features["cd_9"]*(0.042487*factor2 + 0.000971*factor6 + 0.002238*factor8 + 0.002022*factor9)
           z_answer += self.features["wells"]*(0.121581*factor2 + 0.000481*factor6 + 0.000146*factor10 + 0.000329672*factor11)
           z_answer += self.features["deep_wells"]*(0.120814*factor2 + 0.000625*factor6 + 0.000107648*factor11)
           z_answer += self.features["max_well"]*(0.122608*factor2 + 0.000524*factor6)
           z_answer += self.features["cuml_wells"]*(0.119032*factor2 + 0.000464*factor6)
           z_answer += self.features["jaggedness"]*(0.044479*factor2 + 0.019288*factor6 + 0.000362*factor7 + 0.000263*factor9 + 0.000146*factor10 + 0.000658952*factor11)
           z_answer += self.features["max_diffs"]*(0.031886*factor2 + 0.013543*factor6 + 0.001201*factor8 + 0.001194*factor9)
           z_answer += self.features["cd_1"]*(0.038496*factor2 + 0.001007*factor6 + 0.002238*factor8 + 0.001337*factor9 + 0.000147968*factor11)
           #######z_answer += self.features["resp_lat"]*0.0152810854045063
           z_answer += self.features["matches"]*(0.002177*factor2 + 0.001273*factor4 + 0.016701*factor7)
           z_answer += self.features["cd_7"]*(0.000424*factor9)
           z_answer += self.features["cd_8"]*(0.000341*factor8)
           z_answer += self.features["cd_2"]*(0.000152352*factor11)
           z_answer += self.features["d_max_ht"]*(0.001488*factor2 + 0.012226*factor7)
           z_answer += self.features["d_pits"]*(0.001488*factor2 + 0.001277*factor7)

           z_answer += self.prop_drop*(0.018262*factor1 + 0.003221*factor3 + 0.011608*factor4 + 0.001713*factor5 + 0.002048*factor7)
           z_answer += self.rots*(0.050161*factor3 + 0.00063*factor4 + 0.000619*factor5)
           z_answer += (self.rots - self.min_rots)*(0.049324*factor3 + 0.000584*factor4 + 0.000557*factor5)
           #print("{:3d}".format(self.rots) + " " + "{:3d}".format(self.min_rots))
           if self.drop_lat<.001:
              z_answer += int(1000 * (get_time() - self.ep_starttime))*(0.005354*factor3 + 0.021913*factor4 + 0.002672*factor5)
              #print("{:0.1f}".format(get_time()))
              #print("   " + "{:0.3f}".format(self.ep_starttime) + "  " + "{:0.1f}".format(int(1000 * (get_time() - self.ep_starttime))*0.0124717621894591))
           else:
              z_answer += self.drop_lat*(0.005354*factor3 + 0.021913*factor4 + 0.002672*factor5)

           z_answer += (self.trans - self.min_trans)*(0.001156*factor3 + 0.035219*factor5 + 0.000446*factor7)
           z_answer += self.avg_latency*(0.001608*factor3 + 0.026717*factor4 + 0.000335*factor7)
           z_answer += self.trans*(0.000618*factor3 + 0.037343*factor5)
           z_answer += self.initial_lat*(0.013463*factor4 + 0.000403*factor7)

           self.features["z_answer"] = z_answer
           self.newscore = z_answer

           self.metascore = (self.metascore*self.metaticks + z_answer)/(self.metaticks+1)
           self.metaticks = self.metaticks+1
           self.features["z_metascore"] = self.metascore

           #self.scorefile.write(repr(z_answer)+"\n")

           self.roll_avg.append(self.features["z_answer"])
           while len(self.roll_avg) > 3:
               self.roll_avg.pop(0)

           if len(self.roll_avg) == 3:
              roll_sum = 0
              #print('Chris 1')
              for roll_val in self.roll_avg:
                 #print('   Test1: ' + str(roll_val) + ' - Test2: ' + str(roll_sum))
                 roll_sum += roll_val
              self.features["z_rollavg"] = roll_sum/3

           else:
              self.features["z_rollavg"] = 0.0

           logit(self.newscore, "newscore")
           logit(self.metascore, "metascore")
           logit(self.features["z_rollavg"], "rollavg")

           #print(f'So far... z_answer={self.features["z_answer"]:.4f}, z_rolling={self.features["z_rollavg"]:.4f}.')
           if features:
              for f in self.features_set:
                  data.append(self.features[f])
           else:
              for f in self.features_set:
                  data.append(self.features[f])

        else:
            for f in self.features_set:
                data.append("")

        #print('How often does this happen')

        out = "\t".join(map(str,data)) + "\n"

        self.unifile.write(out)

        if self.ep_log:
            if event_type == "EP_SUMM" or event_type == "GAME_SUMM":
                self.epfile.write(out)
        if self.game_log:
            if event_type == "GAME_SUMM":
                self.gamefile.write(out)



    def log_eye_sample( self ):
        if self.fixed_log:
            loglist = ["SID","ECID","session","game_type","game_number","episode_number"]
            self.log_universal("EYE_SAMP",loglist,eyes=True)
        else:
            data = [":ts", get_time() - self.starttime,
                    ":event_type", "EYE_SAMP",
                    ":smi_ts", self.inResponse[0],
                    ":smi_eyes", self.inResponse[1],
                    ":smi_samp_x_l", self.inResponse[2],
                    ":smi_samp_x_r", self.inResponse[3],
                    ":smi_samp_y_l", self.inResponse[4],
                    ":smi_samp_y_r", self.inResponse[5],
                    ":smi_diam_x_l", self.inResponse[6],
                    ":smi_diam_x_r", self.inResponse[7],
                    ":smi_diam_y_l", self.inResponse[8],
                    ":smi_diam_y_r", self.inResponse[9],
                    ":smi_eye_x_l", self.inResponse[10],
                    ":smi_eye_x_r", self.inResponse[11],
                    ":smi_eye_y_l", self.inResponse[12],
                    ":smi_eye_y_r", self.inResponse[13],
                    ":smi_eye_z_l", self.inResponse[14],
                    ":smi_eye_z_r",  self.inResponse[15],]
            if self.fix:
                    data += [":fix_x", self.fix[0], ":fix_y", self.fix[1]]
            else:
                    data += [":fix_x", None, ":fix_y", None]
            self.unifile.write( "\t".join( map(str, data) ) + "\n" )

    def log_episode( self ):
        self.update_stats_move( self.curr_zoid.get_col(), self.curr_zoid.rot, self.curr_zoid.get_row())
        if self.fixed_log:
            loglist = ["SID","ECID","session","game_type","game_number","episode_number",
                        "level","score","lines_cleared",
                        "curr_zoid","next_zoid","danger_mode",
                        "zoid_rot","zoid_col","zoid_row",
                        "board_rep","zoid_rep","evt_sequence","rots","trans","path_length",
                        "newscore","metascore","rollavg",
                        "min_rots","min_trans","min_path",
                        "min_rots_diff","min_trans_diff","min_path_diff",
                        "u_drops","s_drops","prop_u_drops",
                        "initial_lat","drop_lat","avg_lat",
                        "tetrises_game","tetrises_level",
                        "agree","newscore","metascore","rollavg"]
            self.log_universal("EP_SUMM",loglist,features = True)
        else:
            data = [":ts", get_time() - self.starttime,
                    ":event_type", "EP_SUMM",
                    ":SID", self.SID,
                    ":session", self.session,
                    ":game_number", self.game_number,
                    ":episode_number", self.episode_number,
                    ":level", self.level,
                    ":score",self.score,
                    ":lines_cleared", self.lines_cleared]

            data += [":curr_zoid", self.curr_zoid.type,
                     ":next_zoid", self.next_zoid.type,
                     ":danger_mode", self.danger_mode,
                     ":zoid_rot", self.curr_zoid.rot,
                     ":zoid_col", self.curr_zoid.get_col(),
                     ":zoid_row", self.curr_zoid.get_row(),
                     ":board_rep", "'%s'" % json.dumps( self.board ),
                     ":zoid_rep", "'%s'" % json.dumps( self.zoid_in_board() )]


            #board statistics
            for f in self.features_set:
                data += [":"+f, self.features[f]]


            self.unifile.write("\t".join(map(str,data)) + "\n")
            if self.ep_log:
                self.epfile.write("\t".join(map(str,data)) + "\n")


    def log_gameresults( self, complete = True ):
        if self.fixed_log:
            loglist = ["SID","ECID","session","game_type","game_number","episode_number",
                        "level","score","lines_cleared","completed",
                        "game_duration","avg_ep_duration","zoid_sequence","newscore","metascore","rollavg"]
            self.log_universal("GAME_SUMM",loglist, complete = complete)
        else:
            data = [":ts", get_time() - self.starttime,
                    ":event_type", "GAME_SUMM",
                    ":SID", self.SID,
                    ":session", self.session,
                    ":game_type", self.game_type,
                    ":game_number", self.game_number,
                    ":episode_number", self.episode_number,
                    ":level", self.level,
                    ":score", self.score,
                    ":lines_cleared", self.lines_cleared,
                    ":completed", complete,
                    ":game_duration", get_time() - self.game_start_time,
                    ":avg_ep_duration", (get_time() - self.game_start_time)/(self.episode_number+1),
                    ":zoid_sequence", "'%s'" % json.dumps( self.zoid_buff )]

            self.unifile.write("\t".join(map(str,data)) + "\n")
            if self.ep_log:
                self.epfile.write("\t".join(map(str,data)) + "\n")
            if self.game_log:
                self.gamefile.write("\t".join(map(str,data)) + "\n")

        message = ["Game " , str(self.game_number) , ":\n" ,
                    "\tScore: " , str(self.score) , "\n" ,
                    "\tLevel: " , str(self.level) , "\n" ,
                    "\tLines: " , str(self.lines_cleared) , "\n" ,
                    "\tZoids: " , str(self.episode_number) , "\n" ,
                    "\tSID: " , str(self.SID) , "\n" ,
                    "\tComplete: ", str(complete), "\n",
                    "\tSession: " + str(self.session) , "\n" ,
                    "\tGame Type: " + str(self.game_type) + "\n",
                    "\tGame duration:" + str(get_time() - self.game_start_time) + "\n",
                    "\tAvg Ep duration:" + str((get_time() - self.game_start_time)/(self.episode_number+1)) + "\n"
                    ]
        message = "".join(message)
        if complete:
            self.game_scores += [self.score]
        print(message)


    #log a game event
    def log_game_event( self, id, data1 = "", data2 = "" ):
        if self.fixed_log:
            loglist = ["SID","ECID","session","game_type","game_number","episode_number",
                        "level","score","lines_cleared",
                        "curr_zoid","next_zoid","danger_mode",
                        "delaying","dropping",
                        "newscore","metascore","rollavg",
                        "zoid_rot","zoid_col","zoid_row"]
#            loglist = ["SID","ECID","session","game_type","game_number","episode_number",
#                        "level","score","lines_cleared",
#                        "curr_zoid","next_zoid","danger_mode",
#                        "zoid_rot","zoid_col","zoid_row",
#                        "board_rep","zoid_rep","evt_sequence","rots","trans","path_length",
#                        "min_rots","min_trans","min_path",
#                        "min_rots_diff","min_trans_diff","min_path_diff",
#                        "u_drops","s_drops","prop_u_drops",
#                        "initial_lat","drop_lat","avg_lat",
#                        "tetrises_game","tetrises_level",
#                        "agree","z_answer","z_rollavg","z_metascore"]
            self.log_universal("GAME_EVENT", loglist, evt_id = id, evt_data1 = data1, evt_data2 = data2)
        else:
            out = [":ts", get_time() - self.starttime,
                    ":event_type", 'GAME_EVENT',
                   ":evt_id", id,
                   ":evt_data1", data1,
                   ":evt_data2", data2]
            outstr = "\t".join( map( str, out ) ) + "\n"
            self.unifile.write( outstr )





    #log the world state
    def log_world( self ):
        if self.fixed_log:
            loglist = ["SID","ECID","session","game_type","game_number","episode_number",
                        "level","score","lines_cleared","danger_mode",
                        "delaying","dropping","curr_zoid","next_zoid",
                        "zoid_rot","zoid_col","zoid_row","board_rep","zoid_rep",
                        "newscore","metascore","rollavg"]
            self.log_universal("GAME_STATE", loglist)


        else:
            #session and types
            data = [":ts", get_time() - self.starttime,
                    ":event_type", "GAME_STATE"]

            #gameplay values
            data += [":delaying", self.needs_new_zoid,
                     ":dropping", self.interval_toggle,
                     ":curr_zoid", self.curr_zoid.type,
                     ":next_zoid", self.next_zoid.type,
                     ":zoid_rot", self.curr_zoid.rot,
                     ":zoid_col", self.curr_zoid.get_col(),
                     ":zoid_row", self.curr_zoid.get_row(),
                     ":board_rep", "'%s'" % json.dumps( self.board ),
                     ":zoid_rep", "'%s'" % json.dumps( self.zoid_in_board() )]


            self.unifile.write( "\t".join( map( str, data ) ) + "\n" )


    def zoid_in_board( self ):
        zoid = self.curr_zoid.get_shape()
        z_x = self.curr_zoid.col
        z_y = self.game_ht - self.curr_zoid.row

        board = []
        for y in range(0,self.game_ht):
            line = []
            for x in range(0,self.game_wd):
                line.append(0)
            board.append(line)

        for i in range(0,len(zoid)):
            for j in range(0,len(zoid[0])):
                if i + z_y >= 0 and i + z_y < len(board):
                    if j + z_x >= 0 and j + z_x < len(board[0]):
                        board[i + z_y][j + z_x] = zoid[i][j]

        return board




    #####
    # write .history file
    def log_history( self ):

        def hwrite( name ):
            self.histfile.write(name + ": " + str(vars(self)[name]) + "\n")
            #self.unifile.write(":ts\t" + str(get_time()-self.starttime) +  "\t:event_type\t" + "SETUP_EVENT" + "\t" + ":" + name + "\t" + str(vars(self)[name]) + "\n")
            self.log_game_event(name, data1 = vars(self)[name], data2 = "setup")
        def hwrite2( name, val ):
            self.histfile.write(name + ": " + str(val) + "\n")
            #self.unifile.write(":ts\t" + str(get_time()-self.starttime) +  "\t:event_type\t" + "SETUP_EVENT" + "\t" + ":" + name + "\t" + str(val) + "\n")
            self.log_game_event(name, data1 = val, data2 = "setup")

        #capture all static variables

        hwrite("SID")
        hwrite("RIN")
        hwrite("ECID")
        hwrite("game_type")
        hwrite2("Start time", self.starttime)
        hwrite2("Session" ,self.session)
        hwrite("random_seeds")
        hwrite("seed_order")
        hwrite2("Log-Version" ,self.LOG_VERSION)
        hwrite2("Fixed-length logging" ,self.fixed_log)
        hwrite2("Eyetracker" ,self.args.eyetracker)
        hwrite("distance_from_screen")

        self.histfile.write("\nManipulations:\n")
        hwrite("inverted")
        hwrite("tetris_zoids")
        hwrite("pentix_zoids")
        hwrite("tiny_zoids")
        hwrite("gravity")
        hwrite("undo")
        hwrite("visible_board")
        hwrite("visible_zoid")
        hwrite("board_echo_placed")
        hwrite("board_echo_lc")
        hwrite("look_ahead")
        hwrite("far_next")
        hwrite("next_dim")
        hwrite("next_dim_alpha")
        hwrite("next_mask")
        hwrite("board_mask")
        hwrite("ghost_zoid")
        hwrite("zoid_slam")
        hwrite("keep_zoid")
        hwrite("wall_kicking")
        hwrite("feedback_mode")
        hwrite("dimtris")
        hwrite("dimtris_alphas")
        hwrite("gridlines_x")
        hwrite("gridlines_y")
        hwrite("gridlines_color")
        hwrite("grace_period")
        hwrite("grace_refresh")
        hwrite("pause_enabled")
        hwrite("das_chargeable")
        hwrite("das_reversible")
        hwrite("bg_color")
        hwrite("border_color")
        hwrite("kept_bgc")

        self.histfile.write("\nMechanics:\n")
        hwrite("continues")
        hwrite("game_ht")
        hwrite("game_wd")
        hwrite("fullscreen")
        hwrite("fps")
        hwrite("tps")
        hwrite("das_delay")
        hwrite("das_repeat")
        hwrite("are_delay")
        hwrite("lc_delay")
        hwrite("lines_per_lvl")
        hwrite("intervals")
        hwrite("drop_interval")
        hwrite("scoring")
        hwrite("drop_bonus")
        hwrite("seven_bag_switch")
        hwrite("gameover_fixcross")
        hwrite("gameover_fixcross_size")
        hwrite("gameover_fixcross_width")
        hwrite("gameover_fixcross_frames")
        hwrite("gameover_fixcross_tolerance")
        hwrite("gameover_fixcross_frames_tolerance")
        hwrite("gameover_fixcross_color")
        hwrite("gameover_fixcross_timeout")
        hwrite("calibration_points")
        hwrite("calibration_auto")
        hwrite("validation_accuracy")
        hwrite("automated_revalidation")

        self.histfile.write("\nLayout:\n")
        hwrite2("Screen X",self.screeninfo.current_w)
        hwrite2("Screen Y",self.screeninfo.current_h)
        hwrite2("worldsurf_rect.width",self.worldsurf_rect.width)
        hwrite2("worldsurf_rect.height",self.worldsurf_rect.height)
        hwrite2("gamesurf_rect.top",self.gamesurf_rect.top)
        hwrite2("gamesurf_rect.left",self.gamesurf_rect.left)
        hwrite2("gamesurf_rect.width",self.gamesurf_rect.width)
        hwrite2("gamesurf_rect.height",self.gamesurf_rect.height)
        hwrite2("nextsurf_rect.top",self.nextsurf_rect.top)
        hwrite2("nextsurf_rect.left",self.nextsurf_rect.left)
        hwrite2("nextsurf_rect.width",self.nextsurf_rect.width)
        hwrite2("nextsurf_rect.height",self.nextsurf_rect.height)
        if self.keep_zoid:
            hwrite2("keptsurf_rect.top",self.keptsurf_rect.top)
            hwrite2("keptsurf_rect.left",self.keptsurf_rect.left)
            hwrite2("keptsurf_rect.width",self.keptsurf_rect.width)
            hwrite2("keptsurf_rect.height",self.keptsurf_rect.height)
        hwrite("side")
        hwrite("score_lab_left")
        hwrite("lines_lab_left")
        hwrite("level_lab_left")
        hwrite("newscore_lab_left")
        hwrite("score_left")
        hwrite("lines_left")
        hwrite("level_left")
        hwrite("newscore_left")
        self.histfile.write("\n")
        self.histfile.close()


















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


    ####
    #  Drawing
    ####

    #draw text to the screen
    def draw_text( self, text, font, color, loc, surf, justify = "center" ):
        t = font.render( text, True, color )
        tr = t.get_rect()
        setattr( tr, justify, loc )
        surf.blit( t, tr )
        return tr
    ###

    #draw any text box
    def draw_text_box( self ):
        pygame.draw.rect( self.worldsurf, self.message_box_color, self.gamesurf_msg_rect, 0 )

    #when eyetracking is present, draw the fixations
    def draw_fix( self ):
        if self.fix and self.draw_fixation:
            pygame.draw.circle( self.worldsurf, self.NES_colors[self.level % len( self.NES_colors )][0], ( int( self.fix[0] ), int( self.fix[1] ) ), 23, 0 )
            pygame.draw.circle( self.worldsurf, (255,255,255), ( int( self.fix[0] ), int( self.fix[1] ) ), 23, 3 )
        if len( World.gaze_buffer ) > 1:
            if self.draw_samps:
                #draw right eye first, then left
                pygame.draw.lines( self.worldsurf, ( 0, 255, 255 ), False, World.gaze_buffer2, 1 )
                pygame.draw.lines( self.worldsurf, ( 255, 255, 255 ), False, World.gaze_buffer, 1 )
            if self.draw_avg or self.draw_err:
                if self.draw_err:
                    avg_conf = int((self.i_x_conf + self.i_y_conf) * .5)
                    avg_col = max(0, 255 - avg_conf)
                    if self.i_x_conf >= 2 and self.i_y_conf >= 2:
                        conf_rect = pygame.Rect(int(self.i_x_avg - .5*(self.i_x_conf)), int(self.i_y_avg - .5 * (self.i_y_conf)), int(self.i_x_conf), int(self.i_y_conf))
                        pygame.draw.ellipse( self.worldsurf, (avg_col, avg_col, avg_col), conf_rect, 0)
                    else:
                        pygame.draw.circle( self.worldsurf, (255,255,255), (self.i_x_avg, self.i_y_avg), 1, 0)
                if self.draw_avg:
                    pygame.draw.circle( self.worldsurf, (255,255,255), ( self.i_x_avg2, self.i_y_avg2 ), 10, 0 )
                    pygame.draw.circle( self.worldsurf, self.NES_colors[self.level % len( self.NES_colors )][0], ( self.i_x_avg, self.i_y_avg ), 10, 3 )

                    pygame.draw.circle( self.worldsurf, (200,200,200), ( (self.i_x_avg2 + self.i_x_avg) / 2, (self.i_y_avg2 + self.i_y_avg) / 2 ), 5, 0 )

                    pygame.draw.circle( self.worldsurf, (255,255,255), ( self.i_x_avg, self.i_y_avg ), 10, 0 )
                    pygame.draw.circle( self.worldsurf, self.NES_colors[self.level % len( self.NES_colors )][1], ( self.i_x_avg, self.i_y_avg ), 10, 3 )

        if self.spotlight:
            if self.i_x_avg and self.i_y_avg:
                self.spotsurf_rect.center = (self.i_x_avg, self.i_y_avg)
            self.worldsurf.blit( self.spotsurf, self.spotsurf_rect )

    #pre-renders reusable block surfaces
    def generate_block( self, size, lvl, type ):
        if self.color_mode == "STANDARD":
            bg = pygame.Surface( ( size, size ) )
            c = self.STANDARD_colors[type]
            lvl_offset = lvl * 15
            bg_off = -40 + lvl_offset
            fg_off = 40 - lvl_offset
            bgc = tuple([min(max(a + b,0),255) for a, b in zip(c, [bg_off]*3)])
            fgc = tuple([min(max(a + b,0),255) for a, b in zip(c, [fg_off]*3)])
            bg.fill( bgc )
            fg = pygame.Surface( ( size - self.border * 2, size - self.border * 2 ) )
            fg.fill( fgc )
            fgr = fg.get_rect()
            fgr.topleft = ( self.border, self.border )
            bg.blit( fg, fgr )
        else:
            if type == 0:
                bgc = self.NES_colors[lvl][0]
                fgc = ( 255, 255, 255 )
            elif type == 1:
                #if self.color_mode == "other":
                    #bgc = self.NES_colors[lvl][0]
                    #fgc = self.NES_colors[lvl][0]
                if self.color_mode == "REMIX":
                    bgc = self.NES_colors[lvl][1]
                    fgc = self.NES_colors[lvl][0]
            elif type == 2:
                #if self.color_mode == "other":
                    #bgc = self.NES_colors[lvl][1]
                    #fgc = self.NES_colors[lvl][1]
                if self.color_mode == "REMIX":
                    bgc = self.NES_colors[lvl][0]
                    fgc = self.NES_colors[lvl][1]
            bg = pygame.Surface( ( size, size ) )
            bg.fill( bgc )
            fg = pygame.Surface( ( size - self.border * 2, size - self.border * 2 ) )
            fg.fill( fgc )
            fgr = fg.get_rect()
            fgr.topleft = ( self.border, self.border )
            bg.blit( fg, fgr )
            """
            if self.color_mode == "other":
                sheen = self.border - 1
                s1 = pygame.Surface( ( sheen, sheen ) )
                s1.fill( ( 255, 255, 255 ) )
                s1r = s1.get_rect()
                s2 = pygame.Surface( ( 2 * sheen, sheen ) )
                s2.fill( ( 255, 255, 255 ) )
                s2r = s2.get_rect()
                bg.blit( s1, ( s1r.left + 1, s1r.top + 1 ) )
                bg.blit( s2, ( s2r.left + 1 + sheen, s2r.top + 1 + sheen ) )
                bg.blit( s1, ( s1r.left + 1 + sheen, s1r.top + 1 + 2 * sheen ) )
            """
            if self.color_mode == "REMIX":
                sheen = self.border
                s = pygame.Surface( ( sheen,sheen ) )
                s.fill( ( 255, 255, 255 ) )
                sr = s.get_rect()
                sr.topleft = fgr.topleft
                bg.blit( s, sr.topleft )
        pygame.draw.rect( bg, self.bg_color, bg.get_rect(), 1 )
        return bg

    #draw a single square on the board
    def draw_square( self, surface, left, top, color_id , alpha = 255, gray = False):
        lvl = self.level % len( self.NES_colors )
        #if self.color_mode == "other":
        if self.color_mode == "REMIX":
            block = self.blocks[lvl][self.block_color_type[color_id - 1]]
        else:
            block = self.blocks[lvl][color_id] if not gray else self.gray_block

        block.set_alpha(alpha)
        surface.blit( block, ( left, top ) )
    ###

    # Draw the blocks of the current surface as-they-are.
    def draw_blocks( self, obj, surf, rect, x = 0, y = 0, resetX = False, alpha = 255, gray = False):
        ix = x
        iy = y
        for i in obj:
            for j in i:
                if j != 0:
                    self.draw_square( surf, ix, iy, color_id = j, alpha = alpha, gray = gray )
                ix += self.side
            if resetX:
                ix = 0
            else:
                ix = x
            iy += self.side

        if self.inverted:
            self.worldsurf.blit( pygame.transform.flip(surf, False, True), rect)
        else:
            self.worldsurf.blit( surf, rect )

    #draw the game while paused
    def draw_pause( self ):

        if self.show_high_score:
            self.draw_text( "High:", self.scores_font, ( 210, 210, 210 ), self.high_lab_left, self.worldsurf, "midleft" )
            self.draw_text( str( self.high_score ), self.scores_font, ( 210, 210, 210 ), self.high_left, self.worldsurf, "midright" )

        self.draw_text( "Game %d" % self.game_number, self.intro_font, ( 196, 196, 196 ), ( self.gamesurf_rect.centerx, self.gamesurf_rect.top / 2 ), self.worldsurf )
        self.draw_text( "Score:", self.scores_font, ( 210, 210, 210 ), self.score_lab_left, self.worldsurf, "midleft" )
        self.draw_text( "Lines:", self.scores_font, ( 210, 210, 210 ), self.lines_lab_left, self.worldsurf, "midleft" )
        self.draw_text( "Level:", self.scores_font, ( 210, 210, 210 ), self.level_lab_left, self.worldsurf, "midleft" )
        self.draw_text( str( self.score ), self.scores_font, ( 210, 210, 210 ), self.score_left, self.worldsurf, "midright" )
        self.draw_text( str( self.lines_cleared ), self.scores_font, ( 210, 210, 210 ), self.lines_left, self.worldsurf, "midright" )
        self.draw_text( str( self.level ), self.scores_font, ( 210, 210, 210 ), self.level_left, self.worldsurf, "midright" )
        self.draw_newscore()

        self.draw_borders()
        self.draw_text( "PAUSED", self.pause_font, ( 210, 210, 210 ), self.worldsurf_rect.center, self.worldsurf )

    #draw the underlying game board the current zoid interacts with
    def draw_board( self, alpha = 255):
        echo = (self.board_echo_placed and self.are_counter > 0) or (self.board_echo_lc and self.lc_counter > 0)
        if self.visible_board or echo:
            if not self.board_mask or not self.mask_toggle:
                if self.dimtris and not echo:
                    alpha = self.dimtris_alphas[min(self.level, len(self.dimtris_alphas)-1)]
                self.draw_blocks( self.board, self.gamesurf, self.gamesurf_rect, resetX = True, alpha = alpha, gray = self.gray_board)
            else:
                self.gamesurf.fill( self.mask_color )
                self.worldsurf.blit( self.gamesurf , self.gamesurf_rect)

    #draw the current zoid at its current location on the board
    def draw_curr_zoid( self ):
        if self.visible_zoid:
            if not self.board_mask or not self.mask_toggle:
                self.draw_blocks( self.curr_zoid.get_shape(), self.gamesurf, self.gamesurf_rect, self.curr_zoid.col * self.side, ( self.game_ht - self.curr_zoid.row ) * self.side, gray = self.gray_zoid)
                if self.ghost_zoid:
                    self.draw_blocks( self.curr_zoid.get_shape(), self.gamesurf, self.gamesurf_rect, self.curr_zoid.col * self.side, ( self.game_ht - self.curr_zoid.to_bottom()) * self.side, alpha = self.ghost_alpha, gray = self.gray_zoid )

                if self.hint_toggle and self.solved:
                    if not self.hint_context:
                        self.draw_blocks( self.curr_zoid.get_shape(rot = self.solved_rot), self.gamesurf, self.gamesurf_rect, self.solved_col * self.side, ( self.game_ht - self.solved_row) * self.side, alpha = self.ghost_alpha, gray = self.gray_zoid )
                if self.hint_context and self.solved:
                    hint_col_agree = abs(self.solved_col - self.curr_zoid.col) <= self.hint_context_col_tol
                    hint_agree = self.solved_rot == self.curr_zoid.rot and hint_col_agree
                    if hint_agree:
                        self.draw_blocks( self.curr_zoid.get_shape(rot = self.solved_rot), self.gamesurf, self.gamesurf_rect, self.solved_col * self.side, ( self.game_ht - self.solved_row) * self.side, alpha = self.ghost_alpha, gray = self.gray_zoid )

    def draw_AAR_zoids( self ):
        if self.AAR_curr_zoid_hl:
            self.draw_blocks( self.curr_zoid.get_shape(), self.gamesurf, self.gamesurf_rect, self.curr_zoid.col * self.side, ( self.game_ht - self.curr_zoid.row ) * self.side, alpha = self.AAR_dim * 2, gray = self.gray_zoid)
        if self.solved:
            self.draw_blocks( self.curr_zoid.get_shape(rot = self.solved_rot), self.gamesurf, self.gamesurf_rect, self.solved_col * self.side, ( self.game_ht - self.solved_row) * self.side, alpha = 255, gray = self.gray_zoid)


    #draw the next zoid inside the next box
    def draw_next_zoid( self ):
        if self.look_ahead > 0:
            if not self.next_mask or self.mask_toggle:
                next_rep = self.next_zoid.get_next_rep()
                vert = (self.next_size - float(len(next_rep))) / 2.0
                horiz = (self.next_size - float(len(next_rep[0]))) / 2.0
                self.draw_blocks( next_rep, self.nextsurf, self.nextsurf_rect, int( self.side * (horiz + .25) ), int( self.side * (vert + .25) ), alpha = self.next_alpha, gray = self.gray_next)
            else:
                self.nextsurf.fill( self.mask_color )
                self.worldsurf.blit( self.nextsurf , self.nextsurf_rect )

    def draw_kept_zoid( self ):
        if self.kept_zoid != None:
            kept_rep = self.kept_zoid.get_next_rep()
            vert = (self.next_size - float(len(kept_rep))) / 2.0
            horiz = (self.next_size - float(len(kept_rep[0]))) / 2.0
            self.draw_blocks( kept_rep, self.keptsurf, self.keptsurf_rect, int( self.side * (horiz + .25) ), int( self.side * (vert + .25) ), gray = self.gray_kept)
        else:
            self.draw_blocks( Zoid.next_reps['none'], self.keptsurf, self.keptsurf_rect, 0, 0, gray = self.gray_kept)

    #draw the introduction screen
    def draw_intro( self ):
        self.worldsurf.fill( ( 255, 255, 255 ) )
        logo_rect = self.logo.get_rect()
        logo_rect.centerx = self.worldsurf_rect.centerx
        logo_rect.centery = self.worldsurf_rect.centery - self.worldsurf_rect.centery / 6
        self.worldsurf.blit( self.logo, logo_rect )

        cwl_rect = self.cwl_tag.get_rect()
        #cwl_rect.left = logo_rect.left
        #cwl_rect.top = logo_rect.top + logo_rect.height * 2 / 3
        cwl_rect.bottom = logo_rect.bottom
        cwl_rect.left = logo_rect.left
        self.worldsurf.blit( self.cwl_tag, cwl_rect )

        rpi_rect = self.rpi_tag.get_rect()
        #rpi_rect.left = logo_rect.left + logo_rect.width * 3 / 4
        #rpi_rect.top = logo_rect.top + logo_rect.height * 2 / 3
        rpi_rect.bottom = logo_rect.bottom
        rpi_rect.right = logo_rect.right
        self.worldsurf.blit( self.rpi_tag, rpi_rect )


        self.title_blink_timer += 1

        if self.title_blink_timer <= self.fps * 3 / 4:
            if pygame.joystick.get_count() > 0:
                self.draw_text( "press START to begin", self.scores_font, ( 50, 50, 50 ), ( self.worldsurf_rect.centerx, self.worldsurf_rect.height - self.worldsurf_rect.height / 5 ), self.worldsurf )
            else:
                self.draw_text( "press SPACE BAR to begin", self.scores_font, ( 50, 50, 50 ), ( self.worldsurf_rect.centerx, self.worldsurf_rect.height - self.worldsurf_rect.height / 5 ), self.worldsurf )
        if self.title_blink_timer >= self.fps * 3 / 2:
           self.title_blink_timer = 0

    def draw_AAR(self):
        self.worldsurf.fill( self.bg_color )

        self.gamesurf.fill( self.bg_color )

        self.draw_gridlines()


        #self.nextsurf.fill( ( 100, 100, 100 ) )
        self.nextsurf.fill( self.bg_color )
        self.draw_next_zoid()

        if self.keep_zoid:
            self.keptsurf.fill( self.kept_bgc )
            self.draw_kept_zoid()

        if self.show_high_score:
            self.draw_text( "High:", self.scores_font, ( 210, 210, 210 ), self.high_lab_left, self.worldsurf, "midleft" )
            self.draw_text( str( self.high_score ), self.scores_font, ( 210, 210, 210 ), self.high_left, self.worldsurf, "midright" )

        self.draw_text( "Game %d" % self.game_number, self.intro_font, ( 196, 196, 196 ), ( self.gamesurf_rect.centerx, self.gamesurf_rect.top / 2 ), self.worldsurf )
        self.draw_text( "Score:", self.scores_font, ( 210, 210, 210 ), self.score_lab_left, self.worldsurf, "midleft" )
        self.draw_text( "Lines:", self.scores_font, ( 210, 210, 210 ), self.lines_lab_left, self.worldsurf, "midleft" )
        self.draw_text( "Level:", self.scores_font, ( 210, 210, 210 ), self.level_lab_left, self.worldsurf, "midleft" )
        self.draw_text( str( self.score ), self.scores_font, ( 210, 210, 210 ), self.score_left, self.worldsurf, "midright" )
        self.draw_text( str( self.lines_cleared ), self.scores_font, ( 210, 210, 210 ), self.lines_left, self.worldsurf, "midright" )
        self.draw_text( str( self.level ), self.scores_font, ( 210, 210, 210 ), self.level_left, self.worldsurf, "midright" )
        self.draw_newscore()

        self.draw_AAR_zoids()

        self.draw_borders()

        self.draw_board(alpha = self.AAR_dim)
        #self.draw_text( "PAUSED", self.pause_font, ( 210, 210, 210 ), self.worldsurf_rect.center, self.worldsurf )

    #draw the main game when being played
    def draw_game( self ):
        self.worldsurf.fill( self.bg_color )

        self.draw_gridlines()

        self.draw_board()
        if not self.needs_new_zoid:
            self.draw_curr_zoid()

        #self.nextsurf.fill( ( 100, 100, 100 ) )
        self.nextsurf.fill( self.bg_color )
        self.draw_next_zoid()

        if self.keep_zoid:
            self.keptsurf.fill( self.kept_bgc )
            self.draw_kept_zoid()


        self.draw_text( "Game %d" % self.game_number, self.intro_font, ( 196, 196, 196 ), ( self.gamesurf_rect.centerx, self.gamesurf_rect.top / 2 ), self.worldsurf )

    ###

    def draw_scores( self ):
        self.draw_text( "Score:", self.scores_font, ( 210, 210, 210 ), self.score_lab_left, self.worldsurf, "midleft" )
        self.draw_text( "Lines:", self.scores_font, ( 210, 210, 210 ), self.lines_lab_left, self.worldsurf, "midleft" )
        self.draw_text( "Level:", self.scores_font, ( 210, 210, 210 ), self.level_lab_left, self.worldsurf, "midleft" )
        self.draw_text( str( self.score ), self.scores_font, ( 210, 210, 210 ), self.score_left, self.worldsurf, "midright" )
        self.draw_text( str( self.lines_cleared ), self.scores_font, ( 210, 210, 210 ), self.lines_left, self.worldsurf, "midright" )
        self.draw_text( str( self.level ), self.scores_font, ( 210, 210, 210 ), self.level_left, self.worldsurf, "midright" )
        self.draw_newscore()
    ###

    def draw_newscore( self ):
        #Notes
        #Need to do the math to figure out how many pixels out of...100?? I make the bar
        #Also need the lower pixels to be red and then it goes orange, yellow, green as you go up the bar with a score closer to 0
        #Score of 100 would be a few pixels tall red line
        #Score of 0 would be a fully tall line with green at top
        red_score     = 90
        orange_score  = 80
        yellow_score  = 50
        bar_width     = 60
        bar_thickness = 0
        bar_x         = 650
        bar_y         = 545
        bar_height    = max(min(100-self.newscore,100),1)*3
        green_height  = max(min(yellow_score-self.newscore,yellow_score),0)*3
        yellow_height = max(min(orange_score-self.newscore,orange_score-yellow_score),0)*3
        orange_height = max(min(red_score-self.newscore,red_score-orange_score),0)*3
        red_height    = max(min(100-self.newscore,100-red_score),1)*3
        pygame.draw.rect( self.worldsurf, (255, 0, 0), (bar_x,bar_y-red_height,bar_width,red_height), bar_thickness)
        bar_top = bar_y-red_height-orange_height-yellow_height-green_height
        #pygame.draw.rect( self.worldsurf, (0, 0, 255), (bar_x+20,bar_y-bar_height,bar_width,bar_height), bar_thickness)
        if orange_height>0:
            pygame.draw.rect( self.worldsurf, (255, 128, 0), (bar_x,bar_y-red_height-orange_height,bar_width,orange_height), bar_thickness)
        if yellow_height>0:
            pygame.draw.rect( self.worldsurf, (255, 255, 0), (bar_x,bar_y-red_height-orange_height-yellow_height,bar_width,yellow_height), bar_thickness)
        if green_height>0:
            pygame.draw.rect( self.worldsurf, (0, 255, 0), (bar_x,bar_y-red_height-orange_height-yellow_height-green_height,bar_width,green_height), bar_thickness)

        #self.draw_text( "New:", self.scores_font, ( 210, 210, 210 ), self.newscore_lab_left, self.worldsurf, "midleft" )
        self.draw_text( "{:0.2f}".format(self.newscore), self.scores_font, ( 210, 210, 210 ), (bar_x+bar_width+40,bar_top), self.worldsurf, "midright" )
        self.draw_text( "Meta:", self.scores_font, ( 210, 210, 210 ), (600,185), self.worldsurf, "midleft" )
        self.draw_text( "{:0.3f}".format(self.metascore), self.scores_font, ( 210, 210, 210 ), (720,185), self.worldsurf, "midright" )

    ###

    #draw borders around game regions
    def draw_borders( self ):
        if self.args.eyetracker and self.eye_conf_borders:
            avg_conf = int((self.i_x_conf + self.i_y_conf) / 2.0)
            color = (min(250,150+(avg_conf/3)),max(150,250-(avg_conf/3)),50)
        else:
            color = self.border_color
        pygame.draw.rect( self.worldsurf, color, self.gamesurf_border_rect, self.border_thickness )
        if self.look_ahead > 0:
            pygame.draw.rect( self.worldsurf, color, self.nextsurf_border_rect, self.border_thickness )
        if self.keep_zoid:
            pygame.draw.rect( self.worldsurf, color, self.keptsurf_border_rect, self.border_thickness )

    def draw_gridlines( self ):
        if self.gridlines_x:
            for i in range( 1 , self.game_wd ):
                pygame.draw.line( self.gamesurf, self.gridlines_color, (i * self.side - 1, 0), (i*self.side - 1, self.gamesurf_rect.height) , 2)
        if self.gridlines_y:
            for i in range( 1 , self.game_ht ):
                pygame.draw.line( self.gamesurf, self.gridlines_color, (0, i * self.side - 1), (self.gamesurf_rect.width, i*self.side - 1) , 2)

    #draw gameover animation and message
    def draw_game_over( self ):
        tick = self.gameover_anim_tick
        #paint one more of the game world
        if tick == 0:
            self.draw_game()

        #animate
        elif tick > 0 and tick <= self.gameover_tick_max:
            ix = 0
            iy = 0
            for i in range( 0, int(tick / 2) ):
                for j in self.gameover_board[i]:
                    self.draw_square( self.gamesurf, ix, iy, color_id = self.zoidrand.randint( 1, 7 ) )
                    ix += self.side
                ix = 0
                iy += self.side

            if not self.inverted:
                self.worldsurf.blit( self.gamesurf, self.gamesurf_rect )
            elif self.inverted:
                self.worldsurf.blit( pygame.transform.flip(self.gamesurf, False, True), self.gamesurf_rect)

        #give gameover message
        elif tick > self.gameover_tick_max:
            self.draw_text_box()
            msg0 = "GAME OVER"
            msg1 = "Continue? ["+str(self.continues)+"]"

            if pygame.joystick.get_count() > 0:
                msg2 = "Press START"
                msg3 = "Esc to Exit"
            else:
                msg2 = "Press Spacebar"
                msg3 = "Esc to Exit"
            offset = 36
            colors =  self.NES_colors[self.level%len(self.NES_colors)]
            col = colors[1]

            time_up = (get_time() - self.time_limit_start) >= self.time_limit
            game_complete = self.episode_number == self.max_eps - 1
            if self.continues == 0 or time_up:
                msg1 = ""
                msg2 = ""
                msg3 = ""
                offset = 0
                col = colors[0]
            if time_up:
                msg0 = "TIME'S UP!"
            elif game_complete:
                msg0 = "COMPLETED!"
            elif self.continues < 0:
                msg1 = "Continue?"
            self.draw_text( msg0, self.end_font, col, ( self.gamesurf_rect.centerx, self.gamesurf_rect.centery - offset ), self.worldsurf )
            self.draw_text( msg1, self.scores_font, self.end_text_color, ( self.gamesurf_rect.centerx, self.gamesurf_rect.centery + offset ), self.worldsurf )
            if int((tick - self.gameover_tick_max) / (self.fps * 2))% 3 < 2:
                self.draw_text( msg2, self.scores_font, self.end_text_color, ( self.gamesurf_rect.centerx, self.gamesurf_rect.centery + (2 * offset) ), self.worldsurf )
                self.draw_text( msg3, self.scores_font, self.end_text_color, ( self.gamesurf_rect.centerx, self.gamesurf_rect.centery + (3 * offset) ), self.worldsurf )

        self.gameover_anim_tick += self.ticks_per_frame

    #main draw updater
    def draw( self ):
        if self.state == self.STATE_INTRO:
            self.draw_intro()
        elif self.state == self.STATE_PLAY:
            self.bg_color = self.tetris_flash_colors[self.tetris_flash_tick % 2]
            if self.tetris_flash_tick > 0:
                self.tetris_flash_tick -= 1
            self.gamesurf.fill( self.bg_color )
            self.draw_game()
            self.draw_scores()
            self.draw_borders()
        elif self.state == self.STATE_PAUSE:
            self.worldsurf.fill( ( 0, 0, 0 ) )
            self.draw_pause()
        elif self.state == self.STATE_GAMEOVER:
            self.draw_game_over()
            self.draw_scores()
            self.draw_borders()
        elif self.state == self.STATE_AAR:
            self.draw_AAR()
        if self.args.eyetracker and eyetrackerSupport and (self.draw_fixation or self.draw_samps or self.draw_avg or self.draw_err or self.spotlight):
            self.draw_fix()
        self.screen.blit( self.worldsurf, self.worldsurf_rect )
        pygame.display.flip()
    ###







    ####
    #  Input
    ####

    #processes all relevant game input
    def process_input( self ):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:
                dir = "PRESS" if event.type == pygame.KEYDOWN else "RELEASE"
                self.log_game_event( "KEYPRESS", dir, pygame.key.name(event.key))
            elif event.type == pygame.JOYBUTTONUP or event.type == pygame.JOYBUTTONDOWN:
                #print("Stuff 1: ",			 event, ";", event.button)
                dir = "PRESS" if event.type == pygame.JOYBUTTONDOWN else "RELEASE"
                self.log_game_event( "KEYPRESS", dir, self.buttons[event.button] )


            #Universal controls

            #escape clause
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.lc.stop()

            #screenshot clause
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                self.do_screenshot()

            #eyetracker keys (number line)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_5 and self.args.eyetracker:
                self.eye_conf_borders = not self.eye_conf_borders
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_6 and self.args.eyetracker:
                self.spotlight = not self.spotlight
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_7 and self.args.eyetracker:
                self.draw_samps = not self.draw_samps
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_8 and self.args.eyetracker:
                self.draw_avg = not self.draw_avg
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_9 and self.args.eyetracker:
                self.draw_err = not self.draw_err
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_0 and self.args.eyetracker:
                self.draw_fixation = not self.draw_fixation

            #Intro state controls
            if self.state == self.STATE_INTRO:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.state += 1
                        self.time_limit_start = get_time()

                #joystick controls
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == self.JOY_START :
                        self.state += 1
                        self.time_limit_start = get_time()

            #After-Action Review controls
            elif self.state == self.STATE_AAR:
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.input_stop_drop()
                    elif event.key == pygame.K_UP or event.key == pygame.K_w and self.inverted:
                        self.input_stop_drop()
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.input_trans_stop(-1)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.input_trans_stop(1)
                    elif event.key == pygame.K_SPACE and self.AAR_selfpaced:
                        self.input_end_AAR()
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.button == self.JOY_START and self.AAR_selfpaced:
                        self.input_end_AAR()
                elif event.type == pygame.JOYBUTTONUP:
                    if not self.two_player or event.joy == 0:
                        if event.button == self.JOY_DOWN:
                            self.input_stop_drop()
                        elif event.button == self.JOY_UP and self.inverted:
                            self.input_stop_drop()
                        elif event.button == self.JOY_LEFT:
                            self.input_trans_stop(-1)
                        elif event.button == self.JOY_RIGHT:
                            self.input_trans_stop(1)


            #Gameplay state controls
            elif self.state == self.STATE_PLAY:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.input_trans_left()
                        self.das_held = -1
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.input_trans_right()
                        self.das_held = 1

                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        if self.inverted:
                            self.input_rotate_single()
                        else:
                            self.input_start_drop()
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        if self.inverted:
                            self.input_start_drop()
                        else:
                            self.input_rotate_single()

                    elif event.key == pygame.K_j:
                        self.input_clockwise()
                    elif event.key == pygame.K_k:
                        self.input_counterclockwise()

                    elif event.key == pygame.K_r:
                        self.input_undo()

                    elif event.key == pygame.K_SPACE:
                        self.input_slam()
                        self.input_place()

                    elif event.key == pygame.K_e:
                        self.input_swap()


                    elif event.key == pygame.K_q:
                        self.input_mask_toggle(True)

                    #pause clause
                    elif event.key == pygame.K_p:
                        self.input_pause()

                    #solver
                    elif event.key == pygame.K_m:
                        self.input_solve()

                    elif event.key == pygame.K_n:
                        if self.solve_button:
                            self.auto_solve = True

                    #hints
                    elif event.key == pygame.K_h:
                        #if hints aren't continuous, and the button is allowed
                        if self.hint_button and not self.hint_zoid and (self.hints != self.hint_limit):
                            self.hints += 1
                            self.hint_toggle = True


                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.input_stop_drop()
                    elif event.key == pygame.K_UP or event.key == pygame.K_w and self.inverted:
                        self.input_stop_drop()
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.input_trans_stop(-1)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.input_trans_stop(1)
                    elif event.key == pygame.K_q:
                        self.input_mask_toggle(False)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        if self.inverted:
                            if pygame.KMOD_SHIFT:
                                self.add_latency("RL")
                            else:
                                self.add_latency("RR")
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        if not self.inverted:
                            if pygame.KMOD_SHIFT:
                                self.add_latency("RL")
                            else:
                                self.add_latency("RR")
                    elif event.key == pygame.K_j:
                        self.add_latency("RR")
                    elif event.key == pygame.K_k:
                        self.add_latency("RL")

                    #solver
                    elif event.key == pygame.K_n:
                        if self.solve_button:
                            self.auto_solve = False

                    #hints
                    elif event.key == pygame.K_h:
                        #if hints aren't continuous, and the button is allowed
                        if self.hint_button and not self.hint_zoid and self.hint_release:
                            self.hint_toggle = False

                elif event.type == pygame.JOYAXISMOTION:
                    if (not self.two_player or event.joy == 0) and self.joyaxis_enabled:

                        pressed = ""
                        released = ""

                        #key is pressed
                        if event.axis == 0:
                            if round(event.value) == 1.0:
                                pressed = "RIGHT"
                                released = self.last_ud_pressed
                                self.last_ud_pressed = ""
                            elif round(event.value) == -1.0:
                                pressed = "LEFT"
                                released = self.last_ud_pressed
                                self.last_ud_pressed = ""
                            elif round(event.value) == 0.0:
                                released = self.last_lr_pressed
                                self.last_lr_pressed = ""
                        elif event.axis == 1:
                            if round(event.value) == 1.0:
                                pressed = "DOWN"
                                if not self.inverted:
                                    released = self.last_lr_pressed
                                    self.last_lr_pressed = ""
                            elif round(event.value) == -1.0:
                                pressed = "UP"
                                if self.inverted:
                                    released = self.last_lr_pressed
                                    self.last_lr_pressed = ""
                            elif round(event.value) == 0.0:
                                released = self.last_ud_pressed
                                self.last_ud_pressed = ""

                        #resolve release event
                        if released != "":
                            if released == "DOWN":
                                self.input_stop_drop()
                            elif released == "UP" and self.inverted:
                                self.input_stop_drop()
                            elif released == "LEFT":
                                self.input_trans_stop(-1)
                            elif released == "RIGHT":
                                self.input_trans_stop(1)

                            self.log_game_event( "KEYPRESS", "RELEASE", released)
                            #print("released", released)

                        #resolve pressed
                        if pressed != "":
                            if pressed == "DOWN":
                                self.last_ud_pressed = pressed
                                if self.inverted:
                                    self.input_slam()
                                    self.input_undo()
                                else:
                                    self.input_start_drop()
                            elif pressed == "UP":
                                self.last_ud_pressed = pressed
                                if self.inverted:
                                    self.input_start_drop()
                                else:
                                    self.input_slam()
                                    self.input_undo()
                            elif pressed == "LEFT":
                                self.last_lr_pressed = pressed
                                self.input_trans_left()
                                self.das_held = -1
                            elif pressed == "RIGHT":
                                self.last_lr_pressed = pressed
                                self.input_trans_right()
                                self.das_held = 1
                            self.log_game_event( "KEYPRESS", "PRESS", pressed)
                            #print("pressed", pressed)




                elif event.type == pygame.JOYBUTTONDOWN:
                    #player 1
                    if not self.two_player or event.joy == 0:
                        if event.button == self.JOY_LEFT:
                            self.input_trans_left()
                            self.das_held = -1
                        elif event.button == self.JOY_RIGHT:
                            self.input_trans_right()
                            self.das_held = 1
                        elif event.button == self.JOY_DOWN:
                            if self.inverted:
                                self.input_slam()
                                self.input_undo()
                            else:
                                self.input_start_drop()
                        elif event.button == self.JOY_UP:
                            if self.inverted:
                                self.input_start_drop()
                            else:
                                self.input_slam()
                                self.input_undo()

                    #player 2
                    if not self.two_player or event.joy == 1:
                        if event.button == self.JOY_B:
                            self.input_counterclockwise()
                        elif event.button == self.JOY_A:
                            self.input_clockwise()
                        elif event.button == self.JOY_SELECT:
                            self.input_mask_toggle(True)
                            self.input_place()
                            self.input_swap()

                    #both players
                    if event.button == self.JOY_START:
                        if self.pause_enabled:
                            self.input_pause()
                        else:
                            self.input_place()



                elif event.type == pygame.JOYBUTTONUP:
                    if not self.two_player or event.joy == 0:
                        if event.button == self.JOY_DOWN:
                            self.input_stop_drop()
                        elif event.button == self.JOY_UP and self.inverted:
                            self.input_stop_drop()
                        elif event.button == self.JOY_LEFT:
                            self.input_trans_stop(-1)
                        elif event.button == self.JOY_RIGHT:
                            self.input_trans_stop(1)
                        elif event.button == self.JOY_A:
                            self.add_latency("RR")
                        elif event.button == self.JOY_B:
                            self.add_latency("RL")

                    if not self.two_player or event.joy == 1:
                        if event.button == self.JOY_SELECT:
                            self.input_mask_toggle(False)

            elif self.state == self.STATE_PAUSE:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.input_pause()
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == self.JOY_START:
                        self.input_pause()

            #Gameover state controls
            elif self.state == self.STATE_GAMEOVER:
                if self.implement_gameover_fixcross != True or self.time_over() or self.episode_number == self.max_eps - 1:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.input_continue()
                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.button == self.JOY_START:
                            self.input_continue()
                elif self.implement_gameover_fixcross == True and self.time_over() != True and self.episode_number != self.max_eps - 1:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.log_game_event("GAMEOVER_FIXCROSS", "START")
                            self.state = self.STATE_GAMEOVER_FIXATION
                            #self.gameover_params['bg_color'] = self.mask_color
                            self.validator = Validator( self.client, self.screen, reactor = reactor, escape = True, params = self.gameover_params)
                            self.validator.start(self.fixcross)
                            # self.input_continue()
                    if event.type == pygame.JOYBUTTONDOWN:
                        if event.button == self.JOY_START:
                            self.log_game_event("GAMEOVER_FIXCROSS", "START")
                            self.state = self.STATE_GAMEOVER_FIXATION
                            #self.gameover_params['bg_color'] = self.mask_color
                            self.validator = Validator( self.client, self.screen, reactor = reactor, escape = True, params = self.gameover_params)
                            self.validator.start(self.fixcross)
                            # self.input_continue()


        if self.args.eyetracker and eyetrackerSupport and len( World.gaze_buffer ) > 1:
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
                    self.log_game_event("MASK_TOGGLE", self.mask_toggle)


            #HOOK FOR MISDIRECTION / LOOKAWAY EVENTS
            # when in board, normal. when leave board, subtly alter accumulation.
            ## will need crossover detection for event onset
            ## will need board mutator function
            ## could use some helper "in-bounds" or collision functions.

            self.i_x_conf = 0 if int(self.i_x_avg)<=0 else sum(map((lambda a, b: pow(a + b, 2)), xs, [-self.i_x_avg] * len(xs))) / int(self.i_x_avg)#len(xs)
            self.i_y_conf = 0 if int(self.i_y_avg)<=0 else sum(map((lambda a, b: pow(a + b, 2)), ys, [-self.i_y_avg] * len(ys))) / int(self.i_y_avg)#len(ys)



        #for second eye when both are captured
        if self.args.eyetracker and eyetrackerSupport and len( World.gaze_buffer2 ) > 1:


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
    ###

    #pauses game
    def input_pause( self ):
        if self.pause_enabled:
            if self.state == self.STATE_PLAY:
                self.state = self.STATE_PAUSE
                self.log_game_event("PAUSED")
                pygame.mixer.music.pause()
            elif self.state == self.STATE_PAUSE:
                self.state = self.STATE_PLAY
                self.log_game_event("UNPAUSED")
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
            self.log_game_event("ZOID","UNDO")

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
            self.log_game_event("MASK_TOGGLE", on)

    def input_continue( self ):
        if self.continues != 0 and not self.time_over() and self.gameover_anim_tick > self.gameover_tick_max:
            self.state = self.STATE_SETUP

    def input_solve( self ):
        if self.solve_button and self.are_counter < 0 and self.lc_counter < 0:
            self.solve()

    def input_end_AAR( self ):
        self.state = self.STATE_PLAY
        self.AAR_timer = 0
        self.log_game_event("AAR", "END", "SELF")

    #creates a screenshot of the current game.
    def do_screenshot( self ):
        if not os.path.exists( self.logname + sep + "screenshots" ):
            os.mkdir( self.logname + sep + 'screenshots' )
        d = datetime.datetime.now().timetuple()
        filename = self.logname + sep + "screenshots" + sep + "Gm" + str(self.game_number) + "_Ep" + str(self.episode_number) + "_%d-%d-%d_%d-%d-%d.jpeg" % ( d[0], d[1], d[2], d[3], d[4], d[5] )
        pygame.image.save( self.worldsurf, filename )
        self.log_game_event("SCREENSHOT")

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
        if self.state == self.STATE_PLAY:
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
                            self.log_game_event( "EPISODE", "BEGIN", self.episode_number )
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

        elif self.state == self.STATE_SETUP:
           self.setup()
           self.state += 1

        elif self.state == self.STATE_AAR:
            if self.AAR_timer == 0:
                self.state = self.STATE_PLAY
                self.log_game_event("AAR", "END")
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
            self.log_game_event( "DANGER", "BEGIN" )
        #if we've cleared out of danger mode...
        elif not topfull and self.danger_mode:
            self.danger_mode = False
            pygame.mixer.music.stop()
            pygame.mixer.music.load( "media" + sep + "%s.wav" % self.song )
            pygame.mixer.music.play( -1 )
            self.log_game_event( "DANGER", "END" )
    ###

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
            self.log_game_event("ZOID", "SLAMMED")
            self.zoid_slammed = False
        elif self.solved and not (self.hint_zoid or self.hint_button):
            self.sounds['solved1'].play( 0 )
            self.log_game_event("ZOID", "SOLVED")

        else:
            self.sounds['thud'].play( 0 )

        self.log_game_event( "PLACED", self.curr_zoid.type, [self.curr_zoid.rot, self.curr_zoid.get_col(), self.curr_zoid.get_row()])
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
                self.log_game_event( "ZOID_SWAP", self.kept_zoid.type)
            else:
                temp = self.curr_zoid
                self.curr_zoid = self.kept_zoid
                self.kept_zoid = temp
                self.curr_zoid.init_pos()
                self.log_game_event( "ZOID_SWAP", self.kept_zoid.type, self.curr_zoid.type  )

            self.curr_zoid.refresh_floor()
            self.swapped = True
            self.drop_score = 0
            self.sounds['keep'].play( 0 )

    # 7-bag randomization without doubles
    def get_seven_bag( self ):
        if len( self.seven_bag ) == 0:
            self.log_game_event( "7-BAG", "refresh" )
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
        elif self.zoids[z_id] == self.curr_zoid.type and self.state != self.STATE_SETUP:
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

        self.log_game_event( "ZOID", "NEW", self.curr_zoid.type )
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
                self.log_game_event("Clear", numcleared)

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
            self.log_game_event( "LEVELUP", self.level)

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
            self.log_game_event("AAR", "BEGIN")
            self.AAR_conflicts = 0
            self.state = self.STATE_AAR
            self.AAR_timer = self.AAR_dur
            if self.AAR_dur_scaling:
                self.AAR_timer = self.interval[0]

    def controller_agree( self ):
        return self.solved_rot == self.curr_zoid.rot and self.solved_col == self.curr_zoid.col and self.solved_row == self.curr_zoid.row

    #end a trial
    def end_trial( self ):
        if self.solved:
            self.agree = self.controller_agree()
            self.log_game_event( "CONTROLLER", "AGREE?", self.agree)
        if self.AAR and self.state != self.STATE_GAMEOVER:
            self.check_AAR()
        self.place_zoid()
        self.clear_lines()
        self.sim.set_board( self.board)
        self.needs_new_zoid = True
        self.swapped = False

        self.update_evts()

        self.log_episode()

        if self.hint_toggle: #if the hint toggle is still being held
            if self.hint_limit >= 0 or not self.hint_release:
                self.hint_toggle = False

        self.log_game_event( "EPISODE", "END", self.episode_number )
        if self.time_over() and self.episode_timeout == "episode":
            self.game_over()
            self.log_game_event( "TIME_OVER" )
        if self.episode_number == self.max_eps - 1:
            self.game_over()
            self.log_game_event( "EPISODE_LIMIT_REACHED" )

    def time_over( self ):
        return (get_time() - self.time_limit_start) >= self.time_limit

    #game over detected, change state
    def game_over( self ):
        self.log_game_event( "GAME", "END", self.game_number )
        self.log_gameresults(complete = False if self.time_over() else True)
        self.continues -= 1
        self.state = self.STATE_GAMEOVER
        if self.time_over() or self.episode_number == self.max_eps - 1:
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
        self.get_config(self.config_names[self.config_ix%len(self.config_names)])
        self.continues = cur_continues
        #new board
        self.initialize_board()

        #increment game number
        self.game_number += 1

        if self.fixed_seeds:
#             print(self.seed_order)
#             print(self.random_seeds)
            seed = self.random_seeds[self.seed_order[(self.game_number-1)%len(self.random_seeds)]]
#             print(seed)
        else:
            seed = int(get_time() * 10000000000000.0)

        self.zoidrand = random.Random()
        self.zoidrand.seed(seed)
        self.seeds_used += [str(seed)]
        self.log_game_event("SEED", data1 = self.game_number, data2 = seed)

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

        self.gameover_params = {'size' : self.gameover_fixcross_size,
                        'width' : self.gameover_fixcross_width,
                        'frames' : self.gameover_fixcross_frames,
                        'tolerance' : self.gameover_fixcross_tolerance,
                        'frames_tolerance' : self.gameover_fixcross_frames_tolerance,
                        'hit_color' : self.gameover_fixcross_color,
                        'timeout' : self.gameover_fixcross_timeout,
                        'miss_color' : self.border_color,
                        'bg_color' : self.message_box_color,
                        'val_accuracy' : self.validation_accuracy,
                        'automated' : self.automated_revalidation}


        #restart the normal music
        pygame.mixer.music.load( "media" + sep + "%s.wav" % self.song )
        pygame.mixer.music.play( -1 )
        self.danger_mode = False

        self.log_game_event( "GAME", "BEGIN", self.game_number )



    def fixcross ( self, lc ,log = None, results = None ):
        evt_recal = False
        if self.args.eyetracker and eyetrackerSupport:
            event_log = self.validator.log
            validation_results = str(self.validator.validationResults)
            if len(event_log) > 1:
                if "RECALIBRATE" in event_log:
                    evt_recal = True
                event_log = str(event_log)

            self.log_game_event("VALIDATION", event_log, validation_results)

        if event_log == "RECALIBRATE" or evt_recal == True:

            self.log_game_event("RECALIBRATION", "START")
            self.state = self.STATE_CALIBRATE
            self.recalibrate()

        else:
            self.state = self.STATE_GAMEOVER
            self.input_continue()

    def recalibrate( self ) :

        self.calibrator._reset()
        self.calibrator.start(self.runrecalibrate, recalibrate = True, points = self.calibration_points, auto = int(self.calibration_auto ))

    def runrecalibrate( self, lc, results = None ):

        if self.args.eyetracker and eyetrackerSupport:
            self.log_game_event("RECALIBRATION", "COMPLETE", self.calibrator.calibrationResults)
        self.state = self.STATE_GAMEOVER
        self.input_continue()

    ####
    #  Reactor
    ####

    #Twisted event loop refresh logic
    def refresh( self ):
        if self.state != self.STATE_CALIBRATE and self.state != self.STATE_GAMEOVER_FIXATION:
            self.process_input()
            self.process_game_logic()
            self.draw()
        if self.state == self.STATE_PLAY:
            self.log_world()
    ###

    #Twisted event loop setup
    def start( self, lc, results=None ):
        self.state = self.STATE_INTRO
        if self.args.eyetracker and eyetrackerSupport:
            self.log_game_event("CALIBRATION", "Complete", str(self.calibrator.calibrationResults))
        self.lc = LoopingCall( self.refresh )
        #pygame.mixer.music.play( -1 )
        cleanupD = self.lc.start( 1.0 / self.fps )
        cleanupD.addCallbacks( self.quit )
    ###

    #Twisted event loop teardown procedures
    def quit( self, lc ):
        if self.game_number > 0 and not self.state == self.STATE_GAMEOVER:
            self.log_gameresults(complete=False)
        self.criterion_score()
        self.close_files()
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
            self.state = self.STATE_CALIBRATE
            reactor.listenUDP( 5555, self.client )
            self.log_game_event("CALIBRATION", "Start")
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
                self.log_eye_sample( )
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
                self.log_game_event("ERROR", "AOI INDEX")
