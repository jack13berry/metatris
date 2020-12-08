import pygame, platform, numpy
# import time

import states, gui
import introscreen, playscreen, configscreen
from zoid import Zoid


def setupOSWindow(world, w=0, h=0):
  if world.fullscreen:
    world.screen = pygame.display.set_mode( ( 0, 0 ), pygame.FULLSCREEN )
  else:
    if w == 0 and h == 0:
      w = 800
      h = 600
    world.screen = pygame.display.set_mode( (w, h), pygame.RESIZABLE )
    pygame.display.set_caption("Metatris")

  world.worldsurf = world.screen.copy()
  world.worldsurf_rect = world.worldsurf.get_rect()

  world.side = int( world.worldsurf_rect.height / (world.game_ht + 4.0) )
  world.border = int( world.side / 6.0 )
  world.border_thickness = int(round(world.side/4))


def setupColors(world):
  world.NES_colors = Zoid.NES_colors
  world.STANDARD_colors = Zoid.STANDARD_colors

  world.block_color_type = Zoid.all_color_types
  world.end_text_color = ( 210, 210, 210 )
  world.message_box_color = ( 20, 20, 20 )
  world.mask_color = ( 100, 100, 100 )
  world.ghost_alpha = 100

  world.next_alpha = 255
  if world.next_dim:
    world.next_alpha = world.next_dim_alpha


def setupLayout(world):
  world.gamesurf = pygame.Surface( ( world.game_wd * world.side, world.game_ht * world.side ) )
  world.gamesurf_rect = world.gamesurf.get_rect()
  world.gamesurf_rect.center = world.worldsurf_rect.center

  world.gamesurf_msg_rect = world.gamesurf_rect.copy()
  world.gamesurf_msg_rect.height = world.gamesurf_rect.height / 2
  world.gamesurf_msg_rect.center = world.gamesurf_rect.center

  if world.score_align == "right":
    world.score_offset = world.gamesurf_rect.right + 3 * world.side
  elif world.score_align == "left":
    world.score_offset = 2 * world.side

  world.next_offset = world.gamesurf_rect.right + 3 * world.side

  world.next_size = 5 if world.pentix_zoids else 4

  rightColumnWidth = int( (world.next_size + .5) * world.side )
  nextBoxHeight = int( (world.next_size + .5) * world.side )

  world.nextsurf = pygame.Surface((rightColumnWidth, nextBoxHeight))
  world.nextsurf_rect = world.nextsurf.get_rect()
  world.nextsurf_rect.top = world.gamesurf_rect.top
  world.nextsurf_rect.left = world.next_offset

  r = world.nextsurf_rect
  world.metaScorePos = (r.left+(rightColumnWidth/2), r.top + r.height + 15)

  metabarHeight = world.gamesurf_rect.height - r.height - 3 * world.side
  metaw = rightColumnWidth+world.border_thickness*2
  metah = metabarHeight + world.border_thickness

  world.metabarSfc = pygame.Surface( (metaw, metah) )
  world.metabarBox = world.metabarSfc.get_rect()
  world.metabarBox.top = r.top + r.height + 3 * world.side
  world.metabarBox.left = r.left - world.border_thickness

  world.scorebar = pygame.transform.scale(world.scorebarsrc, (metaw-20, metah-30))
  world.scorebarRect = world.scorebar.get_rect()
  world.scorebarRect.top += 30
  world.scorebarRect.left += 10
  world.metabarWidth = metaw
  world.metabarHeight = metah

  if world.far_next:
    r.left = world.worldsurf_rect.width - world.nextsurf_border_rect.width - world.border_thickness / 2
    world.nextsurf_border_rect.left = world.worldsurf_rect.width - world.nextsurf_border_rect.width - world.border_thickness

  if world.keep_zoid:
    world.keptsurf = world.nextsurf.copy()
    world.keptsurf_rect = world.keptsurf.get_rect()
    world.keptsurf_rect.top = world.gamesurf_rect.top
    world.keptsurf_rect.left = world.gamesurf_rect.left - world.keptsurf_rect.width - (4 * world.border_thickness)

  # Text labels
  midtopy = world.worldsurf_rect.height / 2
  lineheight = 50
  world.high_lab_left = ( world.score_offset, midtopy - 2*lineheight )
  world.score_lab_left = ( world.score_offset, midtopy - lineheight)
  world.tetrises_lab_left = ( world.score_offset, midtopy )
  world.lines_lab_left = ( world.score_offset, midtopy + lineheight )
  world.level_lab_left = ( world.score_offset, midtopy + 2*lineheight )
  world.newscore_lab_left = ( world.score_offset, midtopy + 3*lineheight )
  world.metascore_lab_left = ( world.score_offset, midtopy + 4*lineheight )

  world.label_offset = int(280.0 / 1440.0 * world.worldsurf_rect.width)
  world.high_left = ( world.score_offset + world.label_offset, world.high_lab_left[1] )
  world.score_left = ( world.score_offset + world.label_offset, world.score_lab_left[1] )
  world.tetrises_left = ( world.score_offset + world.label_offset, world.tetrises_lab_left[1] )
  world.lines_left = ( world.score_offset + world.label_offset, world.lines_lab_left[1] )
  world.level_left = ( world.score_offset + world.label_offset, world.level_lab_left[1] )
  world.newscore_left = ( world.score_offset + world.label_offset, world.newscore_lab_left[1] )
  world.metascore_left = ( world.score_offset + world.label_offset, world.metascore_lab_left[1] )

  # Animation
  world.gameover_anim_tick = 0
  world.gameover_tick_max = world.game_ht * 2
  world.gameover_board = [[0] * world.game_wd] * world.game_ht

  world.tetris_flash_tick = 0 #currently dependent on framerate
  world.tetris_flash_colors = [world.bg_color, ( 100, 100, 100 )]

  world.blocks = []
  #generate blocks for all levels
  for l in range( 0, 10 ):
    blocks = []
    #and all block-types...
    if world.color_mode == "STANDARD":
      for b in range( 0, len(world.STANDARD_colors)):
        blocks.append( generate_block( world, world.side, l, b ) )
    else:
      for b in range( 0, 3 ):
        blocks.append( generate_block( world, world.side, l, b ) )
    world.blocks.append( blocks )

  world.gray_block = generate_block( world, world.side, 0, 0 )


