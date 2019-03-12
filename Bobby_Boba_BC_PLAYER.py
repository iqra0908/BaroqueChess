'''PlayerSkeletonA.py
The beginnings of an agent that might someday play Baroque Chess.

'''

import BC_state_etc as BC
import copy
import math
import timeit

myPlayer = 1
# index of pieces
pincer = 0
coordinator = 1
leaper = 2
imitator = 3
withdrawer = 4
king = 5
freezer = 6

BLANK = 0 

white_pieces = [3,5,7,9,11,13,15]
black_pieces = [2,4,6,8,10,12,14]

timeLimit = 1000000
t0 = 0

CODE_TO_INIT = {0:'-',2:'p',3:'P',4:'c',5:'C',6:'l',7:'L',8:'i',9:'I',10:'w',11:'W',12:'k',13:'K',14:'f',15:'F'}

DIRECTIONS_WITH_DIAG = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
DIRECTIONS = [(-1,0),(1,0),(0,-1),(0,1)]

# Cycle through remarks in the following categories depending on how our
# alpha-beta search analysis the game is going 
VERY_POSITIVE_REMARK = [
        "This position is the best! Just like my favorite boba, Mango Green Tea!",
        "Move GINGERly! I have the advantage here!",
        "THAI(M) for you to give up! I'm too far ahead!"]
POSITIVE_REMARK = [
        "While I wait in my Oasis of advantage, I wait for you to fail",
        "I'll wash away the taste of your bad play with a Taro Boba",
        "I don't want to keep TEA-sing you, but you're going down!",
        "You're no MATCHA for me!" ]
NEGATIVE_REMARK = [
        "You're bursting me like my favorite bursting cherry boba!",
        "Thank for PUDDING me in my place, I deserve it",
        "HONEY, DEW you mind going a little easier on me?" ]
VERY_NEGATIVE_REMARK = [
        "I feel like one of those bursting boba that's just about to pop!",
        "Stop! You're BERRYing me!",
        "This game isn't going to be a LONGAN with how bad you're beating me!" ]
remark_indices = [0, 0, 0, 0] # which line we last used for each type of remark

def makeMove(currentState, currentRemark, timelimit):
    # Compute the new state for a move.
    # This is a placeholder that just copies the current state.
    newState = BC.BC_state(currentState.board)

    # Fix up whose turn it will be.
    newState.whose_move = 1 - currentState.whose_move
    
    # Construct a representation of the move that goes from the
    # currentState to the newState.
    # Here is a placeholder in the right format but with made-up
    # numbers:
    global t0, timeLimit
    move = False
    iterative_deepening = True
    depth = 0
    if iterative_deepening:
      timeLimit = timelimit
      t0 = timeit.default_timer()
      runtime = 0
      best_move = False
      s = currentState
      while runtime < timelimit:
        (move, newS, value) = alpha_beta_pruning(currentState,-100000, 100000, currentState.whose_move, 2)
        if timeOut():
          break
        if move is not False:
          best_move = move
          s = newS
        depth += 1
        runtime = timeit.default_timer() - t0
        move = best_move
    else:
      (move, s, value) = alpha_beta_pruning(currentState,-100000, 100000, currentState.whose_move, 2)

    newState.whose_move = other(currentState.whose_move) 

    #print("ANALYSIS: full levels searched = " + str(depth))

    newRemark = "I'm BERRY happy to play you!" # default remark
    if value > 5:
        newRemark = VERY_POSITIVE_REMARK[remark_indices[0]]
        remark_indices[0] = (remark_indices[0] + 1) % len(VERY_POSITIVE_REMARK)
    elif value >= 0:
        newRemark = POSITIVE_REMARK[remark_indices[1]]
        remark_indices[1] = (remark_indices[1] + 1) % len(POSITIVE_REMARK)
    elif value < 5:
        newRemark = VERY_NEGATIVE_REMARK[remark_indices[3]]
        remark_indices[3] = (remark_indices[3] + 1) % len(VERY_NEGATIVE_REMARK)
    else:
        newRemark = NEGATIVE_REMARK[remark_indices[2]]
        remark_indices[2] = (remark_indices[2] + 1) % len(NEGATIVE_REMARK)

    newState.board = s.board
    #print('mystate', newState)
    # Make up a new remark

    return [[move, newState], newRemark]

