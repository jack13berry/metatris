import pygame, platform, time
import pygame, numpy

get_time = time.time if platform.system() == 'Windows' else time.process_time

#draw text to the screen
def textSurface( self, text, font, color, loc, surf, justify = "center" ):
  t = font.render( text, True, color )
  tr = t.get_rect()
  setattr( tr, justify, loc )
  surf.blit( t, tr )
  return tr
###

#draw any text box
def textSurface_box( self ):
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
        draw_square(self, surf, ix, iy, color_id = j, alpha = alpha, gray = gray )
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
def pauseView( self ):

  if self.show_high_score:
    textSurface(self, "High:", self.scores_font, ( 210, 210, 210 ), self.high_lab_left, self.worldsurf, "midleft" )
    textSurface(self, str( self.high_score ), self.scores_font, ( 210, 210, 210 ), self.high_left, self.worldsurf, "midright" )

  # textSurface(self, "Game %d" % self.game_number, self.intro_font, ( 196, 196, 196 ), ( self.gamesurf_rect.centerx, self.gamesurf_rect.top / 2 ), self.worldsurf )
  textSurface(self, "Game %d" % self.game_number, self.intro_font, ( 196, 196, 196 ), ( 120, 60 ), self.worldsurf )

  textSurface(self, "Tetrises:", self.scores_font, ( 210, 210, 210 ), self.zoids_lab_left, self.worldsurf, "midleft" )
  textSurface(self, "Score:", self.scores_font, ( 210, 210, 210 ), self.score_lab_left, self.worldsurf, "midleft" )
  textSurface(self, "Lines:", self.scores_font, ( 210, 210, 210 ), self.lines_lab_left, self.worldsurf, "midleft" )
  textSurface(self, "Level:", self.scores_font, ( 210, 210, 210 ), self.level_lab_left, self.worldsurf, "midleft" )

  textSurface(self, str( self.zoids_placed ), self.scores_font, ( 210, 210, 210 ), self.zoids_left, self.worldsurf, "midright" )
  textSurface(self, str( self.score ), self.scores_font, ( 210, 210, 210 ), self.score_left, self.worldsurf, "midright" )
  textSurface(self, str( self.lines_cleared ), self.scores_font, ( 210, 210, 210 ), self.lines_left, self.worldsurf, "midright" )
  textSurface(self, str( self.level ), self.scores_font, ( 210, 210, 210 ), self.level_left, self.worldsurf, "midright" )
  draw_newscore(self)

  draw_borders(self)
  textSurface(self, "PAUSED", self.pause_font, ( 210, 210, 210 ), self.worldsurf_rect.center, self.worldsurf )

#draw the underlying game board the current zoid interacts with
def board( self, alpha = 255):
  echo = (self.board_echo_placed and self.are_counter > 0) or (self.board_echo_lc and self.lc_counter > 0)
  if self.visible_board or echo:
    if not self.board_mask or not self.mask_toggle:
      if self.dimtris and not echo:
        alpha = self.dimtris_alphas[min(self.level, len(self.dimtris_alphas)-1)]
      draw_blocks(self, self.board, self.gamesurf, self.gamesurf_rect, resetX = True, alpha = alpha, gray = self.gray_board)
    else:
      self.gamesurf.fill( self.mask_color )
      self.worldsurf.blit( self.gamesurf , self.gamesurf_rect)

#draw the current zoid at its current location on the board
def draw_curr_zoid( self ):
  if self.visible_zoid:
    if not self.board_mask or not self.mask_toggle:
      draw_blocks(self, self.curr_zoid.get_shape(), self.gamesurf, self.gamesurf_rect, self.curr_zoid.col * self.side, ( self.game_ht - self.curr_zoid.row ) * self.side, gray = self.gray_zoid)
      if self.ghost_zoid:
        draw_blocks(self, self.curr_zoid.get_shape(), self.gamesurf, self.gamesurf_rect, self.curr_zoid.col * self.side, ( self.game_ht - self.curr_zoid.to_bottom()) * self.side, alpha = self.ghost_alpha, gray = self.gray_zoid )

      if self.hint_toggle and self.solved:
        if not self.hint_context:
          draw_blocks(self, self.curr_zoid.get_shape(rot = self.solved_rot), self.gamesurf, self.gamesurf_rect, self.solved_col * self.side, ( self.game_ht - self.solved_row) * self.side, alpha = self.ghost_alpha, gray = self.gray_zoid )
      if self.hint_context and self.solved:
        hint_col_agree = abs(self.solved_col - self.curr_zoid.col) <= self.hint_context_col_tol
        hint_agree = self.solved_rot == self.curr_zoid.rot and hint_col_agree
        if hint_agree:
          draw_blocks(self, self.curr_zoid.get_shape(rot = self.solved_rot), self.gamesurf, self.gamesurf_rect, self.solved_col * self.side, ( self.game_ht - self.solved_row) * self.side, alpha = self.ghost_alpha, gray = self.gray_zoid )

