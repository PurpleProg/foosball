""" Define elements of the game, like a ball """
import math  # for bounce angle calc
import random
from abc import abstractmethod, ABC
import pygame
import settings


class Ball:
    """ ball class, collide with other entities """
    def __init__(self, game, gameplay, pos: pygame.Vector2) -> None:
        super().__init__()

        self.game = game
        self.gameplay = gameplay
        self.speed: int = settings.BALL_SPEED
        self.direction: pygame.Vector2 = pygame.Vector2(
            x=random.uniform(-1, 1),
            y=1)

        self.image: pygame.Surface = pygame.image.load(
            file='assets/Balls/Glass/Ball_Blue_Glass-32x32.png'
        ).convert()
        self.image.set_colorkey('#ff00ff')

        self.rect: pygame.Rect = self.image.get_rect()
        self.pos = pos

        self.rect.centerx = int(self.pos.x)
        self.rect.centery = int(self.pos.y)

    def update(
        self,
        paddle,
        powerups: list,
    ) -> None:
        """change the position of the ball"""

        self.pos.x += self.speed * self.direction.x
        self.pos.y += self.speed * self.direction.y
        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

        self.collide(paddle, powerups)

    def collide(
        self,
        paddle,
        powerups: list
    ) -> None:
        """ bounce on walls and paddle.
        Spawns the powerups.
        """

        self.collide_with_walls()
        self.collide_with_paddle(paddle=paddle)

    def collide_with_walls(self) -> None:
        """ bounce on walls and ceiling """
        if self.rect.left < 0 or self.rect.right > settings.WIDTH :
            self.direction.x *= -1
            # prevent the ball from going out of bounce
            if self.rect.right > settings.WIDTH:
                self.rect.right = settings.WIDTH
                self.direction.x = -1
            elif self.rect.left < 0:
                self.rect.left = 0
                self.direction.x = 1
        # ceiling
        if self.rect.top < 0:
            self.rect.top = 0
            self.direction.y = 1
        # bounce on the bottom too IF cheats are enable in settings
        # gameover is detected on gameplay.update
        if self.rect.bottom > settings.HEIGHT and settings.INVISIBILITY:
            self.direction.y = -1
            self.rect.bottom = settings.HEIGHT

    def collide_with_paddle(self, paddle) -> None:
        """ bounce on paddle, calculate bounce angle """
        if self.rect.colliderect(paddle.rect):
            # calculate angle
            distance = self.rect.centerx - paddle.rect.centerx
            normalized_distance = distance/(paddle.rect.width/2)
            bounce_angle = settings.MAX_BOUNCE_ANGLE * normalized_distance
            bounce_angle_in_radian = math.radians(bounce_angle)

            self.direction.x = math.sin(bounce_angle_in_radian)
            self.direction.y = -math.cos(bounce_angle_in_radian)

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
                    self.rect.centerx + self.direction.x * self.speed * 10,
                    self.rect.centery + self.direction.y * self.speed * 10
                ),
                width=2,
            )


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
            self.direction.x = 1
        elif self.game.keys['LEFT']:
            self.direction.x = -1
        else:
            self.direction.x = 0
        if self.game.keys['UP']:
            self.direction.y = -1
        elif self.game.keys['DOWN']:
            self.direction.y = 1
        else:
            self.direction.y = 0

        # move the paddle
        # self.pos.x += self.speed * self.direction.x
        self.pos.y += self.speed * self.direction.y

        # update rect
        self.rect.centerx = int(self.pos.x)
        self.rect.centery = int(self.pos.y)

        # collide powerups
        for powerup in powerups:
            if self.rect.colliderect(powerup.rect):
                powerup.activate()

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
