'''PlayerSkeletonA.py
The beginnings of an agent that might someday play Baroque Chess.

'''

import BC_state_etc as BC
import copy
import math
import random


# index of pieces
pincer = 0
coordinator = 1
leaper = 2
imitator = 3
withdrawer = 4
king = 5
freezer = 6

DIRECTIONS_WITH_DIAG = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
DIRECTIONS = [(-1,0),(1,0),(0,-1),(0,1)]

BLANK = 0 

white_pieces = [3,5,7,9,11,13,15]
black_pieces = [2,4,6,8,10,12,14]

CODE_TO_INIT = {0:'-',2:'p',3:'P',4:'c',5:'C',6:'l',7:'L',8:'i',9:'I',10:'w',11:'W',12:'k',13:'K',14:'f',15:'F'}


def makeMove(currentState, currentRemark, timelimit):
    # Compute the new state for a move.
    # This is a placeholder that just copies the current state.
    newState = BC.BC_state(currentState.board)

    # Fix up whose turn it will be.
    newState.whose_move = 1 - currentState.whose_move
    #print(currentState, currentState.whose_move)
    #print(possibleMoves(currentState,currentState.whose_move))
    
    # Construct a representation of the move that goes from the
    # currentState to the newState.
    # Here is a placeholder in the right format but with made-up
    # numbers:
    moves = possibleMoves(currentState,currentState.whose_move)
    randKey = random.choice(list(moves.keys()))
    while(not moves[randKey]):
        randKey = random.choice(list(moves.keys()))
    randVal = random.choice(list(moves[randKey]))
    move = (randKey[1], randVal)
    cLoc = capture(currentState.board, randKey[1], randVal, currentState.whose_move)
    if cLoc:
        for x in cLoc:
            newState.board[x[0]][x[1]] = 0
    newState.board[randKey[1][0]][randKey[1][1]] = 0
    newState.board[randVal[0]][randVal[1]] = randKey[0]

    #print('mystate', newState)
    # Make up a new remark
    newRemark = "I'll think harder in some future game. Here's my move"
    #print(move, s, value)

    return [[move, newState], newRemark]

def nickname():
    return "Newman"

def introduce():
    return "I'm Newman Barry, a newbie Baroque Chess agent."

def prepare(player2Nickname):
    pass

def checkBoundaries(location):
  return location[0] >= 0 and location[0]<=7 and location[1]>=0 and location[1] <= 7

def other(player):
    if player == 1:
        return 0
    else:
        return 1

''' Get pieces for the given player'''        
def getPieces(player):
    if player == 1:
        return white_pieces
    else:
        return black_pieces

''' Get all locations given:
    - location = current location of the piece
    - all = number of directions it can move, all or just vertical and horizontal
    - obstacles = friendly or enemy pieces that can block the piece being checked
    - leap = if the piece is leaper so we can disallow double leaps
    - board = board from the current state
    - enemyPieces = pieces of other player'''        
def getLocations(location, obstacles, enemyPieces, board, all, leap):
    directions = []
    b = enemyPieces
    if all:
        directions = DIRECTIONS_WITH_DIAG 
    else:
        directions = DIRECTIONS 
    locations = []
    for dir in directions:
        x = obstacles.copy()
        # new coords
        i = location[0]+dir[0]
        j = location[1]+dir[1]
        while(checkBoundaries((i,j)) and board[i][j] not in x):
            if leap and board[i][j] in b: # if leaper, leap once
                x += b
            else:
                locations.append((i,j))
            i+=dir[0]
            j+=dir[1]
    return locations

''' This function checks which piece it is and sets obstacles accordingly
    to call getLocations function above'''    
def getMoves(newState, i,j,mark,adjacentLocations, friendlyPieces, enemyPieces):
    moves = []
    a = friendlyPieces
    b = enemyPieces
    if mark == a[king]:#King
        for loc in adjacentLocations:
            if newState.board[loc[0]][loc[1]] in b+[0]:
                moves.append(loc)
    elif mark == a[pincer]: #pincer
        obstacles = a + b
        for loc in getLocations((i,j), obstacles, b, newState.board,0,0):
            moves.append(loc)
    elif mark in [a[withdrawer],a[coordinator],a[freezer]]:#Queen, coordinator, freezer
        obstacles = a + b
        for loc in getLocations((i,j), obstacles, b, newState.board,1,0):
            moves.append(loc)
    elif mark == a[leaper]: #leaper
        obstacles = a
        for loc in getLocations((i,j), obstacles, b, newState.board, 1, 1):
            moves.append(loc)
    
    return moves

''' This function iterates once through the board and check for all friendly pieces    
    to generate possible moves using getMoves function. 
    It also checks if there is enemy's freezer in adjacent pieces.
    It returns a dictionary allPossibleMoves with the piece and its location as key
    and a list of all the legal moves as its value.'''