def draw_AAR_zoids( self ):
  if self.AAR_curr_zoid_hl:
    draw_blocks(self, self.curr_zoid.get_shape(), self.gamesurf, self.gamesurf_rect, self.curr_zoid.col * self.side, ( self.game_ht - self.curr_zoid.row ) * self.side, alpha = self.AAR_dim * 2, gray = self.gray_zoid)
  if self.solved:
    draw_blocks(self, self.curr_zoid.get_shape(rot = self.solved_rot), self.gamesurf, self.gamesurf_rect, self.solved_col * self.side, ( self.game_ht - self.solved_row) * self.side, alpha = 255, gray = self.gray_zoid)


#draw the next zoid inside the next box
def draw_next_zoid( self ):
  if self.look_ahead > 0:
    if not self.next_mask or self.mask_toggle:
      next_rep = self.next_zoid.get_next_rep()
      vert = (self.next_size - float(len(next_rep))) / 2.0
      horiz = (self.next_size - float(len(next_rep[0]))) / 2.0
      draw_blocks(self, next_rep, self.nextsurf, self.nextsurf_rect, int( self.side * (horiz + .25) ), int( self.side * (vert + .25) ), alpha = self.next_alpha, gray = self.gray_next)
    else:
      self.nextsurf.fill( self.mask_color )
      self.worldsurf.blit( self.nextsurf , self.nextsurf_rect )

def draw_kept_zoid( self ):
  if self.kept_zoid != None:
    kept_rep = self.kept_zoid.get_next_rep()
    vert = (self.next_size - float(len(kept_rep))) / 2.0
    horiz = (self.next_size - float(len(kept_rep[0]))) / 2.0
    draw_blocks(self,  kept_rep, self.keptsurf, self.keptsurf_rect, int( self.side * (horiz + .25) ), int( self.side * (vert + .25) ), gray = self.gray_kept)
  else:
    draw_blocks(self, Zoid.next_reps['none'], self.keptsurf, self.keptsurf_rect, 0, 0, gray = self.gray_kept)

#draw the introduction screen
def intro( self ):
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
      textSurface(self, "press START to begin", self.scores_font, ( 50, 50, 50 ), ( self.worldsurf_rect.centerx, self.worldsurf_rect.height - self.worldsurf_rect.height / 5 ), self.worldsurf )
    else:
      textSurface(self, "press SPACE BAR to begin", self.scores_font, ( 50, 50, 50 ), ( self.worldsurf_rect.centerx, self.worldsurf_rect.height - self.worldsurf_rect.height / 5 ), self.worldsurf )
  if self.title_blink_timer >= self.fps * 3 / 2:
      self.title_blink_timer = 0

def draw_AAR(self):
  self.worldsurf.fill( self.bg_color )

  self.gamesurf.fill( self.bg_color )

  draw_gridlines(self)

  #self.nextsurf.fill( ( 100, 100, 100 ) )
  self.nextsurf.fill( self.bg_color )
  draw_next_zoid(self)

  if self.keep_zoid:
    self.keptsurf.fill( self.kept_bgc )
    draw_kept_zoid(self)

  if self.show_high_score:
    textSurface(self, "High:", self.scores_font, ( 210, 210, 210 ), self.high_lab_left, self.worldsurf, "midleft" )
    textSurface(self, str( self.high_score ), self.scores_font, ( 210, 210, 210 ), self.high_left, self.worldsurf, "midright" )

  # textSurface(self, "Game %d" % self.game_number, self.intro_font, ( 196, 196, 196 ), ( self.gamesurf_rect.centerx, self.gamesurf_rect.top / 2 ), self.worldsurf )
  textSurface(self, "Game %d" % self.game_number, self.intro_font, ( 196, 196, 196 ), ( 120, 60 ), self.worldsurf )
  draw_scores(self)

  draw_AAR_zoids(self)

  draw_borders(self)

  board(self, alpha = self.AAR_dim)
  #textSurface(self, "PAUSED", self.pause_font, ( 210, 210, 210 ), self.worldsurf_rect.center, self.worldsurf )

#draw the main game when being played
def draw_game( self ):
  self.worldsurf.fill( self.bg_color )

  draw_gridlines(self)

  board(self)
  if not self.needs_new_zoid:
    draw_curr_zoid(self)

  #self.nextsurf.fill( ( 100, 100, 100 ) )
  self.nextsurf.fill( self.bg_color )
  draw_next_zoid(self)

  if self.keep_zoid:
    self.keptsurf.fill( self.kept_bgc )
    draw_kept_zoid(self)


  # textSurface(self, "Game %d" % self.game_number, self.intro_font, ( 196, 196, 196 ), ( self.gamesurf_rect.centerx, self.gamesurf_rect.top / 2 ), self.worldsurf )
  textSurface(self, "Game %d" % self.game_number, self.intro_font, ( 196, 196, 196 ), ( 120, 60 ), self.worldsurf )


