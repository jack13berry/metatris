import os, platform, json

# Log line types:
#   events
#   states
#   ep summs
#   game summs

# initialize log directory
def init( world ):
  if world.args.logfile:
    world.filename = world.SID + "_" + world.args.logfile
    world.logname = os.path.join( world.logdir, world.filename )

    if not os.path.exists( world.logdir ):
      os.makedirs( world.logdir )
    if not os.path.exists( world.logname):
      os.makedirs( world.logname)

    #open file
    world.histfile_path = world.logname + "/_hist_" + world.filename + ".hist"
    world.histfile = open( world.histfile_path, "w")

    world.configfile_path = world.logname + "/_config_" + world.filename + ".config"
    world.configfile = open( world.configfile_path, "w")

    world.unifile_path = world.logname + "/complete_" + world.filename + ".tsv"
    world.unifile = open( world.unifile_path + ".incomplete", "w")
    #world.uni_header()

    world.scorefile_path = world.logname + "/score_" + world.filename + ".tsv"
    world.scorefile = open( world.scorefile_path + ".incomplete", "w")

    if world.ep_log:
      world.epfile_path = world.logname + "/episodes_" + world.filename + ".tsv"
      world.epfile = open(   world.epfile_path + ".incomplete", "w" )

    if world.game_log:
      world.gamefile_path = world.logname + "/games_" + world.filename + ".tsv"
      world.gamefile = open (world.gamefile_path + ".incomplete", "w")

  else:
    world.logfile = sys.stdout

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

  world.fixed_header = uni_header + game_header + event_header + ep_header + state_header + board_header


def close_files( world ):
  game_event(world, "seed_sequence", data1 = world.seeds_used )
  world.unifile.close()
  os.rename( world.unifile_path + ".incomplete", world.unifile_path)
  world.scorefile.close()
  os.rename( world.scorefile_path + ".incomplete", world.scorefile_path)

  if world.ep_log:
    world.epfile.close()
    os.rename( world.epfile_path + ".incomplete", world.epfile_path)

  if world.game_log:
    world.gamefile.close()
    os.rename( world.gamefile_path + ".incomplete", world.gamefile_path)

  world.configfile.write("\n#fixed values to recreate session's seed sequence\n")
  world.configfile.write("random_seeds = " + ",".join(world.seeds_used) + "\n")
  world.configfile.write("permute_seeds = False\n")
  world.configfile.write("fixed_seeds = True\n")
  world.configfile.close()
  """
  world.logfile.close()
  os.rename( world.logfile_path + ".incomplete", world.logfile_path)
  """

def universal_header( world ):
  head = "\t".join( map(str, world.fixed_header) ) + "\n"
  world.unifile.write( head )
  if world.ep_log:
    world.epfile.write( head )
  if world.game_log:
    world.gamefile.write( head )

