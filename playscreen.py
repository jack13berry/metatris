import pygame

import gui
from zoid import Zoid

def draw( world ):
  world.gamesurf.fill( world.bg_color )
  world.worldsurf.fill( world.bg_color )
  draw_gridlines(world)
  draw_scores(world)
  draw_borders(world)

  gui.board(world)

  if not world.needs_new_zoid:
    draw_curr_zoid(world)

  world.nextsurf.fill( world.bg_color )
  draw_next_zoid(world)

  if world.keep_zoid:
    world.keptsurf.fill( world.kept_bgc )
    draw_kept_zoid(world)

  gui.textSurface("Game %d" % world.game_number, world.intro_font, ( 196, 196, 196 ), ( 120, 60 ), world.worldsurf )


def drawPaused( world ):
  world.worldsurf.fill( world.bg_color )
  if world.show_high_score:
    gui.textSurface("High:", world.scores_font, ( 210, 210, 210 ), world.high_lab_left, world.worldsurf, "midleft" )
    gui.textSurface(str( world.high_score ), world.scores_font, ( 210, 210, 210 ), world.high_left, world.worldsurf, "midright" )

  gui.textSurface("Game %d" % world.game_number, world.intro_font, ( 196, 196, 196 ), ( 120, 60 ), world.worldsurf )

  draw_scores(world)
  draw_borders(world)
  gui.textSurface("PAUSED", world.pause_font, ( 210, 210, 210 ), world.worldsurf_rect.center, world.worldsurf )


#draw gameover animation and message
def drawGameOver( world ):
  tick = world.gameover_anim_tick
  #paint one more of the game world
  if tick == 0:
    draw(world)

  #animate
  elif tick > 0 and tick <= world.gameover_tick_max:
    ix = 0
    iy = 0
    for i in range( 0, int(tick / 2) ):
      for j in world.gameover_board[i]:
        gui.square(world, world.gamesurf, ix, iy, color_id = world.zoidrand.randint( 1, 7 ) )
        ix += world.side
      ix = 0
      iy += world.side

    if not world.inverted:
      world.worldsurf.blit( world.gamesurf, world.gamesurf_rect )
    elif world.inverted:
      world.worldsurf.blit( pygame.transform.flip(world.gamesurf, False, True), world.gamesurf_rect)

  #give gameover message
  elif tick > world.gameover_tick_max:
    gui.textSurfaceBox(world)
    msg0 = "GAME OVER"
    msg1 = "Continue? ["+str(world.continues)+"]"

    if pygame.joystick.get_count() > 0:
      msg2 = "Press START"
      msg3 = "Esc to Exit"
    else:
      msg2 = "Press Spacebar"
      msg3 = "Esc to Exit"
    offset = 36
    colors =  world.NES_colors[world.level%len(world.NES_colors)]
    col = colors[1]

    game_complete = world.episode_number == world.max_eps - 1
    if world.continues == 0:
      msg1 = ""
      msg2 = ""
      msg3 = ""
      offset = 0
      col = colors[0]

    if game_complete:
      msg0 = "COMPLETED!"
    elif world.continues < 0:
      msg1 = "Continue?"
    gui.textSurface(msg0, world.end_font, col, ( world.gamesurf_rect.centerx, world.gamesurf_rect.centery - offset ), world.worldsurf )
    gui.textSurface(msg1, world.scores_font, world.end_text_color, ( world.gamesurf_rect.centerx, world.gamesurf_rect.centery + offset ), world.worldsurf )
    if int((tick - world.gameover_tick_max) / (world.fps * 2))% 3 < 2:
      gui.textSurface(msg2, world.scores_font, world.end_text_color, ( world.gamesurf_rect.centerx, world.gamesurf_rect.centery + (2 * offset) ), world.worldsurf )
      gui.textSurface(msg3, world.scores_font, world.end_text_color, ( world.gamesurf_rect.centerx, world.gamesurf_rect.centery + (3 * offset) ), world.worldsurf )

  world.gameover_anim_tick += world.ticks_per_frame


