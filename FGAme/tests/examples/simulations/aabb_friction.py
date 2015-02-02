#-*- coding: utf8 -*-_
'''
Este exemplo demonstra a resposta a colisões com atrito utilizando duas caixas 
AABB.
'''

from FGAme import World, AABB

# Cria mundo com coeficiente de atrito global não-nulo
world = World(dfriction=0.1)
world.make_bounds(10, 790, 10, 590)

# Cria objetos
A = AABB(pos_cm=(400, 100), shape=(50, 50), color='black')
B = AABB(pos_cm=(250, 500), shape=(50, 50), vel_cm=(200, -400), color='red')

# Inicia a simulação
world.add([A, B])
world.listen('key-down', 'p', world.toggle_pause)
world.run()
