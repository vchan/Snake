LEFT, RIGHT, UP, DOWN = range(4)

class Level(object):
    pass

level_shelley = Level()
level_shelley.layout = """

1                                                                              2















































3                                                                              4 

"""
level_shelley.player_directions = {
    1: RIGHT,
    2: DOWN,
    3: UP,
    4: LEFT,
}

level_one = Level()
level_one.layout = """
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
W1                                                                            2W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W3                                                                            4W
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
"""
level_one.player_directions = {
    1: RIGHT,
    2: DOWN,
    3: UP,
    4: LEFT,
}


level_two = Level()
level_two.layout = """
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
W1                                                                            2W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
                          W                         W
                          W                         W
                          W                         W
                          W                         W
                          W                         W
                          W                         W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W3                                                                            4W
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
"""
level_two.player_directions = {
    1: RIGHT,
    2: DOWN,
    3: UP,
    4: LEFT,
}


level_three = Level()
level_three.layout = """
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW          WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                         WWWWWWWWWWWWWWWWWWWWWWWWWWW                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                                              W
W                                                   WWWWWWWWWWWWWWWWWWWWWWWWWWWW
WWWWWWWWWWWWWWWWWWWWWWWWWWW                         W
                        W W                         W
                        W W                         W
                        W W                         W
                        W W                         W
                        W                           W
                        W W                         W
W                       W W                         W                          W
W                       W W                         W                          W
W                       W W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W                         W                          W
W                         W1       3        4      2W                          W
W                         WWWWWWWWWWWWWWWWWWWWWWWWWWW                          W
W                         W                                                    W
W                         W                                                    W
W                         W                                                    W
W                         W                                                    W
W                         W                                                    W
WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW          WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
"""
level_three.player_directions = {
    1: UP,
    2: UP,
    3: UP,
    4: UP,
}