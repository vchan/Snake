from collections import deque
import multiprocessing
import Queue

import pygame
from pygame.locals import *

import game
import game_objects
import level

import process
from ai_vincent import VincentAI
from ai_jason import JasonAI
ai_classes = [VincentAI, JasonAI]

class Menu():
    def __init__(self, options, spacing=50):
        self.options = options
        self.font = pygame.font.SysFont("verdana", 30)
        self.font_color = pygame.Color(255, 255, 255)
        self.selector_color = pygame.Color(255, 255, 255)
        self.selector_padding = 20
        self.spacing = spacing
        self.frames_per_second = 10

    def show(self):
        clock = pygame.time.Clock()
        background = pygame.Surface(game.screen.get_size()).convert()
        background.fill(pygame.Color(0, 0, 0))

        menu_item_height = self.font.get_height() + self.spacing
        # menu_height = menu_item_height * len(self.options)
        # menu_top = (game.WINDOW_HEIGHT - menu_height) / 2
        menu_top = 300

        title_text = game.NAME
        title_color = pygame.Color(0, 255, 0)
        title_font = pygame.font.SysFont("impact", 70)
        title_top = 100
        subtitle_font = pygame.font.SysFont("georgia", 15)
        subtitle_text = "By Vincent and Jason"
        subtitle_top = 190

        option_selected = 0

        while True:
            clock.tick(self.frames_per_second)

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

            # Clear background
            game.screen.blit(background, (0, 0))

            # Draw title
            title = title_font.render(title_text, 1, title_color)
            title_pos = title.get_rect(centerx = game.WINDOW_WIDTH/2, y = title_top)
            game.screen.blit(title, title_pos)

            # Draw subtitle
            subtitle = subtitle_font.render(subtitle_text, 1, title_color)
            subtitle_pos = subtitle.get_rect(centerx = game.WINDOW_WIDTH/2, y = subtitle_top)
            game.screen.blit(subtitle, subtitle_pos)

            # Draw menu options
            for i, option in enumerate(self.options):
                text = self.font.render(option, 1, self.font_color)
                text_position = text.get_rect(centerx = game.WINDOW_WIDTH/2, y = menu_top + menu_item_height * i)
                game.screen.blit(text, text_position)

                # Draw selector
                if i == option_selected:
                    selector = pygame.Rect(text_position.left - self.selector_padding, text_position.top - self.selector_padding, text_position.width + self.selector_padding * 2, text_position.height + self.selector_padding * 2)
                    pygame.draw.rect(game.screen, self.selector_color, selector, 1)

            # Display!
            pygame.display.flip()

