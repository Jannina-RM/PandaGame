import os
import sys
import pygame
import random

from os import path

from .config import *
from .platform import Platform
from .player import Player
from .wall import Wall 
from .coin import Coin


class Game:
    def __init__(self):
        pygame.init()

        self.surface = pygame.display.set_mode( (WIDTH, HEIGHT) )
        pygame.display.set_caption(TITLE)

        self.running = True

        self.clock = pygame.time.Clock()

        self.dir = os.path.dirname(__file__)
        self.dir_sounds = os.path.join(self.dir, 'sources/sounds')
        self.dir_images = os.path.join(self.dir, 'sources/sprites')

        self.font = pygame.font.match_font(FONT)
        self.load_data()

    def load_data(self):
        self.dir = path.dirname(__file__)
        with open(path.join(self.dir, HS_FILE), 'w') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0

    def start(self):
        self.menu()
        self.new()

    def new(self):
        self.score = 0
        self.playing = True
        self.background = pygame.image.load( os.path.join(self.dir_images, 'fondo.png') )

        self.generate_elements()
        self.run()

    def generate_elements(self):
        self.platform = Platform()
        self.player = Player(100, self.platform.rect.top - 200, self.dir_images)

        self.sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()

        self.sprites.add(self.platform)
        self.sprites.add(self.player)

        self.generate_wall()
        self.generate_coins()

    def generate_wall(self):

        last_position = WIDTH + 150

        if not len(self.walls) > 0:

            for w in range(0, 5000):

                left = random.randrange(last_position + 200, last_position + 400)
                wall = Wall(left, self.platform.rect.top, self.dir_images)

                last_position = wall.rect.right

                self.sprites.add(wall)
                self.walls.add(wall)

    def generate_coins(self):
        last__position = WIDTH + 100

        for c in range(0, MAX_COINS):
            pos_x = random.randrange(last__position + 180, last__position + 300)

            coin = Coin(pos_x, 120, self.dir_images)

            last__position = coin.rect.right

            self.sprites.add(coin)
            self.coins.add(coin)

    def run(self):
        clock = pygame.time.Clock()

        while self.running:
            clock.tick(70)
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running == False
                pygame.quit()
                sys.exit

        key = pygame.key.get_pressed()

        if key[pygame.K_SPACE]:
            self.player.jump()

        if key[pygame.K_r] and not self.playing:
            self.new()

    def draw(self): 
        self.surface.blit(self.background, (0, 0))
        self.draw_text()

        self.sprites.draw(self.surface)  

        pygame.display.flip()

    def update(self):
        if self.playing:

            wall = self.player.collide_with(self.walls)
            if wall:
                if self.player.collide_bottom(wall):
                    self.player.skid(wall)

                else:
                    self.stop()

            coin = self.player.collide_with(self.coins)
            if coin:
                self.score += 1
                coin.kill()

                soundBird = pygame.mixer.Sound(os.path.join(self.dir_sounds, 'points.mp3'))
                soundBird.play()

            self.sprites.update()

            self.player.validate_platform(self.platform)

    def update_elements(self, elements):
        for element in elements:
            if not element.rect.right > 0:
                element.kill()

    def stop(self):
        sound = pygame.mixer.Sound(os.path.join(self.dir_sounds, 'loser.mp3'))
        sound.play()

        self.player.stop()
        self.stop_elements(self.walls)

        self.playing = False 

    def stop_elements(self, elements):

        for element in elements:
            element.stop()

    def score_format(self):
        return 'Your score : {}'.format(self.score)

    def draw_text(self):
        self.display_text(self.score_format(), 36, BLACK, 700, 15 )
        self.display_text('High Score: '+ str(self.highscore), 30, BLACK, WIDTH // 2, 15)

        if not self.playing:
            self.display_text('Perdiste'.format(self.score), 65, BLACK, WIDTH // 2, 150 )
            self.display_text('Presiona R para intentar de nuevo', 25, BLACK, WIDTH // 2, 200 )
            if self.score > self.highscore:
                self.highscore = self.score
                self.display_text('NUEVO RECORD', 30, BLACK, WIDTH // 2, 200)
                with open(path.join(self.dir, HS_FILE), 'w') as f:
                    f.write(str(self.score))
            else:
                self.display_text('High Score: '+ str(self.highscore), 30, BLACK, WIDTH // 2, 15)

            pygame.display.flip()

    def display_text(self, text, size, color, pos_x, pos_y):
        font = pygame.font.Font(self.font, size)

        text = font.render(text, True, color)
        rect = text.get_rect()
        rect.midtop = (pos_x, pos_y)

        self.surface.blit(text, rect)

    def menu(self):
        self.intro = pygame.image.load( os.path.join(self.dir_images, 'menu.png') )
        self.surface.blit(self.intro, (0, 0))

        pygame.display.flip()

        self.wait()

    def wait(self):
        wait = True

        while wait:
            self.clock.tick(100)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    wait = False
                    self.running = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYUP:
                    wait = False
