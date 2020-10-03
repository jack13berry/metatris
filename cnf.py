import os

sep = os.path.sep

try:
  import pycogworks.crypto
  cryptoSupport = True
except ImportError:
  # print("Warning: cryptography not supported on this machine.")
  cryptoSupport = False


def write( self ):
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

def load( self, name = "default" ):
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

  # self.set_var('fixed_seeds', False, 'bool')
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

  return True
