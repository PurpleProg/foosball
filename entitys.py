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
        self.diFrection = pygame.Vector2(0, 0)

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

        self.Frect: pygame.FRect = self.image.get_frect()
        self.Frect.centerx = int(self.pos.x)
        self.Frect.centery = int(self.pos.y)

    def update(self, keys: set[str]) -> None:
        """ change the diFrection, move and collide """
        # update diFrection with arrows
        '''if self.keybinds.RIGHT in keys:
            self.diFrection.x = 1
        elif self.keybinds.LEFT in keys:
            self.diFrection.x = -1
        else:
            self.diFrection.x = 0'''
        if self.keybinds.UP in keys:
            self.diFrection.y = -1
        elif self.keybinds.DOWN in keys:
            self.diFrection.y = 1
        else:
            self.diFrection.y = 0

        # move the paddle
        self.pos.x += self.speed * self.diFrection.x
        self.pos.y += self.speed * self.diFrection.y

        # update Frect
        self.Frect.centerx = int(self.pos.x)
        self.Frect.centery = int(self.pos.y)

        # collide powerups
        # for powerup in powerups:
        #    if self.Frect.collideFrect(powerup.Frect):
        #       powerup.activate()

        # prevent paddle from going out of bounds
        # collide with walls
        # x-axis
        '''if self.Frect.right > settings.WIDTH:
            self.Frect.right = settings.WIDTH
            keys.remove('RIGHT')
            self.pos.x = self.Frect.centerx
        elif self.Frect.left < 0:
            self.Frect.left = 0
            self.pos.x = self.Frect.centerx'''
        # y-axis
        if self.Frect.bottom > settings.HEIGHT:
            self.Frect.bottom = settings.HEIGHT
            #keys.remove('DOWN')
            self.pos.y = self.Frect.centery
        elif self.Frect.top < 0:
            self.Frect.top = 0
            self.pos.y = self.Frect.centery

    def render(self, canvas: pygame.Surface) -> None:
        """ blit it's image to a surface """
        canvas.blit(self.image, self.Frect)
        if settings.SHOW_HITBOX:
            pygame.draw.rect(
                surface=canvas,
                color=settings.HITBOX_COLOR,
                rect=self.Frect,
                width=1
            )

        if settings.DEBUG_POS:
            print(f'paddle position : {self.pos.x}, {self.pos.y}')

        if settings.SHOW_DIRECTIONS:
            pygame.draw.line(
                surface=canvas,
                color=settings.DIRECTION_COLOR,
                start_pos=self.Frect.center,
                end_pos=(
                    self.Frect.centerx + self.diFrection.x * self.speed * 20,
                    self.Frect.centery + self.diFrection.y * self.speed * 20
                ),
                width=2,
            )


class Ball:
    """ ball class, collide with other entities """
    def __init__(self, pos: pygame.Vector2) -> None:
        super().__init__()

        self.speed: int = settings.BALL_SPEED
        self.diFrection: pygame.Vector2 = pygame.Vector2(
            x=random.uniform(-1, 1),
            y=0)

        self.image: pygame.Surface = pygame.image.load(
            file='assets/Balls/Glass/Ball_Blue_Glass-32x32.png'
        ).convert()
        self.image.set_colorkey('#ff00ff')

        self.Frect: pygame.FRect = self.image.get_frect()
        self.pos = pos

        self.Frect.centerx = int(self.pos.x)
        self.Frect.centery = int(self.pos.y)

    def update(
        self,
        paddles: list[Paddle],
    ) -> None:
        """change the position of the ball"""

        self.pos.x += self.speed * self.diFrection.x
        self.pos.y += self.speed * self.diFrection.y

        self.Frect.x = int(self.pos.x)
        self.Frect.y = int(self.pos.y)

        self.collide(paddles)

    def collide(
        self,
        paddles: list[Paddle],
    ) -> None:
        """ bounce on walls and paddle. """

        self.collide_with_paddle(paddles=paddles)
        self.collide_with_walls()

        if self.diFrection.magnitude() > 1:
            self.diFrection.normalize_ip()

    def collide_with_walls(self) -> None:
        """ bounce on walls and ceiling """
        if self.Frect.left < 0 or self.Frect.right > settings.WIDTH :
            self.diFrection.x *= -1
            # prevent the ball from going out of bounce
            if self.Frect.right > settings.WIDTH:
                self.Frect.right = settings.WIDTH
                self.diFrection.x = -1
            elif self.Frect.left < 0:
                self.Frect.left = 0
                self.diFrection.x = 1
        # ceiling
        if self.Frect.top < 0:
            self.Frect.top = 0
            self.diFrection.y = 1
        # bounce on the bottom too IF cheats are enable in settings
        # gameover is detected on gameplay.update
        if self.Frect.bottom > settings.HEIGHT and settings.INVISIBILITY:
            self.diFrection.y = -1
            self.Frect.bottom = settings.HEIGHT

    def collide_with_paddle(self, paddles: list[Paddle]) -> None:
        """ bounce on paddle, calculate bounce angle """
        for paddle in paddles:
            if self.Frect.colliderect(paddle.Frect):
                # calculate angle
                distance = self.Frect.centery - paddle.Frect.centery
                normalized_distance = distance/(paddle.Frect.height/2)
                bounce_angle = settings.MAX_BOUNCE_ANGLE * normalized_distance
                bounce_angle_in_radian = math.radians(bounce_angle)

                self.diFrection.y = math.sin(bounce_angle_in_radian)
                if self.pos.x > settings.WIDTH/2:
                    self.diFrection.x = -math.cos(bounce_angle_in_radian)
                else:
                    self.diFrection.x = math.cos(bounce_angle_in_radian)

    def render(self, canvas: pygame.Surface) -> None:
        """ blit it's image to a surface """
        canvas.blit(self.image, self.Frect)
        if settings.SHOW_HITBOX:
            pygame.draw.rect(
                surface=canvas,
                color=settings.HITBOX_COLOR,
                rect=self.Frect,
                width=1
            )

        if settings.SHOW_DIRECTIONS:
            pygame.draw.line(
                surface=canvas,
                color=settings.DIRECTION_COLOR,
                start_pos=self.Frect.center,
                end_pos=(
                    self.Frect.centerx + self.diFrection.x * self.speed * 10,
                    self.Frect.centery + self.diFrection.y * self.speed * 10
                ),
                width=2,
            )

        if settings.DEBUG_POS:
            print(f'ball position : {self.pos.x}, {self.pos.y}')
