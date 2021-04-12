import os

import drawer

sep = os.path.sep

try:
  import pycogworks.crypto
  cryptoSupport = True
except ImportError:
  # print("Warning: cryptography not supported on this machine.")
  cryptoSupport = False


def write( world ):
  for varname in world.configs_to_write:
    if type(getattr(world, varname)) is list or type(getattr(world, varname)) is tuple:
      out = []
      for i in getattr(world, varname):
        out += [str(i)]
      out = ",".join(out)
    else:
      out = str(getattr(world, varname))
    prefix = ""
    if varname in ['permute_seeds', 'random_seeds', 'fixed_seeds']:
      prefix = "#"

    world.configfile.write(prefix + varname + " = " + out + "\n")


def updateUserConfig(world, key, val):
  userconf = world.rawConfDicts["user"]
  userconf[key] = val

  fl = open("configs" + sep + "user.config", "w")
  for (k, v) in userconf.items():
    fl.write(k + " = " + str(v) + "\n")
  fl.close()

  setattr(world, key, val)
  drawer.setupLayout(world)
  drawer.setupColors(world)
  world.updateVolumes()


def read(world, flname):
  flpath = "configs" + sep + flname + ".config"
  if not os.path.isfile(flpath):
    print("Config file '%s' does not exist" % flpath)
    world.rawConfDicts[flname] = {}
    return

  fl = open(flpath)
  lines = fl.readlines()
  fl.close()

  confdict = {}

  for line in [rawline.strip().split("#") for rawline in lines]:
    if line[0] == '':
      continue

    line = line[0].split("=")
    key = line[0].strip()
    val = line[1].strip()
    world.config[key] = val
    confdict[key] = val

  world.rawConfDicts[flname] = confdict


def set_var( world, name, default, type ):
  setattr(world, name, default)
  if name in world.config:
    val = []
    if type == 'float' or type == 'int':
      val = eval(type)(world.config[name])
    elif type == 'bool':
      entry = world.config[name].lower()
      val = ( entry == 'true') or (entry == 't') or (entry == 'yes') or (entry == 'y')
    elif type == 'string':
      val = world.config[name]
    elif type == 'int_list' or 'color':
      list = world.config[name].split(",")
      for i in list:
        val.append(int(i.strip()))
      if type == 'color':
        val = tuple(val)

    setattr(world, name, val)

  world.configs_to_write += [name]


