""" Define elements of the game, like a ball """
import random
import math
import pygame
import settings


class Paddle:
    """ move with keys, collide with walls and powerups """
    def __init__(self, game, pos: pygame.Vector2, keybinds) -> None:
        super().__init__()

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

        self.pos = pos
        self.keybinds = keybinds

        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.centerx = int(self.pos.x)
        self.rect.centery = int(self.pos.y)

    def update(self, keys: set[str]) -> None:
        """ change the direction, move and collide """
        # update direction with arrows
        if self.keybinds.RIGHT in keys:
            self.direction.x = 1
        elif self.keybinds.LEFT in keys:
            self.direction.x = -1
        else:
            self.direction.x = 0
        if self.keybinds.UP in keys:
            self.direction.y = -1
        elif self.keybinds.DOWN in keys:
            self.direction.y = 1
        else:
            self.direction.y = 0

        # move the paddle
        self.pos.x += self.speed * self.direction.x
        self.pos.y += self.speed * self.direction.y

        # update rect
        self.rect.centerx = int(self.pos.x)
        self.rect.centery = int(self.pos.y)

        # collide powerups
        # for powerup in powerups:
        #    if self.rect.colliderect(powerup.rect):
        #       powerup.activate()

        # prevent paddle from going out of bounds
        # collide with walls
        # x-axis
        if self.rect.right > settings.WIDTH:
            self.rect.right = settings.WIDTH
            keys.remove('RIGHT')
            self.pos.x = self.rect.centerx
        elif self.rect.left < 0:
            self.rect.left = 0
            self.pos.x = self.rect.centerx
        # y-axis
        # if self.rect.bottom > settings.HEIGHT:
            # self.rect.bottom = settings.HEIGHT
            # keys.remove('DOWN')
            # self.pos.y = self.rect.centery
        # elif self.rect.top < 0:
            # self.rect.top = 0
            # self.pos.y = self.rect.centery

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

        if settings.DEBUG_POS:
            print(f'paddle position : {self.pos.x}, {self.pos.y}')

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


class Ball:
    """ ball class, collide with other entities """
    def __init__(self, pos: pygame.Vector2) -> None:
        super().__init__()

        self.speed: int = settings.BALL_SPEED
        self.direction: pygame.Vector2 = pygame.Vector2(
            x=random.uniform(-1, 1),
            y=0)

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
        paddles: list[Paddle],
    ) -> None:
        """change the position of the ball"""

        self.pos.x += self.speed * self.direction.x
        self.pos.y += self.speed * self.direction.y

        self.rect.x = int(self.pos.x)
        self.rect.y = int(self.pos.y)

        self.collide(paddles)

    def collide(
        self,
        paddles: list[Paddle],
    ) -> None:
        """ bounce on walls and paddle. """

        self.collide_with_paddle(paddles=paddles)
        self.collide_with_walls()

        if self.direction.magnitude() > 1:
            self.direction.normalize_ip()

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

    def collide_with_paddle(self, paddles: list[Paddle]) -> None:
        """ bounce on paddle, calculate bounce angle """
        for paddle in paddles:
            if self.rect.colliderect(paddle.rect):
                # calculate angle
                distance = self.rect.centery - paddle.rect.centery
                normalized_distance = distance/(paddle.rect.height/2)
                bounce_angle = settings.MAX_BOUNCE_ANGLE * normalized_distance
                bounce_angle_in_radian = math.radians(bounce_angle)

                self.direction.y = math.sin(bounce_angle_in_radian)
                if self.pos.x > settings.WIDTH/2:
                    self.direction.x = -math.cos(bounce_angle_in_radian)
                else:
                    self.direction.x = math.cos(bounce_angle_in_radian)

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

        if settings.DEBUG_POS:
            print(f'ball position : {self.pos.x}, {self.pos.y}')
