""" define game states and menus """
from collections.abc import Callable
from abc import ABC, abstractmethod
import pygame
from entitys import Paddle, Ball
import utils
import settings


class State(ABC):
    """ abstract class for the state stack """

    def __init__(self, game) -> None:
        self.game = game
        self.prev_state: State

    @abstractmethod
    def update(self, keys: set[str]) -> None:
        """ abstract state method
        each state must have an update method """

    @abstractmethod
    def render(self, canvas: pygame.Surface) -> None:
        """ abstract state method
        each state must have a render method """

    def enter_state(self) -> None:
        """ append itself to the stack """
        if len(self.game.stack) > 1:
            self.prev_state = self.game.stack[-1]
        self.game.stack.append(self)

    def exit_state(self) -> None:
        """ pop itself form the stack """
        if len(self.game.stack) > 1:
            self.game.stack.pop()
        else:
            # the stack shall NEVER be empty
            # idk maybe quit the game ?
            pass


class Menu(State):
    """ Parent class of all menus, handel buttons and labels rendering.
    The first button declared is the bottom one.
    Exactly one button shall be set selected.
    The labels can be placed anywhere """

    class Label:
        """ text to put  anywhere on a menu """

        def __init__(
                self,
                text: str,
                font: pygame.font.Font,
                pos: tuple[int, int],
        ) -> None:
            self.font = font
            self.pos = pos

            self.update(new_text=text)

        def update(self, new_text: str) -> None:
            """ recreate an image from text and font """
            self.image: pygame.Surface = self.font.render(new_text, False, settings.FONT_COLOR)
            self.frect: pygame.FRect = self.image.get_frect()
            self.frect.center = self.pos

        def render(self, canvas: pygame.Surface) -> None:
            """ bruh it's just a blit """
            canvas.blit(self.image, self.frect)

    class Button:
        """ button to pass to the menu.
        a method must be associated to each button. """

        def __init__(
                self,
                text: str,
                function: Callable[[], None],
                font: pygame.font.Font,
                selected: bool = False,
        ) -> None:
            self.text = text
            self.function = function
            self.font = font
            self.selected = selected

            self.image: pygame.Surface = self.font.render(self.text, False, color=(0, 0, 0))
            self.frect: pygame.FRect = self.image.get_frect()

        def update(self) -> None:
            """ add ">button<" arround the button if selected """
            if self.selected:
                self.image = self.font.render(('>' + self.text + '<'), False, color=(50, 50, 50))
            else:
                self.image = self.font.render(self.text, False, color=(0, 0, 0))

            self.frect = self.image.get_frect()

        def render(self, canvas: pygame.Surface, dest: tuple[float, float]) -> None:
            """ i hate you pylint """
            canvas.blit(self.image, dest=dest)

    def __init__(
            self,
            game,
            background_color: settings.Color,
            is_transparent: bool = False
    ) -> None:
        super().__init__(game)
        # background
        self.background_color = background_color
        self.is_transparent = is_transparent

        # font
        self.font = pygame.font.Font('font/PixeloidSans.ttf', 30)
        self.bold_font = pygame.font.Font('font/PixeloidSansBold.ttf', 35)
        self.big_font = pygame.font.Font('font/PixeloidSansBold.ttf', 80)

        # create buttons and labels list for each child
        self.buttons: list[Menu.Button] = []
        self.labels: list[Menu.Label] = []

    def update(self, keys: set[str]) -> None:
        """ move the selected/focus across buttons
        and apply action if a button is pressed """

        # exit the menu if ESC is pressed
        if 'ESCAPE' in keys:
            keys.remove('ESCAPE')
            self.exit_state()

        for i, button in enumerate(self.buttons):
            if 'UP' in keys and button.selected and i != len(self.buttons) - 1:
                keys.remove('UP')
                self.buttons[i + 1].selected = True
                button.selected = False
                self.buttons[i + 1].update()
                button.update()
                break
            if 'DOWN' in keys and button.selected and i != 0:
                keys.remove('DOWN')
                self.buttons[i - 1].selected = True
                self.buttons[i - 1].update()
                button.selected = False
                button.update()
                break

            # button action
            if 'RETURN' in keys and button.selected:
                keys.remove('RETURN')
                button.function()
                # break

    def render(self, canvas: pygame.Surface) -> None:
        """ blit buttons, labels and a background to the given surface """
        # background
        if self.is_transparent:
            self.prev_state.render(canvas=canvas)
            # not optimized but avoid needing to reload the stack every resolution change
            transparent_background = pygame.Surface(size=(settings.WIDTH, settings.HEIGHT))
            transparent_background.fill(self.background_color)
            transparent_background.set_alpha(settings.TRANSPARENCY_ALPHA)

            canvas.blit(source=transparent_background, dest=(0, 0))
        else:
            canvas.fill(self.background_color)

        # blit the buttons
        for i, button in enumerate(self.buttons):
            # center this shit was a pain in the ass
            x = settings.WIDTH // 2 - button.frect.width // 2
            y = (
                    (settings.HEIGHT // 2 - (button.frect.height // 2) * ((3 * i) + 1)) +
                    (len(self.buttons) // 2) * button.frect.height
            )
            button.render(canvas, (x, y))

        # blit the labels
        for label in self.labels:
            label.render(canvas)


class Gameplay(State):
    """ main part of the game.
    is a state on the stack
    """
    def __init__(self, game) -> None:
        super().__init__(game)

        # reset score
        settings.score['RIGHT'] = 0
        settings.score['LEFT'] = 0
        self.last_score = settings.score

        self.score_font = pygame.font.Font('font/PixeloidSansBold.ttf', 50)
        self.score_image = self.score_font.render('score', False, '#FFFFFF')
        self.score_image = self.score_font.render(
            f'{settings.score['LEFT']}-{settings.score['RIGHT']}', False, settings.SCORE_COLOR
            )

        # add itself to the stack
        self.enter_state()

        self.playtime_in_frames = 0

        # timer
        self.countdown_in_frames = settings.COUNTDOWN*settings.FPS

        # create objects
        self.paddles: list[Paddle] = []
        self.paddles.append(Paddle(
            pos=(settings.WIDTH / 10, settings.HEIGHT / 2),
            keybinds=settings.P1Keys,
        ))
        self.paddles.append(Paddle(
            pos=(settings.WIDTH * 0.9, settings.HEIGHT / 2),
            keybinds=settings.P2Keys,
        ))

        self.ball = Ball(pos=(settings.WIDTH/2, settings.HEIGHT/2))

    def update(self, keys: set[str]) -> None:
        """ update the balls, powerups and paddle """
        # update the paddles
        for paddle in self.paddles:
            paddle.update(keys=keys)


        self.ball.update(self.paddles)

        if self.last_score != settings.score:
            self.score_image = self.score_font.render(
                f'{settings.score['LEFT']}-{settings.score['RIGHT']}', False, settings.SCORE_COLOR
            )
            self.last_score = settings.score

        # process keys press
        if 'ESCAPE' in keys:
            keys.remove('ESCAPE')  # prevent the pause to immediately quit
            Pause(self.game)
        if 'p' in keys and settings.CHEATS:
            keys.remove('p')
            Win(self.game)

    def render(self, canvas: pygame.Surface) -> None:
        """ blit paddles to the given surface """
        canvas.fill(color=settings.BACKGROUND_COLOR)

        if settings.SHOW_HITBOX:
            pygame.draw.line(
            surface=canvas,
            color='#ff0000',
            start_pos=(settings.WIDTH / 2, 0),
            end_pos=(settings.WIDTH / 2, settings.HEIGHT)
        )

        self.ball.render(canvas=canvas)

        # render the paddles
        for paddle in self.paddles:
            paddle.render(canvas=canvas)

        # blit score label

        canvas.blit(
            source=self.score_image,
            dest=(
                (settings.WIDTH/2) - (self.score_image.width/2),
                self.score_image.height + 20
            )
        )


class Mainmenu(Menu):
    """ this is the first state in the stack """

    def __init__(self, game) -> None:
        super().__init__(game, settings.MAINMENU_BACKGROUND_COLOR)

        # enter state
        self.enter_state()

        # init buttons
        self.buttons.extend([
            Menu.Button(
                text='exit',
                function=utils.exit_game,
                font=self.font,
            ),  # exit
            Menu.Button(
                text='settings',
                function=self.to_settings,
                font=self.font,
            ),  # settings
            Menu.Button(
                text='difficulties',
                function=self.to_difficulties_choice,
                font=self.font,
            ),  # difficulties
            Menu.Button(
                text='play',
                function=self.play,
                font=self.font,
                selected=True
            ),  # play
        ])

        for button in self.buttons:
            button.update()

        # create labels
        self.labels.append(Menu.Label(
            text='MAIN MENU',
            font=self.big_font,
            pos=(settings.WIDTH // 2, settings.HEIGHT // 10),
        ))  # main menu

    def to_difficulties_choice(self) -> None:
        """ create new Difficulties state """
        Difficulties(self.game)

    def to_settings(self) -> None:
        """ new Settings state """
        Settings(self.game)

    def play(self) -> None:
        """ new gameplay state """
        Gameplay(self.game)


class Gameover(Menu):
    """ gameover state, is a Menu.
    save highscore to file if needed
    shows score and highscore
    """

    def __init__(self, game) -> None:
        super().__init__(game, settings.GAMEOVER_BACKGROUND_COLOR)
        # append itself to the stack
        self.enter_state()

        # create buttons
        self.buttons.append(Menu.Button(
            text='menu',
            function=self.to_menu,
            font=self.font
        ))  # menu
        self.buttons.append(Menu.Button(
            text='replay',
            function=self.replay,
            font=self.font,
            selected=True
        ))  # replay

        for button in self.buttons:
            button.update()

        # create labels
        self.labels.append(Menu.Label(
            text='GAME OVER',
            font=self.big_font,
            pos=(settings.WIDTH // 2, settings.HEIGHT // 10)
        ))  # GAME OVER
        self.labels.append(Menu.Label(
            text=f'score : {settings.score['RIGHT']}-{settings.score['LEFT']}',
            font=self.bold_font,
            pos=(settings.WIDTH // 2, (settings.HEIGHT // 16) * 11)
        ))  # score : 99
        self.labels.append(Menu.Label(
            text=f"highscore : {settings.highscore['RIGHT']}-{settings.highscore['LEFT']}",
            font=self.bold_font,
            pos=(settings.WIDTH // 2, (settings.HEIGHT // 16) * 13)
        ))  # highscore : 9999

    def to_menu(self) -> None:
        """ go back to the mainmenu by poping the states stack """
        # stack :               mainmenu > gameplay > gameover
        self.exit_state()  # back to gameplay
        self.exit_state()  # back to menu

    def replay(self) -> None:
        """ create a new Gameplay state and modify the state stack """
        # stack :               mainmenu > gameplay > gameover
        self.exit_state()  # back to gameplay
        self.exit_state()  # back to menu
        Gameplay(self.game)


class Win(Menu):
    """ Win state,
    ave the highscore to file if needed.
    show score and highscore
    """

    def __init__(self, game) -> None:
        super().__init__(game, settings.WIN_BACKGROUND_COLOR)
        # append itself to the stack
        self.enter_state()

        # create buttons
        self.buttons.append(Menu.Button(
            text='menu',
            function=self.to_menu,
            font=self.font,
        ))  # menu
        self.buttons.append(Menu.Button(
            text='replay',
            function=self.replay,
            font=self.font,
            selected=True
        ))  # replay

        for button in self.buttons:
            button.update()

        # create labels
        self.labels.extend([
            Menu.Label(
                text='YOU WON !!!',
                font=self.big_font,
                pos=(settings.WIDTH // 2, settings.HEIGHT // 10),
            ),  # YOU WON
            Menu.Label(
                text=f'score : {settings.score['LEFT']}-{settings.score['RIGHT']}',
                font=self.bold_font,
                pos=(settings.WIDTH // 2, (settings.HEIGHT // 16) * 11),
            ),  # score : 090
            Menu.Label(
                text=f"highscore : {settings.score['LEFT']}-{settings.score['RIGHT']}",
                font=self.bold_font,
                pos=(settings.WIDTH // 2, (settings.HEIGHT // 16) * 13),
            ),  # highscore
        ])

    def to_menu(self) -> None:
        """ pop stack twice """
        self.exit_state()  # back to gameplay
        self.exit_state()  # back to menu

    def replay(self) -> None:
        """ recreate a gamplay state """
        self.exit_state()  # back to menu
        Gameplay(self.game)


class Pause(Menu):
    """ is a state of the stack,
    background transparent, so you can see the last frame of the last state
    """

    def __init__(self, game) -> None:
        super().__init__(game, settings.PAUSE_BACKGROUND_COLOR, is_transparent=True)

        # append itself to the stack
        self.enter_state()

        self.buttons.append(Menu.Button(
            text='menu',
            function=self.to_mainmenu,
            font=self.font
        ))  # menu
        self.buttons.append(Menu.Button(
            text='resume',
            function=self.resume,
            font=self.font,
            selected=True
        ))  # resume

        # buttons are not updated each frame
        # first update after being append
        for button in self.buttons:
            button.update()

        # labels
        self.labels.append(Menu.Label(
            text='Pause',
            font=self.big_font,
            pos=(settings.WIDTH // 2, settings.HEIGHT // 10)
        ))  # settings
        self.labels.append(Menu.Label(
            text=f'score : {settings.score['LEFT']}-{settings.score['RIGHT']}',
            font=self.bold_font,
            pos=(settings.WIDTH // 2, int(settings.HEIGHT * 0.8))
        ))  # score : 999
        if settings.DEBUG:
            self.labels.append(Menu.Label(
                text=f'Highscore : {settings.highscore}',
                font=self.font,
                pos=(150, 30),
            ))  # highscore

    def resume(self) -> None:
        """ after pause restart a counter """
        self.exit_state()

    def to_mainmenu(self) -> None:
        """ exit state twice"""
        # the stack :
        # >main>gameplay>pause
        self.exit_state()
        # >main>gameplay
        self.exit_state()
        # >main


class Settings(Menu):
    """ settings menu, give access to resolution, difficulties """

    def __init__(self, game) -> None:
        super().__init__(game, settings.SETTINGS_BACKGROUND_COLOR, is_transparent=False)

        # append itself to the stack
        self.enter_state()

        # create buttons
        self.buttons.extend([
            Menu.Button(
                text='sound',
                function=self.to_sound_settings,
                font=self.font,
            ),  # sound
            Menu.Button(
                text='resolution',
                function=self.to_resolution_settings,
                font=self.font,
                selected=True
            ),  # resolution
        ])

        if settings.DEBUG:
            self.buttons.append(
                Menu.Button(
                    text='save score to highscore file',
                    function=self.save_score,
                    font=self.font
                ),  # save score
            )

        for button in self.buttons:
            button.update()

        # Title
        self.labels.append(Menu.Label(
            text='Settings',
            font=self.big_font,
            pos=(settings.WIDTH // 2, settings.HEIGHT // 10)
        ))  # settings Title

    def to_sound_settings(self) -> None:
        """ not implemented yet """
        print('Coming (not) Soon !')

    def to_resolution_settings(self) -> None:
        """ create new Resolution state """
        Resolution(self.game)

    def save_score(self) -> None:
        """ force save score to highscore file.
        this is a debug feature.
        """
        raise NotImplementedError('not yet...')
        # utils.save(score=settings.score)
        # utils.load_highscore()


class Difficulties(Menu):
    """ select a difficulties.
    Change values in settings
    """

    def __init__(self, game) -> None:
        super().__init__(game, background_color=settings.SETTINGS_BACKGROUND_COLOR)
        self.enter_state()

        # buttons
        self.buttons.extend([
            Menu.Button(
                text='hard',
                function=self.hard,
                font=self.font
            ),  # hard
            Menu.Button(
                text='Normal',
                function=self.normal,
                font=self.font,
                selected=True
            ),  # normal
            Menu.Button(
                text='Easy',
                function=self.easy,
                font=self.font
            ),  # easy
        ])

        for button in self.buttons:
            button.update()

    def hard(self) -> None:
        """ change settings values to tweak speeds and stuff """
        settings.BALL_SPEED = 6
        settings.PADDLE_SPEED = 7
        settings.POWERUP_SPEED = 5
        settings.POWERUP_BIG_PADLLE_DURATION = 5
        settings.BALL_MULTIPLYER = 1
        settings.MAX_BOUNCE_ANGLE = 120
        settings.POWERUP_PADDLE_CHANCE = 7
        settings.POWERUP_BALL_CHANCE = 3
        settings.POWERUP_PADDLE_SIZE = 1.1
        self.exit_state()

    def normal(self) -> None:
        """ change settings values to tweak speeds and stuff """
        settings.BALL_SPEED = 5
        settings.PADDLE_SPEED = 8
        settings.POWERUP_SPEED = 2
        settings.POWERUP_BIG_PADLLE_DURATION = 10
        settings.BALL_MULTIPLYER = 2
        settings.MAX_BOUNCE_ANGLE = 60
        settings.POWERUP_PADDLE_CHANCE = 10
        settings.POWERUP_BALL_CHANCE = 10
        settings.POWERUP_PADDLE_SIZE = 1.2
        self.exit_state()

    def easy(self) -> None:
        """ change settings values to tweak speeds and stuff """
        settings.BALL_SPEED = 4
        settings.PADDLE_SPEED = 8
        settings.POWERUP_SPEED = 1
        settings.POWERUP_BIG_PADLLE_DURATION = 15
        settings.BALL_MULTIPLYER = 3
        settings.MAX_BOUNCE_ANGLE = 45
        settings.POWERUP_PADDLE_CHANCE = 25
        settings.POWERUP_BALL_CHANCE = 15
        settings.POWERUP_PADDLE_SIZE = 1.4
        self.exit_state()


class Resolution(Menu):
    """ change settings.WIDTH and settings.HEIGHT.
    Also toggle fullscreen
    """

    def __init__(self, game) -> None:
        super().__init__(game, background_color=settings.SETTINGS_BACKGROUND_COLOR)
        self.enter_state()

        # buttons
        self.buttons.extend([
            Menu.Button(
                text='512x256',
                function=self.res_512x256,
                font=self.font,
            ),  # 512x256
            Menu.Button(
                text='1024x512',
                function=self.res_1024x512,
                font=self.font,
            ),  # 1024x512
            Menu.Button(
                text='Toggle fullscreen',
                function=self.toggle_fullscreen,
                font=self.font,
                selected=True
            ),  # fullscreen
        ])

        for button in self.buttons:
            button.update()

        # label
        self.labels.append(Menu.Label(
            text='Resolutions',
            font=self.big_font,
            pos=(settings.WIDTH // 2, settings.HEIGHT // 10)
        ))  # resolution title

    def toggle_fullscreen(self) -> None:
        """ re-set the pygame display,
        update settings screen size
        """
        if self.game.fullscreen:
            self.game.display = pygame.display.set_mode(
                size=(settings.WIDTH_BACKUP, settings.HEIGHT_BACKUP)
            )
            settings.WIDTH, settings.HEIGHT = settings.WIDTH_BACKUP, settings.HEIGHT_BACKUP
            self.game.fullscreen = False
        else:
            self.game.display = pygame.display.set_mode(size=(0, 0), flags=pygame.FULLSCREEN)
            settings.WIDTH, settings.HEIGHT = self.game.display.get_size()
            self.game.fullscreen = True

    def res_512x256(self) -> None:
        """ recreate the pygame display at a given size
        and update settings.WIDTH and settings.HEIGHT
        """
        self.game.display = pygame.display.set_mode(size=(512, 256))
        settings.WIDTH, settings.HEIGHT = 512, 256

    def res_1024x512(self) -> None:
        """ recreate the pygame display at a given size
        and update settings.WIDTH and settings.HEIGHT
        """
        self.game.display = pygame.display.set_mode(size=(1024, 512))
        settings.WIDTH, settings.HEIGHT = 1024, 512