def universal( world, event_type, loglist, complete = False, evt_id = False, evt_data1 = False, evt_data2 = False, features = False):
  data = []
  def logit(val, key):
    data.append(val if key in loglist else "")

  #["ts","event_type"]
  data.append(world.moment - world.startTime)
  data.append(event_type)

  #["SID","session","game_number","game_type","episode_number","level","score","lines_cleared"
  #                "completed","game_duration","avg_ep_duration","zoid_sequence"]
  logit(world.SID, "SID")
  logit(world.ECID, "ECID")
  logit(world.session, "session")
  logit(world.game_type, "game_type")
  logit(world.game_number, "game_number")
  logit(world.episode_number, "episode_number")
  logit(world.level, "level")
  logit(world.score, "score")
  logit(world.lines_cleared, "lines_cleared")
  logit(complete, "completed")
  logit(world.moment - world.gameStartTime, "game_duration")
  logit((world.moment - world.gameStartTime) / (world.episode_number + 1), "avg_ep_duration")
  logit("'%s'" % json.dumps( world.zoid_buff ), "zoid_sequence")

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
  logit(world.curr_zoid.type, "curr_zoid")
  logit(world.next_zoid.type, "next_zoid")
  logit(world.danger_mode, "danger_mode")
  logit(json.dumps(world.evt_sequence), "evt_sequence")
  logit(world.rots, "rots")
  logit(world.trans, "trans")
  logit(world.rots + world.trans, "path_length")
  logit(world.min_rots, "min_rots")
  logit(world.min_trans, "min_trans")
  logit(world.min_rots + world.min_trans, "min_path")
  logit(world.rots - world.min_rots, "min_rots_diff")
  logit(world.trans - world.min_trans, "min_trans_diff")
  logit((world.rots - world.min_rots) + (world.trans - world.min_trans), "min_path_diff")
  logit(world.u_drops, "u_drops")
  logit(world.s_drops, "s_drops")
  logit(world.prop_drop, "prop_u_drops")
  logit(world.initial_lat, "initial_lat")
  logit(world.drop_lat, "drop_lat")
  logit(world.avg_latency, "avg_lat")
  logit(world.tetrises_game, "tetrises_game")
  logit(world.tetrises_level, "tetrises_level")
  logit(world.agree, "agree")

  #["delaying","dropping","zoid_rot","zoid_col","zoid_row"]
  logit(world.needs_new_zoid, "delaying")
  logit(1 if world.isDropping else 0, "dropping")
  logit(world.curr_zoid.rot, "zoid_rot")
  logit(world.curr_zoid.get_col(), "zoid_col")
  logit(world.curr_zoid.get_row(), "zoid_row")
  #logit(12345.0, "my_chris")



  #["board_rep","zoid_rep"]
  logit("'%s'" % json.dumps( world.board ), "board_rep")
  logit("'%s'" % json.dumps( zoid_in_board(world) ), "zoid_rep")


  if features or (event_type == "GAME_EVENT" and evt_id == "KEYPRESS" and evt_data1 == "PRESS" and world.episode_number > 0):
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

    z_answer =  world.features["pattern_div"]*(0.064355*factor1 + 0.003902*factor2 + 0.002922*factor6 + 0.002172*factor10 + 0.000086528*factor11 + 0.000236992*factor12)
    z_answer += world.features["mean_ht"]*(0.193209*factor1 + 0.009624*factor2 + 0.000498*factor6 + 0.000686*factor8 + 0.00027*factor9 + 0.000147968*factor11 + 0.000074263*factor12)
    z_answer += world.features["max_ht"]*(0.149666*factor1 + 0.011828*factor2 + 0.004558*factor6 + 0.000899*factor8 + 0.000083232*factor11 + 0.000081648*factor12)
    z_answer += world.features["weighted_cells"]*(0.179315*factor1 + 0.010358*factor2 + 0.001098*factor8 + 0.000543*factor9 + 0.000207088*factor12)
    z_answer += world.features["min_ht"]*(0.207176*factor1 + 0.003856*factor2 + 0.00081*factor6 + 0.00103*factor10)
    z_answer += world.features["row_trans"]*(0.154613*factor1 + 0.012476*factor2 + 0.006403*factor6 + 0.000112*factor10 + 0.000329672*factor11)
    z_answer += world.features["pits"]*(0.222091*factor1 + 0.000163*factor9)
    z_answer += world.features["pit_rows"]*(0.224396*factor1)
    z_answer += world.features["landing_height"]*(0.153465*factor1 + 0.009769*factor2 + 0.000506*factor6 + 0.001861*factor7 + 0.000789*factor8 + 0.000363*factor9 + 0.000170528*factor11)
    z_answer += world.features["col_trans"]*(0.21254*factor1 + 0.000677047*factor12)
    z_answer += world.features["pit_depth"]*(0.211193*factor1 + 0.000346*factor10 + 0.000091592*factor11)
    z_answer += world.features["lumped_pits"]*(0.21209*factor1 + 0.000499023*factor12)
    z_answer += world.features["cd_9"]*(0.042487*factor2 + 0.000971*factor6 + 0.002238*factor8 + 0.002022*factor9)
    z_answer += world.features["wells"]*(0.121581*factor2 + 0.000481*factor6 + 0.000146*factor10 + 0.000329672*factor11)
    z_answer += world.features["deep_wells"]*(0.120814*factor2 + 0.000625*factor6 + 0.000107648*factor11)
    z_answer += world.features["max_well"]*(0.122608*factor2 + 0.000524*factor6)
    z_answer += world.features["cuml_wells"]*(0.119032*factor2 + 0.000464*factor6)
    z_answer += world.features["jaggedness"]*(0.044479*factor2 + 0.019288*factor6 + 0.000362*factor7 + 0.000263*factor9 + 0.000146*factor10 + 0.000658952*factor11)
    z_answer += world.features["max_diffs"]*(0.031886*factor2 + 0.013543*factor6 + 0.001201*factor8 + 0.001194*factor9)
    z_answer += world.features["cd_1"]*(0.038496*factor2 + 0.001007*factor6 + 0.002238*factor8 + 0.001337*factor9 + 0.000147968*factor11)
    #######z_answer += world.features["resp_lat"]*0.0152810854045063
    z_answer += world.features["matches"]*(0.002177*factor2 + 0.001273*factor4 + 0.016701*factor7)
    z_answer += world.features["cd_7"]*(0.000424*factor9)
    z_answer += world.features["cd_8"]*(0.000341*factor8)
    z_answer += world.features["cd_2"]*(0.000152352*factor11)
    z_answer += world.features["d_max_ht"]*(0.001488*factor2 + 0.012226*factor7)
    z_answer += world.features["d_pits"]*(0.001488*factor2 + 0.001277*factor7)

    z_answer += world.prop_drop*(0.018262*factor1 + 0.003221*factor3 + 0.011608*factor4 + 0.001713*factor5 + 0.002048*factor7)
    z_answer += world.rots*(0.050161*factor3 + 0.00063*factor4 + 0.000619*factor5)
    z_answer += (world.rots - world.min_rots)*(0.049324*factor3 + 0.000584*factor4 + 0.000557*factor5)
    #print("{:3d}".format(world.rots) + " " + "{:3d}".format(world.min_rots))
    if world.drop_lat<.001:
      z_answer += int(1000 * (world.moment - world.epStartTime))*(0.005354*factor3 + 0.021913*factor4 + 0.002672*factor5)
      #print("{:0.1f}".format(world.moment))
      #print("   " + "{:0.3f}".format(world.epStartTime) + "  " + "{:0.1f}".format(int(1000 * (world.moment - world.epStartTime))*0.0124717621894591))
    else:
      z_answer += world.drop_lat*(0.005354*factor3 + 0.021913*factor4 + 0.002672*factor5)

    z_answer += (world.trans - world.min_trans)*(0.001156*factor3 + 0.035219*factor5 + 0.000446*factor7)
    z_answer += world.avg_latency*(0.001608*factor3 + 0.026717*factor4 + 0.000335*factor7)
    z_answer += world.trans*(0.000618*factor3 + 0.037343*factor5)
    z_answer += world.initial_lat*(0.013463*factor4 + 0.000403*factor7)

    world.features["z_answer"] = z_answer
    world.newscore = z_answer

    world.metascore = (world.metascore*world.metaticks + z_answer)/(world.metaticks+1)
    world.metaticks = world.metaticks+1
    world.features["z_metascore"] = world.metascore

    #world.scorefile.write(repr(z_answer)+"\n")

    world.roll_avg.append(world.features["z_answer"])
    while len(world.roll_avg) > 3:
      world.roll_avg.pop(0)

    if len(world.roll_avg) == 3:
      roll_sum = 0
      #print('Chris 1')
      for roll_val in world.roll_avg:
        #print('   Test1: ' + str(roll_val) + ' - Test2: ' + str(roll_sum))
        roll_sum += roll_val
      world.features["z_rollavg"] = roll_sum/3

    else:
      world.features["z_rollavg"] = 0.0

    logit(world.newscore, "newscore")
    logit(world.metascore, "metascore")
    logit(world.features["z_rollavg"], "rollavg")

      #print(f'So far... z_answer={world.features["z_answer"]:.4f}, z_rolling={world.features["z_rollavg"]:.4f}.')
    if features:
      for f in world.features_set:
        data.append(world.features[f])
    else:
      for f in world.features_set:
        data.append(world.features[f])

  else:
    for f in world.features_set:
      data.append("")

  #print('How often does this happen')

  out = "\t".join(map(str,data)) + "\n"

  world.unifile.write(out)

  if world.ep_log:
    if event_type == "EP_SUMM" or event_type == "GAME_SUMM":
      world.epfile.write(out)
  if world.game_log:
    if event_type == "GAME_SUMM":
      world.gamefile.write(out)


