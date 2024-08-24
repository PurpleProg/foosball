""" constants and global var """
from typing import NewType

Color = NewType('Color', str)


# global score
score: dict[str, int] = {'RIGHT': 0, 'LEFT': 0,}


# debugs
CHEATS = True
SHOW_HITBOX = True           # draw the rect
SHOW_DIRECTIONS = True       # draw a line
INVISIBILITY = CHEATS      # dont die
DEBUG_POS = False
DEBUG_STACK = False           # print stack
DEBUG_SCORE = False          # print score and highscore

WIN_SCORE = 10

# screen
WIDTH = 1024
HEIGHT = 512

FPS = 60

WIDTH_BACKUP = WIDTH
HEIGHT_BACKUP = HEIGHT

APPROX_CORNER_COLLISION = 10


# GOAL
GOAL_TOP = HEIGHT * 0.1
GOAL_BOTTOM = HEIGHT * 0.9


# keys
# pylint: disable=too-few-public-methods
class P1Keys:
    """ hold the keybinds of the player 1 """
    RIGHT = 'd'
    LEFT = 'a'
    UP = 'w'
    DOWN = 's'

class P2Keys:
    """ hold the keybinds of the player 2 """
    RIGHT = 'RIGHT'
    LEFT = 'LEFT'
    UP = 'UP'
    DOWN = 'DOWN'
# pylint: enable=too-few-public-methods


# BACKGROUND COLORS
BACKGROUND_COLOR = Color('#000000')  # to replace with assets
PAUSE_BACKGROUND_COLOR = Color('#ffff00')
MAINMENU_BACKGROUND_COLOR = Color('#00ffff')
GAMEOVER_BACKGROUND_COLOR = Color('#ff0000')
WIN_BACKGROUND_COLOR = Color('#00ff00')
SETTINGS_BACKGROUND_COLOR = Color('#00ffff')
HITBOX_COLOR = Color('#ff0000')
DIRECTION_COLOR = Color('#0000ff')
TRANSPARENCY_ALPHA = 150
SCORE_COLOR = '#ffffff'

# default font. There also is a bold and a mono variant.
FONT_NAME = 'font/PixeloidSans.ttf'
FONT_SIZE = 30
FONT_COLOR = Color('#000000')


# entities
MAX_BALLS = 10


BALL_RADIUS = 8

# those are change for each difficulty, default is normal difficulty.
####################################################################
POWERUP_BIG_PADLLE_DURATION = 10  # in second
POWERUP_SPEED = 2
BALL_MULTIPLYER = 2  # for every ball spawn X more ball

# percentages
POWERUP_PADDLE_SIZE = 1.5
POWERUP_PADDLE_CHANCE = 5
POWERUP_BALL_CHANCE = 5

MAX_BOUNCE_ANGLE = 60

BALL_SPEED = 7
PADDLE_SPEED = 8
