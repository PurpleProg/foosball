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

        self.speed: int = settings.PADDLE_SPEED
        self.direction: int = 0

        self.image: pygame.Surface = pygame.image.load(
            file='assets/Paddles/Style B/Paddle_B_Purple_128x28.png'
        ).convert()
        self.image.set_colorkey('#ff00ff')
        self.pos: pygame.Vector2 = pygame.Vector2(
            x=settings.WIDTH / 2,
            y=settings.HEIGHT - (settings.HEIGHT / 10)
        )  # center the paddle on x and 10% of height on y

        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.centerx = int(self.pos.x)
        self.rect.centery = int(self.pos.y)

    def update(self, powerups: list) -> None:
        """ change the direction, move and collide """
        # update direction with arrows
        if self.game.keys['RIGHT']:
            self.direction = 1
        elif self.game.keys['LEFT']:
            self.direction = -1
        else:
            self.direction = 0

        # move the paddle
        self.pos.x += self.speed * self.direction
        self.rect.centerx = int(self.pos.x)

        # collide powerups
        for powerup in powerups:
            if self.rect.colliderect(powerup.rect):
                powerup.activate()

        # prevent paddle from going out of bouds
        # collide with walls
        if self.rect.right > settings.WIDTH:
            self.rect.right = settings.WIDTH
            self.game.keys['RIGHT'] = False
            self.pos.x = self.rect.centerx
        elif self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = self.rect.centerx

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
                    self.rect.centerx + self.direction * self.speed * 20,
                    self.rect.centery
                ),
                width=2,
            )