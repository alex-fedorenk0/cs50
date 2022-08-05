"""
Tic Tac Toe Player
"""

from copy import deepcopy
import random

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    x_count = sum(row.count(X) for row in board)
    o_count = sum(row.count(O) for row in board)

    if o_count < x_count:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    action_set = set()
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == EMPTY:
                action_set.add((i, j))
    return action_set


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action
    if board[i][j] == EMPTY:
        new_board = deepcopy(board)
        new_board[i][j] = player(board)
        return new_board
    else:
        raise ValueError('Cell not empty')
    #return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    if board == initial_state():
        return None
    
    def the_same(lst):
        return (EMPTY not in lst) and all(x == lst[0] for x in lst)

    # Check rows
    for row in board:
        if the_same(row):
            return row[0]

    # Check columns
    rotated_board = list(list(x) for x in zip(*board))[::-1]
    for row in rotated_board:
        if the_same(row):
            return row[0]

    # Check diagonals
    diag_1 = [board[i][i] for i in range(len(board))]
    diag_2 = [rotated_board[i][i] for i in range(len(rotated_board))]
    if the_same(diag_1):
        return diag_1[0]
    if the_same(diag_2):
        return diag_2[0]

    return None



def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    return winner(board) or sum(row.count(EMPTY) for row in board) == 0



def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    def max_value(state):
        v = -2
        if terminal(state):
            return utility(state)
        for action in actions(state):
            v = max(v, min_value(result(state, action)))
            if v >= 1: return v # Is it alpha-beta pruning ?
        return v

    def min_value(state):
        v = 2
        if terminal(state):
            return utility(state)
        for action in actions(state):
            v = min(v, max_value(result(state, action)))
            if v <= -1: return v # Is it alpha-beta pruning ?
        return v
    
    
    if terminal(board):
        return None
    
    if player(board) == X:
        v = -2
        for action in actions(board):
            best_value = min_value(result(board, action))
            if best_value > v:
                v = best_value
                best_action = action
        return best_action
    else:
        v = 2
        for action in actions(board):
            best_value = max_value(result(board, action))
            if best_value < v:
                v = best_value
                best_action = action
        return best_action

