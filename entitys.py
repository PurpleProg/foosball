""" Define elements of the game, like a ball """
import pygame
import settings


class Paddle:
    """ move with keys, collide with walls and powerups """
    def __init__(self, game, player) -> None:
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

        self.player=player
        if self.player == 1:
            self.pos: pygame.Vector2 = pygame.Vector2(
                x=settings.WIDTH / 10,
                y=settings.HEIGHT - (settings.HEIGHT / 2)
                )  # center the paddle on x and 10% of height on y
        elif self.player == 2:
            self.pos: pygame.Vector2 = pygame.Vector2(
                x=settings.WIDTH - settings.WIDTH / 10,
                y=settings.HEIGHT - (settings.HEIGHT / 2)
                )  # center the paddle on x and 10% of height on y

        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.centerx = int(self.pos.x)
        self.rect.centery = int(self.pos.y)

    def update(self, keys: set[str]) -> None:
        """ change the direction, move and collide """
        # update direction with arrows
        if 'RIGHT' in keys:
            self.direction.x = 1
        elif 'LEFT' in keys:
            self.direction.x = -1
        else:
            self.direction.x = 0
        if 'UP' in keys:
            self.direction.y = -1
        elif 'DOWN' in keys:
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