def episode( world ):
  world.update_stats_move( world.curr_zoid.get_col(), world.curr_zoid.rot, world.curr_zoid.get_row())
  if world.fixed_log:
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
    universal(world, "EP_SUMM", loglist, features = True)
  else:
    data = [":ts", world.moment - world.startTime,
        ":event_type", "EP_SUMM",
        ":SID", world.SID,
        ":session", world.session,
        ":game_number", world.game_number,
        ":episode_number", world.episode_number,
        ":level", world.level,
        ":score",world.score,
        ":lines_cleared", world.lines_cleared]

    data += [":curr_zoid", world.curr_zoid.type,
          ":next_zoid", world.next_zoid.type,
          ":danger_mode", world.danger_mode,
          ":zoid_rot", world.curr_zoid.rot,
          ":zoid_col", world.curr_zoid.get_col(),
          ":zoid_row", world.curr_zoid.get_row(),
          ":board_rep", "'%s'" % json.dumps( world.board ),
          ":zoid_rep", "'%s'" % json.dumps( zoid_in_board(world) )]


    #board statistics
    for f in world.features_set:
      data += [":"+f, world.features[f]]

    world.unifile.write("\t".join(map(str,data)) + "\n")
    if world.ep_log:
      world.epfile.write("\t".join(map(str,data)) + "\n")

