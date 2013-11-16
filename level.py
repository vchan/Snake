LEFT, RIGHT, UP, DOWN = range(4)

class Level(object):
    pass

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
