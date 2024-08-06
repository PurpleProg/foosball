""" main file of a breakout game
Copyright me
Licence GPL-3+
"""
import sys
import pygame
import states
import settings

class Game:
    """ main class of breakout
    contain some global game var (like display)
    """
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        pygame.display.init()

        # init the display
        self.display: pygame.Surface = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        pygame.display.set_caption("Pong Game")
        self.fullscreen = False

        # init the stack
        self.stack: list[states.Menu | states.Gameplay] = []
        states.Mainmenu(self)

        # init global game var
        self.score: float = 0.0
        self.running: bool = True
        self.clock = pygame.time.Clock()
        self.keys = set()

        self.load_highscore()

    def load_highscore(self) -> None:
        """ attemp to load  the highscore file and store into self.highscore """
        try:
            self.highscore = settings.read_b64_json_file(file_name='highscore')
        except FileNotFoundError:
            # if the file is not found, create it with hiscore 0
            self.highscore = {'manu': 0,}
            settings.write_encode_string(file_name='highscore', data=self.highscore)

    def main_loop(self) -> None:
        """ main game loop.
        executed once each frame.
        handle events, updates and rendering.
        """
        while self.running:
            self.event()
            self.update()
            self.render()

    def event(self) -> None:
        """get event like keyboard press or mouse input and gather them in a dict"""
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            self.keys.add('ESCAPE')
                        case pygame.K_RETURN:
                            self.keys.add('RETURN')
                        case pygame.K_UP:
                            self.keys.add('UP')
                            #print('up')
                        case pygame.K_DOWN:
                            self.keys.add('DOWN')
                            #print('down')
                        case pygame.K_RIGHT:
                            self.keys.add('RIGHT')
                        case pygame.K_LEFT:
                            self.keys.add('LEFT')
                        case pygame.K_p:
                            self.keys.add('p')
                case pygame.KEYUP:
                    match event.key:
                        case pygame.K_ESCAPE:
                            self.keys.discard('ESCAPE')
                        case pygame.K_RETURN:
                            self.keys.discard('RETURN')
                        case pygame.K_UP:
                            self.keys.discard('UP')
                        case pygame.K_DOWN:
                            self.keys.discard('DOWN')
                        case pygame.K_RIGHT:
                            self.keys.discard('RIGHT')
                        case pygame.K_LEFT:
                            self.keys.discard('LEFT')
                        case pygame.K_p:
                            self.keys.discard('p')

    def update(self) -> None:
        """ update the last gamestate in the stack """
        self.stack[-1].update()

    def render(self) -> None:
        """ render last state in stack, update screen and limit FPS."""

        self.stack[-1].render(self.display)

        pygame.display.flip()
        self.clock.tick(settings.FPS)


def main():
    """ main entrypoint """
    game = Game()
    game.main_loop()


if __name__ == "__main__":
    main()
