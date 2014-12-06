#-*- coding: utf8 -*-
from FGAme.backends.core import Screen, InputListener
import pygame
import string
from pygame.locals import *
from pygame import locals as keys
from math import trunc

class PyGameScreen(Screen):
    '''Implementa a interface Screen, utilizando a biblioteca Pygame'''

    def __init__(self, width, height, set_mode_args=(), **kwds):
        super(PyGameScreen, self).__init__(width, height, **kwds)
        self._screen = pygame.display.set_mode((width, height), *set_mode_args)

    def show(self):
        pygame.display.update()

    def _map_point(self, point):
        x, y = super(PyGameScreen, self)._map_point(point)
        X, Y = self.width, self.height
        x += 0.5 * X
        y = 0.5 * Y - y
        return (trunc(x), trunc(y))

    #===========================================================================
    # Desenho
    #===========================================================================
    def draw_circle(self, pos, radius, color=(0, 0, 0), solid=True):
        pos = self._map_point(pos)
        pygame.draw.circle(self._screen, color, pos, trunc(radius))

    def draw_poly(self, points, color=(0, 0, 0), solid=True):
        points = [ self._map_point(pt) for pt in points ]
        pygame.draw.polygon(self._screen, color, points)

    def draw_rect(self, pos, shape, color=(0, 0, 0), solid=True):
        x, y = self._map_point(pos)
        dx, dy = shape
        dx = trunc(dx * self.zoom)
        dy = trunc(dy * self.zoom)
        y -= dy
        pygame.draw.rect(self._screen, color, (x, y, dx, dy))

    def draw_line(self, pt1, pt2, color=(0, 0, 0), solid=True):
        raise NotImplementedError

    def clear(self, color=None):
        color = color or self.background
        self._screen.fill(color)

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

def init():
    pygame.init()