def draw_AAR_zoids( world ):
  if world.AAR_curr_zoid_hl:
    gui.blocks(world, world.curr_zoid.get_shape(), world.gamesurf, world.gamesurf_rect, world.curr_zoid.col * world.side, ( world.game_ht - world.curr_zoid.row ) * world.side, alpha = world.AAR_dim * 2, gray = world.gray_zoid)
  if world.solved:
    gui.blocks(world, world.curr_zoid.get_shape(rot = world.solved_rot), world.gamesurf, world.gamesurf_rect, world.solved_col * world.side, ( world.game_ht - world.solved_row) * world.side, alpha = 255, gray = world.gray_zoid)


def draw_AAR(world):
  world.worldsurf.fill( world.bg_color )

  world.gamesurf.fill( world.bg_color )

  draw_gridlines(world)

  #world.nextsurf.fill( ( 100, 100, 100 ) )
  world.nextsurf.fill( world.bg_color )
  draw_next_zoid(world)

  if world.keep_zoid:
    world.keptsurf.fill( world.kept_bgc )
    draw_kept_zoid(world)

  if world.show_high_score:
    gui.textSurface("High:", world.scores_font, ( 210, 210, 210 ), world.high_lab_left, world.worldsurf, "midleft" )
    gui.textSurface(str( world.high_score ), world.scores_font, ( 210, 210, 210 ), world.high_left, world.worldsurf, "midright" )

  # gui.textSurface("Game %d" % world.game_number, world.intro_font, ( 196, 196, 196 ), ( world.gamesurf_rect.centerx, world.gamesurf_rect.top / 2 ), world.worldsurf )
  gui.textSurface("Game %d" % world.game_number, world.intro_font, ( 196, 196, 196 ), ( 120, 60 ), world.worldsurf )
  draw_scores(world)

  draw_AAR_zoids(world)

  draw_borders(world)

  gui.board(world, alpha = world.AAR_dim)
  #gui.textSurface("PAUSED", world.pause_font, ( 210, 210, 210 ), world.worldsurf_rect.center, world.worldsurf )


def draw_borders( world ):
  gui.borderOutsideOfRect(world.worldsurf, world.newscoreColor, world.border_thickness, world.gamesurf_rect)
  if world.look_ahead > 0:
    gui.borderOutsideOfRect( world.worldsurf, world.newscoreColor, world.border_thickness, world.nextsurf_rect)
  if world.keep_zoid:
    gui.borderOutsideOfRect( world.worldsurf, world.border_color, world.border_thickness, world.keptsurf_rect)


def draw_gridlines( world ):
  if world.gridlines_x:
    for i in range( 1 , world.game_wd ):
      pygame.draw.line( world.gamesurf, world.gridlines_color, (i * world.side - 1, 0), (i*world.side - 1, world.gamesurf_rect.height) , 2)
  if world.gridlines_y:
    for i in range( 1 , world.game_ht ):
      pygame.draw.line( world.gamesurf, world.gridlines_color, (0, i * world.side - 1), (world.gamesurf_rect.width, i*world.side - 1) , 2)


