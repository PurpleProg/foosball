""" Define elements of the game, like a ball """
import math  # for bounce angle calc
import random
from abc import abstractmethod, ABC
import pygame
import settings


class Brick:
    """ brick constructor """
    def __init__(self, pos_x, pos_y) -> None:
        super().__init__()
        self.pos: pygame.Vector2 = pygame.Vector2(pos_x, pos_y)
        self.image: pygame.Surface = pygame.image.load(
            file='assets/Bricks/Colored/Colored_Purple-64x32.png'
        ).convert()
        self.image.set_colorkey('#ffffff')
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.topleft = int(self.pos.x), int(self.pos.y)

    def update(self) -> None:
        """ TODO:
        change image
        make a brick have multiple lifes
        """

    def render(self, canvas) -> None:
        """ blit it's image to a surface """
        canvas.blit(self.image, self.rect)


class Powerup(ABC):
    """abstract parent class"""
    def __init__(self, game, gameplay, pos: tuple) -> None:
        super().__init__()
        self.game = game
        self.gameplay = gameplay
        self.active = False
        self.image: pygame.Surface = pygame.Surface(size=(16, 16))
        self.rect: pygame.Rect = pygame.Rect(pos[0], pos[1], 16, 16)

    def activate(self) -> None:
        """make it invisible and apply the powerup"""
        self.image.set_alpha(0)
        self.rect.y = 0
        self.active = True
        self.powerup()

    @abstractmethod
    def powerup(self) -> None:
        """ every powerup shall overwrite this method """

    def update(self) -> None:
        """ move the powerup down"""
        if not self.active:
            self.rect.y += settings.POWERUP_SPEED
            if self.rect.top > settings.HEIGHT:
                self.gameplay.powerups.remove(self)

    def render(self, canvas: pygame.Surface) -> None:
        """ blit it's image to a canvas """
        canvas.blit(self.image, self.rect)


class PaddleGrowup(Powerup):
    """ Bonus that makes the paddle bigger """
    def __init__(self, game, gameplay, pos: tuple) -> None:
        super().__init__(game, gameplay, pos)
        self.gameplay = gameplay
        self.image.fill('#00ffff')
        self.countdown_in_frames = settings.POWERUP_BIG_PADLLE_DURATION * settings.FPS

    def update(self) -> None:
        """ overwrite for use a countdown """
        if self.active:
            self.countdown_in_frames -= 1
            if self.countdown_in_frames < 0:
                self.unpowerup()
                self.gameplay.powerups.remove(self)
        else:
            self.rect.y += settings.POWERUP_SPEED
            if self.rect.top > settings.HEIGHT:
                self.gameplay.powerups.remove(self)

    def powerup(self) -> None:
        """ add X% to the paddle size """

        if (self.gameplay.paddle.rect.width * settings.POWERUP_PADDLE_SIZE) > settings.WIDTH:
            self.gameplay.powerups.remove(self)
            return

        # strech the image
        self.gameplay.paddle.image = pygame.transform.scale(
            surface=self.gameplay.paddle.image,
            size=(
                self.gameplay.paddle.rect.width*settings.POWERUP_PADDLE_SIZE,
                self.gameplay.paddle.rect.height
            )
        )
        # create a new rect
        self.gameplay.paddle.rect = self.gameplay.paddle.image.get_rect()
        # center it
        self.gameplay.paddle.rect.centerx = int(self.gameplay.paddle.pos.x)
        self.gameplay.paddle.rect.centery = int(self.gameplay.paddle.pos.y)

    def unpowerup(self) -> None:
        """ shrink the paddle """

        # shrink the image
        self.gameplay.paddle.image = pygame.transform.scale(
            surface=self.gameplay.paddle.image,
            size=(
                self.gameplay.paddle.rect.width/settings.POWERUP_PADDLE_SIZE,
                self.gameplay.paddle.rect.height
            )
        )
        # create new rect
        self.gameplay.paddle.rect = self.gameplay.paddle.image.get_rect()
        # center it
        self.gameplay.paddle.rect.centerx = int(self.gameplay.paddle.pos.x)
        self.gameplay.paddle.rect.centery = int(self.gameplay.paddle.pos.y)


class MultipleBalls(Powerup):
    """ Bonus that spawns more balls """
    def __init__(self, game, gameplay, pos: tuple) -> None:
        super().__init__(game, gameplay, pos)
        self.image.fill('#ffff00')
        self.gameplay = gameplay

    def powerup(self) -> None:
        tmp_list = []
        # be carefull dont modify something you're iterating
        for ball in self.gameplay.balls:
            for _ in range(settings.BALL_MULTIPLYER):
                if len(self.gameplay.balls) >= settings.MAX_BALLS:
                    # linit exponential balls resulting in lag then crash
                    break
                tmp_list.append(Ball(
                    game=self.game,
                    gameplay=self.gameplay,
                    pos=pygame.Vector2(ball.pos.x, ball.pos.y)))
        for ball in tmp_list:
            self.gameplay.balls.append(ball)

        self.gameplay.powerups.remove(self)
