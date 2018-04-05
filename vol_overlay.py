import gc
import Queue
from display_bcm import Display
from OpenGL.GL import *
from display_common import Rectangle, Point, Color, Location, Texture, Shader, ProgressBar
from vol_control import VolControl

# Settings
OMX_LAYER = 2
HIDE_DELAY = 5

# Colors (red, green, blue, alpha)
BACKGROUND_COLOR = Color(0.1, 0.1, 0.1, 0.9)
BACKGROUNDBAR_COLOR = Color(0.1, 0.1, 0.1, 1.0)
BAR_COLOR = Color(1.0, 1.0, 0.0, 1.0)

class State(object):
    def __init__(self, volume = 100, mute = 0):
        self.volume = volume
        self.mute = mute

state = None
queue = Queue.Queue()

def callback(volume, mute):
    queue.put(State(volume, mute))

VolControl(callback).listen()

display = Display(layer = OMX_LAYER)

s = Shader()

textureBackground = Texture("background.png")
textureBar = Texture("bar.png")
textureSpeaker = Texture("speaker.png")
textureMuted = Texture("muted.png")

ratio = display.width / display.height

screenWidth = 1
backgroundSize = 0.2
barSize = 0.09
imageSize = 0.15
imageOffset = (backgroundSize - imageSize) / 2

background = Rectangle(
    0,
    1.0 - backgroundSize,
    screenWidth,
    backgroundSize,
    colour = BACKGROUND_COLOR)

barBackground = Rectangle(
    0 + imageSize,
    1.0 - backgroundSize + (backgroundSize - barSize) / 2,
    screenWidth - imageOffset - imageSize,
    barSize,
    colour = BACKGROUNDBAR_COLOR)

bar = ProgressBar(
    0 + imageSize,
    1.0 - backgroundSize + (backgroundSize - barSize) / 2,
    screenWidth - imageOffset - imageSize,
    barSize,
    colour = BAR_COLOR)

image = Rectangle(
    0 + imageOffset,
    1.0 - backgroundSize + imageOffset * ratio,
    imageSize,
    imageSize * ratio)

glClearColor(0.0, 0.0, 0.0, 0.0)
glViewport(0, 0, display.width, display.height)

glMatrixMode(GL_PROJECTION)
glLoadIdentity()

glMatrixMode(GL_MODELVIEW)

glLoadIdentity()

glEnable(GL_BLEND)
glBlendEquationSeparate(GL_FUNC_ADD, GL_FUNC_ADD)
glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE, GL_ONE_MINUS_SRC_ALPHA);

gc.collect()

def draw(state):
    glClear(GL_COLOR_BUFFER_BIT)

    if state is not None:
        bar.value = state.volume

        background.draw(s, textureBackground)
        barBackground.draw(s, textureBar)

        if state.mute or state.volume == 0:
            image.draw(s, textureMuted)
        else:
            bar.draw(s, textureBar)
            image.draw(s, textureSpeaker)

    display.swapBuffers()

def getNewState():
    try:
        # Timeout required to allow Ctrl+C to work
        return queue.get(timeout = 1)
    except Queue.Empty:
        return None

def mainPoll():
    state = getNewState()

    if state is not None:
        while state is not None:
            draw(state)

            x = 0
            state = None
            while state is None and x < HIDE_DELAY:
                state = getNewState()
                x += 1

        draw(state) # Clear, as state is None at this time

try:
    print "Waiting on input..."

    while 1:
        mainPoll()

except KeyboardInterrupt:
    print "Quitting"
