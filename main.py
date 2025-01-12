""" main file of the foosball game
Copyright us
Licence GPL-3+
"""
import sys
import pygame
import states
import settings


class Game:
    """ main class of the game
    get events (keypress)
    hold the stack
    """
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        pygame.display.init()

        # init the display
        self.display: pygame.Surface = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        pygame.display.set_caption("Foosball")
        self.fullscreen = False

        # init the stack
        self.stack: list[states.State] = []
        states.Mainmenu(self)

        # init global game var
        self.running: bool = True
        self.clock = pygame.time.Clock()
        self.keys: set[str] = set()

    def main_loop(self) -> None:
        """ main game loop.
        executed once each frame.
        handle events, updates and rendering.
        """
        while self.running:
            self.event()
            self.update()
            self.render()

            # debug stack
            if settings.DEBUG_STACK:
                for state in self.stack:
                    print(f'{type(state).__name__} > ', end='')
                print()
            # debug score
            if settings.DEBUG_SCORE:
                print(f'score : {settings.score}')

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
                            # print('up')
                        case pygame.K_DOWN:
                            self.keys.add('DOWN')
                            # print('down')
                        case pygame.K_RIGHT:
                            self.keys.add('RIGHT')
                        case pygame.K_LEFT:
                            self.keys.add('LEFT')
                        case pygame.K_p:
                            self.keys.add('p')
                        case pygame.K_a:
                            self.keys.add('a')
                        case pygame.K_d:
                            self.keys.add('d')
                        case pygame.K_s:
                            self.keys.add('s')
                        case pygame.K_w:
                            self.keys.add('w')
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
                        case pygame.K_a:
                            self.keys.discard('a')
                        case pygame.K_d:
                            self.keys.discard('d')
                        case pygame.K_s:
                            self.keys.discard('s')
                        case pygame.K_w:
                            self.keys.discard('w')

    def update(self) -> None:
        """ update the last game state in the stack """
        self.stack[-1].update(self.keys)

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
