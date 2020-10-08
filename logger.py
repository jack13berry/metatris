import os, platform, time, json

get_time = time.time if platform.system() == 'Windows' else time.process_time

# Log line types:
#   events
#   states
#   ep summs
#   game summs

# initialize log directory
def init( self ):
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

  #immediate only
  state_header = ["delaying","dropping","zoid_rot","zoid_col","zoid_row"]
  board_header = ["board_rep","zoid_rep","newscore","metascore","rollavg"]

  #game and up
  game_header = ["SID","ECID","session","game_type","game_number","episode_number","level","score","lines_cleared",
          "completed","game_duration","avg_ep_duration","zoid_sequence"]

  #event slots
  event_header = ["evt_id","evt_data1","evt_data2"]

  uni_header = ["ts","event_type"]

  #episode and up
  ep_header = [
    "curr_zoid","next_zoid","danger_mode",
    "evt_sequence","rots","trans","path_length",
    "min_rots","min_trans","min_path",
    "min_rots_diff","min_trans_diff","min_path_diff",
    "u_drops","s_drops","prop_u_drops",
    "initial_lat","drop_lat","avg_lat",
    "tetrises_game","tetrises_level",
    "agree"
  ]

  self.fixed_header = uni_header + game_header + event_header + ep_header + state_header + board_header


def close_files( self ):
  game_event(self, "seed_sequence", data1 = self.seeds_used )
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
  """

def universal_header( self ):
  head = "\t".join( map(str, self.fixed_header) ) + "\n"
  self.unifile.write( head )
  if self.ep_log:
    self.epfile.write( head )
  if self.game_log:
    self.gamefile.write( head )

def universal( self, event_type, loglist, complete = False, evt_id = False, evt_data1 = False, evt_data2 = False, features = False):
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
  logit("'%s'" % json.dumps( zoid_in_board(self) ), "zoid_rep")


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


def episode( self ):
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
    universal(self, "EP_SUMM", loglist, features = True)
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
          ":zoid_rep", "'%s'" % json.dumps( zoid_in_board(self) )]


    #board statistics
    for f in self.features_set:
      data += [":"+f, self.features[f]]

    self.unifile.write("\t".join(map(str,data)) + "\n")
    if self.ep_log:
      self.epfile.write("\t".join(map(str,data)) + "\n")

def gameresults( self, complete = True ):
  if self.fixed_log:
    loglist = ["SID","ECID","session","game_type","game_number","episode_number",
          "level","score","lines_cleared","completed",
          "game_duration","avg_ep_duration","zoid_sequence","newscore","metascore","rollavg"]
    universal(self, "GAME_SUMM",loglist, complete = complete)
  else:
    data = [
      ":ts", get_time() - self.starttime,
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
      ":zoid_sequence", "'%s'" % json.dumps( self.zoid_buff )
    ]

    self.unifile.write("\t".join(map(str,data)) + "\n")
    if self.ep_log:
      self.epfile.write("\t".join(map(str,data)) + "\n")
    if self.game_log:
      self.gamefile.write("\t".join(map(str,data)) + "\n")

  message = [
    "Game " , str(self.game_number) , ":\n" ,
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
def game_event( self, id, data1 = "", data2 = "" ):
  if self.fixed_log:
    loglist = [
      "SID","ECID","session","game_type","game_number","episode_number",
      "level","score","lines_cleared", "curr_zoid","next_zoid","danger_mode",
      "delaying","dropping", "newscore","metascore","rollavg",
      "zoid_rot", "zoid_col", "zoid_row"
    ]
    universal(self, "GAME_EVENT", loglist, evt_id = id, evt_data1 = data1, evt_data2 = data2)

  else:
    out = [
      ":ts", get_time() - self.starttime,
      ":event_type", 'GAME_EVENT',
      ":evt_id", id,
      ":evt_data1", data1,
      ":evt_data2", data2
    ]
    outstr = "\t".join( map( str, out ) ) + "\n"
    self.unifile.write( outstr )

#log the world state
def world( self ):
  if self.fixed_log:
    loglist = [
      "SID","ECID","session","game_type","game_number","episode_number",
      "level","score","lines_cleared","danger_mode",
      "delaying","dropping","curr_zoid","next_zoid",
      "zoid_rot","zoid_col","zoid_row","board_rep","zoid_rep",
      "newscore","metascore","rollavg"
    ]
    universal(self, "GAME_STATE", loglist)


  else:
    #session and types
    data = [":ts", get_time() - self.starttime,
        ":event_type", "GAME_STATE"]

    #gameplay values
    data += [
      ":delaying", self.needs_new_zoid,
      ":dropping", self.interval_toggle,
      ":curr_zoid", self.curr_zoid.type,
      ":next_zoid", self.next_zoid.type,
      ":zoid_rot", self.curr_zoid.rot,
      ":zoid_col", self.curr_zoid.get_col(),
      ":zoid_row", self.curr_zoid.get_row(),
      ":board_rep", "'%s'" % json.dumps( self.board ),
      ":zoid_rep", "'%s'" % json.dumps( zoid_in_board(self) )
    ]

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


# write .history file
def history( self ):
  def hwrite( name ):
    self.histfile.write(name + ": " + str(vars(self)[name]) + "\n")
    #self.unifile.write(":ts\t" + str(get_time()-self.starttime) +  "\t:event_type\t" + "SETUP_EVENT" + "\t" + ":" + name + "\t" + str(vars(self)[name]) + "\n")
    game_event(self, name, data1 = vars(self)[name], data2 = "setup")
  def hwrite2( name, val ):
    self.histfile.write(name + ": " + str(val) + "\n")
    #self.unifile.write(":ts\t" + str(get_time()-self.starttime) +  "\t:event_type\t" + "SETUP_EVENT" + "\t" + ":" + name + "\t" + str(val) + "\n")
    game_event(self, name, data1 = val, data2 = "setup")

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