def draw_scores( self ):
  textSurface(self, "Tetrises:", self.scores_font, ( 210, 210, 210 ), self.zoids_lab_left, self.worldsurf, "midleft" )
  textSurface(self, "Score:", self.scores_font, ( 210, 210, 210 ), self.score_lab_left, self.worldsurf, "midleft" )
  textSurface(self, "Lines:", self.scores_font, ( 210, 210, 210 ), self.lines_lab_left, self.worldsurf, "midleft" )
  textSurface(self, "Level:", self.scores_font, ( 210, 210, 210 ), self.level_lab_left, self.worldsurf, "midleft" )

  textSurface(self, str( self.zoids_placed ), self.scores_font, ( 210, 210, 210 ), self.zoids_left, self.worldsurf, "midright" )
  textSurface(self, str( self.score ), self.scores_font, ( 210, 210, 210 ), self.score_left, self.worldsurf, "midright" )
  textSurface(self, str( self.lines_cleared ), self.scores_font, ( 210, 210, 210 ), self.lines_left, self.worldsurf, "midright" )
  textSurface(self, str( self.level ), self.scores_font, ( 210, 210, 210 ), self.level_left, self.worldsurf, "midright" )
  draw_newscore(self)


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

  #textSurface(self, "New:", self.scores_font, ( 210, 210, 210 ), self.newscore_lab_left, self.worldsurf, "midleft" )
  # print ("Score: '%s' / '%s'" % (self.newscore, self.metascore))
  textSurface(self, "{:0.2f}".format(self.newscore), self.scores_font, ( 210, 210, 210 ), (bar_x+bar_width+40,bar_top), self.worldsurf, "midright" )
  textSurface(self, "Meta:", self.scores_font, ( 210, 210, 210 ), (600,185), self.worldsurf, "midleft" )
  textSurface(self, "{:0.3f}".format(self.metascore), self.scores_font, ( 210, 210, 210 ), (720,185), self.worldsurf, "midright" )
  textSurface(self, "{:0.3f}".format(self.newscore), self.scores_font, (77, 77, 77), (400, 30), self.worldsurf)

###

#draw borders around game regions
def draw_borders( self ):
  if self.args.eyetracker and self.eye_conf_borders:
    avg_conf = int((self.i_x_conf + self.i_y_conf) / 2.0)
    color = (min(250,150+(avg_conf/3)),max(150,250-(avg_conf/3)),50)
  else:
    color = self.border_color

  metagreen = max(0, int( (100-self.newscore)*(2.55) ))
  metared = min(400 - metagreen, 255)
  metacolor = ( metared, metagreen, 90 )
  pygame.draw.rect( self.worldsurf, metacolor, self.gamesurf_border_rect, self.border_thickness )
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
    draw_game(self)

  #animate
  elif tick > 0 and tick <= self.gameover_tick_max:
    ix = 0
    iy = 0
    for i in range( 0, int(tick / 2) ):
      for j in self.gameover_board[i]:
        draw_square(self, self.gamesurf, ix, iy, color_id = self.zoidrand.randint( 1, 7 ) )
        ix += self.side
      ix = 0
      iy += self.side

    if not self.inverted:
      self.worldsurf.blit( self.gamesurf, self.gamesurf_rect )
    elif self.inverted:
      self.worldsurf.blit( pygame.transform.flip(self.gamesurf, False, True), self.gamesurf_rect)

  #give gameover message
  elif tick > self.gameover_tick_max:
    textSurface_box(self)
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
    textSurface(self, msg0, self.end_font, col, ( self.gamesurf_rect.centerx, self.gamesurf_rect.centery - offset ), self.worldsurf )
    textSurface(self, msg1, self.scores_font, self.end_text_color, ( self.gamesurf_rect.centerx, self.gamesurf_rect.centery + offset ), self.worldsurf )
    if int((tick - self.gameover_tick_max) / (self.fps * 2))% 3 < 2:
      textSurface(self, msg2, self.scores_font, self.end_text_color, ( self.gamesurf_rect.centerx, self.gamesurf_rect.centery + (2 * offset) ), self.worldsurf )
      textSurface(self, msg3, self.scores_font, self.end_text_color, ( self.gamesurf_rect.centerx, self.gamesurf_rect.centery + (3 * offset) ), self.worldsurf )

  self.gameover_anim_tick += self.ticks_per_frame

#main draw updater
def drawTheWorld( self ):
  if self.state == self.STATE_INTRO:
    intro(self)
  elif self.state == self.STATE_PLAY:
    self.bg_color = self.tetris_flash_colors[self.tetris_flash_tick % 2]
    if self.tetris_flash_tick > 0:
      self.tetris_flash_tick -= 1
    self.gamesurf.fill( self.bg_color )
    draw_game(self)
    draw_scores(self)
    draw_borders(self)
  elif self.state == self.STATE_PAUSE:
    self.worldsurf.fill( ( 0, 0, 0 ) )
    pauseView(self)
  elif self.state == self.STATE_GAMEOVER:
    draw_game_over(self)
    draw_scores(self)
    draw_borders(self)
  elif self.state == self.STATE_AAR:
    draw_AAR(self)
  if self.args.eyetracker and eyetrackerSupport and (self.draw_fixation or self.draw_samps or self.draw_avg or self.draw_err or self.spotlight):
    draw_fix(self)
  self.screen.blit( self.worldsurf, self.worldsurf_rect )
  pygame.display.flip()
###
