import ConfigParser
import os.path

directions = {
    'left': 0,
    'right': 1,
    'up': 2,
    'down': 3,
}

class Level(object):
    def __init__(self, config_file):
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        self.layout = config.get('level', 'layout')

        self.num_players = config.getint('snake', 'num_players')
        self.num_apples = config.getint('snake', 'num_apples')

        self.player_directions = dict((key, directions.get(value)) for key, value in config.items('player_directions'))

level_shelley = Level('levels/level_shelley.ini')
level_one = Level('levels/level1.ini')
level_two = Level('levels/level2.ini')