import pygame

import gui

def draw( self ):
  self.worldsurf.fill( self.bg_color )
  draw_gridlines(self)

  gui.board(self)
  if not self.needs_new_zoid:
    draw_curr_zoid(self)

  #self.nextsurf.fill( ( 100, 100, 100 ) )
  self.nextsurf.fill( self.bg_color )
  draw_next_zoid(self)

  if self.keep_zoid:
    self.keptsurf.fill( self.kept_bgc )
    draw_kept_zoid(self)

  gui.textSurface(self, "Game %d" % self.game_number, self.intro_font, ( 196, 196, 196 ), ( 120, 60 ), self.worldsurf )

  draw_scores(self)
  draw_borders(self)


def drawPaused( self ):
  if self.show_high_score:
    gui.textSurface(self, "High:", self.scores_font, ( 210, 210, 210 ), self.high_lab_left, self.worldsurf, "midleft" )
    gui.textSurface(self, str( self.high_score ), self.scores_font, ( 210, 210, 210 ), self.high_left, self.worldsurf, "midright" )

  gui.textSurface(self, "Game %d" % self.game_number, self.intro_font, ( 196, 196, 196 ), ( 120, 60 ), self.worldsurf )

  draw_scores(self)
  draw_borders(self)
  gui.textSurface(self, "PAUSED", self.pause_font, ( 210, 210, 210 ), self.worldsurf_rect.center, self.worldsurf )


#draw gameover animation and message
def drawGameOver( self ):
  tick = self.gameover_anim_tick
  #paint one more of the game world
  if tick == 0:
    draw(self)

  #animate
  elif tick > 0 and tick <= self.gameover_tick_max:
    ix = 0
    iy = 0
    for i in range( 0, int(tick / 2) ):
      for j in self.gameover_board[i]:
        gui.square(self, self.gamesurf, ix, iy, color_id = self.zoidrand.randint( 1, 7 ) )
        ix += self.side
      ix = 0
      iy += self.side

    if not self.inverted:
      self.worldsurf.blit( self.gamesurf, self.gamesurf_rect )
    elif self.inverted:
      self.worldsurf.blit( pygame.transform.flip(self.gamesurf, False, True), self.gamesurf_rect)

  #give gameover message
  elif tick > self.gameover_tick_max:
    gui.textSurfaceBox(self)
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

    game_complete = self.episode_number == self.max_eps - 1
    if self.continues == 0:
      msg1 = ""
      msg2 = ""
      msg3 = ""
      offset = 0
      col = colors[0]

    if game_complete:
      msg0 = "COMPLETED!"
    elif self.continues < 0:
      msg1 = "Continue?"
    gui.textSurface(self, msg0, self.end_font, col, ( self.gamesurf_rect.centerx, self.gamesurf_rect.centery - offset ), self.worldsurf )
    gui.textSurface(self, msg1, self.scores_font, self.end_text_color, ( self.gamesurf_rect.centerx, self.gamesurf_rect.centery + offset ), self.worldsurf )
    if int((tick - self.gameover_tick_max) / (self.fps * 2))% 3 < 2:
      gui.textSurface(self, msg2, self.scores_font, self.end_text_color, ( self.gamesurf_rect.centerx, self.gamesurf_rect.centery + (2 * offset) ), self.worldsurf )
      gui.textSurface(self, msg3, self.scores_font, self.end_text_color, ( self.gamesurf_rect.centerx, self.gamesurf_rect.centery + (3 * offset) ), self.worldsurf )

  self.gameover_anim_tick += self.ticks_per_frame
  draw_scores(self)
  draw_borders(self)


