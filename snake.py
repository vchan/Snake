from collections import deque

import pygame
from pygame.locals import *

import game
import game_objects
import level

def main_loop():
    pygame.init()
    pygame.display.set_caption("Jason's Snake Game")
    clock = pygame.time.Clock()

    background = pygame.Surface(game.screen.get_size()).convert()
    background.fill((0, 0, 0))

    player1_controls = [K_LEFT, K_RIGHT, K_UP, K_DOWN]
    player2_controls = [K_a, K_d, K_w, K_s]
    player3_controls = [K_j, K_l, K_i, K_k]
    player4_controls = [K_f, K_h, K_t, K_g]

    game.load_level(level.level_two)

    frames_until_update = 3
    frame_count = 0

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
