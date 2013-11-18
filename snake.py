from collections import deque

import pygame
from pygame.locals import *

import game
import game_objects
import level

class Menu():
    def __init__(self, options, spacing=50):
        self.options = options
        self.font = pygame.font.SysFont("verdana", 30)
        self.font_color = pygame.Color(255, 255, 255)
        self.selector_color = pygame.Color(255, 255, 255)
        self.selector_padding = 20
        self.spacing = spacing
        self.fps = 10

    def show(self):
        clock = pygame.time.Clock()
        background = pygame.Surface(game.screen.get_size()).convert()
        background.fill(pygame.Color(0, 0, 0))

        menu_item_height = self.font.get_height() + self.spacing
        menu_height = menu_item_height * len(self.options)
        menu_top = (game.WINDOW_HEIGHT - menu_height) / 2

        option_selected = 0

        while True:
            clock.tick(self.fps)

            for event in pygame.event.get():
                if event.type == QUIT:
                    return False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return False
                    elif event.key == K_UP:
                        option_selected -= 1
                    elif event.key == K_DOWN:
                        option_selected += 1
                    elif event.key == K_RETURN:
                        return option_selected

            if option_selected < 0:
                option_selected = len(self.options)-1
            if option_selected >= len(self.options):
                option_selected = 0

            game.screen.blit(background, (0, 0))

            for i, option in enumerate(self.options):
                text = self.font.render(option, 1, self.font_color)
                text_position = text.get_rect(centerx = game.WINDOW_WIDTH/2, y = menu_top + menu_item_height * i)
                game.screen.blit(text, text_position)

                if i == option_selected:
                    selector = pygame.Rect(text_position.left - self.selector_padding, text_position.top - self.selector_padding, text_position.width + self.selector_padding * 2, text_position.height + self.selector_padding * 2)
                    pygame.draw.rect(game.screen, self.selector_color, selector, 1)

            pygame.display.flip()

def main_loop():
    pygame.init()
    pygame.display.set_caption("Jason's Snake Game")
    clock = pygame.time.Clock()

    frames_until_update = 3
    frame_count = 0

    background = pygame.Surface(game.screen.get_size()).convert()
    background.fill(pygame.Color(0, 0, 0))

    player1_controls = [K_LEFT, K_RIGHT, K_UP, K_DOWN]
    player2_controls = [K_a, K_d, K_w, K_s]
    player3_controls = [K_j, K_l, K_i, K_k]
    player4_controls = [K_f, K_h, K_t, K_g]

    # Choose player mode
    options = ["Single player", "Two players", "Three players", "Four players"]
    selection = Menu(options).show()
    if selection is False:
        return
    else:
        game.num_players = selection+1

    # Choose level
    game.load_level(level.level_three)

    while True:
        clock.tick(60)

        # Get input
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                elif event.key == K_SPACE:
                     game.players[0].grow = True
                elif event.key in player1_controls:
                    game.players[0].set_direction(player1_controls.index(event.key))
                elif event.key in player2_controls and game.num_players > 1:
                    game.players[1].set_direction(player2_controls.index(event.key))
                elif event.key in player3_controls and game.num_players > 2:
                    game.players[2].set_direction(player3_controls.index(event.key))
                elif event.key in player4_controls and game.num_players > 3:
                    game.players[3].set_direction(player4_controls.index(event.key))

        # Update effects
        for effect in game.effects:
            effect.update()

        # Update game - we update less often than we draw to slow down the frame rate
        if frame_count < frames_until_update:
            frame_count += 1
        else:
            game.update()
            frame_count = 0

        # Draw the screen
        game.screen.blit(background, (0, 0))
        game.draw()

        for effect in game.effects:
            effect.draw()
        pygame.display.flip()

if __name__ == '__main__':
    main_loop()
