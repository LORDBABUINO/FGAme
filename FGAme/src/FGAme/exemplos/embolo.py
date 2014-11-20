#-*- coding: utf8 -*-
'''
Este exemplo mostra um gás de esferas rígidas em contato com um êmbulo sujeito a
uma força viscosa. A energia é dissipada no movimento do êmbolo e aos poucos
as partículas cessam o movimento. 
'''

from FGAme import *
from random import uniform, choice
#set_backend('pygame')

# Inicializa o mundo
class Gas(World):
    def __init__(self, gravity=50, friction=0.0, num_balls=100, speed=200, radius=10):
        '''Cria uma simulação de um gás de partículas confinado por um êmbolo
        com `num_balls` esferas de raio `radius` com velocidades no intervalo 
        de +/-`speed`.'''

        super(Gas, self).__init__(gravity=gravity, dfriction=friction)
        self.make_bounds(-390, 390, -290, 800, delta=400)

        # Inicia bolas
        self.bolas = []
        for _ in range(num_balls):
            pos = Vector(uniform(-380, 380), uniform(-290, 100))
            vel = Vector(uniform(-speed, speed), uniform(-speed, speed))
            bola = Circle(radius=radius, vel_cm=vel, pos_cm=pos, color=(200, 180, 0), mass=1)
            self.bolas.append(bola)
            self.add(bola)

        # Inicia êmbolo
        embolo = AABB(bbox=(-379.9, 379.9, 120, 170), color=(150, 0, 0), mass=num_balls / 2)
        embolo.external_force = lambda t:-100 * embolo.vel_cm
        self.add(embolo)

        # Pausa/continua simulação
        self.listen('key-down', 'space', self.toggle_pause)
        self.listen('long-press', 'up', self.energy_up)
        self.listen('long-press', 'down', self.energy_down)

    def energy_up(self):
        '''Aumenta a energia de todas as partículas'''

        for bola in self.bolas:
            bola.vel_cm *= 1.01

    def energy_down(self):
        '''Diminui a energia de todas as partículas'''

        for bola in self.bolas:
            bola.vel_cm *= 0.99

# Inicia a simulação
if __name__ == '__main__':
    Gas().run()