def setAll(world):
  # Added
  set_var(world, 'render_scores', False, 'bool')

  set_var(world, 'logdir', 'data', 'string')
  set_var(world, 'SID', 'Test', 'string')

  set_var(world, 'RIN', '000000000', 'string')

  set_var(world, 'ECID', 'NIL', 'string')

  if cryptoSupport:
    world.RIN = pycogworks.crypto.rin2id(world.RIN)[0]

  set_var(world, 'game_type', "standard", 'string')

  set_var(world, 'distance_from_screen', -1.0, 'float')

  set_var(world, 'fixed_log', True, 'bool')
  set_var(world, 'ep_log', True, 'bool')
  set_var(world, 'game_log', True, 'bool')


  set_var(world, 'continues', 0, 'int')

  ## Game definitions

  # Manipulable variable setup

  set_var(world, 'music_vol', 0.5, 'float')
  set_var(world, 'sfx_vol', 1.0, 'float')
  set_var(world, 'song', "music-1.ogg", 'string')

  set_var(world, 'fullscreen', False, 'bool')

  # Frames per second, updates per frame
  set_var(world, 'fps', 30 ,'int')
  set_var(world, 'tps', 60 ,'int')

  # render
  set_var(world, 'inverted', False ,'bool')

  # zoid set
  set_var(world, 'tetris_zoids', True ,'bool')
  set_var(world, 'pentix_zoids', False ,'bool')
  set_var(world, 'tiny_zoids', False ,'bool')

  # Held left-right repeat delays
  set_var(world, 'das_delay', 16, 'int')
  set_var(world, 'das_repeat', 6, 'int')

  # Zoid placement delay
  set_var(world, 'are_delay', 10 ,'int')

  # Line clear delay
  set_var(world, 'lc_delay', 20 ,'int')

  # Lines per level
  set_var(world, 'lines_per_lvl', 10 ,'int')

  # Game speed information
  set_var(world, 'timingSetup', 'NesNtsc' ,'string')

  set_var(world, 'intervals', [48, 43, 38, 33, 28, 23, 18, 13, 8, 6, 5, 5, 5, 4, 4, 4, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1] ,'int_list')
  set_var(world, 'drop_interval', 2 ,'int')

  set_var(world, 'gravity', True ,'bool')


  # Starting board information
  set_var(world, 'boardname', 'empty', 'string')

  set_var(world, 'game_ht', 20 ,'int')
  set_var(world, 'game_wd', 10 ,'int')

  # Invisible tetris
  set_var(world, 'visible_board', True ,'bool')
  set_var(world, 'visible_zoid', True ,'bool')
  set_var(world, 'board_echo_placed', True ,'bool')
  set_var(world, 'board_echo_lc', True ,'bool')

  # Number of next pieces to display (currently only 0 or 1)
  set_var(world, 'look_ahead', 1 ,'int')

  set_var(world, 'seven_bag_switch', False ,'bool')

  set_var(world, 'drop_bonus', True ,'bool')

  set_var(world, 'scoring', [40,100,300,1200,6000] ,'int_list')

  # manipulations
  set_var(world, 'undo', False ,'bool')

  set_var(world, 'far_next', False ,'bool')
  set_var(world, 'next_dim', True ,'bool')
  set_var(world, 'next_dim_alpha', 50 ,'int')

  set_var(world, 'next_mask', False ,'bool')
  set_var(world, 'board_mask', False, 'bool')


  #modern game features
  set_var(world, 'ghost_zoid', False ,'bool')
  set_var(world, 'zoid_slam', False ,'bool')
  set_var(world, 'keep_zoid', False ,'bool')

  # allow rotations to "kick" away from wall and piece collisions
  set_var(world, 'wall_kicking', False ,'bool')


  #must include board states, placement summaries, and piece events once implemented
  set_var(world, 'feedback_mode', False ,'bool')

  #dimtris!
  set_var(world, 'dimtris', False, 'bool')
  set_var(world, 'dimtris_alphas', [255,225,200,175,150,125,100,75,50,25,0], 'int_list')

  #gridlines
  set_var(world, 'gridlines_x', False, 'bool')
  set_var(world, 'gridlines_y', False, 'bool')
  set_var(world, 'gridlines_color', (50,50,50), 'color')

  #draw fixations?
  set_var(world, 'draw_avg', False, 'bool')
  set_var(world, 'draw_err', False, 'bool')
  set_var(world, 'gaze_window', 30, 'int')

  set_var(world, 'spotlight', False, 'bool')
  set_var(world, 'spot_radius', 350, 'int')
  set_var(world, 'spot_color', (50,50,50), 'color')
  set_var(world, 'spot_alpha', 255, 'int')
  set_var(world, 'spot_gradient', True, 'bool')

  #unimplemented
  set_var(world, 'grace_period', 0, 'int') #UNIMPLEMENTED
  set_var(world, 'grace_refresh', False, 'bool') #UNIMPLEMENTED
  ###

  set_var(world, 'bg_color', (26,26,26), 'color')
  set_var(world, 'border_color', (250,250,250), 'color')

  set_var(world, 'kept_bgc', ( 50, 50, 50 ), 'color')

  set_var(world, 'pause_enabled', True, 'bool')

  set_var(world, 'das_chargeable', True, 'bool')
  set_var(world, 'das_reversible', True, 'bool')

  set_var(world, 'two_player', False, 'bool')

  set_var(world, 'misdirection', False, 'bool') #UNIMPLEMENTED

  set_var(world, 'max_eps', -1, 'int')

  set_var(world, 'show_high_score', False, 'bool')

  set_var(world, 'starting_level', 0, 'int')


  set_var(world, 'ep_screenshots', False, 'bool')


  set_var(world, 'n_back', False, 'bool')
  set_var(world, 'nback_n', 2, 'int')

  set_var(world, 'ax_cpt', False, 'bool')
  set_var(world, 'ax_cue', 'O', 'string')
  set_var(world, 'ax_target', 'I', 'string')

  # set_var(world, 'fixed_seeds', False, 'bool')
  set_var(world, 'random_seeds', [int(world.startTime * 10000000000000.0)], 'int_list')
  set_var(world, 'permute_seeds', False, 'bool')
  set_var(world, 'shuffle_seed', int(world.startTime * 10000000000000.0), 'int')


  set_var(world, 'joystick_type', "NES_RETRO-USB", 'string')

  set_var(world, 'solve_button', False, 'bool')
  set_var(world, 'auto_solve', False, 'bool')

  set_var(world, 'hint_zoid', False, 'bool')
  set_var(world, 'hint_button', False, 'bool')
  set_var(world, 'hint_release', True, 'bool')
  set_var(world, 'hint_limit', -1, 'int')

  set_var(world, 'controller', "dellacherie", 'string')
  set_var(world, 'sim_overhangs', True, 'bool')
  set_var(world, 'sim_force_legal', True, 'bool')

  set_var(world, 'color_mode', "STANDARD", 'string')

  #tutoring system modes
    #NONE, CONSTANT, CONTEXT, CONFLICT

  #context-only hint zoids (i.e., correct rotation and column found)
  set_var(world, 'hint_context', False, 'bool')
  set_var(world, 'hint_context_col_tol', 0, 'int')

  #after-action review
  set_var(world, 'AAR', False, 'bool')
  set_var(world, 'AAR_max_conflicts', 1, 'int')
  set_var(world, 'AAR_dim', 50, 'int')
  set_var(world, 'AAR_dur', 20, 'int')
  set_var(world, 'AAR_dur_scaling', True, 'bool')
  set_var(world, 'AAR_curr_zoid_hl', True, 'bool')
  set_var(world, 'AAR_selfpaced', False, 'bool')

  set_var(world, 'score_align', 'left', 'string')

  set_var(world, 'gray_zoid', False, 'bool')
  set_var(world, 'gray_board', False, 'bool')
  set_var(world, 'gray_next', True, 'bool')
  set_var(world, 'gray_kept', False, 'bool')

  return True