def gameresults( world, complete = True ):
  if world.fixed_log:
    loglist = ["SID","ECID","session","game_type","game_number","episode_number",
          "level","score","lines_cleared","completed",
          "game_duration","avg_ep_duration","zoid_sequence","newscore","metascore","rollavg"]
    universal(world, "GAME_SUMM",loglist, complete = complete)
  else:
    data = [
      ":ts", world.moment - world.startTime,
      ":event_type", "GAME_SUMM",
      ":SID", world.SID,
      ":session", world.session,
      ":game_type", world.game_type,
      ":game_number", world.game_number,
      ":episode_number", world.episode_number,
      ":level", world.level,
      ":score", world.score,
      ":lines_cleared", world.lines_cleared,
      ":completed", complete,
      ":game_duration", world.moment - world.gameStartTime,
      ":avg_ep_duration", (world.moment - world.gameStartTime)/(world.episode_number+1),
      ":zoid_sequence", "'%s'" % json.dumps( world.zoid_buff )
    ]

    world.unifile.write("\t".join(map(str,data)) + "\n")
    if world.ep_log:
      world.epfile.write("\t".join(map(str,data)) + "\n")
    if world.game_log:
      world.gamefile.write("\t".join(map(str,data)) + "\n")

  message = [
    "Game " , str(world.game_number) , ":\n" ,
    "\tScore: " , str(world.score) , "\n" ,
    "\tLevel: " , str(world.level) , "\n" ,
    "\tLines: " , str(world.lines_cleared) , "\n" ,
    "\tZoids: " , str(world.episode_number) , "\n" ,
    "\tSID: " , str(world.SID) , "\n" ,
    "\tComplete: ", str(complete), "\n",
    "\tSession: " + str(world.session) , "\n" ,
    "\tGame Type: " + str(world.game_type) + "\n",
    "\tGame duration:" + str(world.moment - world.gameStartTime) + "\n",
    "\tAvg Ep duration:" + str((world.moment - world.gameStartTime)/(world.episode_number+1)) + "\n"
  ]

  message = "".join(message)
  if complete:
    world.game_scores += [world.score]
  print(message)

#log a game event
def game_event( world, id, data1 = "", data2 = "" ):
  if world.fixed_log:
    loglist = [
      "SID","ECID","session","game_type","game_number","episode_number",
      "level","score","lines_cleared", "curr_zoid","next_zoid","danger_mode",
      "delaying","dropping", "newscore","metascore","rollavg",
      "zoid_rot", "zoid_col", "zoid_row"
    ]
    universal(world, "GAME_EVENT", loglist, evt_id = id, evt_data1 = data1, evt_data2 = data2)

  else:
    out = [
      ":ts", world.moment - world.startTime,
      ":event_type", 'GAME_EVENT',
      ":evt_id", id,
      ":evt_data1", data1,
      ":evt_data2", data2
    ]
    outstr = "\t".join( map( str, out ) ) + "\n"
    world.unifile.write( outstr )

