#-*- coding: utf8 -*-
from mathutils import Vector
from math import trunc

class Screen(object):
    '''Backend para as funções de desenhar na tela do computador'''

    def __init__(self, width, height, pos=(0, 0), zoom=1, background=(255, 255, 255)):
        self.width = width
        self.height = height
        self.pos = Vector(*pos)
        self.zoom = zoom
        self.background = background

    @property
    def shape(self):
        return self.width, self.height

    #===========================================================================
    # Drawing functions
    #===========================================================================
    def draw_circle(self, pos, radius, color=(0, 0, 0), solid=True):
        raise NotImplementedError

    def draw_poly(self, L_points, color=(0, 0, 0), solid=True):
        raise NotImplementedError

    def draw_aabb(self, xmin, xmax, ymin, ymax, color=(0, 0, 0), solid=True):
        dx, dy = xmax - xmin, ymax - ymin
        self.draw_rect((xmin, ymin), (dx, dy), color=color, solid=solid)

    def draw_rect(self, pos, shape, color=(0, 0, 0), solid=True):
        raise NotImplementedError

    def draw_line(self, pt1, pt2, color=(0, 0, 0), solid=True):
        raise NotImplementedError

    def clear(self, color=None):
        raise NotImplementedError

    #===========================================================================
    # Other API functions
    #===========================================================================
    def init(self):
        raise NotImplementedError

    def show(self):
        raise NotImplementedError

    def _map_point(self, point):
        return point

class PyGameScreen(Screen):
    '''Implementa a interface Screen, utilizando a biblioteca Pygame'''

    def __init__(self, width, height, **kwds):
        super(PyGameScreen, self).__init__(width, height, **kwds)

        import pygame

        self._pygame = pygame
        self._screen = pygame.display.set_mode((width, height))

    def init(self):
        self._pygame.init()

    def show(self):
        self._pygame.display.update()

    def _map_point(self, point):
        x, y = super(PyGameScreen, self)._map_point(point)
        X, Y = self._screen.get_width(), self._screen.get_height()
        x += 0.5 * X
        y = 0.5 * Y - y
        return (trunc(x), trunc(y))

    #===========================================================================
    # Drawing functions
    #===========================================================================
    def draw_circle(self, pos, radius, color=(0, 0, 0), solid=True):
        pos = self._map_point(pos)
        self._pygame.draw.circle(self._screen, color, pos, trunc(radius))

    def draw_poly(self, points, color=(0, 0, 0), solid=True):
        points = [ self._map_point(pt) for pt in points ]
        self._pygame.draw.polygon(self._screen, color, points)

    def draw_rect(self, pos, shape, color=(0, 0, 0), solid=True):
        x, y = self._map_point(pos)
        dx, dy = shape
        dx = trunc(dx * self.zoom)
        dy = trunc(dy * self.zoom)
        y -= dy
        self._pygame.draw.rect(self._screen, color, (x, y, dx, dy))

    def draw_line(self, pt1, pt2, color=(0, 0, 0), solid=True):
        raise NotImplementedError

    def clear(self, color=None):
        color = color or self.background
        self._screen.fill(color)

if __name__ == '__main__':
    import pygame
    import time
    print
    t0 = time.time()
    while time.time() < t0 + 5:
        screen = PyGameScreen(800, 600)
        screen.init()
        screen.clear()
        screen.draw_circle((0, 0), 50)
        screen.draw_rect((0, 0), (200, 100), color=(255, 0, 0))
        screen.show()
