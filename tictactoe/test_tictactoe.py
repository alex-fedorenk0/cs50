from tictactoe import EMPTY, X, O, initial_state, \
    winner, player, actions, result, terminal, utility, minimax
from pytest import raises


def test_initial_state():
    assert(initial_state() == [[EMPTY, EMPTY, EMPTY],
                               [EMPTY, EMPTY, EMPTY],
                               [EMPTY, EMPTY, EMPTY]])


def test_player():
    assert(player([[EMPTY, EMPTY, EMPTY],
                   [EMPTY, EMPTY, EMPTY],
                   [EMPTY, EMPTY, EMPTY]]) == X)
    assert(player([[X, EMPTY, EMPTY],
                   [EMPTY, EMPTY, EMPTY],
                   [EMPTY, EMPTY, EMPTY]]) == O)
    assert(player([[X, O, EMPTY],
                   [EMPTY, EMPTY, EMPTY],
                   [EMPTY, EMPTY, EMPTY]]) == X)
    assert(player([[X, O, X],
                   [O, X, X],
                   [O, X, O]]) == O)


def test_actions():
    assert(actions([[EMPTY, EMPTY, EMPTY],
                    [EMPTY, EMPTY, EMPTY],
                    [EMPTY, EMPTY, EMPTY]]) == {(0, 0), (0, 1), (0, 2),
                                                (1, 0), (1, 1), (1, 2),
                                                (2, 0), (2, 1), (2, 2)})
    assert(actions([[X, O, X],
                    [X, O, X],
                    [O, X, O]]) == set())
    assert(actions([[O, EMPTY, EMPTY],
                    [EMPTY, X, EMPTY],
                    [EMPTY, EMPTY, X]]) == {(0, 1), (0, 2), (1, 0),
                                            (1, 2), (2, 0), (2, 1)})

def test_result():
    assert(result([[EMPTY, EMPTY, EMPTY],
                   [EMPTY, EMPTY, EMPTY],
                   [EMPTY, EMPTY, EMPTY]], (0, 0)) == [[X, EMPTY, EMPTY],
                                                       [EMPTY, EMPTY, EMPTY],
                                                       [EMPTY, EMPTY, EMPTY]])
    assert(result([[X, EMPTY, EMPTY],
                   [EMPTY, EMPTY, EMPTY],
                   [EMPTY, EMPTY, EMPTY]], (1, 1)) == [[X, EMPTY, EMPTY],
                                                       [EMPTY, O, EMPTY],
                                                       [EMPTY, EMPTY, EMPTY]])
    with raises(ValueError):
        result([[X, EMPTY, EMPTY],
                [EMPTY, EMPTY, EMPTY],
                [EMPTY, EMPTY, EMPTY]], (0, 0))
    # Check for not changing passed board
    test_board = [[X, EMPTY, EMPTY],
                  [EMPTY, O, EMPTY],
                  [EMPTY, EMPTY, X]]
    assert(result(test_board, (1, 0)) == [[X, EMPTY, EMPTY],
                                          [O, O, EMPTY],
                                          [EMPTY, EMPTY, X]])
    assert(test_board[1][0] == EMPTY)    


def test_winner():
    assert(winner([[X, X, X],
                   [O, O, X],
                   [X, O, O]]) == X)
    assert(winner([[O, X, O],
                   [O, X, O],
                   [X, O, X]]) is None)
    assert(winner([[O, X, X],
                   [O, O, O],
                   [X, O, X]]) == O)
    assert(winner([[O, X, X],
                   [O, X, O],
                   [O, O, X]]) == O)
    assert(winner([[X, O, EMPTY],
                   [X, O, EMPTY],
                   [X, EMPTY, EMPTY]]) == X)
    assert(winner([[X, O, EMPTY],
                   [X, O, EMPTY],
                   [EMPTY, EMPTY, EMPTY]]) is None)
    assert(winner([[EMPTY, EMPTY, EMPTY],
                   [EMPTY, EMPTY, EMPTY],
                   [EMPTY, EMPTY, EMPTY]]) is None)
    assert(winner([[O, X, X],
                   [X, O, O],
                   [X, O, O]]) == O) # first diagonal
    assert(winner([[O, X, X],
                   [X, X, O],
                   [X, O, O]]) == X) # second diagonal


def test_terminal():
    assert(terminal([[O, X, X],
                     [X, O, O],
                     [X, O, O]]))
    assert(not terminal([[EMPTY, X, X],
                         [X, O, O],
                         [X, O, O]]))
    assert(terminal([[EMPTY, X, X],
                     [O, X, O],
                     [X, O, O]]))


def test_utility():
    assert utility([[X, X, X],
                    [O, O, X],
                    [X, O, O]]) == 1
    assert utility([[O, X, X],
                    [X, O, O],
                    [X, O, O]]) == -1
    assert utility([[O, X, X],
                    [X, X, O],
                    [O, O, X]]) == 0
                    
def test_minimax():
    assert minimax([[EMPTY, X, X],
                    [O, X, O],
                    [X, O, O]]) is None
    assert minimax([[EMPTY, X, EMPTY],
                    [O, X, O],
                    [X, O, O]]) == (0, 2)
    assert minimax([[O, X, X],
                    [X, O, O],
                    [X, EMPTY, EMPTY]]) == (2, 2)