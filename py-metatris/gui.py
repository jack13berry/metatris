import pygame, math


def borderOutside(surface, color, weight, x, y, w, h):
  pygame.draw.rect( surface, color, [(x-weight, y-weight), (w+weight, weight)])
  pygame.draw.rect( surface, color, [(x+w, y-weight), (weight, h+weight)])
  pygame.draw.rect( surface, color, [(x, y+h), (w+weight, weight)])
  pygame.draw.rect( surface, color, [(x-weight, y), (weight, h+weight)])


def pillOutside(surface, color, weight, x, y, w, h):
  ax = x-weight
  ay = y-weight
  r = h+2*weight
  lx = ax+(h+1)/2-weight
  lw = w+2*weight-h
  l2y = y+h+1-weight
  a2x = ax+lw-2*weight

  pygame.draw.rect( surface, color, [(lx, ay), (lw, weight)])
  pygame.draw.rect( surface, color, [(x+w, y-weight), (weight, h+weight)])
  pygame.draw.rect( surface, color, [(lx, l2y), (lw, weight)])
  pygame.draw.rect( surface, color, [(x-weight, y), (weight, h+weight)])
  pygame.draw.arc(surface, color, [(ax,ay),(r,r)], 0.5*math.pi, 1.5*math.pi, weight)
  pygame.draw.arc(surface, color, [(a2x,ay),(r,r)], 1.5*math.pi, 0.5*math.pi, weight)


def borderOutsideOfRect(surface, color, weight, rect):
  borderOutside(surface, color, weight, rect.left, rect.top, rect.width, rect.height)


def textSurface( text, font, color, loc, surf, justify = "center", upsideDown=False):
  t = font.render( text, True, color )
  tr = t.get_rect()
  if upsideDown:
    t = pygame.transform.flip(t, False, True)

  setattr( tr, justify, loc )
  surf.blit( t, tr )
  return tr


def textSurfaceBox( self ):
  return pygame.draw.rect(
    self.worldsurf, self.message_box_color, self.gamesurf_msg_rect, 0 )


def textInput(world, txt, x, y, w, h,
  focused=False, withTicks=True,
  clr1=(120,200,50), clr2 = (120,200,40)):

  srfc = world.worldsurf
  borderOutside(srfc, clr1, 2, x, y, w, h)

  if focused:
    pygame.draw.rect( srfc, clr1, [(x, y), (w, h)]) # button fill
  textSurface(txt, world.scores_font, (255,255,255), (x + w // 2, y + h // 2), srfc, "center")


def button(world, txt, x, y, w, h,
  focused=False, withTicks=True,
  clr1=(120,200,50), clr2 = (120,200,40)):

  srfc = world.worldsurf
  borderOutside(srfc, clr1, 2, x, y, w, h)

  if focused:
    pygame.draw.rect( srfc, clr1, [(x, y), (w, h)]) # button fill

    clr2 = world.bg_color # text and arrow color

    # arrows
    tx, ty, t2x = x-2, y+(h-20)/2, x+w+2
    if withTicks:
      pygame.draw.polygon(srfc, clr2, [(tx, ty), (tx+14, ty+10), (tx,ty+20)])
      pygame.draw.polygon(srfc, clr2, [(t2x, ty), (t2x-14, ty+10), (t2x,ty+20)])

  textSurface(txt, world.scores_font, clr2, (x+w//2, y+h//2), srfc, "center")


def verticalTab(world, txt, x, y, w, h, focused=False,
    clrFocused = (120,200,50),
    clrBlurred = (60,140,10),
    clrFocusedText = None,
    clrBlurredText = (60,140,10)
):

  if clrFocusedText == None:
    clrFocusedText = world.bg_color
  if clrBlurredText == None:
    clrBlurredText = clrBlurred

  srfc = world.worldsurf
  marginBottom = 1
  if focused:
    h += 4
    w += 10
    y -= 2
    x -= 6
    marginBottom = -3
    pygame.draw.rect( srfc, clrFocused, [(x, y), (w, h)]) # button fill

    clrTxt = clrFocusedText # text and arrow color

    # arrows
    ty = y+(h-20)/2
    pygame.draw.polygon(srfc, clrBlurred,
      [(x-2, ty), (x+14, ty+10), (x-2,ty+20)])

  else:
    # pygame.draw.rect( srfc, clr1, [(x, y), (w, 2)])
    # pygame.draw.rect( srfc, clrBlurred, [(x+w, y), (1, h)])
    pygame.draw.rect( srfc, clrBlurred, [(x, y+h), (w+1, 1)])
    clrTxt = clrBlurredText

  textSurface(txt, world.scores_font, clrTxt, (x+w//2, y+h//2), srfc, "center")

  return y+h+marginBottom


def simpleText(world, text, x=-1, y=-1, color=(120,200,50), srf=None, alignment="center"):
  if srf == None:
    srf = world.worldsurf

  return textSurface(text, world.scores_font, color, (x, y), srf, alignment)


def infoText(world, text, x=-1, y=-1, color=(120,200,50), srf = None):
  if x == -1 or y == -1:
    rect = world.worldsurf_rect
    if x == -1:
      x = int(rect.width/4)*3 + 15
    if y == -1:
      y = int(rect.height/2)

  return simpleText(world, text, x, y, color, srf, "center")


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

      blocks(
        self, self.board, self.gamesurf, self.gamesurf_rect,
        resetX = True, alpha = alpha, gray = self.gray_board
      )

    else:
      self.gamesurf.fill( self.mask_color )
      self.worldsurf.blit( self.gamesurf , self.gamesurf_rect)
