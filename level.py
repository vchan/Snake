import ConfigParser
import os

directions = {
    'left': 0,
    'right': 1,
    'up': 2,
    'down': 3,
}

class Level(object):
    def __init__(self, config_file):
        config = ConfigParser.SafeConfigParser()
        config.read(config_file)

        self.num_apples = config.getint('snake', 'num_apples')
        self.name = config.get('snake', 'name')
        self.layout = config.get('level', 'layout')

        self.player_directions = dict((key, directions.get(value)) for key, value in config.items('player_directions'))

def get_levels():
    return [Level(os.path.join('levels', level_file)) for level_file in os.listdir('levels')]