def nickname():
    return "Boba Boy Bob"

def introduce():
    return '''I'm Bob, a Baroque Chess newbie and buff of Boba beverages. 
              I was created by the following human boba:
              Iqra Imtiaz, iqra0908@uw.edu and Matt Vaughn, mpvaughn@uw.edu
            '''

def prepare(player2Nickname):
    pass

def checkBoundaries(location):
  return location[0] >= 0 and location[0]<=7 and location[1]>=0 and location[1] <= 7

def timeOut():
	global t0, timeLimit
	timeLapsed = timeit.default_timer() - t0
	return  timeLapsed > timeLimit-0.2
	
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
		
def alpha_beta_pruning(state, alpha, beta, whoseMove, plyLeft):
	if timeOut() or plyLeft==0:
		return False, state, static_eval(state)
	if whoseMove == myPlayer:
		provisional = -100000
	else:
		provisional = 100000	
	best_move = False
	newState = state
	for s in successors(state, whoseMove):
		(lastMove, lastState, newVal) = alpha_beta_pruning(s[0], alpha, beta, other(whoseMove), plyLeft-1)
		#print(s)
		if whoseMove == myPlayer:
			if newVal > provisional:
				provisional = newVal
				newState = s[0]
				best_move = s[1]
			alpha = max(alpha, provisional)
		else:
			if newVal < provisional:
				provisional=newVal
				newState = s[0]
				best_move = s[1]
			beta = min(beta, provisional)
		if alpha >= beta:
			return best_move, newState, provisional
	
	return best_move, newState, provisional

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

''' This function creates new states from all the possible moves found
    and the pieces that will be captured as a result of those moves.'''
def successors(state, whoseMove):
    successors = []
    board = state.board
    who = whoseMove
    new_who = other(who)
    possibleLocations = possibleMoves(state, whoseMove)
    for (piece, starting_location) in possibleLocations:
        for end_location in possibleLocations[(piece, starting_location)]:
            new_state = BC.BC_state(board, new_who)
            capturedLoations = capture(board, starting_location, \
                                end_location, whoseMove)
            if capturedLoations:
                for cLoc in capturedLoations:
                    new_state.board[cLoc[0]][cLoc[1]] = 0
            new_state.board[starting_location[0]][starting_location[1]] = 0
            new_state.board[end_location[0]][end_location[1]] = piece
            successors.append((new_state, (starting_location, end_location)))
    return successors
    
# Given a legal move, return the location(s) of any piece(s) captured by the move 
#   currentState    = current board state
#   start           = starting position of the piece
#   end             = ending position of the piece
#   player          = player who made the given move
#   pieceType       = the type of piece capturing (explicitly stated so we can
#                     force imitator to act like another piece) 
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