def draw_scores( world ):
  gui.textSurface("Score:", world.scores_font, ( 210, 210, 210 ), world.score_lab_left, world.worldsurf, "midleft" )
  gui.textSurface("Tetrises:", world.scores_font, ( 210, 210, 210 ), world.tetrises_lab_left, world.worldsurf, "midleft" )
  gui.textSurface("Lines:", world.scores_font, ( 210, 210, 210 ), world.lines_lab_left, world.worldsurf, "midleft" )
  gui.textSurface("Level:", world.scores_font, ( 210, 210, 210 ), world.level_lab_left, world.worldsurf, "midleft" )

  gui.textSurface(str( world.score ), world.scores_font, ( 210, 210, 210 ), world.score_left, world.worldsurf, "midright" )
  gui.textSurface(str( world.tetrises_game ), world.scores_font, ( 210, 210, 210 ), world.tetrises_left, world.worldsurf, "midright" )
  gui.textSurface(str( world.lines_cleared ), world.scores_font, ( 210, 210, 210 ), world.lines_left, world.worldsurf, "midright" )
  gui.textSurface(str( world.level ), world.scores_font, ( 210, 210, 210 ), world.level_left, world.worldsurf, "midright" )

  newscore = world.newscore
  if newscore <= 100:
    newscoreText = "{:0.2f}".format(world.newscore)
    s = int(newscore)
    world.newscoreColor = ( 5 + 5 * min(50, s), 255 - 5 * max(0, s-50), 0)
    lineColor = (255,255,255)
  else:
    newscore = 100
    world.newscoreColor = (255,0,0)
    newscoreText = "100+"
    lineColor = (255,0,0)

  world.newscoreText = newscoreText
  world.metabarSfc.fill( world.bg_color )
  world.metabarSfc.blit( world.scorebar, world.scorebarRect )
  cent = (world.metabarHeight-30) / 100
  spc = world.metabarHeight - (100-newscore)*cent # score percentage
  textTop = spc-4

  pygame.draw.rect( world.metabarSfc, world.bg_color, [(0, 0), (world.metabarWidth, spc)])
  pygame.draw.rect( world.metabarSfc, lineColor, [(0, spc-2), (world.metabarWidth, 2)])

  gui.textSurface(newscoreText, world.instantScoreFont, ( 255, 255, 255 ),
    (int(world.metabarWidth/2), textTop), world.metabarSfc, "midbottom"
  )
  world.worldsurf.blit( world.metabarSfc, world.metabarBox )

  gui.textSurface("Meta: {:0.3f}".format(world.metascore), world.scores_font,
    ( 210, 210, 210 ), world.metaScorePos, world.worldsurf, "midtop" )

  gui.textSurface(world.newscoreText, world.inBoardScoreFont, ( 35, 35, 35 ),
    (world.gamesurf_rect.width//2, 10), world.gamesurf, "midtop"
  )

#draw the current zoid at its current location on the board
def draw_curr_zoid( world ):
  if (not world.visible_zoid) or world.board_mask or world.mask_toggle:
    return

  gui.blocks(world, world.curr_zoid.get_shape(), world.gamesurf, world.gamesurf_rect, world.curr_zoid.col * world.side, ( world.game_ht - world.curr_zoid.row ) * world.side, gray = world.gray_zoid)
  if world.ghost_zoid:
    gui.blocks(world, world.curr_zoid.get_shape(), world.gamesurf, world.gamesurf_rect, world.curr_zoid.col * world.side, ( world.game_ht - world.curr_zoid.to_bottom()) * world.side, alpha = world.ghost_alpha, gray = world.gray_zoid )

  if world.hint_toggle and world.solved:
    if not world.hint_context:
      gui.blocks(world, world.curr_zoid.get_shape(rot = world.solved_rot), world.gamesurf, world.gamesurf_rect, world.solved_col * world.side, ( world.game_ht - world.solved_row) * world.side, alpha = world.ghost_alpha, gray = world.gray_zoid )

  if world.hint_context and world.solved:
    hint_col_agree = abs(world.solved_col - world.curr_zoid.col) <= world.hint_context_col_tol
    hint_agree = world.solved_rot == world.curr_zoid.rot and hint_col_agree
    if hint_agree:
      gui.blocks(world, world.curr_zoid.get_shape(rot = world.solved_rot), world.gamesurf, world.gamesurf_rect, world.solved_col * world.side, ( world.game_ht - world.solved_row) * world.side, alpha = world.ghost_alpha, gray = world.gray_zoid )


#draw the next zoid inside the next box
def draw_next_zoid( world ):
  if world.look_ahead > 0:
    if not world.next_mask or world.mask_toggle:
      next_rep = world.next_zoid.get_next_rep()
      vert = (world.next_size - float(len(next_rep))) / 2.0
      horiz = (world.next_size - float(len(next_rep[0]))) / 2.0
      gui.blocks(world, next_rep, world.nextsurf, world.nextsurf_rect, int( world.side * (horiz + .25) ), int( world.side * (vert + .25) ), alpha = world.next_alpha, gray = world.gray_next)
    else:
      world.nextsurf.fill( world.mask_color )
      world.worldsurf.blit( world.nextsurf , world.nextsurf_rect )


def draw_kept_zoid( world ):
  if world.kept_zoid != None:
    kept_rep = world.kept_zoid.get_next_rep()
    vert = (world.next_size - float(len(kept_rep))) / 2.0
    horiz = (world.next_size - float(len(kept_rep[0]))) / 2.0
    gui.blocks(world,  kept_rep, world.keptsurf, world.keptsurf_rect, int( world.side * (horiz + .25) ), int( world.side * (vert + .25) ), gray = world.gray_kept)
  else:
    gui.blocks(world, Zoid.next_reps['none'], world.keptsurf, world.keptsurf_rect, 0, 0, gray = world.gray_kept)
