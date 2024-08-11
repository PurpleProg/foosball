""" Define elements of the game, like a ball """
import random
import math
import pygame
import settings


class Paddle:
    """ move with keys, collide with walls and powerups """
    def __init__(self, game, pos: tuple[int, int], keybinds) -> None:
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

        self.FRect: pygame.FRect = self.image.get_frect()
        self.FRect.center = pos

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
        self.FRect.x += self.speed * self.direction.x
        self.FRect.y += self.speed * self.direction.y

        # collide powerups
        # for powerup in powerups:
        #    if self.FRect.collideFrect(powerup.FRect):
        #       powerup.activate()

        # collide with walls
        # y-axis
        if self.FRect.bottom > settings.HEIGHT:
            self.FRect.bottom = settings.HEIGHT
            #keys.remove('DOWN')
        elif self.FRect.top < 0:
            self.FRect.top = 0

    def render(self, canvas: pygame.Surface) -> None:
        """ blit it's image to a surface """
        canvas.blit(self.image, self.FRect)
        if settings.SHOW_HITBOX:
            pygame.draw.rect(
                surface=canvas,
                color=settings.HITBOX_COLOR,
                rect=self.FRect,
                width=1
            )

        if settings.DEBUG_POS:
            print(f'paddle position : {self.FRect.x}, {self.FRect.y}')

        if settings.SHOW_DIRECTIONS:
            pygame.draw.line(
                surface=canvas,
                color=settings.DIRECTION_COLOR,
                start_pos=self.FRect.center,
                end_pos=(
                    self.FRect.centerx + self.direction.x * self.speed * 20,
                    self.FRect.centery + self.direction.y * self.speed * 20
                ),
                width=2,
            )


class Ball:
    """ ball class, collide with other entities """
    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__()

        self.speed: int = settings.BALL_SPEED
        self.direction: pygame.Vector2 = pygame.Vector2(
            x=random.uniform(-1, 1),
            y=0)

        self.image: pygame.Surface = pygame.image.load(
            file='assets/Balls/Glass/Ball_Blue_Glass-32x32.png'
        ).convert()
        self.image.set_colorkey('#ff00ff')

        self.FRect: pygame.FRect = self.image.get_frect()
        self.FRect.center = pos

    def update(
        self,
        paddles: list[Paddle],
    ) -> None:
        """change the position of the ball"""

        self.FRect.x += self.speed * self.direction.x
        self.FRect.y += self.speed * self.direction.y

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
        if self.FRect.left < 0 or self.FRect.right > settings.WIDTH :
            self.direction.x *= -1
            # prevent the ball from going out of bounce
            if self.FRect.right > settings.WIDTH:
                self.FRect.right = settings.WIDTH
                self.direction.x = -1
            elif self.FRect.left < 0:
                self.FRect.left = 0
                self.direction.x = 1
        # ceiling
        if self.FRect.top < 0:
            self.FRect.top = 0
            self.direction.y = 1
        # bounce on the bottom too IF cheats are enable in settings
        # gameover is detected on gameplay.update
        if self.FRect.bottom > settings.HEIGHT and settings.INVISIBILITY:
            self.direction.y = -1
            self.FRect.bottom = settings.HEIGHT

    def collide_with_paddle(self, paddles: list[Paddle]) -> None:
        """ bounce on paddle, calculate bounce angle """
        for paddle in paddles:
            if self.FRect.colliderect(paddle.FRect):
                # calculate angle
                distance = self.FRect.centery - paddle.FRect.centery
                normalized_distance = distance/(paddle.FRect.height/2)
                bounce_angle = settings.MAX_BOUNCE_ANGLE * normalized_distance
                bounce_angle_in_radian = math.radians(bounce_angle)

                self.direction.y = math.sin(bounce_angle_in_radian)
                # clamp left or right direction depending on the paddle position
                # if the paddle is on the right the ball bounce to the left
                if self.FRect.x > settings.WIDTH/2:
                    self.direction.x = -math.cos(bounce_angle_in_radian)
                else:
                    self.direction.x = math.cos(bounce_angle_in_radian)

    def render(self, canvas: pygame.Surface) -> None:
        """ blit it's image to a surface """
        canvas.blit(self.image, self.FRect)
        if settings.SHOW_HITBOX:
            pygame.draw.rect(
                surface=canvas,
                color=settings.HITBOX_COLOR,
                rect=self.FRect,
                width=1
            )

        if settings.SHOW_DIRECTIONS:
            pygame.draw.line(
                surface=canvas,
                color=settings.DIRECTION_COLOR,
                start_pos=self.FRect.center,
                end_pos=(
                    self.FRect.centerx + self.direction.x * self.speed * 10,
                    self.FRect.centery + self.direction.y * self.speed * 10
                ),
                width=2,
            )

        if settings.DEBUG_POS:
            print(f'ball position : {self.FRect.x}, {self.FRect.y}')
