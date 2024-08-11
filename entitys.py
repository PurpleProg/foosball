""" Define elements of the game, like a ball """
import random
import math
import pygame
import settings


class Paddle:
    """ move with keys, collide with walls and powerups """
    def __init__(self, pos: tuple[float, float], keybinds) -> None:
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

        self.keybinds = keybinds

        self.frect: pygame.FRect = self.image.get_frect()
        self.frect.center = pos

    def update(self, keys: set[str]) -> None:
        """ change the direction, move and collide """
        # update direction with arrows
        if self.keybinds.UP in keys:
            self.direction.y = -1
        elif self.keybinds.DOWN in keys:
            self.direction.y = 1
        else:
            self.direction.y = 0

        # move the paddle
        self.frect.x += self.speed * self.direction.x
        self.frect.y += self.speed * self.direction.y

        # collide powerups
        # for powerup in powerups:
        #    if self.frect.collideFrect(powerup.FRect):
        #       powerup.activate()

        # collide with walls
        # y-axis
        if self.frect.bottom > settings.HEIGHT:
            self.frect.bottom = settings.HEIGHT
            #keys.remove('DOWN')
        elif self.frect.top < 0:
            self.frect.top = 0

    def render(self, canvas: pygame.Surface) -> None:
        """ blit it's image to a surface """
        canvas.blit(self.image, self.frect)
        if settings.SHOW_HITBOX:
            pygame.draw.rect(
                surface=canvas,
                color=settings.HITBOX_COLOR,
                rect=self.frect,
                width=1
            )

        if settings.DEBUG_POS:
            print(f'paddle position : {self.frect.x}, {self.frect.y}')

        if settings.SHOW_DIRECTIONS:
            pygame.draw.line(
                surface=canvas,
                color=settings.DIRECTION_COLOR,
                start_pos=self.frect.center,
                end_pos=(
                    self.frect.centerx + self.direction.x * self.speed * 20,
                    self.frect.centery + self.direction.y * self.speed * 20
                ),
                width=2,
            )


class Ball:
    """ ball class, collide with other entities """
    def __init__(self, pos: tuple[float, float]) -> None:
        super().__init__()

        self.speed: int = settings.BALL_SPEED
        self.direction: pygame.Vector2 = pygame.Vector2(
            x=random.uniform(-1, 1),
            y=0)

        self.image: pygame.Surface = pygame.image.load(
            file='assets/Balls/Glass/Ball_Blue_Glass-32x32.png'
        ).convert()
        self.image.set_colorkey('#ff00ff')

        self.frect: pygame.FRect = self.image.get_frect()
        self.frect.center = pos

    def update(
        self,
        paddles: list[Paddle],
    ) -> None:
        """change the position of the ball"""

        self.frect.x += self.speed * self.direction.x
        self.frect.y += self.speed * self.direction.y

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
        if self.frect.left < 0 or self.frect.right > settings.WIDTH :
            self.direction.x *= -1
            # prevent the ball from going out of bounce
            if self.frect.right > settings.WIDTH:
                self.frect.right = settings.WIDTH
                self.direction.x = -1
            elif self.frect.left < 0:
                self.frect.left = 0
                self.direction.x = 1
        # ceiling
        if self.frect.top < 0:
            self.frect.top = 0
            self.direction.y = 1
        # bounce on the bottom too IF cheats are enable in settings
        # gameover is detected on gameplay.update
        if self.frect.bottom > settings.HEIGHT and settings.INVISIBILITY:
            self.direction.y = -1
            self.frect.bottom = settings.HEIGHT

    def collide_with_paddle(self, paddles: list[Paddle]) -> None:
        """ bounce on paddle, calculate bounce angle """
        for paddle in paddles:
            if self.frect.colliderect(paddle.frect):
                # calculate angle
                distance = self.frect.centery - paddle.frect.centery
                normalized_distance = distance/(paddle.frect.height/2)
                bounce_angle = settings.MAX_BOUNCE_ANGLE * normalized_distance
                bounce_angle_in_radian = math.radians(bounce_angle)

                self.direction.y = math.sin(bounce_angle_in_radian)
                # clamp left or right direction depending on the paddle position
                # if the paddle is on the right the ball bounce to the left
                if self.frect.x > settings.WIDTH/2:
                    self.direction.x = -math.cos(bounce_angle_in_radian)
                else:
                    self.direction.x = math.cos(bounce_angle_in_radian)

    def render(self, canvas: pygame.Surface) -> None:
        """ blit it's image to a surface """
        canvas.blit(self.image, self.frect)
        if settings.SHOW_HITBOX:
            pygame.draw.rect(
                surface=canvas,
                color=settings.HITBOX_COLOR,
                rect=self.frect,
                width=1
            )

        if settings.SHOW_DIRECTIONS:
            pygame.draw.line(
                surface=canvas,
                color=settings.DIRECTION_COLOR,
                start_pos=self.frect.center,
                end_pos=(
                    self.frect.centerx + self.direction.x * self.speed * 10,
                    self.frect.centery + self.direction.y * self.speed * 10
                ),
                width=2,
            )

        if settings.DEBUG_POS:
            print(f'ball position : {self.frect.x}, {self.frect.y}')