def main_loop():
    pygame.init()
    pygame.display.set_caption(game.NAME)
    clock = pygame.time.Clock()

    background = pygame.Surface(game.screen.get_size()).convert()
    background.fill(pygame.Color(0, 0, 0))

    input_queue = multiprocessing.Queue()

    while True:
        # Choose player mode
        options = ["Single player", "Two players", "Three players", "Four players"]
        selection = Menu(options).show()
        if selection is False:
            return
        else:
            game.num_players = selection + 1

        # Choose level
        levels = level.get_levels()
        selection = Menu([lvl.name for lvl in levels]).show()
        if selection is False:
            continue
        else:
            game.level = levels[selection]

            # If single player, add an AI player
            if game.num_players == 1:
                game.num_players = 4
                game.init_level()

                ai_engines = []
                ai_processes = []
                ai_engines.append(ai_classes[game.ai_index])
                ai_engines.append(ai_classes[game.ai_index])
                ai_engines.append(ai_classes[game.ai_index])
                ai_engines.append(ai_classes[game.ai_index])
                shared_apples = multiprocessing.Array(process.GameObject,
                        list((apple.x, apple.y) for apple in game.apples))
                shared_players = multiprocessing.Array(process.MovableGameObject,
                        list(((player.x, player.y), player.direction)
                            for player in game.players))
                ai_processes = [_class(player_index=i, board=game.shared_board, players=shared_players, apples=shared_apples, player=game.players[i], args=(input_queue,)) for i, _class in enumerate(ai_engines)]
                # Load threaded AI
                if game.use_multiprocessing:
                    map(lambda proc: proc.start(), ai_processes)
            else:
                game.init_level()

        # Start game loop
        return_to_menu = False
        game_status = None
        ai_frame_count = 1

        while not return_to_menu:
            clock.tick(game.frames_per_second)

            while True:
                # Process key presses from AI threads.
                # Pulls values from input queue, creates pygame Events, and
                # submits to event queue.
                try:
                    pygame.event.post(pygame.event.Event(KEYDOWN, {'key':
                        input_queue.get_nowait(),}))
                except Queue.Empty, qe:
                    break

            # Process non multiprocessing AI moves
            if not game.use_multiprocessing:
                map(lambda proc: proc.execute(), ai_processes)
                if ai_frame_count < 3:
                    ai_frame_count += 1
                else:
                    # map(lambda proc: proc.execute(), ai_processes)
                    ai_frame_count = 1

            # Get input
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    return_to_menu = True
                    # Shutdown all AI processes
                    if game.use_multiprocessing:
                        map(lambda proc: proc.shutdown(), ai_processes)
                    break

                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        game.players[0].grow = True
                    elif event.key == K_RETURN and game_status == "win":
                        game.init_level()
                        game_status = None
                        continue
                    elif event.key in game.player_controls[0]:
                        game.players[0].set_direction(game.player_controls[0].index(event.key))
                    elif event.key in game.player_controls[1] and game.num_players > 1:
                        game.players[1].set_direction(game.player_controls[1].index(event.key))
                    elif event.key in game.player_controls[2] and game.num_players > 2:
                        game.players[2].set_direction(game.player_controls[2].index(event.key))
                    elif event.key in game.player_controls[3] and game.num_players > 3:
                        game.players[3].set_direction(game.player_controls[3].index(event.key))

            # Update effects
            for effect in game.effects:
                effect.update()

            # Update game
            game.update()

            # Update shared board
            for i, v in enumerate([(apple.x, apple.y) for apple in game.apples]):
                shared_apples[i] = v

            for i, v in enumerate([((player.x, player.y), player.direction, player.get_length()) for player in game.players]):
                shared_players[i] = v

            # Draw the screen
            game.screen.blit(background, (0, 0))
            game.draw()
            for effect in game.effects:
                effect.draw()

            # Draw scoreboard
            score_icon_size = 30
            score_width = 55
            score_margin = 120
            all_score_widths = game.num_players * score_width + (game.num_players-1) * score_margin
            score_x = (game.WINDOW_WIDTH - all_score_widths)/2
            score_y = game.WINDOW_HEIGHT - game.SCOREBOARD_HEIGHT + (game.SCOREBOARD_HEIGHT-score_icon_size)/2
            for i, player in enumerate(game.players):
                icon = pygame.Rect(score_x + i*(score_width+score_margin), score_y, score_icon_size, score_icon_size)
                text = str(len(player.kills))

                score = pygame.font.SysFont('impact', 30).render(text, 1, pygame.Color("white"))
                score_pos = score.get_rect(left = icon.right + 10, centery = icon.centery)

                game.screen.blit(score, score_pos)
                pygame.draw.rect(game.screen, player.color, icon)

            # Check for the win condition
            winners = filter(lambda p: len(p.kills) >= game.level.kills_to_win, game.players)
            if winners:
                game_status = 'win'

                # Check for ties
                least_deaths = min(len(w.deaths) for w in winners)
                winners = filter(lambda w: len(w.deaths) == least_deaths, winners)
                if len(winners) > 1:
                    title = pygame.font.SysFont("impact", 100).render("Draw!", 1, pygame.Color("white"))
                else:
                    title = pygame.font.SysFont("impact", 100).render(winners[0].name + " wins!", 1, pygame.Color("white"))

                # Draw title
                title_pos = title.get_rect(centerx = game.WINDOW_WIDTH/2, centery = 200)
                game.screen.blit(title, title_pos)

                # Draw subtitle
                subtext = pygame.font.SysFont("verdana", 15).render("Press [ENTER] to play again, or [ESC] to return to the main menu.", 1, pygame.Color("white"))
                subtext_pos = subtext.get_rect(centerx = game.WINDOW_WIDTH/2, y = title_pos.bottom + 10)
                game.screen.blit(subtext, subtext_pos)

                # Draw summary
                header_width = 200
                header_height = 30
                header_margin = 0
                header_x = (game.WINDOW_WIDTH - header_width * game.num_players) / 2
                header_y = subtext_pos.bottom + 50
                cell_margin = 20

                for i, player in enumerate(game.players):
                    # Draw header box
                    header = pygame.Rect(header_x + (header_width+header_margin)*i, header_y, header_width, header_height)
                    pygame.draw.rect(game.screen, player.color, header)

                    # Draw header text
                    text = pygame.font.SysFont("arial", 16, bold=True).render(player.name, 1, pygame.Color("white"))
                    text_pos = text.get_rect(centerx = header.centerx, centery = header.centery)
                    game.screen.blit(text, text_pos)

                    # Draw death summary
                    s = "Total deaths: " + str(len(player.deaths))
                    death_summary_font = pygame.font.SysFont("arial", 14, bold=True).render(s, 1, pygame.Color("white"))
                    death_summary_pos = death_summary_font.get_rect(centerx = header.centerx, centery = header.bottom + cell_margin)
                    game.screen.blit(death_summary_font, death_summary_pos)

                    strings = []
                    strings.append(str(len(filter(lambda c: isinstance(c, game_objects.SnakePart) and c.player is not player, player.deaths))) + " by collision")
                    strings.append(str(len(filter(lambda c: isinstance(c, game_objects.Missile) and c.player is not player, player.deaths))) + " by missile")
                    strings.append(str(len(filter(lambda c: isinstance(c, game_objects.Wall), player.deaths))) + " by wall")
                    strings.append(str(len(filter(lambda c: (isinstance(c, game_objects.Missile) and c.player is player) or (isinstance(c, game_objects.SnakePart) and c.player is player), player.deaths))) + " by suicide")

                    for i, s in enumerate(strings):
                        text = pygame.font.SysFont("arial", 13).render(s, 1, pygame.Color("white"))
                        text_pos = text.get_rect(centerx = header.centerx, centery = death_summary_pos.bottom + (i+1)*cell_margin)
                        game.screen.blit(text, text_pos)

                    # Draw kill summary
                    s = "Total kills: " + str(len(player.kills))
                    kill_summary_font = pygame.font.SysFont("arial", 14, bold=True).render(s, 1, pygame.Color("white"))
                    kill_summary_pos = kill_summary_font.get_rect(centerx = header.centerx, centery = header.bottom + cell_margin + 130)
                    game.screen.blit(kill_summary_font, kill_summary_pos)

                    for i, opponent in enumerate(player.kills):
                        text = pygame.font.SysFont("arial", 13).render(opponent.name, 1, opponent.color)
                        text_pos = text.get_rect(centerx = header.centerx, centery = kill_summary_pos.bottom + (i+1)*cell_margin)
                        game.screen.blit(text, text_pos)


            # Display!
            pygame.display.flip()

if __name__ == '__main__':
    main_loop()
