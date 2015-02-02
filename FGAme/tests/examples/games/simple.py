#-*- coding: utf8 -*-
from FGAme import *

# Cria mundo e povoa com dois círculos
world = World()
obj1 = Poly.regular(4, 100)
obj2 = Circle(50, color='red')
world.add([obj1, obj2])

# Modifica algumas propriedades dos círculos
obj1.mass = 10
obj2.mass = 20
obj1.pos_cm = (150, 50)
obj1.vel_cm = (-100, 0)
obj1.move((150, 0))

# Torna o objeto c2 estático
obj2.make_static()
assert obj2.is_dynamic('linear') == False

# Pausa a simulação quando apertar espaço
world.listen('key-down', 'space', world.toggle_pause)

# Controle de gravidade
world.gravity = (0, -50)
world.adamping = 0.1
obj3 = Circle(20, (0, -100), gravity=(20, 50), world=world, color='blue')


# Inicia a simulação
world.run()
