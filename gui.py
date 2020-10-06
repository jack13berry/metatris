import pygame

#draw text to the screen
def textSurface( self, text, font, color, loc, surf, justify = "center" ):
  t = font.render( text, True, color )
  tr = t.get_rect()
  setattr( tr, justify, loc )
  surf.blit( t, tr )
  return tr
###

#draw any text box
def textSurfaceBox( self ):
  pygame.draw.rect( self.worldsurf, self.message_box_color, self.gamesurf_msg_rect, 0 )

#draw a single square on the board
def square( self, surface, left, top, color_id , alpha = 255, gray = False):
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
def blocks( self, obj, surf, rect, x = 0, y = 0, resetX = False, alpha = 255, gray = False):
  ix = x
  iy = y
  for i in obj:
    for j in i:
      if j != 0:
        square(self, surf, ix, iy, color_id = j, alpha = alpha, gray = gray )
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


#draw the underlying game board the current zoid interacts with
def board( self, alpha = 255):
  echo = (self.board_echo_placed and self.are_counter > 0) or (self.board_echo_lc and self.lc_counter > 0)
  if self.visible_board or echo:
    if not self.board_mask or not self.mask_toggle:
      if self.dimtris and not echo:
        alpha = self.dimtris_alphas[min(self.level, len(self.dimtris_alphas)-1)]
      blocks(self, self.board, self.gamesurf, self.gamesurf_rect, resetX = True, alpha = alpha, gray = self.gray_board)
    else:
      self.gamesurf.fill( self.mask_color )
      self.worldsurf.blit( self.gamesurf , self.gamesurf_rect)