def draw_AAR_zoids( self ):
  if self.AAR_curr_zoid_hl:
    gui.blocks(self, self.curr_zoid.get_shape(), self.gamesurf, self.gamesurf_rect, self.curr_zoid.col * self.side, ( self.game_ht - self.curr_zoid.row ) * self.side, alpha = self.AAR_dim * 2, gray = self.gray_zoid)
  if self.solved:
    gui.blocks(self, self.curr_zoid.get_shape(rot = self.solved_rot), self.gamesurf, self.gamesurf_rect, self.solved_col * self.side, ( self.game_ht - self.solved_row) * self.side, alpha = 255, gray = self.gray_zoid)


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
    gui.textSurface(self, "High:", self.scores_font, ( 210, 210, 210 ), self.high_lab_left, self.worldsurf, "midleft" )
    gui.textSurface(self, str( self.high_score ), self.scores_font, ( 210, 210, 210 ), self.high_left, self.worldsurf, "midright" )

  # gui.textSurface(self, "Game %d" % self.game_number, self.intro_font, ( 196, 196, 196 ), ( self.gamesurf_rect.centerx, self.gamesurf_rect.top / 2 ), self.worldsurf )
  gui.textSurface(self, "Game %d" % self.game_number, self.intro_font, ( 196, 196, 196 ), ( 120, 60 ), self.worldsurf )
  draw_scores(self)

  draw_AAR_zoids(self)

  draw_borders(self)

  gui.board(self, alpha = self.AAR_dim)
  #gui.textSurface(self, "PAUSED", self.pause_font, ( 210, 210, 210 ), self.worldsurf_rect.center, self.worldsurf )


#draw borders around game regions
def draw_borders( self ):
  color = self.border_color

  metagreen = max(0, int( (100-self.newscore)*(2.00) ))
  metared = min(300 - metagreen, 200)
  metacolor = ( metared, metagreen, 20 )
  pygame.draw.rect( self.worldsurf, metacolor, self.gamesurf_border_rect, self.border_thickness )
  if self.look_ahead > 0:
    pygame.draw.rect( self.worldsurf, metacolor, self.nextsurf_border_rect, self.border_thickness )
  if self.keep_zoid:
    pygame.draw.rect( self.worldsurf, color, self.keptsurf_border_rect, self.border_thickness )

def draw_gridlines( self ):
  if self.gridlines_x:
    for i in range( 1 , self.game_wd ):
      pygame.draw.line( self.gamesurf, self.gridlines_color, (i * self.side - 1, 0), (i*self.side - 1, self.gamesurf_rect.height) , 2)
  if self.gridlines_y:
    for i in range( 1 , self.game_ht ):
      pygame.draw.line( self.gamesurf, self.gridlines_color, (0, i * self.side - 1), (self.gamesurf_rect.width, i*self.side - 1) , 2)


def draw_scores( self ):
  gui.textSurface(self, "Score:", self.scores_font, ( 210, 210, 210 ), self.score_lab_left, self.worldsurf, "midleft" )
  gui.textSurface(self, "Tetrises:", self.scores_font, ( 210, 210, 210 ), self.tetrises_lab_left, self.worldsurf, "midleft" )
  gui.textSurface(self, "Lines:", self.scores_font, ( 210, 210, 210 ), self.lines_lab_left, self.worldsurf, "midleft" )
  gui.textSurface(self, "Level:", self.scores_font, ( 210, 210, 210 ), self.level_lab_left, self.worldsurf, "midleft" )

  gui.textSurface(self, str( self.score ), self.scores_font, ( 210, 210, 210 ), self.score_left, self.worldsurf, "midright" )
  gui.textSurface(self, str( self.tetrises_game ), self.scores_font, ( 210, 210, 210 ), self.tetrises_left, self.worldsurf, "midright" )
  gui.textSurface(self, str( self.lines_cleared ), self.scores_font, ( 210, 210, 210 ), self.lines_left, self.worldsurf, "midright" )
  gui.textSurface(self, str( self.level ), self.scores_font, ( 210, 210, 210 ), self.level_left, self.worldsurf, "midright" )
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
    pygame.draw.rect( self.worldsurf, (20, 162, 20), (bar_x,bar_y-red_height-orange_height-yellow_height-green_height,bar_width,green_height), bar_thickness)

  #gui.textSurface(self, "New:", self.scores_font, ( 210, 210, 210 ), self.newscore_lab_left, self.worldsurf, "midleft" )
  # print ("Score: '%s' / '%s'" % (self.newscore, self.metascore))
  gui.textSurface(self, "{:0.2f}".format(self.newscore), self.scores_font, ( 210, 210, 210 ), (bar_x+bar_width+40,bar_top), self.worldsurf, "midright" )
  gui.textSurface(self, "Meta:", self.scores_font, ( 210, 210, 210 ), (600,185), self.worldsurf, "midleft" )
  gui.textSurface(self, "{:0.3f}".format(self.metascore), self.scores_font, ( 210, 210, 210 ), (720,185), self.worldsurf, "midright" )
  gui.textSurface(self, "{:0.3f}".format(self.newscore), self.scores_font, (77, 77, 77), (400, 30), self.worldsurf)