#pre-renders reusable block surfaces
def generate_block( world, size, lvl, type ):
  if world.color_mode == "STANDARD":
    bg = pygame.Surface( ( size, size ) )
    c = world.STANDARD_colors[type]
    lvl_offset = lvl * 15
    bg_off = -40 + lvl_offset
    fg_off = 40 - lvl_offset
    bgc = tuple([min(max(a + b,0),255) for a, b in zip(c, [bg_off]*3)])
    fgc = tuple([min(max(a + b,0),255) for a, b in zip(c, [fg_off]*3)])
    bg.fill( bgc )
    fg = pygame.Surface( ( size - world.border * 2, size - world.border * 2 ) )
    fg.fill( fgc )
    fgr = fg.get_rect()
    fgr.topleft = ( world.border, world.border )
    bg.blit( fg, fgr )
  else:
    if type == 0:
      bgc = world.NES_colors[lvl][0]
      fgc = ( 255, 255, 255 )
    elif type == 1:
      #if world.color_mode == "other":
        #bgc = world.NES_colors[lvl][0]
        #fgc = world.NES_colors[lvl][0]
      if world.color_mode == "REMIX":
        bgc = world.NES_colors[lvl][1]
        fgc = world.NES_colors[lvl][0]
    elif type == 2:
      #if world.color_mode == "other":
        #bgc = world.NES_colors[lvl][1]
        #fgc = world.NES_colors[lvl][1]
      if world.color_mode == "REMIX":
        bgc = world.NES_colors[lvl][0]
        fgc = world.NES_colors[lvl][1]
    bg = pygame.Surface( ( size, size ) )
    bg.fill( bgc )
    fg = pygame.Surface( ( size - world.border * 2, size - world.border * 2 ) )
    fg.fill( fgc )
    fgr = fg.get_rect()
    fgr.topleft = ( world.border, world.border )
    bg.blit( fg, fgr )
    """
    if world.color_mode == "other":
      sheen = world.border - 1
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
    if world.color_mode == "REMIX":
      sheen = world.border
      s = pygame.Surface( ( sheen,sheen ) )
      s.fill( ( 255, 255, 255 ) )
      sr = s.get_rect()
      sr.topleft = fgr.topleft
      bg.blit( s, sr.topleft )
  pygame.draw.rect( bg, world.bg_color, bg.get_rect(), 1 )
  return bg


#main draw updater
def drawTheWorld( world ):
  if world.state == states.Intro:
    introscreen.draw(world)
  elif world.state == states.Play:
    world.bg_color = world.tetris_flash_colors[world.tetris_flash_tick % 2]
    if world.tetris_flash_tick > 0:
      world.tetris_flash_tick -= 1
    playscreen.draw(world)
  elif world.state == states.Pause:
    playscreen.drawPaused(world)
  elif world.state == states.Gameover:
    playscreen.drawGameOver(world)
  elif world.state == states.Aar:
    playscreen.draw_AAR(world)
  elif world.state >= states.Config:
    configscreen.draw(world)

  world.screen.blit( world.worldsurf, world.worldsurf_rect )
  # t1 = time.perf_counter()*1000
  pygame.display.flip()
  # t2 = time.perf_counter()*1000
  # if t2-t1 > 1:
  #   print("DRAW TIME:", t2-t1, t2-world.moment*1000, pygame.time.Clock().get_fps())