# Assume white
def expensive_static_eval(currentState):
    otherPlayer = other(1)
    myPlayer = 1
    moves_MyPlayer = possibleMoves(currentState, myPlayer)
    moves_OtherPlayer = possibleMoves(currentState, otherPlayer)
    myPieces = getPieces(myPlayer)
    enemyPieces = getPieces(otherPlayer)
    K = K_bar = W = W_bar = C = C_bar = F = F_bar = I = I_bar \
    = L = L_bar = P = P_bar = M = M_bar = B = B_bar = 0

    for x in moves_MyPlayer:
        K += x[0]==myPieces[king]
        W += x[0]==myPieces[withdrawer]
        C += x[0]==myPieces[coordinator]
        F += x[0]==myPieces[freezer]
        L += x[0]==myPieces[leaper]
        I += x[0]==myPieces[imitator]
        P += x[0]==myPieces[pincer]
        B += x[0]==myPieces[pincer] and not moves_MyPlayer[x]
        M += len(moves_MyPlayer[x])
        
    for y in moves_OtherPlayer:
        K_bar += y[0]==enemyPieces[king]
        W_bar += y[0]==enemyPieces[withdrawer]
        C_bar += y[0]==enemyPieces[coordinator]
        F_bar += y[0]==enemyPieces[freezer]
        L_bar += y[0]==enemyPieces[leaper]
        I_bar += y[0]==enemyPieces[imitator]
        P_bar += y[0]==enemyPieces[pincer]
        B_bar += y[0]==enemyPieces[pincer] and not moves_OtherPlayer[y]
        M_bar += len(moves_OtherPlayer[y])

    #print(B-B_bar)
    value = 200*(K-K_bar)+9*(W-W_bar)+5*(C-C_bar + F-F_bar)+\
            3*(L-L_bar + I-I_bar)+1*(P-P_bar)+0.1*(M-M_bar)-\
            0.5*(B-B_bar)
    return value

def static_eval(currentState):

    otherPlayer = other(1)
    myPlayer = 1
    myPieces = getPieces(myPlayer)
    enemyPieces = getPieces(otherPlayer)

    board = currentState.board

    K = K_bar = W = W_bar = C = C_bar = F = F_bar = I = I_bar \
    = L = L_bar = P = P_bar = M = M_bar = B = B_bar = 0

    # Extra points for developing pincers well- we want <= 2 per row
    pincer_crowd_penalty = .5 # penalty per pincer > 2 per row
    bad_pincer_count = 0
    enemy_bad_pincer_count = 0

    # Development of all pieces: prefer to have 5 layers with friendlies filled
    friendly_row_count = 0
    enemy_row_count = 0

    for i in range(len(board)):
        pincer_count = 0 # pincers per row
        enemy_pincer_count = 0
        friendlySpotted = False
        enemySpotted = False
        for j in range(len(board[0])):
            K += board[i][j]==myPieces[king]
            W += board[i][j]==myPieces[withdrawer]
            C += board[i][j]==myPieces[coordinator]
            F += board[i][j]==myPieces[freezer]
            L += board[i][j]==myPieces[leaper]
            I += board[i][j]==myPieces[imitator]

            if board[i][j] == myPieces[pincer]:
                pincer_count += 1
                P += 1
                if pincer_count >= 2:
                    bad_pincer_count += 1

            if board[i][j] in myPieces and friendlySpotted == False:
                friendlySpotted = True
                friendly_row_count += 1

            if board[i][j] in enemyPieces and enemySpotted == False:
                enemySpotted = True
                enemy_row_count += 1

            K_bar += board[i][j]==enemyPieces[king]
            W_bar += board[i][j]==enemyPieces[withdrawer]
            C_bar += board[i][j]==enemyPieces[coordinator]
            F_bar += board[i][j]==enemyPieces[freezer]
            L_bar += board[i][j]==enemyPieces[leaper]
            I_bar += board[i][j]==enemyPieces[imitator]
            P_bar += board[i][j]==enemyPieces[pincer]

            if board[i][j] == myPieces[pincer]:
                enemy_pincer_count += 1
                P_bar += 1
                if pincer_count >= 2:
                    enemy_bad_pincer_count += 1

    #print(B-B_bar)
    value = 200*(K-K_bar)+9*(W-W_bar)+5*(C-C_bar + F-F_bar)+\
            3*(L-L_bar + I-I_bar)+1*(P-P_bar)+\
			pincer_crowd_penalty * (bad_pincer_count
              - enemy_bad_pincer_count) + .25 * (friendly_row_count
                      - enemy_row_count)

    return value

#BC.test_starting_board()
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
newState = BC.BC_state(board, 0)
#print(newState)
#print(alpha_beta_pruning(newState,-100000, 100000, 'B', 3))
#print(static_eval(newState))
#print(capture(newState.board, (3, 3), (4, 4), 'W'))
# print(possibleMoves(newState, 1))