def possibleMoves(currentState, player):
    allPossibleMoves = dict()
    friendlyPieces = getPieces(player)
    enemyPieces = getPieces(other(player))
    #print('legal moves of player', player, newState)
    for i in range(8):
        for j in range(8):
            mark = currentState.board[i][j]
            if mark in friendlyPieces:
                locations = [(i-1,j),(i+1,j),(i,j-1),(i,j+1),(i-1,j-1),(i-1,j+1),(i+1,j-1),(i+1,j+1)]
                adjacentLocations = [x for x in locations if checkBoundaries(x)]
                adjacentPieces = [currentState.board[y[0]][y[1]] for y in adjacentLocations]
                moves = []
                if enemyPieces[freezer] not in adjacentPieces: #freeze if enemy's freezer adjacent
                    if mark == friendlyPieces[imitator]: #Imitator
                        for x in adjacentPieces:
                            moves += getMoves(currentState, i,j,x+1,adjacentLocations, friendlyPieces, enemyPieces)
                    else:
                        moves = getMoves(currentState, i,j,mark,adjacentLocations, friendlyPieces, enemyPieces)
                    
                allPossibleMoves[(mark,(i,j))] = moves    
    return allPossibleMoves


	
# Given a legal move, return the location(s) of any piece(s) captured by the move 
#   currentState = current board state
#   start        = starting position of the piece
#   end         = ending position of the piece
#   player       = player who made the given move
def capture(board, start, end, player, pieceType=None):
    friendlyPieces = getPieces(player)
    enemyPieces = getPieces(other(player))

    if pieceType == None:
        mark = board[start[0]][start[1]]
    else:
        mark = pieceType

    # No need to handle freezers because we assume the piece could move
    # legally, so we assume it isn't frozen

    # If the king ended where another piece currently is, it is captured by
    # the king
    if mark == friendlyPieces[king]:
        if board[end[0]][end[1]] in enemyPieces:
            return [end] 

    # if there was a piece in the direction opposite of which the
    # withdrawer moved, that piece is captured
    elif mark == friendlyPieces[withdrawer]:        
        direction = (end[0] - start[0], end[1] - start[1]) 
        normalized = (math.copysign(min(1, abs(direction[0])), direction[0]), \
                math.copysign(min(1, abs(direction[1])), direction[1]))
        opposite = (math.floor(-1 * normalized[0]), math.floor(-1 * normalized[1]))
        possiblyWithdrawn = (opposite[0] + start[0], opposite[1] + start[1]) 
        if checkBoundaries(possiblyWithdrawn):
            if board[possiblyWithdrawn[0]][possiblyWithdrawn[1]] in enemyPieces:
                return [possiblyWithdrawn]

    # Coordinator captures pieces at (row of coordinator, col of king) or (row of
    # king, col of coordinator)
    elif mark == friendlyPieces[coordinator]:
        # Find the location of the king
        king_location = (-1, -1)
        for i in range(8):
            for j in range(8):
                if board[i][j] == friendlyPieces[king]:
                    king_location = (i, j)
                    break

        first_target = (end[0], king_location[1])
        second_target = (king_location[0], end[1])
        if board[end[0]][king_location[1]] in enemyPieces \
        and board[king_location[0]][end[1]] in enemyPieces:
            return [(king_location[0], end[1]), (end[0], king_location[1])]
        if board[end[0]][king_location[1]] in enemyPieces:
            return [(end[0], king_location[1])]
        if board[king_location[0]][end[1]] in enemyPieces:
            return [(king_location[0], end[1])]

    # Pincer/pawner captures any pieces horizontally or vertically in between
    # their end position and a friendly piece
    elif mark == friendlyPieces[pincer]:
        # enemySpotted == We've seen one enemy and no friendlies 
        enemySpotted = { (0, 1): None, (1, 0): None, (0, -1): None, (-1, 0):None}
        # Canceled == we've seen two enemies
        canceled = { (0, 1): False, (1, 0): False, (0, -1): False, (-1, 0): False }
        # pinced == we've seen an enemy followed by a friendly (pinced enemy)
        pinced = { (0, 1): False, (1, 0): False, (0, -1): False, (-1, 0): False}
        for i in range(8):
            for mov in DIRECTIONS:
                location = (end[0] + i * mov[0], end[1] + i * mov[1]) 
                if checkBoundaries(location):
                    if pinced[mov] == True or canceled == True:
                        continue
                    if board[location[0]][location[1]] in enemyPieces:
                        if enemySpotted[mov] == None:
                            enemySpotted[mov] = location 
                        else:
                            canceled[mov] = True
                    if board[location[0]][location[1]] in friendlyPieces:
                        if enemySpotted[mov] != None: 
                            pinced[mov] = True 
                        if enemySpotted[mov] == None:
                            canceled[mov] = True
        
        captured = []
        for mov in DIRECTIONS:
            if pinced[mov] != False:
                captured.append(enemySpotted[mov])

        return captured

    # Long-leaper captures by leaping over enemies in a straight/diagonal line
    elif mark == friendlyPieces[leaper]:
        diff = (end[0] - start[0], end[1] - start[1])
        dist = max(abs(diff[0]), abs(diff[1]))
        direction = (math.copysign(min(1, abs(diff[0])), diff[0]), \
                    math.copysign(min(1, abs(diff[1])), diff[1]))
        direction = (math.floor(direction[0]), math.floor(direction[1]))
        for i in range(dist):
            location = (start[0] + i * direction[0], start[1] + i * direction[1])
            if checkBoundaries(location) and board[location[0]][location[1]] in enemyPieces:
                return [location]


    # For imitators, it can leap only leapers, pince only pincers, etc...
    elif mark == friendlyPieces[imitator]:
        locations = [(start[0]-1,start[1]), (start[0]+1,start[1]), (start[0],start[1]-1), \
                (start[0],start[1]+1), (start[0]-1,start[1]-1), (start[0]-1,start[1]+1),
                (start[0]+1,start[1]-1), (start[0]+1,start[1]+1)]
        adjacentLocations = [x for x in locations if checkBoundaries(x)]
        adjacentPieces = [board[y[0]][y[1]] for y in adjacentLocations]

        # If the imitator started adjacent to a withdrawer or king check for
        # their respective captures 
        if enemyPieces[withdrawer] in adjacentPieces:
            captures = capture(board, start, end, player, friendlyPieces[withdrawer]) 
            if(captures != None):
                return captures
        if enemyPieces[king] in adjacentPieces:
            captures = capture(board, start, end, player, friendlyPieces[king]) 
            if (captures != None):
                return captures

        # If the imitator ends with line-of-sight horizontally or vertically of
        # a pincer, check for pinces
        for mov in DIRECTIONS:
            for i in range(8):
                location = (end[0] + i * mov[0], end[1] + i * mov[1])
                if checkBoundaries(location):
                    if board[location[0]][location[1]] in friendlyPieces:
                        continue
                    if board[location[0]][location[1]] == enemyPieces[pincer]:
                        captures = capture(board, start, end, player, friendlyPieces[pincer])
                        if captures != None:
                            return captures
                    if board[location[0]][location[1]] in enemyPieces:
                        continue
        
        # If imitator ends with line-of-sight of a leaper in any of the
        # 8 directions, check for leaps
        for mov in DIRECTIONS_WITH_DIAG:
            for i in range(8):
                location = (end[0] + i * mov[0], end[1] + i * mov[1])
                if checkBoundaries(location):
                    if board[location[0]][location[1]] in friendlyPieces:
                        continue
                    if board[location[0]][location[1]] == enemyPieces[leaper]:
                        captures = capture(board, start, end, player, friendlyPieces[leaper])
                        if captures != None:
                            return captures
                    if board[location[0]][location[1]] in enemyPieces:
                        continue

        # Check if the imitator can capture a coordinator 
        king_location = (-1, -1)
        for i in range(8):
            for j in range(8):
                if board[i][j] == friendlyPieces[king]:
                    king_location = (i, j)
                    break

        first_target = (end[0], king_location[1])
        second_target = (king_location[0], end[1])
        if board[end[0]][king_location[1]] == enemyPieces[coordinator]:
            return [(end[0], king_location[1])]
        if board[king_location[0]][end[1]] == enemyPieces[coordinator]:
            return [(king_location[0], end[1])]

    return None # Don't return a capture if there isn't one to be made 

# Returns whether a space in the board is occupied by an enemy piece
def isEnemyPiece(board, coord, enemies): 
    if board[coord[0]][coord[1]] in enemies:
      return True
    return False

BC.test_starting_board()
board = BC.parse('''
c l i w k i l f
p p p p p p p p
- - - - - - - -
- - - - - - - -
- - - - - - - -
P - - - - - - -
- P P P P P P P
F L I W K I L C
''')
'''board = BC.parse(
- - - - - - - -
- - - - - - - -
- - - - - - - -
- - - I - - - -
- - - - - - - -
- - - - - - - -
- - - - - - - -
- - - - - - - -
)'''
newState = BC.BC_state(board, 0)
#print(newState)
#print(possibleMoves(newState,0))
#print(possibleMoves(newState,1))
#print(alpha_beta_pruning(newState,-100000, 100000, 'B', 2))
#print(static_eval(newState))
#print(capture(newState.board, (3, 3), (4, 4), 'W'))