#log the world state
def worldState( world ):
  if world.fixed_log:
    loglist = [
      "SID","ECID","session","game_type","game_number","episode_number",
      "level","score","lines_cleared","danger_mode",
      "delaying","dropping","curr_zoid","next_zoid",
      "zoid_rot","zoid_col","zoid_row","board_rep","zoid_rep",
      "newscore","metascore","rollavg"
    ]
    universal(world, "GAME_STATE", loglist)


  else:
    #session and types
    data = [":ts", world.moment - world.startTime,
        ":event_type", "GAME_STATE"]

    #gameplay values
    data += [
      ":delaying", world.needs_new_zoid,
      ":dropping", 1 if world.isDropping else 0,
      ":curr_zoid", world.curr_zoid.type,
      ":next_zoid", world.next_zoid.type,
      ":zoid_rot", world.curr_zoid.rot,
      ":zoid_col", world.curr_zoid.get_col(),
      ":zoid_row", world.curr_zoid.get_row(),
      ":board_rep", "'%s'" % json.dumps( world.board ),
      ":zoid_rep", "'%s'" % json.dumps( zoid_in_board(world) )
    ]

    world.unifile.write( "\t".join( map( str, data ) ) + "\n" )


def zoid_in_board( world ):
  zoid = world.curr_zoid.get_shape()
  z_x = world.curr_zoid.col
  z_y = world.game_ht - world.curr_zoid.row

  board = []
  for y in range(0,world.game_ht):
    line = []
    for x in range(0,world.game_wd):
      line.append(0)
    board.append(line)

  for i in range(0,len(zoid)):
    for j in range(0,len(zoid[0])):
      if i + z_y >= 0 and i + z_y < len(board):
        if j + z_x >= 0 and j + z_x < len(board[0]):
          board[i + z_y][j + z_x] = zoid[i][j]

  return board


# write .history file
def history( world ):
  def hwrite( name ):
    world.histfile.write(name + ": " + str(vars(world)[name]) + "\n")
    #world.unifile.write(":ts\t" + str(world.moment-world.startTime) +  "\t:event_type\t" + "SETUP_EVENT" + "\t" + ":" + name + "\t" + str(vars(world)[name]) + "\n")
    game_event(world, name, data1 = vars(world)[name], data2 = "setup")
  def hwrite2( name, val ):
    world.histfile.write(name + ": " + str(val) + "\n")
    #world.unifile.write(":ts\t" + str(world.moment-world.startTime) +  "\t:event_type\t" + "SETUP_EVENT" + "\t" + ":" + name + "\t" + str(val) + "\n")
    game_event(world, name, data1 = val, data2 = "setup")

  #capture all static variables

  hwrite("SID")
  hwrite("RIN")
  hwrite("ECID")
  hwrite("game_type")
  hwrite2("Start time", world.startTime)
  hwrite2("Session" ,world.session)
  hwrite("random_seeds")
  hwrite("seed_order")
  hwrite2("Log-Version" ,world.LOG_VERSION)
  hwrite("distance_from_screen")

  world.histfile.write("\nManipulations:\n")
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

  world.histfile.write("\nMechanics:\n")
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

  world.histfile.write("\nLayout:\n")
  hwrite2("Screen X",world.screeninfo.current_w)
  hwrite2("Screen Y",world.screeninfo.current_h)
  hwrite2("worldsurf_rect.width",world.worldsurf_rect.width)
  hwrite2("worldsurf_rect.height",world.worldsurf_rect.height)
  hwrite2("gamesurf_rect.top",world.gamesurf_rect.top)
  hwrite2("gamesurf_rect.left",world.gamesurf_rect.left)
  hwrite2("gamesurf_rect.width",world.gamesurf_rect.width)
  hwrite2("gamesurf_rect.height",world.gamesurf_rect.height)
  hwrite2("nextsurf_rect.top",world.nextsurf_rect.top)
  hwrite2("nextsurf_rect.left",world.nextsurf_rect.left)
  hwrite2("nextsurf_rect.width",world.nextsurf_rect.width)
  hwrite2("nextsurf_rect.height",world.nextsurf_rect.height)

  if world.keep_zoid:
    hwrite2("keptsurf_rect.top",world.keptsurf_rect.top)
    hwrite2("keptsurf_rect.left",world.keptsurf_rect.left)
    hwrite2("keptsurf_rect.width",world.keptsurf_rect.width)
    hwrite2("keptsurf_rect.height",world.keptsurf_rect.height)

  hwrite("side")
  hwrite("score_lab_left")
  hwrite("lines_lab_left")
  hwrite("level_lab_left")
  hwrite("newscore_lab_left")
  hwrite("score_left")
  hwrite("lines_left")
  hwrite("level_left")
  hwrite("newscore_left")
  world.histfile.write("\n")
  world.histfile.close()
