from pygame.locals import *

# ? Réglages & constantes générales
TITLE = "Dash Run"
FPS = 60
WIDTH = 640
HEIGHT = 360
WINDOW_SIZE = (WIDTH, HEIGHT)
DISPLAY_SIZE = (WIDTH / 2, HEIGHT / 2)
TILE_SIZE = 16
FONT_SIZE = 16
CHUNK_SIZE = 8
FULLSCREEN_MODE = False
DEBUG_MODE = False

# ? Contrôles
RIGHT_KEYS = [K_RIGHT, K_d]
LEFT_KEYS = [K_LEFT, K_q]
UP_KEYS = [K_UP, K_z, K_SPACE]
DOWN_KEYS = [K_DOWN, K_s]
FULLSCREEN_KEYS = [K_f, K_F11]
DEBUG_KEYS = [K_F3]


# ? Réglages du joueur
X_START = 50
Y_START = 100
SPEED = 2
FRICTION = 0.5
DASH_SPEED = 20
Y_LIMIT = 200