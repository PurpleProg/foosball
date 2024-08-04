""" Define elements of the game, like a ball """
import math  # for bounce angle calc
import random
from abc import abstractmethod, ABC
import pygame
import settings




class Paddle:
    """ move with keys, collide with walls and powerups """
    def __init__(self, game) -> None:
        super().__init__()

        self.game = game

        self.speed = settings.PADDLE_SPEED
        self.direction = pygame.Vector2(0, 0)

        self.image: pygame.Surface = pygame.image.load(
            file='assets/Paddles/Style B/Paddle_B_Purple_128x28.png'
        ).convert()
        self.image.set_colorkey('#ff00ff')
        self.image = pygame.transform.rotate(
            surface=self.image,
            angle=90,
        )
        self.pos: pygame.Vector2 = pygame.Vector2(
            x=settings.WIDTH / 10,
            y=settings.HEIGHT / 2
        )  # center the paddle on x and 10% of height on y

        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.centerx = int(self.pos.x)
        self.rect.centery = int(self.pos.y)

    def update(self, powerups: list) -> None:
        """ change the direction, move and collide """
        # update direction with arrows
        if self.game.keys['UP']:
            self.direction.x = 1
        elif self.game.keys['LEFT']:
            self.direction.x = -1
        else:
            self.direction.x = 0
        if self.game.keys['UP']:
            self.direction.y = -1
            #print('up')
        elif self.game.keys['DOWN']:
            self.direction.y = 1
            #print ('down')
        else:
            self.direction.y = 0

        # move the paddle
        # self.pos.x += self.speed * self.direction.x
        self.pos.y += self.speed * self.direction.y

        # update rect
        self.rect.centerx = int(self.pos.x)
        self.rect.centery = int(self.pos.y)

        # collide powerups
        '''for powerup in powerups:
            if self.rect.colliderect(powerup.rect):
                powerup.activate()'''

        # prevent paddle from going out of bouds
        # collide with walls
        # x axis
        if self.rect.right > settings.WIDTH:
            self.rect.right = settings.WIDTH
            self.game.keys['RIGHT'] = False
            self.pos.x = self.rect.centerx
        elif self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = self.rect.centerx
        # y axis
        if self.rect.bottom > settings.HEIGHT:
            self.rect.bottom = settings.HEIGHT
            self.game.keys['DOWN'] = False
            self.pos.y = self.rect.centery
        elif self.rect.top < 0:
            self.rect.top = 0
            self.pos.y = self.rect.centery

    def render(self, canvas: pygame.Surface) -> None:
        """ blit it's image to a surface """
        canvas.blit(self.image, self.rect)
        if settings.SHOW_HITBOX:
            pygame.draw.rect(
                surface=canvas,
                color=settings.HITBOX_COLOR,
                rect=self.rect,
                width=1
            )
        if settings.SHOW_DIRECTIONS:
            pygame.draw.line(
                surface=canvas,
                color=settings.DIRECTION_COLOR,
                start_pos=self.rect.center,
                end_pos=(
                    self.rect.centerx + self.direction.x * self.speed * 20,
                    self.rect.centery + self.direction.y * self.speed * 20
                ),
                width=2,
            )