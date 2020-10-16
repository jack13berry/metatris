import pygame, math


def borderOutside(surface, color, weight, x, y, w, h):
  pygame.draw.rect( surface, color, [(x-weight, y-weight), (w+weight, weight)])
  pygame.draw.rect( surface, color, [(x+w, y-weight), (weight, h+weight)])
  pygame.draw.rect( surface, color, [(x, y+h), (w+weight, weight)])
  pygame.draw.rect( surface, color, [(x-weight, y), (weight, h+weight)])


def pillOutside(surface, color, weight, x, y, w, h):
  pygame.draw.rect( surface, color, [(x-weight, y-weight), (w+weight, weight)])
  pygame.draw.rect( surface, color, [(x+w, y-weight), (weight, h+weight)])
  pygame.draw.rect( surface, color, [(x, y+h), (w+weight, weight)])
  pygame.draw.rect( surface, color, [(x-weight, y), (weight, h+weight)])
  # pygame.draw.arc(surface, color, [(x-weight,y),(h,h+weight)], math.pi/2, 1.5*math.pi, weight)


def borderOutsideOfRect(surface, color, weight, rect):
  borderOutside(surface, color, weight, rect.left, rect.top, rect.width, rect.height)


def textSurface( text, font, color, loc, surf, justify = "center" ):
  t = font.render( text, True, color )
  tr = t.get_rect()
  setattr( tr, justify, loc )
  surf.blit( t, tr )
  return tr


def textSurfaceBox( self ):
  pygame.draw.rect( self.worldsurf, self.message_box_color, self.gamesurf_msg_rect, 0 )


def button(world, txt, x, y, w, h):
  pillOutside(world.worldsurf, (120,200,50), 2, x,y,w,h)
  textSurface(txt, world.scores_font, (120,200,40), (x+w//2, y+h//2),
    world.worldsurf, "center"
  )


def square( self, surface, left, top, color_id , alpha = 255, gray = False):
  lvl = self.level % len( self.NES_colors )
  if self.color_mode == "REMIX":
    block = self.blocks[lvl][self.block_color_type[color_id - 1]]
  else:
    block = self.blocks[lvl][color_id] if not gray else self.gray_block

  block.set_alpha(alpha)
  surface.blit( block, ( left, top ) )


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
  echo = (
    (self.board_echo_placed and self.are_counter > 0) or
    (self.board_echo_lc and self.lc_counter > 0)
  )

  if self.visible_board or echo:
    if not self.board_mask or not self.mask_toggle:
      if self.dimtris and not echo:
        alpha = self.dimtris_alphas[min(self.level, len(self.dimtris_alphas)-1)]
      blocks(self, self.board, self.gamesurf, self.gamesurf_rect, resetX = True, alpha = alpha, gray = self.gray_board)
    else:
      self.gamesurf.fill( self.mask_color )
      self.worldsurf.blit( self.gamesurf , self.gamesurf_rect)