#draw the current zoid at its current location on the board
def draw_curr_zoid( self ):
  if (not self.visible_zoid) or self.board_mask or self.mask_toggle:
    return

  gui.blocks(self, self.curr_zoid.get_shape(), self.gamesurf, self.gamesurf_rect, self.curr_zoid.col * self.side, ( self.game_ht - self.curr_zoid.row ) * self.side, gray = self.gray_zoid)
  if self.ghost_zoid:
    gui.blocks(self, self.curr_zoid.get_shape(), self.gamesurf, self.gamesurf_rect, self.curr_zoid.col * self.side, ( self.game_ht - self.curr_zoid.to_bottom()) * self.side, alpha = self.ghost_alpha, gray = self.gray_zoid )

  if self.hint_toggle and self.solved:
    if not self.hint_context:
      gui.blocks(self, self.curr_zoid.get_shape(rot = self.solved_rot), self.gamesurf, self.gamesurf_rect, self.solved_col * self.side, ( self.game_ht - self.solved_row) * self.side, alpha = self.ghost_alpha, gray = self.gray_zoid )

  if self.hint_context and self.solved:
    hint_col_agree = abs(self.solved_col - self.curr_zoid.col) <= self.hint_context_col_tol
    hint_agree = self.solved_rot == self.curr_zoid.rot and hint_col_agree
    if hint_agree:
      gui.blocks(self, self.curr_zoid.get_shape(rot = self.solved_rot), self.gamesurf, self.gamesurf_rect, self.solved_col * self.side, ( self.game_ht - self.solved_row) * self.side, alpha = self.ghost_alpha, gray = self.gray_zoid )


#draw the next zoid inside the next box
def draw_next_zoid( self ):
  if self.look_ahead > 0:
    if not self.next_mask or self.mask_toggle:
      next_rep = self.next_zoid.get_next_rep()
      vert = (self.next_size - float(len(next_rep))) / 2.0
      horiz = (self.next_size - float(len(next_rep[0]))) / 2.0
      gui.blocks(self, next_rep, self.nextsurf, self.nextsurf_rect, int( self.side * (horiz + .25) ), int( self.side * (vert + .25) ), alpha = self.next_alpha, gray = self.gray_next)
    else:
      self.nextsurf.fill( self.mask_color )
      self.worldsurf.blit( self.nextsurf , self.nextsurf_rect )


def draw_kept_zoid( self ):
  if self.kept_zoid != None:
    kept_rep = self.kept_zoid.get_next_rep()
    vert = (self.next_size - float(len(kept_rep))) / 2.0
    horiz = (self.next_size - float(len(kept_rep[0]))) / 2.0
    gui.blocks(self,  kept_rep, self.keptsurf, self.keptsurf_rect, int( self.side * (horiz + .25) ), int( self.side * (vert + .25) ), gray = self.gray_kept)
  else:
    gui.blocks(self, Zoid.next_reps['none'], self.keptsurf, self.keptsurf_rect, 0, 0, gray = self.gray_kept)