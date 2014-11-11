# -*- coding: utf8 -*-

def adjust_overlap(A, B, col=None):
    '''Ajusta a posiçao de dois objetos para que cesse a superposição.'''

    # return NotImplemented
    self.adjust_superposition_aabb(other, dt)

def adjust_superposition_steps(self, other, dt, maxiter=5):
    '''Ajusta a colisão entre os dois objetos para que cesse a superposição.
    
    Pode retornar uma nova tupla de colisão, caso a original mereça ser
    modificada.'''

    return NotImplemented
    self.update(-dt / 4)
    other.update(-dt / 4)

def adjust_overlap_aabb(A, B, col=None):
    '''Implementa adjust_superposition() para as caixas de contorno AABB's.'''

    deltax = shadow_x(self, other)
    deltay = shadow_y(self, other)

    # desloca em y
    if deltax > deltay:
        delta = (0.5 if other.ymin < self.ymin else -0.5) * deltay

        # previne deslocamentos de menos de 1px
        delta = delta if abs(delta) > 2 else 0
        self.move((0, delta))
        other.move((0, -delta))

    # desloca em x
    else:
        delta = (0.5 if other.xmin < self.xmin else -0.5) * deltax

        # previne deslocamentos de menos de 1px
        delta = delta if abs(delta) > 2 else 0
        self.move((delta, 0))
        other.move((-delta, 0))

def avoid_other(A, other, col=None):
    '''Atualiza a própria posição para evitar a colisão com o outro objeto
    na colisão `collision`'''

    return self.avoid_superposition_aabb(other, dt)

    return NotImplemented

def avoid_superposition_steps(self, other, dt, maxiter=5):
    self.update(-dt / 2)

def avoid_superposition_aabb(self, other, dt):
    '''Evita a superposição das caixas de contorno AABB'''

    deltax = shadow_x(self, other)
    deltay = shadow_y(self, other)

    # desloca em y
    if deltax > deltay:
        n = 1 if other.ymin < self.ymin else -1
        self.move((0, n * deltay))
    # desloca em x
    else:
        n = 1 if other.xmin < self.xmin else -1
        self.move((n * deltax, 0))
