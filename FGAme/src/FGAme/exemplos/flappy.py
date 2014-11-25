#-*- coding: utf8 -*-
'''
Flappy Triangle on 18/11/2014
'''

from FGAme import *
from random import uniform

class Flappy(Poly):
    def __init__(self, **kwds):
        super(Flappy, self).__init__([(0, 0), (40, 0), (20, 80)], color='red', **kwds)
        self.pos_cm = (-200, 0)
        self.rotate(uniform(0, 2 * pi))
        self.inertia *= 10
        self.omega_cm = uniform(-2, 2)
        self.receiving_input = True

    @listen('key-down', 'space')
    def flappy_up(self):
        '''Aumenta a velocidade vertical do flappy'''

        if self.receiving_input:
            self.boost((0, 150))

    @listen('key-down', 'left', (0.2,))
    @listen('key-down', 'right', (-0.2,))
    def change_omega(self, delta):
        '''Modifica a velocidade angular do flappy por um fator delta'''

        if self.receiving_input:
            self.omega_cm += delta

    @listen('collision')
    def block_input(self, col=None):
        '''Bloqueia a entrada do usuário'''

        self.receiving_input = False

class Game(World):
    def __init__(self):
        super(Game, self).__init__(gravity=200)

        # Adiciona obstáculos
        self.N = N = 4
        self.obstacles = []
        for i in range(N):
            self.new_obstacle((800 / N) * (i + 1))
        self.listen('frame-enter', self.detect_exit)

        # Adiciona o chão e teto
        self.floor = AABB(bbox=(-400, 400, -400, -290), mass='inf', world=self)
        self.ceiling = AABB(bbox=(-400, 400, 290, 500), mass='inf', world=self)

        # Adiciona o Flappy
        self.flappy = Flappy(world=self)

    def new_obstacle(self, pos_x):
        '''Cria um novo obstáculo na posição pos_x'''

        size = 50
        speed = 50
        middle = uniform(-250 + size, 250 - size)
        lower = AABB(bbox=(pos_x, pos_x + 30, -300, middle - size),
                     mass='inf', vel_cm=(-speed, 0), world=self)
        upper = AABB(bbox=(pos_x, pos_x + 30, middle + size, 300),
                     mass='inf', vel_cm=(-speed, 0), world=self)
        self.obstacles.append([lower, upper])

    def detect_exit(self):
        '''Detecta se um obstáculo saiu da tela e insere um novo em caso 
        afirmativo'''

        L = self.obstacles
        if L[0][0].xmax < -400:
            self.remove(L[0][0])
            self.remove(L[0][1])
            del L[0]
            new_x = L[-1][0].xmin + 800 / self.N
            self.new_obstacle(new_x)

        if self.flappy.xmax < -400:
            self.game_over()

    def game_over(self):
        '''Game over'''

        self.stop()
        GameOver().run()

class GameOver(World):
    def __init__(self):
        super(GameOver, self).__init__(background=(255, 0, 0), gravity=10)
        Poly.rect(shape=(600, 100), pos_cm=(0, -200), theta_cm=pi / 9,
                  centered=True, world=self, mass='inf', color=(255, 0, 0))
        letters = add_word('game over', self, scale=5, pos=(-220, 50))
        for l in letters:
            l.inertia *= 20

        self.listen('key-down', 'enter', self.reinit)

    def reinit(self):
        self.stop()
        Flappy().run()

if __name__ == '__main__':
    Game().run()
