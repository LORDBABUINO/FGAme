#-*- coding: utf8 -*-
'''
Implementação do tradicional jogo Pong.
'''

from FGAme import *
from random import uniform, choice, random
from math import pi

class Pong(World):
    def __init__(self, **kwds):
        super(Pong, self).__init__()
        self.make_bounds(-800, 800, -290, 290)

        # Linha central
        self.add(AABB(shape=(15, 550), color=(200, 200, 200)), has_collision=False)

        # Cria a bola com uma velocidade aleatória
        self.ball = Circle(30, color='red', world=self, inertia='inf')
        self.ball.vel_cm = (-400, choice([-1, 1]) * uniform(200, 400))

        # Cria a barras
        self.pong1 = AABB(shape=[20, 130], pos_cm=(350, 0), world=self, mass='inf')
        self.pong2 = AABB(shape=[20, 130], pos_cm=(-350, 0), world=self, mass='inf')

        # Registra eventos
        self.listen('long-press', 'up', self.move_up, (self.pong1,))
        self.listen('long-press', 'down', self.move_down, (self.pong1,))
        self.listen('long-press', 'w', self.move_up, (self.pong2,))
        self.listen('long-press', 's', self.move_down, (self.pong2,))
        self.listen('key-down', 'space', self.toggle_pause)

    def move_up(self, pong):
        '''Move a raquete fornecida para cima'''

        if pong.ymax < 290:
            pong.move(Vector(0, 10))

    def move_down(self, pong):
        '''Move a raquete fornecida para baixo'''

        if pong.ymin > -290:
            pong.move(Vector(0, -10))

if __name__ == '__main__':
    Pong().run()
