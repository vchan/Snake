import ConfigParser
import os

import pygame

import game
import game_objects

player_colors = {
    '1': pygame.Color(0, 255, 0),
    '2': pygame.Color(0, 0, 255),
    '3': pygame.Color(255, 0, 255),
    '4': pygame.Color(0, 128, 128),
}

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

    def parse_layout(self):
        layout = self.layout.split('\n')[1:]
        for y, row in enumerate(layout):
            for x, column in enumerate(row):
                if column == 'W':
                    game.walls.append(game_objects.Wall(x, y))
                if column == 'I':
                    game.walls.append(game_objects.IndestructableWall(x, y))
                elif column in ('1', '2', '3', '4'):
                    if int(column) <= game.num_players:
                        game.players.append(game_objects.Player('Player %s' % column, x, y, self.player_directions[column], player_colors[column]))
        for i in range(self.num_apples):
            game.add_apple()

def get_levels():
    return [Level(os.path.join('levels', level_file)) for level_file in os.listdir('levels')]
