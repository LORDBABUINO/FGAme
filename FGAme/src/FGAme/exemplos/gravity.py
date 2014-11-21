#-*- coding: utf8 -*-
'''
Implementa o exemplo de "pseudo-gravidade" da documentação.
'''

from FGAme import *
from FGAme.force import SpringF, GravityF

get_mainloop(fps=240)

class Gravity(World):
    def __init__(self):
        # Chamamos o __init__ da classe pai
        super(Gravity, self).__init__()

        # Criamos dois objetos
        A = Circle(20, pos_cm=(100, 0), vel_cm=(100, 300), color='red')
        B = Circle(20, pos_cm=(-100, 0), vel_cm=(-100, -300))
        self.A, self.B = A, B
        self.add([A, B])

        # Definimos a força de interação entre ambos
        K = self.K = A.mass
        F = SpringF(A, B, (K, 2 * K))
        F = GravityF(A, B, 3e4)
        A.external_force, B.external_force = F.forces()

        E0 = F.totalE()
        @self.listen('frame-enter')
        def printP():
            print(F.totalE() / E0)

if __name__ == '__main__':
    Gravity().run()
