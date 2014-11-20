#-*- coding: utf8 -*-
from FGAme.backends.core import Screen, InputListener, MainLoop
import pygame
import pyglet
import string
from pygame.locals import *
from pygame import locals as keys
from math import trunc

WINDOW = None

class PyGletScreen(Screen):
    '''Implementa a interface Screen, utilizando a biblioteca Pygame'''

    def __init__(self, width, height, **kwds):
        global WINDOW
        
        super(PyGletScreen, self).__init__(width, height, **kwds)
        self._window = pyglet.window.Window(width, height)
        WINDOW = self._window

    def show(self):
        self._window.flip()

    def _map_point(self, point):
        x, y = super(PyGletScreen, self)._map_point(point)
        X, Y = self.width, self.height
        x += 0.5 * X
        y = 0.5 * Y - y
        return (trunc(x), trunc(y))

    #===========================================================================
    # Desenho
    #===========================================================================
    def draw_circle(self, pos, radius, color=(0, 0, 0), solid=True):
        pos = self._map_point(pos)
        #pygame.draw.circle(self._screen, color, pos, trunc(radius))

    def draw_poly(self, points, color=(0, 0, 0), solid=True):
        points = [ self._map_point(pt) for pt in points ]
        #pygame.draw.polygon(self._screen, color, points)

    def draw_rect(self, pos, shape, color=(0, 0, 0), solid=True):
        x, y = self._map_point(pos)
        dx, dy = shape
        dx = trunc(dx * self.zoom)
        dy = trunc(dy * self.zoom)
        y -= dy
        #pygame.draw.rect(self._screen, color, (x, y, dx, dy))
        pyglet.graphics.draw(2, pyglet.gl.GL_POINTS,
                             ('v2i', (10, 15, 30, 35))
        )

    def draw_line(self, pt1, pt2, color=(0, 0, 0), solid=True):
        raise NotImplementedError

    def clear(self, color=None):
        #color = color or self.background
        #self._screen.fill(color)
        self._window.clear()
        R, G, B = self.background
        pyglet.gl.glClearColor(R / 255., G / 255., B / 255., 1)

        win = self._window
        verts = [ (win.width * 0.9, win.height * 0.9),
                  (win.width * 0.5, win.height * 0.1),
                  (win.width * 0.1, win.height * 0.9), ]
        colors = [ (255, 000, 000),
                   (000, 255, 000),
                   (000, 000, 255), ]
        glBegin(GL_TRIANGLES)
        for idx in range(len(verts)):
            glColor3ub(*colors[idx])
            glVertex2f(*verts[idx])
        glEnd()

from pyglet.gl import *

class PyGameListener(InputListener):
    '''Objetos do tipo listener.'''

    #===========================================================================
    # Conversões entre strings e teclas
    #===========================================================================
    # Setas direcionais
    KEY_CONVERSIONS = {
        'up': K_UP, 'down': K_DOWN, 'left': K_LEFT, 'right': K_RIGHT,
        'return': K_RETURN, 'space': K_SPACE, 'enter': K_RETURN,
    }

    # Adiciona as letras e números
    chars = '0123456789' + string.ascii_lowercase
    for c in chars:
        KEY_CONVERSIONS[c] = getattr(keys, 'K_' + c)

    #===========================================================================
    # Laço principal de escuta de eventos
    #===========================================================================

    def step(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                raise SystemExit
            elif event.type == KEYDOWN:
                self.on_key_down(event.key)
            elif event.type == KEYUP:
                self.on_key_up(event.key)
            elif event.type == MOUSEMOTION:
                # TODO: converter para coordenadas locais em screen
                self.on_mouse_motion(event.pos)

        self.on_long_press()

class PyGletMainLoop(MainLoop):
    def __init__(self, fps=60, *args, **kwds):
        super(PyGletMainLoop, self).__init__(fps,*args, **kwds)
        self.screen = PyGletScreen(800, 600)

    def run(self, timeout=None, phys_timeout=None):
        print('start pyglet run')
        label = pyglet.text.Label('Hello, world',
                          font_name='Times New Roman',
                          font_size=36,
                          x=WINDOW.width//2, y=WINDOW.height//2,
                          anchor_x='center', anchor_y='center')
        @WINDOW.event
        def on_draw():
            WINDOW.clear()
            label.draw()
        
        
        pyglet.app.run()

def init():
    pygame.init()


if __name__ == '__main__':
    from FGAme.exemplos import aabb_friction
