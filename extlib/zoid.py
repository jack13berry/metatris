"""
John K. Lindstedt
"""

import math

class Zoid( object ):
    next_reps = {
        'none' : [[]],
        'I' : [[1, 1, 1, 1]],
        'O' : [[2, 2], [2, 2]],
        'T' : [[3, 3, 3], [0, 3, 0]],
        'S' : [[0, 4, 4], [4, 4, 0]],
        'Z' : [[5, 5, 0], [0, 5, 5]],
        'J' : [[6, 6, 6], [0, 0, 6]],
        'L' : [[7, 7, 7], [7, 0, 0]],
        'BIG_T': [[8,8,8],[0,8,0],[0,8,0]],
        'BIG_I':  [[9,9,9,9,9]],
        'BIG_J':  [[10,10,10,10],[0,0,0,10]],
        'BIG_L':  [[11,11,11,11],[11,0,0,0]],
        'BIG_S':  [[0,12,12],[0,12,0],[12,12,0]],
        'BIG_Z':  [[13,13,0],[0,13,0],[0,13,13]],
        'PLUS':   [[0,14,0],[14,14,14],[0,14,0]],
        'U':      [[15,15,15],[15,0,15]],
        'BIG_V':  [[16,16,16],[16,0,0],[16,0,0]],
        'D':      [[17,17,17,0],[0,17,17,0]],
        'B':      [[0,18,18,18],[0,18,18,0]],
        'W':      [[0,19,19],[19,19,0],[19,0,0]],
        'J_DOT':  [[0,20,20],[20,20,0],[0,20,0]],
        'L_DOT':  [[21,21,0],[0,21,21],[0,21,0]],
        'J_STILT':[[22,22,22,22],[0,0,22,0]],
        'L_STILT':[[23,23,23,23],[0,23,0,0]],
        'LONG_S':  [[0,24,24,24],[24,24,0,0]],
        'LONG_Z':  [[25,25,25,0],[0,0,25,25]],
        'MINI_I': [[26,26,26]],
        'V':      [[27,27],[27,0]],
        'TWO':    [[28,28]],
        'ONE':    [[29]]
        }
    
    #piece representation in game
    #empty rows present to aid in rotation.
    shapes = {
        'I' : [[[0, 0, 0, 0], [0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0]],
               [[0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0], [0, 0, 1, 0]]],
        'O' : [[[0, 0, 0, 0], [0, 2, 2, 0], [0, 2, 2, 0], [0, 0, 0, 0]]],
        'T' : [[[0, 0, 0], [3, 3, 3], [0, 3, 0]],
               [[0, 3, 0], [3, 3, 0], [0, 3, 0]],
               [[0, 3, 0], [3, 3, 3], [0, 0, 0]],
               [[0, 3, 0], [0, 3, 3], [0, 3, 0]]],
        'S' : [[[0, 0, 0], [0, 4, 4], [4, 4, 0]],
               [[0, 4, 0], [0, 4, 4], [0, 0, 4]]],
        'Z' : [[[0, 0, 0], [5, 5, 0], [0, 5, 5]],
               [[0, 0, 5], [0, 5, 5], [0, 5, 0]]],
        'J' : [[[0, 0, 0], [6, 6, 6], [0, 0, 6]],
               [[0, 6, 0], [0, 6, 0], [6, 6, 0]],
               [[6, 0, 0], [6, 6, 6], [0, 0, 0]],
               [[0, 6, 6], [0, 6, 0], [0, 6, 0]]],
        'L' : [[[0, 0, 0], [7, 7, 7], [7, 0, 0]],
               [[7, 7, 0], [0, 7, 0], [0, 7, 0]],
               [[0, 0, 7], [7, 7, 7], [0, 0, 0]],
               [[0, 7, 0], [0, 7, 0], [0, 7, 7]]],
               
        #Pentix pieces
        'BIG_T':  [[[8,8,8], [0,8,0],[0,8,0]],
                   [[0,0,8], [8,8,8],[0,0,8]],
                   [[0,8,0], [0,8,0],[8,8,8]],
                   [[8,0,0], [8,8,8],[8,0,0]]],
        'BIG_I':  [[[0,0,0,0,0],[0,0,0,0,0],[9,9,9,9,9],[0,0,0,0,0],[0,0,0,0,0]],
                   [[0,0,9,0,0],[0,0,9,0,0],[0,0,9,0,0],[0,0,9,0,0],[0,0,9,0,0]]],
        'BIG_J':  [[[0,0,0,0],[10,10,10,10],[0,0,0,10],[0,0,0,0]],
                   [[0,0,10,0],[0,0,10,0],[0,0,10,0],[0,10,10,0]],
                   [[0,0,0,0],[10,0,0,0],[10,10,10,10],[0,0,0,0]],
                   [[0,10,10,0],[0,10,0,0],[0,10,0,0],[0,10,0,0]]],
        'BIG_L':  [[[0,0,0,0],[11,11,11,11],[11,0,0,0],[0,0,0,0]],
                   [[0,11,11,0],[0,0,11,0],[0,0,11,0],[0,0,11,0]],
                   [[0,0,0,0],[0,0,0,11],[11,11,11,11],[0,0,0,0]],
                   [[0,11,0,0],[0,11,0,0],[0,11,0,0],[0,11,11,0]]],
                   
        'BIG_S':  [[[0,12,12],[0,12,0],[12,12,0]],
                   [[12,0,0],[12,12,12],[0,0,12]]],
        'BIG_Z':  [[[13,13,0],[0,13,0],[0,13,13]],
                   [[0,0,13],[13,13,13],[13,0,0]]],
        'PLUS':   [[[0,14,0],[14,14,14],[0,14,0]]],
        'U':      [[[0,0,0],[15,15,15],[15,0,15]],
                   [[15,15,0],[0,15,0],[15,15,0]],
                   [[15,0,15],[15,15,15],[0,0,0]],
                   [[0,15,15],[0,15,0],[0,15,15]]],
        'BIG_V':  [[[16,16,16],[16,0,0],[16,0,0]],
                   [[16,16,16],[0,0,16],[0,0,16]],
                   [[0,0,16],[0,0,16],[16,16,16]],
                   [[16,0,0],[16,0,0],[16,16,16]]],
        'D':      [[[0,0,0,0],[17,17,17,0],[0,17,17,0],[0,0,0,0]],
                   [[0,0,17,0],[0,17,17,0],[0,17,17,0],[0,0,0,0]],
                   [[0,0,0,0],[0,17,17,0],[0,17,17,17],[0,0,0,0]],
                   [[0,0,0,0],[0,17,17,0],[0,17,17,0],[0,17,0,0]]],
        'B':      [[[0,0,0,0],[0,18,18,18],[0,18,18,0],[0,0,0,0]],
                   [[0,0,0,0],[0,18,18,0],[0,18,18,0],[0,0,18,0]],
                   [[0,0,0,0],[0,18,18,0],[18,18,18,0],[0,0,0,0]],
                   [[0,18,0,0],[0,18,18,0],[0,18,18,0],[0,0,0,0]]],
        'W':      [[[0,19,19],[19,19,0],[19,0,0]],
                   [[19,19,0],[0,19,19],[0,0,19]],
                   [[0,0,19],[0,19,19],[19,19,0]],
                   [[19,0,0],[19,19,0],[0,19,19]]],
        'J_DOT':  [[[0,20,20],[20,20,0],[0,20,0]],
                   [[0,20,0],[20,20,20],[0,0,20]],
                   [[0,20,0],[0,20,20],[20,20,0]],
                   [[20,0,0],[20,20,20],[0,20,0]]],
        'L_DOT':  [[[21,21,0],[0,21,21],[0,21,0]],
                   [[0,0,21],[21,21,21],[0,21,0]],
                   [[0,21,0],[21,21,0],[0,21,21]],
                   [[0,21,0],[21,21,21],[21,0,0]]],
        'J_STILT':[[[0,0,0,0],[22,22,22,22],[0,0,22,0],[0,0,0,0]],
                   [[0,0,22,0],[0,0,22,0],[0,22,22,0],[0,0,22,0]],
                   [[0,0,0,0],[0,22,0,0],[22,22,22,22],[0,0,0,0]],
                   [[0,22,0,0],[0,22,22,0],[0,22,0,0],[0,22,0,0]]],
        'L_STILT':[[[0,0,0,0],[23,23,23,23],[0,23,0,0],[0,0,0,0]],
                   [[0,0,23,0],[0,23,23,0],[0,0,23,0],[0,0,23,0]],
                   [[0,0,0,0],[0,0,23,0],[23,23,23,23],[0,0,0,0]],
                   [[0,23,0,0],[0,23,0,0],[0,23,23,0],[0,23,0,0]]],
        'LONG_S':  [[[0,0,0,0],[0,24,24,24],[24,24,0,0],[0,0,0,0]],
                   [[0,24,0,0],[0,24,24,0],[0,0,24,0],[0,0,24,0]],
                   [[0,0,0,0],[0,0,24,24],[24,24,24,0],[0,0,0,0]],
                   [[0,24,0,0],[0,24,0,0],[0,24,24,0],[0,0,24,0]]],
        'LONG_Z':  [[[0,0,0,0],[25,25,25,0],[0,0,25,25],[0,0,0,0]],
                   [[0,0,25,0],[0,0,25,0],[0,25,25,0],[0,25,0,0]],
                   [[0,0,0,0],[25,25,0,0],[0,25,25,25],[0,0,0,0]],
                   [[0,0,25,0],[0,25,25,0],[0,25,0,0],[0,25,0,0]]],
        
        #Pentix FULL pieces
        'MINI_I': [[[0,0,0],[26,26,26],[0,0,0]],
                   [[0,26,0],[0,26,0],[0,26,0]]],
        'V':      [[[27,27],[27,0]],
                   [[27,27],[0,27]],
                   [[0,27],[27,27]],
                   [[27,0],[27,27]]],
        'TWO':    [[[28,28],[0,0]],
                   [[28,0],[28,0]]],
        'ONE':    [[[29]]]
        }
    
    
    set_tetris = ["I", "O", "T", "S", "Z", "J", "L"]
    set_pentix = ["BIG_T","BIG_I","BIG_J","BIG_L","BIG_S","BIG_Z",
                  "PLUS","U","BIG_V","D","B","W",
                  "J_DOT","L_DOT","J_STILT","L_STILT","LONG_S","LONG_Z"]
    set_tiny = ["MINI_I","V","TWO","ONE"]
    
    #NES color types
    tetris_color_types = [0, 0, 0, 2, 1, 2, 1]
    pentix_color_types =  [0, 0, 2, 1, 2, 1, 
                         0, 0, 0, 2, 1, 0, 
                         2, 1, 2, 1, 2, 1]
    tiny_color_types = [0, 0, 0, 0]
    
    all_color_types = tetris_color_types + pentix_color_types + tiny_color_types
        
    NES_colors = [
            [( 74, 0, 255 ), ( 0, 165, 255 )], #L0
            [( 0, 148, 0 ), ( 148, 214, 0 )], #L1
            [( 173, 0, 189 ), ( 230, 99, 255 )], #L2
            [( 74, 0, 255 ), ( 0, 230, 0 )], #L3
            [( 189, 0, 82 ), ( 0, 222, 132 )], #L4
            [( 0, 222, 132 ), ( 132, 132, 255 )], #L5
            [( 189, 66, 0 ), ( 107, 107, 107 )], #L6
            [( 123, 0, 255 ), ( 123, 0, 0 )], #L7
            [( 74, 0, 255 ), ( 189, 66, 0 )], #L8
            [( 189, 66, 0 ), ( 239, 166, 0 )], #L9
            ]
    
    #IOTSZJL
    STANDARD_colors = [
            (200,200,200),
            (49, 198, 239),
            (247, 211, 48),
            (173, 77, 156),
            (41, 253, 46),
            (252, 13, 27),
            (11, 36, 251),
            (239, 121, 33)
            ]
    
    #for starting position and location logging
            #['Type'][rotation][row,col]
    offset = {'I':[[2,0],[0,2]], 
              'O':[[1,1]], 
              'T':[[1,0],[0,0],[0,0],[0,1]], 
              'S':[[1,0],[0,1]], 
              'Z':[[1,0],[0,1]], 
              'J':[[1,0],[0,0],[0,0],[0,1]], 
              'L':[[1,0],[0,0],[0,0],[0,1]], 
              'BIG_T':[[0,0],[0,0],[0,0],[0,0]], 
              'BIG_I':[[2,0],[0,2]],
              
              'BIG_J':[[1,0],[0,1],[1,0],[0,1]], 
              'BIG_L':[[1,0],[0,1],[1,0],[0,1]], 
              'BIG_S':[[0,0],[0,0]], 
              'BIG_Z':[[0,0],[0,0]], 
              'PLUS':[[0,0]], 
              'U': [[1,0],[0,0],[0,0],[0,1]], 
              'BIG_V': [[0,0],[0,0],[0,0],[0,0]], 
              'D': [[1,0],[1,0],[1,1],[1,1]], 
              'B': [[1,1],[1,1],[1,0],[0,1]], 
              'W': [[0,0],[0,0],[0,0],[0,0]], 
              'J_DOT': [[0,0],[0,0],[0,0],[0,0]], 
              'L_DOT': [[0,0],[0,0],[0,0],[0,0]], 
              'J_STILT': [[1,0],[0,1],[1,0],[0,1]], 
              'L_STILT': [[1,0],[0,1],[1,0],[0,1]], 
              'LONG_S': [[1,0],[0,1],[1,0],[0,1]], 
              'LONG_Z': [[1,0],[0,1],[1,0],[0,1]], 
              'MINI_I': [[1,0],[0,1]], 
              'V': [[0,0],[0,0],[0,0],[0,0]], 
              'TWO': [[0,0],[0,0]], 
              'ONE': [[0,0]]
              }

    def __init__( self, type, world ):
        self.world = world
        self.type = type
        self.init_pos()
        self.shape = Zoid.shapes[type]
        self.rots = len( self.shape )
        self.floor = 0
        self.floor_bonus = 0
        self.refresh_floor()
        ##account for proper initial placement
        #...#
    
    ###
    
    def init_pos( self ):
        self.col = int(self.world.game_wd / 2) - 2 #normally column 3
        self.row = Zoid.offset[self.type][0][0] + self.world.game_ht 
        self.rot = 0

    def get_shape( self, rot = None ):
        if rot == None:
            rot = self.rot
        return self.shape[rot]
    ###
    
    def get_row( self ):
        return self.row - Zoid.offset[self.type][self.rot][0]
    
    def get_col( self ):
        return self.col + Zoid.offset[self.type][self.rot][1]
    
    def get_pos( self ):
        return[self.get_col(), self.get_row()]
            
    def get_next_rep( self ):
        return Zoid.next_reps[self.type]
    
    #remember: + is CLOCKWISE, - is COUNTERCLOCKWISE
    def rotate( self, dir ):
        if dir == 1:
            #self.world.add_latency("SRR")
            self.world.rots += 1
        elif dir == -1:
            #self.world.add_latency("SRL")
            self.world.rots += 1
        self.world.log_game_event( "ZOID", "ROTATE", dir )
        new_rot = ( self.rot + dir ) % self.rots
        if not self.collide( self.col, self.row, new_rot, self.world.board ):
            self.rot = new_rot
            self.world.sounds['rotate'].play()
        
        else:
            self.world.log_game_event( "ZOID", data1 = "ROTATE", data2 = "FAILURE")
            if self.world.wall_kicking:
                if not self.collide( self.col - 1, self.row, new_rot, self.world.board ):
                    self.rot = new_rot
                    self.col = self.col - 1
                    self.world.sounds['rotate'].play()
                elif not self.collide( self.col + 1, self.row, new_rot, self.world.board ):
                    self.rot = new_rot
                    self.col = self.col + 1
                    self.world.sounds['rotate'].play()
                elif self.type == "I" and not self.collide( self.col + 2, self.row, new_rot, self.world.board ):
                    self.rot = new_rot
                    self.col = self.col + 2
                    self.world.sounds['rotate'].play()
        self.refresh_floor()
        
    ###

    def translate( self, dir ):
        self.world.log_game_event( "ZOID", "TRANSLATE", dir )
        new_col = self.col + dir
        if not self.collide( new_col, self.row, self.rot, self.world.board ):
            self.col = new_col
            self.world.sounds['trans'].play()
        else:
            self.world.log_game_event( "ZOID", data1 = "TRANSLATE", data2 = "FAILURE")
        self.refresh_floor()
    ###

    def down( self , user_down ):
        #log event
        if user_down == 0:
            self.world.log_game_event( "ZOID", "DOWN" )
            self.world.add_latency("SD")
            self.world.s_drops += 1
        else:
            self.world.log_game_event( "ZOID", "U-DOWN")
            self.world.add_latency("UD")
            self.world.u_drops += 1
        
        #If no collision
        new_row = self.row - 1
        if not self.collide( self.col, new_row, self.rot, self.world.board ):
            self.row = new_row
            
            #score bonus for user-downs
            if user_down == 1 and self.world.drop_bonus:
                self.world.drop_score += 1
        
        #otherwise
        elif self.world.gravity:
            self.world.end_trial()
            
        #player-downs award 1 point per down
    ###
    
    def to_bottom( self, move = False ):
        if move:
            self.row = self.floor
            self.world.drop_score += self.floor_bonus
        return self.floor
    
    #made this so it only calculates when needed, as opposed to every drawing frame!
    def refresh_floor( self ): 
        if self.world.zoid_slam or self.world.ghost_zoid:
            self.floor = self.row
            self.floor_bonus = 0
            for i in range( 0 , self.world.game_ht):
                #if no collision, keep moving
                if not self.collide( self.col, self.floor - 1, self.rot, self.world.board ):
                    self.floor -= 1
                    if self.world.drop_bonus:
                        self.floor_bonus += 1
        
    
    def place( self ):
        new_row = self.row - 1
        if self.collide( self.col, new_row, self.rot, self.world.board ):
            self.world.end_trial()
    
    def place_pos( self, col, rot, row, move = True):
        #print("col:",self.col,"rot:",self.rot,"row",self.row)
        newcol = col - Zoid.offset[self.type][rot][1]
        newrot = rot
        newrow = row + Zoid.offset[self.type][rot][0]
        if move:
            self.col = newcol
            self.rot = newrot
            self.row = newrow
        return (newcol, newrot, newrow)
        #print("col2:",self.col,"rot2:",self.rot,"row2",self.row)
        #self.world.end_trial()

    def left( self ):
        self.translate( -1 )
        #self.world.add_latency("STL")
        self.world.trans += 1
    ###

    def right( self ):
        self.translate( 1 )
        #self.world.add_latency("STR")
        self.world.trans += 1
    ###

    def collide( self, new_col, new_row, new_rot, board ):

        #simulate for overlap
        ix = new_col
        iy = self.world.game_ht - new_row
        for i in self.shape[new_rot]:
            for j in i:
                #only calculate when there's a zoid segment AND it's on the board
                if j != 0 and iy >= 0:
                    #hit bottom
                    if iy >= self.world.game_ht:
                        return True
                    #hit walls
                    if ix >= self.world.game_wd or ix < 0:
                        return True
                    #segment collision from zoid to board
                    if board[iy][ix] != 0: #segment collision
                        return True

                #special case for wall collisions above board
                if j != 0 and iy < 0 and ( ix >= self.world.game_wd or ix < 0 ):
                        return True

                ix += 1
            ix = new_col
            iy += 1
    ###

    def overboard( self, board ):
        ix = self.col
        iy = self.world.game_ht - self.row
        for i in self.shape[self.rot]:
            for j in i:
                if j != 0 and iy < 0:
                    return True
            iy += 1
        return False
    ###

    