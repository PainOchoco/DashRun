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
BIG_CHUNK_SIZE = 100
FULLSCREEN_MODE = False
DEBUG_MODE = False
PARTICLE_RADIUS = 5

# ? String
PRESS_KEY = "Press [ {} ] to start!"
DEATH_MSG = ["You died!", "Game Over", "D34D!", "G4M3 0V3R", "What have you done?", "Rest in peace", "You're dead. Again.", "Time to reload..."]
SCORE = "Score: {}"
PB = "Personal Best: {}"

# ? Couleurs
BG_COLOR = (4, 44, 54)
LIGHT = (222, 173, 167)
GRAY = (222, 173, 167)
YELLOW = (255, 255, 51)
ORANGE = (255, 53, 3)

# ? Contrôles
RIGHT_KEYS = [K_RIGHT, K_d]
LEFT_KEYS = [K_LEFT, K_q]
UP_KEYS = [K_UP, K_z, K_SPACE]
DOWN_KEYS = [K_DOWN, K_s]
DASH_KEYS = [K_LSHIFT, K_RSHIFT, K_TAB]
FULLSCREEN_KEYS = [K_f, K_F11]
DEBUG_KEYS = [K_F3]
START_KEY = K_RETURN


# ? Réglages du joueur
X_START = 50
Y_START = 50
SPEED = 2
DASH_SPEED = 5
DASH_TIMER = 20
DASH_COOLDOWN = 120
DASH_BAR_SIZE = (50, 10)
DASH_BAR_POS = (3, (HEIGHT / 2) - DASH_BAR_SIZE[1] - 3)
SCORE_POS = (3, 3)
DASH_ZOOM = (WIDTH / 4, HEIGHT / 4)
Y_LIMIT = 200
SCREEN_SHAKE_FORCE = 15
COUNTDOWN = 3